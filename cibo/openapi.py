from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

if TYPE_CHECKING:

    from .blueprint import Blueprint


def get_tag(
    blueprint,  # type: Blueprint
    blueprint_name: str,
) -> Dict[str, Any]:
    """Get tag from blueprint objec"""
    tag: Dict[str, Any]
    _tag = getattr(blueprint, "openapi_tag", None)  # type: Optional[Union[dict, str]]
    if _tag:
        if isinstance(_tag, dict):
            tag = _tag
        else:
            tag = {"name": _tag, "description": blueprint.tag_description}
    else:
        tag = {"name": blueprint_name, "description": blueprint.tag_description}
    return tag


def get_operation_tags(
    blueprint,  # type: Blueprint
    blueprint_name: str,
) -> List[str]:
    """Get operation tag from blueprint objec"""
    tags: List[str]
    tag = getattr(blueprint, "tag", None)  # type: Optional[Union[dict, str]]
    if tag:
        if isinstance(tag, dict):
            tags = [tag["name"]]
        else:
            tags = [tag]
    else:
        tags = [blueprint_name.title()]
    return tags


def get_path_description(func: Callable) -> str:
    """Get path description from the docstring of the view function."""
    docs = (func.__doc__ or "").strip().split("\n")
    if len(docs) > 1:
        # use the remain lines of docstring as description
        return "\n".join(docs[1:]).strip()
    return ""


def add_response(
    operation: dict,
    status_code: str,
    schema,
    description: str,
    example: Optional[Any] = None,
    examples: Optional[Dict[str, Any]] = None,
    links: Optional[Dict[str, Any]] = None,
) -> None:
    """Add response to operation."""
    operation["responses"][status_code] = {}
    if status_code != "204":
        operation["responses"][status_code]["content"] = {"application/json": {"schema": schema}}
    operation["responses"][status_code]["description"] = description
    if example is not None:
        operation["responses"][status_code]["content"]["application/json"]["example"] = example
    if examples is not None:
        operation["responses"][status_code]["content"]["application/json"]["examples"] = examples
    if links is not None:
        operation["responses"][status_code]["links"] = links


def add_response_with_schema(
    spec, operation: dict, status_code: str, schema, schema_name: str, description: str  # APISpec
) -> None:
    """Add response with given schema to operation."""
    if isinstance(schema, type):
        schema = schema()
        add_response(operation, status_code, schema, description)
    elif isinstance(schema, dict):
        if schema_name not in spec.components.schemas:
            spec.components.schema(schema_name, schema)
        schema_ref = {"$ref": f"#/components/schemas/{schema_name}"}
        add_response(operation, status_code, schema_ref, description)
    else:
        raise TypeError()


def get_argument(argument_type: str, argument_name: str) -> Dict[str, Any]:
    """Make argument from given type and name."""
    argument: Dict[str, Any] = {
        "in": "path",
        "name": argument_name,
    }
    if argument_type == "int:":
        argument["schema"] = {"type": "integer"}
    elif argument_type == "float:":
        argument["schema"] = {"type": "number"}
    else:
        argument["schema"] = {"type": "string"}
    return argument
