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
        func_sig = inspect.signature(view_func, follow_wrapped=True)
        if "context" not in func_sig.parameters:
            raise Exception(f"param `context` does't found in `{view_func}`")
        if not issubclass(func_sig.parameters.get("context").annotation, cls.context_cls):
            # if _context is not sig.parameters.get("context").annotation:
            raise Exception(
                f"`{func_sig.parameters.get('context').name}` must specify annotation `{cls.context_cls}`"
            )

        parameter_map = {}  # type: Dict[str, Type[BaseModel]]
        Query = getattr(cls, "Query", None)  # type: Type[BaseApiQuery]
        Body = getattr(cls, "Body", None)  # type: Type[BaseApiBody]

        def _validate_query_and_body_parameters(type_: str, class_, parameter_map: Dict):
            if type_ in func_sig.parameters:
                if not class_:
                    raise Exception(
                        f"`query` exists in {cls.handle_func_name}'s params but `{class_.__name__}` not found in `class {cls.__name__}`"
                    )
                elif not issubclass(class_, BaseModel):
                    raise Exception(f"{class_.__name__} object is not subclass of BaseModel")
                elif func_sig.parameters.get(type_).annotation is not class_:
                    raise Exception(f"parameter query type not match cls.{class_.__name__}")
                else:
                    parameter_map[type_] = class_
            else:
                if class_:
                    raise Exception(f"handle method not have query parameter")

        _validate_query_and_body_parameters("query", Query, parameter_map)
        _validate_query_and_body_parameters("body", Body, parameter_map)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            parameters = {}
            if "query" in parameter_map:
                query = request.args
                parameters["query"] = Query.parse_request_args(query)  # type:ignore
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
