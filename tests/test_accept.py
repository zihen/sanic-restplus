# -*- coding: utf-8 -*-
import quart_restplus as restplus


class Foo(restplus.Resource):
    async def get(self):
        return 'data'


async def test_accept_default_application_json(app, client):
    api = restplus.Api(app)
    api.add_resource(Foo, '/test/')

    res = await client.get('/test/')
    assert res.status_code == 200
    assert res.content_type == 'application/json'


async def test_accept_application_json_by_default(app, client):
    api = restplus.Api(app)
    api.add_resource(Foo, '/test/')

    res = await client.get('/test/', headers=[('Accept', 'application/json')])
    assert res.status_code == 200
    assert res.content_type == 'application/json'


async def test_accept_no_default_match_acceptable(app, client):
    api = restplus.Api(app, default_mediatype=None)
    api.add_resource(Foo, '/test/')

    res = await client.get('/test/', headers=[('Accept', 'application/json')])
    assert res.status_code == 200
    assert res.content_type == 'application/json'


async def test_accept_default_override_accept(app, client):
    api = restplus.Api(app)
    api.add_resource(Foo, '/test/')

    res = await client.get('/test/', headers=[('Accept', 'text/plain')])
    assert res.status_code == 200
    assert res.content_type == 'application/json'


async def test_accept_default_any_pick_first(app, client):
    api = restplus.Api(app)

    @api.representation('text/plain')
    def text_rep(data, status_code, headers=None):
        resp = app.make_response((str(data), status_code, headers))
        return resp

    api.add_resource(Foo, '/test/')

    res = await client.get('/test/', headers=[('Accept', '*/*')])
    assert res.status_code == 200
    assert res.content_type == 'application/json'


async def test_accept_no_default_no_match_not_acceptable(app, client):
    api = restplus.Api(app, default_mediatype=None)
    api.add_resource(Foo, '/test/')

    res = await client.get('/test/', headers=[('Accept', 'text/plain')])
    assert res.status_code == 406
    assert res.content_type == 'application/json'


async def test_accept_no_default_custom_repr_match(app, client):
    api = restplus.Api(app, default_mediatype=None)
    api.representations = {}

    @api.representation('text/plain')
    def text_rep(data, status_code, headers=None):
        resp = app.make_response((str(data), status_code, headers))
        return resp

    api.add_resource(Foo, '/test/')

    res = await client.get('/test/', headers=[('Accept', 'text/plain')])
    assert res.status_code == 200
    assert res.content_type == 'text/plain'


async def test_accept_no_default_custom_repr_not_acceptable(app, client):
    api = restplus.Api(app, default_mediatype=None)
    api.representations = {}

    @api.representation('text/plain')
    def text_rep(data, status_code, headers=None):
        resp = app.make_response((str(data), status_code, headers))
        return resp

    api.add_resource(Foo, '/test/')

    res = await client.get('/test/', headers=[('Accept', 'application/json')])
    assert res.status_code == 406
    assert res.content_type == 'text/plain'


async def test_accept_no_default_match_q0_acceptable(app, client):
    api = restplus.Api(app, default_mediatype=None)
    api.add_resource(Foo, '/test/')

    res = await client.get('/test/', headers=[('Accept', 'application/json; q=0')])
    assert res.status_code == 200
    assert res.content_type == 'application/json'


async def test_accept_no_default_accept_highest_quality_of_two(app, client):
    api = restplus.Api(app, default_mediatype=None)

    @api.representation('text/plain')
    def text_rep(data, status_code, headers=None):
        resp = app.make_response((str(data), status_code, headers))
        return resp

    api.add_resource(Foo, '/test/')

    res = await client.get('/test/', headers=[('Accept', 'application/json; q=0.1, text/plain; q=1.0')])
    assert res.status_code == 200
    assert res.content_type == 'text/plain'


async def test_accept_no_default_accept_highest_quality_of_three(app, client):
    api = restplus.Api(app, default_mediatype=None)

    @api.representation('text/html')
    @api.representation('text/plain')
    def text_rep(data, status_code, headers=None):
        resp = app.make_response((str(data), status_code, headers))
        return resp

    api.add_resource(Foo, '/test/')

    res = await client.get('/test/',
                           headers=[('Accept', 'application/json; q=0.1, text/plain; q=0.3, text/html; q=0.2')])
    assert res.status_code == 200
    assert res.content_type == 'text/plain'


async def test_accept_no_default_no_representations(app, client):
    api = restplus.Api(app, default_mediatype=None)
    api.representations = {}

    api.add_resource(Foo, '/test/')

    res = await client.get('/test/', headers=[('Accept', 'text/plain')])
    assert res.status_code == 406
    assert res.content_type == 'text/plain'


async def test_accept_invalid_default_no_representations(app, client):
    api = restplus.Api(app, default_mediatype='nonexistant/mediatype')
    api.representations = {}

    api.add_resource(Foo, '/test/')

    res = await client.get('/test/', headers=[('Accept', 'text/plain')])
    assert res.status_code == 500
