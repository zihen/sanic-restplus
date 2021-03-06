# -*- coding: utf-8 -*-
import asyncio

from quart import request, Response
from quart.views import MethodView

from .model import ModelBase
from .utils import unpack


class Resource(MethodView):
    """
    Represents an abstract RESTPlus resource.

    Concrete resources should extend from this class
    and expose methods for each supported HTTP method.
    If a resource is invoked with an unsupported HTTP method,
    the API will return a response with status 405 Method Not Allowed.
    Otherwise the appropriate method is called and passed all arguments
    from the url rule used when adding the resource to an Api instance.
    See :meth:`~quart_restplus.Api.add_resource` for details.
    """

    representations = None
    method_decorators = []

    def __init__(self, api=None, *args, **kwargs):
        self.api = api

    async def dispatch_request(self, *args, **kwargs):
        # Taken from quart
        handler = getattr(self, request.method.lower(), None)
        if handler is None and request.method == 'HEAD':
            handler = getattr(self, 'get', None)
        assert handler is not None, 'Unimplemented method %r' % request.method

        for decorator in self.method_decorators:
            handler = decorator(handler)

        await self.validate_payload(handler)

        resp = handler(*args, **kwargs)
        while asyncio.iscoroutine(resp):
            resp = await resp

        if isinstance(resp, Response):
            return resp

        representations = self.representations or {}

        mediatype = request.accept_mimetypes.best_match(representations, default=None)
        if mediatype in representations:
            data, code, headers = unpack(resp)
            resp = representations[mediatype](data, code, headers)
            resp.headers['Content-Type'] = mediatype
            return resp

        return resp

    async def __validate_payload(self, expect, collection=False):
        """
        :param ModelBase expect: the expected model for the input payload
        :param bool collection: False if a single object of a resource is
        expected, True if a collection of objects of a resource is expected.
        """
        # TODO: proper content negotiation
        data = await request.get_json()
        if collection:
            data = data if isinstance(data, list) else [data]
            for obj in data:
                expect.validate(obj, self.api.refresolver, self.api.format_checker)
        else:
            expect.validate(data, self.api.refresolver, self.api.format_checker)

    async def validate_payload(self, func):
        """Perform a payload validation on expected model if necessary"""
        if getattr(func, '__apidoc__', False) is not False:
            doc = func.__apidoc__
            validate = doc.get('validate', None)
            validate = validate if validate is not None else self.api._validate
            if validate:
                for expect in doc.get('expect', []):
                    # TODO: handle third party handlers
                    if isinstance(expect, list) and len(expect) == 1:
                        if isinstance(expect[0], ModelBase):
                            await self.__validate_payload(expect[0], collection=True)
                    if isinstance(expect, ModelBase):
                        await self.__validate_payload(expect, collection=False)
