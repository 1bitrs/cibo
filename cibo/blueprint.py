from typing import Type

from flask.blueprints import Blueprint as _Blueprint

from .deorators import inject_args_decorator, inject_context_decorator
from .handler import Handler


class Blueprint(_Blueprint):
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
