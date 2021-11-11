import json

from pydantic import BaseModel
from werkzeug.datastructures import ImmutableMultiDict


class BaseApiArgs(BaseModel):
    ...


class BaseApiBody(BaseApiArgs):
    ...


class BaseApiQuery(BaseApiArgs):
    @classmethod
    def parse_request_args(cls, obj: ImmutableMultiDict) -> "BaseApiQuery":
        obj_dict = dict(obj).copy()
        for field_name, field in cls.__fields__.items():
            if hasattr(field.outer_type_, "__origin__") and field.outer_type_.__origin__ in (
                list,
                set,
                tuple,
            ):
                field_name = field.alias or field_name
                obj_value = obj.get(field_name, None)
                if obj_value is not None:
                    if re.match("^\[.*\]$", obj_value):  # type: ignore
                        obj_dict[field_name] = json.loads(obj_value)
                    else:
                        value_ = obj_value.split(",")
                        if len(value_) == 1 and value_[0] == "":
                            value_ = None
                        obj_dict[field_name] = value_
        return cls.parse_obj(obj_dict)
