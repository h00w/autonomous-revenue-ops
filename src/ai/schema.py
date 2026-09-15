from copy import deepcopy
from typing import Type

from pydantic import BaseModel


def strict_model_schema(model_type: Type[BaseModel]) -> dict:
    """Return a JSON schema suitable for strict structured-output APIs."""
    schema = deepcopy(model_type.model_json_schema())

    def normalize(node: object) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object":
                node.setdefault("additionalProperties", False)
            for value in node.values():
                normalize(value)
        elif isinstance(node, list):
            for value in node:
                normalize(value)

    normalize(schema)
    return schema
