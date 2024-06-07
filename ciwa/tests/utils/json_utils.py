import random
import uuid
from typing import Any, Dict, List
import string


def generate_random_text(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits + " ", k=length))


def generate_fake_json(schema: Dict[str, Any]) -> Dict[str, Any]:
    def generate_value(prop_schema: Dict[str, Any]) -> Any:
        if "enum" in prop_schema:
            return random.choice(prop_schema["enum"])
        if prop_schema["type"] == "boolean":
            return random.choice([True, False])
        elif prop_schema["type"] == "integer":
            return random.randint(1, 100)
        elif prop_schema["type"] == "string":
            return generate_random_text()
        elif prop_schema["type"] == "array":
            item_schema = prop_schema["items"]
            return [generate_value(item_schema) for _ in range(random.randint(1, 5))]
        elif prop_schema["type"] == "object":
            return generate_fake_json(prop_schema)
        return None

    return {
        prop: generate_value(prop_schema)
        for prop, prop_schema in schema["properties"].items()
    }
