from typing import Callable, Dict, List, Optional, Set, Type

from flask.views import MethodView
from pydantic import BaseModel
from typing_extensions import Literal

from .context import Context
from .types import TCorsConfig

__all__ = ["Handler"]


class Handler(MethodView):

    methods: Set[Literal["GET", "POST", "PUT", "DELETE"]]
    handle_func_name = "handle"
    decorators: List[Callable] = list()
    cors_config: Optional[TCorsConfig] = None

    context_cls: Type[Context] = Context

    Query: Optional[BaseModel] = None
    Body: Optional[BaseModel] = None

    path: List
    parameters: List[Dict]
    request_body: Dict
    responses: Dict

    @classmethod
    def as_view(cls, name: str = None, *args, **kwargs):
        if not hasattr(cls, cls.handle_func_name):
            raise ValueError(f"class `{cls}` does not have {cls.handle_func_name} method")

        name = name or cls.__name__
        return super().as_view(name, *args, **kwargs)
