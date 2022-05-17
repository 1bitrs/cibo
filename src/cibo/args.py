import json
import re
from ast import literal_eval
from typing import Any, Dict, List, Optional, Type, Union, cast

from pydantic import BaseModel
from werkzeug.datastructures import ImmutableMultiDict

from .types import MediaType

__all__ = ["BaseApiArgs", "BaseApiPath", "BaseApiSuccessResp", "BaseApiBody", "BaseApiQuery"]


class BaseApiArgs(BaseModel):
    _schema_alias: str


class BaseApiPath(BaseApiArgs):
    @classmethod
    def parse_path_args(cls, path: dict) -> "BaseApiPath":
        return cls.parse_obj(path)

    @classmethod
    def get_openapi_path(cls) -> List[Dict]:
        properties = cls.schema().get("properties", {})
        required = cls.schema().get("required", [])
        _schema = list()
        for k, v in properties.items():
            _schema.append(
                {
                    "in": "path",
                    "required": k in required,
                    "name": k,
                    "description": v.get("description", ""),
                    "schema": {"type": v.get("type")},
                    "styple": "simple",
                }
            )

        return _schema


class BaseApiSuccessResp(BaseApiArgs):
    success: bool = True
    status_code = 200
    status_msg = "ok"
    _headers: Dict[str, Any]
    _links: Dict[str, Any]
    _schema_alias: str
    _content_type: MediaType = "application/json"

    @classmethod
    def get_openapi_response(cls) -> Dict:
        components_responses[cls._schema_alias] = cls
        return {"$ref": f"#/components/responses/{cls._schema_alias}"}


class BaseApiBody(BaseApiArgs):
    _schema_alias: str
    _content_type: MediaType = "application/json"

    @classmethod
    def parse_form_args(cls, form: ImmutableMultiDict) -> "BaseApiBody":
        obj_dict = dict(form)
        for field_name, field in cls.__fields__.items():
            if field.outer_type_ not in (str, list, set, tuple, dict):
                _name = field.alias or field_name
                _value: Optional[str] = form.get(_name, None)
                if _value is not None:
                    if re.match(r"\[.*\]", _value):
                        obj_dict[_name] = literal_eval(_value)
                    elif re.match(r"{.*}", _value):
                        obj_dict[_name] = json.loads(_value)

        return cls.parse_obj(obj_dict)

    @classmethod
    def get_openapi_request_body(cls):
        components_request_bodies[cls._schema_alias] = cls
        return {"$ref": f"#/components/requestBodies/{cls._schema_alias}"}


class BaseApiQuery(BaseApiArgs):
    _schema_alias: str

    @classmethod
    def parse_request_args(cls, query: ImmutableMultiDict) -> "BaseApiQuery":
        obj_dict = dict(query)
        for field_name, field in cls.__fields__.items():
            if hasattr(field.outer_type_, "__origin__") and field.outer_type_.__origin__ in (
                list,
                set,
                tuple,
                dict,
            ):
                _name = field.alias or field_name
                _value: Optional[str] = query.get(_name, None)
                if _value is not None:
                    if re.match(r"\[.*\]", _value):
                        obj_dict[_name] = literal_eval(_value)
                    elif re.match(r"{.*}", _value):
                        obj_dict[_name] = json.loads(_value)
        return cls.parse_obj(obj_dict)

    @classmethod
    def get_openapi_parameters(cls):
        components_parameters[cls._schema_alias] = cls
        return [
            {"$ref": f"#/components/parameters/{cls._schema_alias}"},
        ]


components_parameters = dict()  # type: Dict[str, Type[BaseApiQuery]]
components_request_bodies = dict()  # type: Dict[str, Type[BaseApiBody]]
components_responses = dict()  # type: Dict[str, Type[BaseApiSuccessResp]]
components_schemas = dict()  # type: Dict[str, Union[Type[BaseModel], dict]]
_extra_definitions = dict()  # type: Dict[str, Dict]


def _destory():  # type:ignore
    global components_parameters
    global components_request_bodies
    global components_responses
    global components_schemas
    global _extra_definitions

    components_parameters.clear()
    components_request_bodies.clear()
    components_responses.clear()
    components_schemas.clear()
    _extra_definitions.clear()

    del components_parameters
    del components_request_bodies
    del components_responses
    del components_schemas
    del _extra_definitions


