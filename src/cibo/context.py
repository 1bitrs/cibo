from typing import Tuple

from flask import Response

from .utils import error as _error
from .utils import jsonify_with_encoder
from .utils import success as _success

__all__ = ["Context", "ErrorContext", "SimpleContext"]


class Context:
    @staticmethod
    def success(
        status_message: str = "ok",
        status_code: int = 200,
        jsonify_func=jsonify_with_encoder,
        **data,
    ) -> Tuple[Response, int]:
        return _success(
            status_message=status_message,
            status_code=status_code,
            jsonify_func=jsonify_func,
            **data,
        )

    @staticmethod
    def error(
        status_message: str = "ok",
        status_code: int = 400,
        jsonify_func=jsonify_with_encoder,
        **data,
    ) -> Tuple[Response, int]:
        return _error(
            status_message=status_message,
            status_code=status_code,
            jsonify_func=jsonify_func,
            **data,
        )


class ErrorContext(Context):
    ...


class SimpleContext(Context):
    ...
