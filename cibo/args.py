import json
import re
from ast import literal_eval
from typing import Optional

from pydantic import BaseModel
from werkzeug.datastructures import ImmutableMultiDict


class BaseApiArgs(BaseModel):
    ...


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
