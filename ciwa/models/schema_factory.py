# filename: ciwa/models/schema_factory.py

from typing import Dict, Any
import jsonschema
from jsonschema import Draft7Validator


class SchemaFactory:
    OBJECT_TYPES = ["vote", "submission", "topic"]

    @staticmethod
    def create_object_schema(
        object_type: str, object_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates a schema for a model object. For consistency json for objects should take the form {"object_type": <something>},
        where <something> is defined by the object_schema.
        """
        if object_type not in SchemaFactory.OBJECT_TYPES:
            raise ValueError(
                f"Unsupported object_type for schema: {object_type}. Supported types are: {SchemaFactory.OBJECT_TYPES}"
            )

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {object_type: object_schema},
            "required": [object_type],
            "additionalProperties": False,
        }
        SchemaFactory.validate_schema(schema)
        return schema

    @staticmethod
    def validate_schema(schema: Dict[str, Any]) -> None:
        try:
            Draft7Validator.check_schema(schema)
        except jsonschema.exceptions.SchemaError as e:
            raise ValueError(f"Invalid schema: {e.message}")
