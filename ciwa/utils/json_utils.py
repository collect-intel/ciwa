# utils/json_utils.py


import jsonschema
from jsonschema import Draft7Validator
import random
import uuid
from typing import Any, Dict, List, Union
import string
import json
import re


def generate_random_text(length=10) -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def generate_fake_json(schema: Dict[str, Any]) -> Dict[str, Any]:
    def generate_value(prop_schema: Dict[str, Any]) -> Any:
        if "enum" in prop_schema:
            return random.choice(prop_schema["enum"])
        if prop_schema["type"] == "boolean":
            return random.choice([True, False])
        elif prop_schema["type"] == "integer":
            minimum = prop_schema.get("minimum", 1)
            maximum = prop_schema.get("maximum", 100)
            return random.randint(minimum, maximum)
        elif prop_schema["type"] == "string":
            return generate_random_text()
        elif prop_schema["type"] == "array":
            item_schema = prop_schema["items"]
            min_items = prop_schema.get("minItems", 1)
            max_items = prop_schema.get("maxItems", 5)
            if prop_schema.get("uniqueItems", False):
                range_min = item_schema.get("minimum", 1)
                range_max = item_schema.get("maximum", 100)
                return random.sample(range(range_min, range_max + 1), max_items)
            else:
                return [
                    generate_value(item_schema)
                    for _ in range(random.randint(min_items, max_items))
                ]
        elif prop_schema["type"] == "object":
            return generate_fake_json(prop_schema)
        return None

    return {
        prop: generate_value(prop_schema)
        for prop, prop_schema in schema["properties"].items()
    }


def extract_json(text: str) -> str:
    """
    Extracts the JSON string from the LLM response text.

    Args:
        text (str): The LLM response.

    Returns:
        str: The extracted JSON string.
    """
    # Try to find JSON enclosed in code blocks first
    json_pattern_code_block = r"```json\s*([\s\S]*?)\s*```"
    match = re.search(json_pattern_code_block, text)
    if match:
        return match.group(1)

    # Try to find standalone JSON objects in the text
    stack = []
    json_str = ""
    inside_json = False

    for char in text:
        if char == "{":
            stack.append(char)
            inside_json = True
        if inside_json:
            json_str += char
        if char == "}":
            stack.pop()
            if not stack:
                inside_json = False
                try:
                    json.loads(json_str)
                    return json_str
                except json.JSONDecodeError:
                    json_str = ""

    return ""


def extract_json_schema(text: str) -> dict:
    # Define a regular expression pattern to match JSON-like structures
    # pattern = re.compile(r"\{[^{}]*\}")
    # Use a greedy match for the content between the opening { and closing }
    schema_regex = r'"\$schema":.+\}'
    pattern = re.compile(schema_regex, re.DOTALL)

    # Find all matches in the text
    matches = pattern.findall(text)

    for match in matches:
        try:
            # Attempt to parse each match as JSON
            json_obj = json.loads("{" + match.replace("'", '"'))
            # Check for the presence of the $schema key
            if "$schema" in json_obj:
                validate_schema(json_obj)
                return json_obj
        except json.JSONDecodeError:
            continue

    import pdb

    pdb.set_trace()
    # If no valid JSON schema is found, return None
    return None


def is_valid_json_for_schema(json_data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    try:
        jsonschema.validate(instance=json_data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError:
        return False


def get_json(input_data: Union[str, Dict[str, Any]]) -> Union[Dict[str, Any], None]:
    """
    Convert input data to JSON if it's a valid JSON string or return it if it's a dictionary.

    Args:
        input_data (Union[str, Dict[str, Any]]): The input data to check and convert.

    Returns:
        Union[Dict[str, Any], None]: The valid JSON data as a dictionary or None if invalid.
    """
    if isinstance(input_data, str):
        try:
            data = json.loads(input_data)
            return data
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e.msg}")
            return None
    elif isinstance(input_data, dict):
        return input_data
    else:
        print("Invalid input type. Must be a JSON string or a dictionary.")
        return None


def get_json_string(data: Dict[str, Any]) -> str:
    """
    Convert a dictionary to a JSON string.

    Args:
        data (Dict[str, Any]): The dictionary to convert.

    Returns:
        str: The JSON string representation of the dictionary.
    """
    return json.dumps(data, indent=2)


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


class SchemaFactory:
    """
    A factory class for creating and validating JSON schemas for model objects.

    Attributes:
        OBJECT_TYPES (List[str]): The list of supported object types.
    """

    OBJECT_TYPES = ["vote", "submission", "topic", "content", "submissions"]

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
        validate_schema(schema)
        return schema
