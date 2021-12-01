import json
import re
from ast import literal_eval
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel
from werkzeug.datastructures import ImmutableMultiDict

from .types import MediaType


class BaseApiArgs(BaseModel):
    _schema_alias: str


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
components_schemas = dict()  # type: Dict


def _destory():  # type:ignore
    global components_parameters
    global components_request_bodies
    global components_responses
    global components_schemas

    components_parameters.clear()
    components_request_bodies.clear()
    components_responses.clear()
    components_schemas.clear()

    del components_parameters
    del components_request_bodies
    del components_responses
    del components_schemas


def translate_schema_to_openapi(args_class: Type[BaseApiArgs]) -> Dict:
    schema = args_class.schema()
    properties = schema.get("properties", {})
    definitions = schema.get("definitions", {})
    for _, v in properties.items():
        if "allOf" in v:
            for all_of in v["allOf"]:
                if "$ref" in all_of:
                    _name = all_of["$ref"].split("/")[-1]
                    all_of["$ref"] = f"#/components/schemas/{_name}"
                    components_schemas[_name] = definitions.pop(_name) or {}
        if "$ref" in v:
            _name: str = v["$ref"].split("/")[-1]
            innter_schema_class = getattr(args_class, _name, type)
            if issubclass(innter_schema_class, BaseModel):
                # 内部的BaseModel类，避免schema之间重名
                _name_alias = f"{args_class._schema_alias}${innter_schema_class.__name__}"
            else:
                _name_alias = _name

            v["$ref"] = f"#/components/schemas/{_name_alias}"
            components_schemas[_name_alias] = definitions.pop(_name)

    if "definitions" in schema:
        del schema["definitions"]
    return schema