def translate_schema_to_openapi(args_class: Union[Type[BaseModel], dict]) -> dict:
    if type(args_class) is dict:
        schema: dict = cast(dict, args_class)
    else:
        args_class = cast(Type[BaseApiArgs], args_class)
        schema: dict = args_class.schema()
    properties = schema.get("properties", {})
    definitions = schema.get("definitions", {})

    def _handle_array(v: Dict):
        items = v.get("items", None)  # type: Optional[Union[List, Dict]]
        if not items:
            return
        elif type(items) is list:
            return
        elif type(items) is dict:
            if "$ref" in items:
                _handle_ref(items)
            elif items["type"] == "object":
                _handle_object(items)

    def _handle_object(v: Dict[str, Dict]):
        if "additionalProperties" in v:
            if "$ref" in v["additionalProperties"]:
                _handle_ref(v["additionalProperties"])

    def _handle_ref(value: Dict):
        _name: str = value["$ref"].split("/")[-1]
        innter_schema_class = getattr(args_class, _name, type)
        if issubclass(innter_schema_class, BaseModel):
            # 在Query、Body、Resp内部的BaseModel类，避免schema之间重名
            _name_alias = f"{args_class._schema_alias}${innter_schema_class.__name__}"  # type: ignore
            setattr(innter_schema_class, "_schema_alias", _name_alias)
            components_schemas[_name_alias] = innter_schema_class
        else:
            _name_alias = _name
            if _name in definitions:
                components_schemas[_name_alias] = definitions.pop(_name)
            else:
                if _name in _extra_definitions:
                    components_schemas[_name_alias] = _extra_definitions.pop(_name)

        value["$ref"] = f"#/components/schemas/{_name_alias}"

    def _handle_all_of(all_of_list: List[Dict[str, str]]):
        for all_of in all_of_list:
            if "$ref" in all_of:
                _handle_ref(all_of)

    def _handle_any_of(any_of_list: List[Dict[str, str]]):
        for any_of in any_of_list:
            if "$ref" in any_of:
                _handle_ref(any_of)

    for _, v in properties.items():
        if v.get("type") == "object":
            _handle_object(v)
        elif v.get("type") == "array":
            _handle_array(v)
        elif v.get("$ref"):
            _handle_ref(v)
        elif v.get("allOf"):
            _handle_all_of(v["allOf"])
        elif v.get("anyOf"):
            _handle_any_of(v["anyOf"])

    if "definitions" in schema:
        _extra_definitions.update(schema["definitions"])
        del schema["definitions"]

    return schema


# def translate_schema_to_openapi(args_class) -> Dict[str, Union[str, bool, int, List, Dict]]:
#     if type(args_class) is dict:
#         schema = args_class
#     else:
#         schema = args_class.schema()
#     properties = schema.get("properties", {})
#     definitions = schema.get("definitions", {})

#     def _handle_array(v: Dict):
#         items = v.get("items", None)  # type: Optional[Union[List, Dict]]
#         if not items:
#             return
#         elif type(items) is list:
#             return
#         elif type(items) is dict:
#             if "$ref" in items:
#                 _handle_ref(items)
#             elif items["type"] == "object":
#                 _handle_object(items)

#     def _handle_object(v: Dict[str, Dict]):
#         if "additionalProperties" in v:
#             if "$ref" in v["additionalProperties"]:
#                 _handle_ref(v["additionalProperties"])

#     def _handle_ref(value: Dict):
#         _name: str = value["$ref"].split("/")[-1]
#         innter_schema_class = getattr(args_class, _name, type)
#         if issubclass(innter_schema_class, BaseModel):
#             # 在Query、Body、Resp内部的BaseModel类，避免schema之间重名
#             _name_alias = f"{args_class._schema_alias}${innter_schema_class.__name__}"
#         else:
#             _name_alias = _name

#         value["$ref"] = f"#/components/schemas/{_name_alias}"
#         if _name in definitions:
#             definition = definitions.pop(_name)
#             components_schemas[_name_alias] = _handle_definitions(definition)

#     def _handle_all_of(all_of_list: List[Dict[str, str]]):
#         for all_of in all_of_list:
#             if "$ref" in all_of:
#                 _handle_ref(all_of)

#     def _handle_definitions(v: Dict[str, Dict]):
#         return translate_schema_to_openapi(v)

#     for _, v in properties.items():
#         if v.get("type") == "object":
#             _handle_object(v)
#         elif v.get("type") == "array":
#             _handle_array(v)
#         elif v.get("$ref"):
#             _handle_ref(v)
#         elif v.get("allOf"):
#             _handle_all_of(v["allOf"])

#     if definitions:
#         components_schemas.update(definitions)

#     if "definitions" in schema:
#         del schema["definitions"]

#     return schema


# def translate_schema_to_openapi(args_class: Type[BaseApiArgs]) -> Dict:
#     schema = args_class.schema()
#     properties = schema.get("properties", {})
#     definitions = schema.get("definitions", {})
#     for _, v in properties.items():
#         if "allOf" in v:
#             for all_of in v["allOf"]:
#                 if "$ref" in all_of:
#                     _name = all_of["$ref"].split("/")[-1]
#                     all_of["$ref"] = f"#/components/schemas/{_name}"
#                     components_schemas[_name] = definitions.pop(_name) or {}
#         if "$ref" in v:
#             _name: str = v["$ref"].split("/")[-1]
#             innter_schema_class = getattr(args_class, _name, type)
#             if issubclass(innter_schema_class, BaseModel):
#                 # 内部的BaseModel类，避免schema之间重名
#                 _name_alias = f"{args_class._schema_alias}${innter_schema_class.__name__}"
#             else:
#                 _name_alias = _name

#             v["$ref"] = f"#/components/schemas/{_name_alias}"
#             components_schemas[_name_alias] = definitions.pop(_name)
#         if "items" in v:
#             if "$ref" in v["items"]:
#                 _name: str = v["items"]["$ref"].split("/")[-1]
#                 innter_schema_class = getattr(args_class, _name, type)
#                 if issubclass(innter_schema_class, BaseModel):
#                     # 内部的BaseModel类，避免schema之间重名
#                     _name_alias = f"{args_class._schema_alias}${innter_schema_class.__name__}"
#                 else:
#                     _name_alias = _name

#                 v["items"]["$ref"] = f"#/components/schemas/{_name_alias}"
#                 components_schemas[_name_alias] = definitions.pop(_name)

#     if "definitions" in schema:
#         del schema["definitions"]
#     return schema
