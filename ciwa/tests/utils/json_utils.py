# tests/utils/json_utils.py

import random
import uuid
from typing import Any, Dict, List, Union
import string
import jsonschema
import json


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
