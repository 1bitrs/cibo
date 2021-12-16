import inspect
from functools import wraps
from typing import Callable, Dict, Optional, Type

from flask import g, request
from pydantic import BaseModel

from .args import BaseApiBody, BaseApiPath, BaseApiQuery
from .handler import Handler


def inject_args_decorator(cls: Type[Handler]) -> Callable:
    """inject body & query"""

    def decorator(fn):
        view_func = getattr(cls, cls.handle_func_name)
        func_sig = inspect.signature(view_func, follow_wrapped=True)
        if "context" not in func_sig.parameters:
            raise Exception(f"param `context` does't found in `{view_func}`")
        context = func_sig.parameters.get("context")
        if not context:
            raise Exception("Not Found context")
        if not issubclass(context.annotation, cls.context_cls):
            # if _context is not sig.parameters.get("context").annotation:
            raise Exception(f"`{context.name}` must specify annotation `{cls.context_cls}`")

        parameter_map = {}  # type: Dict[str, Type[BaseModel]]
        Query = getattr(cls, "Query", None)  # type: Optional[Type[BaseApiQuery]]
        Body = getattr(cls, "Body", None)  # type: Optional[Type[BaseApiBody]]
        Path = getattr(cls, "Path", None)  # type: Optional[Type[BaseApiPath]]

        def _validate_query_and_body_parameters(type_: str, class_, parameter_map: Dict):
            if type_ in func_sig.parameters:
                api_args = func_sig.parameters.get(type_)
                if not api_args:
                    raise Exception()
                if not class_:
                    raise Exception(
                        f"`query` exists in {cls.handle_func_name}'s params but `{class_.__name__}` not found in `class {cls.__name__}`"
                    )
                elif not issubclass(class_, BaseModel):
                    raise Exception(f"{class_.__name__} object is not subclass of BaseModel")
                elif api_args.annotation is not class_:
                    raise Exception(f"parameter query type not match cls.{class_.__name__}")
                else:
                    parameter_map[type_] = class_
            else:
                if class_:
                    raise Exception(f"handle method not have query parameter")

        _validate_query_and_body_parameters("query", Query, parameter_map)
        _validate_query_and_body_parameters("body", Body, parameter_map)
        _validate_query_and_body_parameters("path", Path, parameter_map)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            parameters = {}
            if "query" in parameter_map:
                query = request.args
                parameters["query"] = Query.parse_request_args(query)  # type:ignore
            if "body" in parameter_map and Body:
                if request.content_type == "application/json":
                    body = dict(request.json) if request.json else {}
                    parameters["body"] = Body.parse_obj(body)
                elif request.content_type == "application/x-www-form-urlencoded":
                    body = Body.parse_form_args(request.form) if request.form else {}  # type:ignore
                    parameters["body"] = body
                else:
                    parameters["body"] = {}
            if "path" in parameter_map and Path:
                parameters["path"] = Path.parse_path_args(request.view_args)
                for k, _ in request.view_args.items():
                    if k in kwargs:
                        del kwargs[k]
                request.view_args.clear()

            return fn(*args, **kwargs, **parameters)

        return wrapper

    return decorator


def inject_context_decorator(cls: Type[Handler]) -> Callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            context = cls.context_cls()
            g._context = context
            return fn(*args, context=context, **kwargs)

        return wrapper

    return decorator
