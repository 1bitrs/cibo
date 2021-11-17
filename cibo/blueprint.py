from dataclasses import dataclass
from typing import Optional, Type

from flask.blueprints import Blueprint as _Blueprint
from typing_extensions import Literal

from .args import BaseApiBody, BaseApiQuery, BaseApiSuccessResp
from .deorators import inject_args_decorator, inject_context_decorator
from .handler import Handler


@dataclass
class ApiAuthInfo:
    auth_type: Literal["normal", "corp"]
    optional: bool


class Blueprint(_Blueprint):
    @staticmethod
    def _parser_doc(_cls):
        """
        需要解析授权类型
        需要解析文档字符串里面的 @returns
        需要解析 `Body` `Query`
        """
        Body = getattr(_cls, "Body", None)  # type: Optional[Type[BaseApiBody]]
        Query = getattr(_cls, "Query", None)  # type: Optional[Type[BaseApiQuery]]
        Resp = getattr(_cls, "Resp", None)  # type: Optional[Type[BaseApiSuccessResp]]
        if Query:
            _cls.parameters.extend(Query.get_swag_query_param())
        if Body:
            _cls.parameters.append(Body.get_swag_body_param())
        if Resp:
            _cls.responses["200"] = Resp.get_swag_resp_schema()
        _cls.security.append(ApiAuthInfo(auth_type="normal", optional=True))

    def register_view(self, rule: str, method: str, endpoint: str = None):
        def decorator(cls: Type[Handler]):
            if not issubclass(cls, Handler):
                raise ValueError(f"class {cls} must be extended from class Handler")

            # 初始化 Swagger 参数, 使用可变对象做默认值在这里会有问题
            cls.tags = [rule.strip("/").split("/", 1)[0].title() + ":"]
            cls.parameters = []
            cls.responses = {}
            cls.deprecated = []
            cls.definitions = []
            cls.security = []
            cls.externalDocs = {}

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
        self._parser_doc(cls)
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

    def post(self, rule: str, endpoint: str = None):
        return self.register_view(rule, method="post", endpoint=endpoint)

    def get(self, rule: str, endpoint: str = None):
        return self.register_view(rule, method="get", endpoint=endpoint)

    def put(self, rule: str, endpoint: str = None):
        return self.register_view(rule, method="put", endpoint=endpoint)

    def delete(self, rule: str, endpoint: str = None):
        return self.register_view(rule, method="delete", endpoint=endpoint)
