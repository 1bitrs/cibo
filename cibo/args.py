import json
import re
from ast import literal_eval
from typing import Dict, List, Optional, Union

from pydantic import BaseModel
from werkzeug.datastructures import ImmutableMultiDict


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


class BaseApiArgs(BaseModel):
    ...


class BaseApiSuccessResp(BaseApiArgs):
    success = True
    status_code = 200
    status_msg = "ok"

    @classmethod
    def get_swag_resp_schema(cls) -> Dict:
        return schema_to_swagger(cls.schema())


class BaseApiBody(BaseApiArgs):
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
    def get_swag_body_param(cls):
        _swagger = schema_to_swagger(cls.schema())
        return {
            "in": "body",
            "name": "body",
            "required": True,
            "description": "请求 Body",
            "schema": _swagger,
        }


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

    @classmethod
    def get_swag_query_param(cls) -> List[Dict[str, Union[str, bool]]]:
        _schema = schema_to_swagger(cls.schema())
        properties = _schema.get("properties", {})
        required = _schema.get("required", [])
        params = []
        for k, v in properties.items():
            item = {"in": "query", "name": k}
            for _k, _v in v.items():
                if _k in ["default", "type", "description", "enum"]:
                    item[_k] = _v
            item["required"] = k in required
            params.append(item)
        return params
