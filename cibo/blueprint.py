from typing import Optional, Type, Union

from flask.blueprints import Blueprint as _Blueprint

from .args import BaseApiBody, BaseApiPath, BaseApiQuery, BaseApiSuccessResp
from .decorators import inject_args_decorator, inject_context_decorator
from .handler import Handler

__all__ = ["Blueprint"]


class Blueprint(_Blueprint):
    def __init__(
        self,
        name,
        import_name,
        static_folder=None,
        static_url_path=None,
        template_folder=None,
        url_prefix=None,
        subdomain=None,
        url_defaults=None,
        root_path=None,
        cli_group=None,
        openapi_tag: Union[dict, str] = None,
        enable_openapi: bool = True,
        tag_description: str = None,
    ):
        super().__init__(
            name,
            import_name,
            static_folder,
            static_url_path,
            template_folder,
            url_prefix,
            subdomain,
            url_defaults,
            root_path,
            cli_group,
        )

        self.openapi_tag = openapi_tag or name
        self.enable_openapi = enable_openapi
        self.tag_description = tag_description

    @staticmethod
    def _parse_parameters_and_responses(_cls: Type[Handler]):
        Path = getattr(_cls, "Path", None)  # type: Optional[Type[BaseApiPath]]
        Query = getattr(_cls, "Query", None)  # type: Optional[Type[BaseApiQuery]]
        Body = getattr(_cls, "Body", None)  # type: Optional[Type[BaseApiBody]]
        Resp = getattr(_cls, "Resp", None)  # type: Optional[Type[BaseApiSuccessResp]]

        setattr(_cls, "path", list())
        setattr(_cls, "responses", dict())
        setattr(_cls, "parameters", list())
        setattr(_cls, "request_body", dict())
        if Path:
            _cls.path = Path.get_openapi_path()
        if Query:
            setattr(Query, "_schema_alias", f"{_cls.__name__}${Query.__name__}")
            _cls.parameters.extend(Query.get_openapi_parameters())
        if Body:
            setattr(Body, "_schema_alias", f"{_cls.__name__}${Body.__name__}")
            _cls.request_body = Body.get_openapi_request_body()
        if Resp:
            setattr(Resp, "_schema_alias", f"{_cls.__name__}${Resp.__name__}")
            _cls.responses["200"] = Resp.get_openapi_response()

    def register_view(self, rule: str, method: str, endpoint: str = None):
        def decorator(cls: Type[Handler]):
            if not issubclass(cls, Handler):
                raise ValueError(f"class {cls} must be extended from class Handler")

            methods = {method.upper()}
            if cls.cors_config is not None:
                # https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CORS#%E5%8A%9F%E8%83%BD%E6%A6%82%E8%BF%B0
                methods.add("OPTIONS")
            setattr(cls, "methods", methods)

            self._handle_view_cls_handle_func(cls)
            setattr(cls, method, getattr(cls, cls.handle_func_name))
            self.add_url_rule(rule, endpoint, cls.as_view())
            return cls

        return decorator

    def _handle_view_cls_handle_func(self, cls: Type[Handler]):
        """注册装饰器"""
        self._parse_parameters_and_responses(cls)
        decorators = []

        decorators.extend(
            [
                inject_context_decorator(cls),
                inject_args_decorator(cls),
            ]
        )
        if not cls.decorators:
            cls.decorators = decorators
        else:
            cls.decorators += decorators

        if cls.cors_config is not None:
            from .cors import enable_cors_decorator

            cls.decorators.append(enable_cors_decorator(cls))

        return cls

    def get(self, rule: str, endpoint: str = None):
        return self.register_view(rule, method="get", endpoint=endpoint)

    def post(self, rule: str, endpoint: str = None):
        return self.register_view(rule, method="post", endpoint=endpoint)

    def put(self, rule: str, endpoint: str = None):
        return self.register_view(rule, method="put", endpoint=endpoint)

    def patch(self, rule: str, endpoint: str = None):
        return self.register_view(rule, method="patch", endpoint=endpoint)

    def delete(self, rule: str, endpoint: str = None):
        return self.register_view(rule, method="delete", endpoint=endpoint)
