import inspect
from functools import wraps
from typing import Callable, Dict, Type

from flask import g, request
from pydantic import BaseModel

from .args import BaseApiBody, BaseApiQuery
from .handler import Handler


def inject_context_to_g_decorator(cls: Type[Handler]) -> Callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            _context = kwargs.get("context")
            if _context:
                g._context = _context
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def inject_args_decorator(cls: Type[Handler]) -> Callable:
    """inject body & query"""

    def decorator(fn):
        view_func = getattr(cls, cls.handle_func_name)
        sig = inspect.signature(view_func, follow_wrapped=True)
        if "context" not in sig.parameters:
            raise Exception("context param not fount in handler")
        _context = cls.context_cls
        if not issubclass(sig.parameters.get("context").annotation, _context):
            # if _context is not sig.parameters.get("context").annotation:
            raise Exception(
                f"`{sig.parameters.get('context').name}` must specify annotation `{_context}`"
            )

        parameter_map = {}  # type: Dict[str, Type[BaseModel]]
        Query = getattr(cls, "Query", BaseApiQuery)  # type: Type[BaseApiQuery]
        Body = getattr(cls, "Body", BaseApiBody)  # type: Type[BaseApiBody]

        if "query" in sig.parameters and not Query:
            raise Exception(
                f"`query` exists in {cls.handle_func_name}'s params but `Query` not found in `class {cls.__name__}`"
            )
        if "body" in sig.parameters and not Body:
            raise Exception(
                f"`body` exists in {cls.handle_func_name}'s params but `Body` not found in `class {cls.__name__}`"
            )

        if Query:
            if not issubclass(Query, BaseModel):
                raise Exception("Query object is not subclass of BaseModel")
            if "query" not in sig.parameters:
                raise Exception(f"handle method not have query parameter")
            if sig.parameters.get("query").annotation is not Query:
                raise Exception(f"parameter query type not match cls.Query")

            parameter_map["query"] = Query

        if Body:
            if not issubclass(Body, BaseModel):
                raise Exception("Body object is not subclass of BaseModel")
            if "body" not in sig.parameters:
                raise Exception(f"handle method not have body parameter")
            if sig.parameters.get("body").annotation is not Body:
                raise Exception(f"parameter body type not match cls.Query")

            parameter_map["body"] = Body

        @wraps(fn)
        def wrapper(*args, **kwargs):
            parameters = {}
            if "query" in parameter_map:
                query = request.args
                parameters["query"] = Query.parse_request_args(query)  # type: ignore
            if "body" in parameter_map:
                body = dict(request.json) if request.json else {}
                parameters["body"] = parameter_map["body"].parse_obj(body)

            return fn(*args, **kwargs, **parameters)

        return wrapper

    return decorator


def inject_context_decorator(cls: Type[Handler]) -> Callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            context_cls = cls.context_cls
            context = context_cls()
            kwargs["context"] = context
            g._context = context
            return fn(*args, **kwargs)

        return wrapper

    return decorator
