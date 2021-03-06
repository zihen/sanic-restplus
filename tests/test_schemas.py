# -*- coding: utf-8 -*-
import pytest

from jsonschema import ValidationError

from quart_restplus import errors, schemas


class TestSchemas:
    def test_lazyness(self):
        schema = schemas.LazySchema('oas-2.0.json')
        assert schema._schema is None

        _ = '' in schema  # Trigger load
        assert schema._schema is not None
        assert isinstance(schema._schema, dict)

    def test_oas2_schema_is_present(self):
        assert hasattr(schemas, 'OAS_20')
        assert isinstance(schemas.OAS_20, schemas.LazySchema)


class TestValidation:
    def test_oas_20_valid(self):
        assert schemas.validate({
            'swagger': '2.0',
            'info': {
                'title': 'An empty minimal specification',
                'version': '1.0',
            },
            'paths': {},
        })

    def test_oas_20_invalid(self):
        with pytest.raises(schemas.SchemaValidationError) as excinfo:
            schemas.validate({
                'swagger': '2.0',
                'should': 'not be here',
            })
        for error in excinfo.value.errors:
            assert isinstance(error, ValidationError)

    def test_unknown_schema(self):
        with pytest.raises(errors.SpecsError):
            schemas.validate({'valid': 'no'})

    def test_unknown_version(self):
        with pytest.raises(errors.SpecsError):
            schemas.validate({'swagger': '42.0'})
