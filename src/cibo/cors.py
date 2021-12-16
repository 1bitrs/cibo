from functools import wraps
from typing import Callable, Type, TypeVar

from flask import g

from .handler import Handler
from .types import TCorsConfig, TFlaskResponse

DEFAULT_CORS_CONFIG = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": [
        "Keep-Alive",
        "User-Agent",
        "X-Requested-With",
        "If-Modified-Since",
        "Cache-Control",
        "Content-Type",
    ],
    "Access-Control-Allow-Methods": ["GET", "POST", "OPTIONS"],
}

_R = TypeVar("_R", bound=TFlaskResponse)


def _set_cors_headers(resp: _R, cors_config: TCorsConfig) -> _R:
    if cors_config is not None:
        if isinstance(resp, tuple):
            r = resp[0]
        else:
            r = resp
        if not r.headers.get("Access-Control-Allow-Origin"):
            for k, v in DEFAULT_CORS_CONFIG.items():
                if k in cors_config:
                    r.headers.add(k, ",".join(cors_config[k]))
                else:
                    r.headers.add(k, ",".join(v))
    return resp


def enable_cors_decorator(cls: Type[Handler]) -> Callable:
    """允许跨域"""

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            g.cors_config = cls.cors_config
            resp = fn(*args, **kwargs)
            if cls.cors_config:
                _set_cors_headers(resp, cls.cors_config)
            return resp

        return wrapper

    return decorator
