# models/schema_factory.py

"""
This module provides the SchemaFactory class for creating and validating JSON schemas
for different types of objects, such as votes, submissions, and topics.
"""

from typing import Dict, Any
import jsonschema
from jsonschema import Draft7Validator


class SchemaFactory:
    """
    A factory class for creating and validating JSON schemas for model objects.

    Attributes:
        OBJECT_TYPES (List[str]): The list of supported object types.
    """

    OBJECT_TYPES = ["vote", "submission", "topic"]

    @staticmethod
    def create_object_schema(
        object_type: str, object_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates a schema for a model object. For consistency, JSON for objects should take
        the form {"object_type": <something>}, where <something> is defined by the object_schema.

        Args:
            object_type (str): The type of object for which to create the schema.
            object_schema (Dict[str, Any]): The schema definition for the object.

        Returns:
            Dict[str, Any]: The complete schema for the object.

        Raises:
            ValueError: If the object_type is not supported.
        """
        if object_type not in SchemaFactory.OBJECT_TYPES:
            raise ValueError(
                f"Unsupported object_type for schema: {object_type}. Supported types are: "
                f"{SchemaFactory.OBJECT_TYPES}"
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
        """
        Validates a JSON schema.

        Args:
            schema (Dict[str, Any]): The schema to validate.

        Raises:
            ValueError: If the schema is invalid.
        """
        try:
            Draft7Validator.check_schema(schema)
        except jsonschema.exceptions.SchemaError as e:
            raise ValueError(f"Invalid schema: {e.message}") from e
