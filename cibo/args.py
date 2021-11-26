import json
import re
from ast import literal_eval
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel
from werkzeug.datastructures import ImmutableMultiDict

from .types import MediaType


class BaseApiArgs(BaseModel):
    ...


def get_property(key: str, definitions: dict):
    """从 definitions 中获取参数定义"""
    _property = definitions[key]
    for k, v in _property.get("properties", {}).items():
        if isinstance(v, dict):
            if "items" in v and "$ref" in v["items"]:
                definition_key = v["items"]["$ref"].rsplit("/")[-1]
                _property["properties"][k]["items"] = get_property(definition_key, definitions)
            elif "$ref" in v:
                definition_key = v["$ref"].rsplit("/")[-1]
                _property["properties"][k] = get_property(definition_key, definitions)
            elif "allOf" in v:
                # score_rule: Optional[ScoreRuleSchema]: [{'$ref': '#/definitions/ScoreRuleSchema'}]
                for index, sub_property in enumerate(v["allOf"]):
                    if "$ref" in sub_property:
                        definition_key = sub_property["$ref"].rsplit("/")[-1]
                        _property["properties"][k]["allOf"][index] = get_property(
                            definition_key, definitions
                        )
                _property["properties"][k].pop("title", "")

    return _property


def schema_to_swagger(schema: dict) -> dict:
    """展开并删除 schema 中自动生成的 definitions"""
    definitions = schema.get("definitions", {})
    properties = schema.get("properties", {})
    for k, v in properties.items():
        if "items" in v and "$ref" in v["items"]:
            # rules: List[ScoreRuleItemSchema]
            # {'title': 'Rules', 'type': 'array', 'items': {'$ref': '#/definitions/ScoreRuleItemSchema'}}
            definition_key = v["items"]["$ref"].rsplit("/")[-1]
            properties[k]["items"] = get_property(definition_key, definitions)
        elif "$ref" in v:
            definition_key = v["$ref"].rsplit("/")[-1]
            properties[k] = get_property(definition_key, definitions)
        elif "allOf" in v:
            # score_rule: Optional[ScoreRuleSchema]: [{'$ref': '#/definitions/ScoreRuleSchema'}]
            for index, _ in enumerate(v["allOf"]):
                if "$ref" in v:
                    definition_key = v["$ref"].rsplit("/")[-1]
                    properties[k]["allOf"][index] = get_property(definition_key, definitions)

        properties[k].pop("title", "")
        properties[k].pop("validator", "")
    schema["properties"] = properties
    schema["definitions"] = {}
    return schema


class BaseApiSuccessResp(BaseApiArgs):
    success = True
    status_code = 200
    status_msg = "ok"
    _headers: Dict[str, Any]
    _links: Dict[str, Any]
    _schema_alias: str
    _content_type: MediaType = "application/json"

    @classmethod
    def translate_schema_to_openapi(cls) -> Dict:
        return {
            "description": cls.__doc__ or "Response",
            "headers": getattr(cls, "_headers", {}),
            "links": getattr(cls, "_links", {}),
            "content": {
                "application/json": {
                    "schema": {"$ref": f"#/components/schemas/{cls._schema_alias}"}
                }
            },
        }

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

    # @classmethod
    # def get_swag_body_param(cls):
    #     _swagger = schema_to_swagger(cls.schema())
    #     return {
    #         "in": "body",
    #         "name": "body",
    #         "required": True,
    #         "description": "请求 Body",
    #         "schema": _swagger,
    #     }
    @classmethod
    def translate_schema_to_openapi(cls):
        _schema = cls.schema()
        return {
            "schema": {
                "type": _schema["type"],
                "required": _schema.get("required", []),
                "properties": _schema.get("properties", {}),
            }
        }

    @classmethod
    def get_openapi_request_body(cls):
        components_request_bodies[cls._schema_alias] = cls
        return {"$ref": f"#/components/requestBodies/{cls._schema_alias}"}


class BaseApiQuery(BaseApiArgs):
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

    _schema_alias: str
    # @classmethod
    # def get_swag_query_param(cls) -> List[Dict[str, Union[str, bool]]]:
    #     _schema = schema_to_swagger(cls.schema())
    #     properties = _schema.get("properties", {})
    #     required = _schema.get("required", [])
    #     params = []
    #     for k, v in properties.items():
    #         item = {"in": "query", "name": k}
    #         for _k, _v in v.items():
    #             if _k in ["default", "type", "description", "enum"]:
    #                 item[_k] = _v
    #         item["required"] = k in required
    #         params.append(item)
    #     return params
    @classmethod
    def get_openapi_parameters(cls):
        components_parameters[cls._schema_alias] = cls
        return [
            {"$ref": f"#/components/parameters/{cls._schema_alias}"},
        ]

    @classmethod
    def translate_schema_to_openapi(cls):
        _schema = cls.schema()
        return {
            "name": cls.__name__,
            "in": "query",
            "description": cls.__doc__ or "请求 Query",
            "required": True,
            "deprecated": False,
            "allowEmptyValue": False,
            "schema": _schema,
        }


components_parameters = dict()  # type: Dict[str, Type[BaseApiQuery]]
components_request_bodies = dict()  # type: Dict[str, Type[BaseApiBody]]
components_responses = dict()  # type: Dict[str, Type[BaseApiSuccessResp]]
components_schemas = dict()  # type: Dict[str, Type[BaseModel]]


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


def translate_schema_to_openapi(schema: Dict) -> Dict:
    properties = schema.get("properties", {})
    definitions = schema.get("definitions", {})
    for _, v in properties.items():
        if "allOf" in v:
            for all_of in v["allOf"]:
                if "$ref" in all_of:
                    _name = all_of["$ref"].split("/")[-1]
                    all_of["$ref"] = f"#/components/schemas/{_name}"
                    components_schemas[_name] = definitions.pop(_name) or {}  # type: ignore
        if "$ref" in v:
            _name = v["$ref"].split("/")[-1]
            v["$ref"] = f"#/components/schemas/{_name}"

    return schema
