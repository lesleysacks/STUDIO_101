"""Subset JSON Schema validator with file and JSON-path errors.

Supported keywords: type, properties, required, additionalProperties, items,
minItems, maxItems, minLength, maxLength, minimum, maximum, pattern, enum,
default, and local ``#/definitions/...`` references. Unknown keywords are
ignored so the files stay readable as JSON Schema.
"""

from __future__ import annotations

import re
from typing import Any

from .errors import ConfigIssue

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
}


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    python_type = _TYPES.get(expected)
    return python_type is not None and isinstance(value, python_type)


def _deref(root: dict, schema: dict, file: str, path: str) -> dict:
    if "$ref" not in schema:
        return schema
    ref = schema["$ref"]
    if not isinstance(ref, str) or not ref.startswith("#/"):
        raise ValueError(str(ConfigIssue("error", file, path, f"Unsupported schema reference {ref!r}.")))
    node: Any = root
    for part in ref[2:].split("/"):
        if not isinstance(node, dict) or part not in node:
            raise ValueError(str(ConfigIssue("error", file, path, f"Schema reference {ref!r} cannot be resolved.")))
        node = node[part]
    if not isinstance(node, dict):
        raise ValueError(str(ConfigIssue("error", file, path, f"Schema reference {ref!r} is not an object.")))
    return node


def apply_defaults(schema: dict, data: Any, root: dict | None = None) -> Any:
    """Fill missing object properties from schema defaults. Does not invent content."""
    root = schema if root is None else root
    schema = _deref(root, schema, "", "$")
    if schema.get("type") == "object" and isinstance(data, dict):
        for key, prop in schema.get("properties", {}).items():
            prop = _deref(root, prop, "", f"$.{key}")
            if key not in data and "default" in prop:
                data[key] = prop["default"]
            if key in data:
                apply_defaults(prop, data[key], root)
    elif schema.get("type") == "array" and isinstance(data, list):
        item_schema = schema.get("items", {})
        for item in data:
            apply_defaults(item_schema, item, root)
    return data


def validate_schema(schema: dict, data: Any, file: str, path: str = "$", root: dict | None = None) -> list[ConfigIssue]:
    root = schema if root is None else root
    try:
        schema = _deref(root, schema, file, path)
    except ValueError as exc:
        return [ConfigIssue("error", file, path, str(exc))]

    issues: list[ConfigIssue] = []
    expected = schema.get("type")
    if expected and not _matches_type(data, expected):
        issues.append(ConfigIssue("error", file, path, f"Expected {expected}, got {type(data).__name__}."))
        return issues

    if "enum" in schema and data not in schema["enum"]:
        allowed = ", ".join(repr(item) for item in schema["enum"])
        issues.append(ConfigIssue("error", file, path, f"Value {data!r} is not one of: {allowed}."))

    if expected == "object":
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in data:
                issues.append(ConfigIssue("error", file, f"{path}.{key}", "This field is required."))
        additional = schema.get("additionalProperties", True)
        for key, value in data.items():
            child = f"{path}.{key}"
            if key in properties:
                issues.extend(validate_schema(properties[key], value, file, child, root))
            elif additional is False:
                issues.append(ConfigIssue("error", file, child, "Unknown field."))
    elif expected == "array":
        minimum = schema.get("minItems")
        maximum = schema.get("maxItems")
        if minimum is not None and len(data) < minimum:
            issues.append(ConfigIssue("error", file, path, f"Expected at least {minimum} item(s)."))
        if maximum is not None and len(data) > maximum:
            issues.append(ConfigIssue("error", file, path, f"Expected at most {maximum} item(s)."))
        item_schema = schema.get("items", {})
        for index, item in enumerate(data):
            issues.extend(validate_schema(item_schema, item, file, f"{path}[{index}]", root))
    elif expected == "string":
        if "minLength" in schema and len(data) < schema["minLength"]:
            issues.append(ConfigIssue("error", file, path, f"Shorter than the minimum length of {schema['minLength']}."))
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            issues.append(ConfigIssue("error", file, path, f"Longer than the maximum length of {schema['maxLength']}."))
        if "pattern" in schema and re.fullmatch(schema["pattern"], data) is None:
            issues.append(ConfigIssue("error", file, path, f"Does not match the required pattern {schema['pattern']}."))
    elif expected in {"integer", "number"}:
        if "minimum" in schema and data < schema["minimum"]:
            issues.append(ConfigIssue("error", file, path, f"Below the minimum of {schema['minimum']}."))
        if "maximum" in schema and data > schema["maximum"]:
            issues.append(ConfigIssue("error", file, path, f"Above the maximum of {schema['maximum']}."))
    return issues
