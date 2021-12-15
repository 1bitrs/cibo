from random import randint
from typing import Tuple

from flask import Response, current_app, jsonify
from typing_extensions import Literal, TypedDict


def success(
    status_message: str = "ok", status_code: int = 200, jsonify_func=None, **data
) -> Tuple[Response, int]:
    """返回成功数据"""
    if status_code < 200 or status_code > 299:
        raise ValueError("success status_code should be 200~299")
    res_data = dict(
        status_code=status_code,
        status_message=status_message,
        success=True,
    )
    for k, v in data.items():
        res_data[k] = v

    if jsonify_func:
        ret = jsonify_func(res_data)
    else:
        ret = jsonify(res_data)
    return ret, 200


class DCommonErrorResp(TypedDict):
    success: Literal[False]
    status_code: int
    status_message: str
    error_hint: str


def base62_encode(number):
    if not isinstance(number, int):
        raise TypeError("number must be an integer")
    if number < 0:
        raise ValueError("number must be positive")

    alphabet, base62 = ["0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", ""]

    while number:
        number, i = divmod(number, 62)
        base62 = alphabet[i] + base62

    return base62 or alphabet[0]


def error(
    status_message: str = "error", status_code: int = 400, jsonify_func=None, *, data: dict = None
) -> Tuple[Response, int]:
    """返回失败信息"""
    n = randint(14776338, 916132832)
    error_hint = base62_encode(n)
    if status_code >= 200 and status_code <= 299:
        raise ValueError("error status_code can not be 2XX")
    res_data = DCommonErrorResp(
        status_code=status_code, status_message=status_message, error_hint=error_hint, success=False
    )
    if data:
        for k, v in data.items():
            res_data[k] = v

    if jsonify_func:
        ret = jsonify_func(res_data)
    else:
        ret = jsonify(res_data)
    return ret, 200


from dataclasses import asdict, is_dataclass
from datetime import datetime
from decimal import Decimal
from math import log10
from typing import Any, Iterable, Union
from uuid import UUID

from flask.json import JSONEncoder, dumps
from pydantic import BaseModel


class JSONEncoder(JSONEncoder):
    def default(self, o: Any) -> Union[str, list, dict, Any]:
        if isinstance(o, UUID):
            return str(o)
        elif isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(o, int) and log10(o) > 11:
            return str(o)
        elif isinstance(o, Decimal):
            return float(o)
        elif is_dataclass(o):
            return asdict(o)
        elif hasattr(o, "to_dict_v2"):
            return o.to_dict_v2()  # type: ignore
        elif hasattr(o, "to_dict"):
            return o.to_dict()  # type: ignore
        elif isinstance(o, BaseModel):
            return o.dict()
        elif isinstance(o, Iterable):  # Document是Iterable对象
            return list(o)
        return super().default(o)


def jsonify_with_encoder(*args, **kwargs):
    indent = None
    separators = (",", ":")

    if current_app.config["JSONIFY_PRETTYPRINT_REGULAR"] or current_app.debug:
        indent = 2
        separators = (", ", ": ")

    if args and kwargs:
        raise TypeError("jsonify() behavior undefined when passed both args and kwargs")
    elif len(args) == 1:  # single args are passed directly to dumps()
        data = args[0]
    else:
        data = args or kwargs

    return current_app.response_class(
        dumps(data, indent=indent, separators=separators, cls=JSONEncoder) + "\n",
        mimetype=current_app.config["JSONIFY_MIMETYPE"],
    )
