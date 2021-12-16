from typing import Any, Dict, List, Optional, Type, Union, cast

from apispec.core import APISpec
from flask import Flask as _Flask
from flask import render_template_string

from .blueprint import Blueprint
from .handler import Handler
from .ui_templates import DOCS_TEMPLATE, OAUTH2_REDIRECT_TEMPLATE, REDOC_TEMPLATE

__all__ = ["Flask"]


class Flask(_Flask):
    openapi_version: str
    tags: List
    _spec: Union[str, dict] = ""

    def __init__(
        self,
        import_name: str,
        *,
        static_url_path: Optional[str] = None,
        static_folder: str = "static",
        static_host: Optional[str] = None,
        host_matching: bool = False,
        subdomain_matching: bool = False,
        template_folder: str = "templates",
        instance_path: Optional[str] = None,
        instance_relative_config: bool = False,
        root_path: Optional[str] = None,
        enable_doc: bool = True,
        openapi_url_prefix: str = None,
        # NOTE openapi 相关参数 https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md
        # openapi
        openapi: str = "3.0.2",
        # info
        title: str,
        description: str = None,
        terms_of_service: str = None,
        contact: Dict = None,
        license: Dict = None,
        version: str,
        # servers
        servers: List[Dict] = None,
        # paths
        # components
        # security
        # tags
        # externalDocs
        external_docs: Dict = None,
        docs_path: str = "/docs",
        docs_oauth2_redirect_path: str = "/docs/oauth2-redirect",
        redoc_path: str = "/redoc",
        spec_path: str = "/openapi.json",
    ) -> None:
        super().__init__(
            import_name,
            static_url_path=static_url_path,
            static_folder=static_folder,
            static_host=static_host,
            host_matching=host_matching,
            subdomain_matching=subdomain_matching,
            template_folder=template_folder,
            instance_path=instance_path,
            instance_relative_config=instance_relative_config,
            root_path=root_path,
        )

        self.enable_doc = enable_doc
        self.openapi_url_prefix = openapi_url_prefix
        self.openapi = openapi
        self.title = title
        self.description = description
        self.terms_of_service = terms_of_service
        self.contact = contact
        self.license = license
        self.version = version
        self.servers = servers

        self.external_docs = external_docs

        self.docs_path = docs_path
        self.docs_oauth2_redirect_path = docs_oauth2_redirect_path
        self.redoc_path = redoc_path
        self.spec_path = spec_path
        self._register_openapi_blueprint()

    def _register_openapi_blueprint(self):
        """注册openapi蓝图"""
        bp = Blueprint("_openapi", __name__, url_prefix=self.openapi_url_prefix)
        if self.spec_path:
            """openapi.json"""

            @bp.route(self.spec_path)
            def spec():  # type: ignore
                return self._get_spec(force_update=False)

        if self.docs_path:
            """Swagger"""

            @bp.route(self.docs_path)
            def docs() -> str:  # type: ignore
                return render_template_string(
                    DOCS_TEMPLATE, oauth2_redirect_path=self.docs_oauth2_redirect_path
                )

        if self.docs_oauth2_redirect_path:

            @bp.route(self.docs_oauth2_redirect_path)
            def oauth_redirect() -> str:  # type: ignore
                return render_template_string(OAUTH2_REDIRECT_TEMPLATE)

        if self.redoc_path:
            """Redoc"""

            @bp.route(self.redoc_path)
            def redoc() -> str:  # type: ignore
                return render_template_string(REDOC_TEMPLATE)

        if self.enable_doc and (self.docs_path or self.redoc_path):
            self.register_blueprint(bp)

    def _get_spec(self, spec_format: str = "json", force_update=False) -> Union[dict, str]:

        if not force_update and self._spec:
            return self._spec

        if spec_format == "json":
            self._spec = self._generate_spec().to_dict()
        else:
            self._spec = self._generate_spec().to_yaml()

        return self._spec

    def _generate_spec(self) -> APISpec:
        kwargs = {}
        if self.servers:
            kwargs["servers"] = self.servers
        if self.external_docs:
            kwargs["external_docs"] = self.external_docs
        spec: APISpec = APISpec(
            title=self.title,
            version=self.version,
            openapi_version=self.openapi,
            info=self._make_info(),
            tags=self._make_tags(),
            components=self._make_components(),
            paths=self._make_paths(),
            **kwargs,
        )
        from .args import _destory

        _destory()

        return spec

    def _make_info(self) -> dict:
        """Make OpenAPI info object."""
        info = {
            "title": "",
            "description": "",
            "termsOfService": "",
            "contact": {},
            "license": {},
            "version": "",
        }
        if self.contact:
            info["contact"] = self.contact
        if self.license:
            info["license"] = self.license
        if self.terms_of_service:
            info["termsOfService"] = self.terms_of_service
        if self.description:
            info["description"] = self.description
        return info

    def _make_tags(self) -> List[Dict[str, Any]]:
        """Make OpenAPI tags object."""
        tags = list()
        for blueprint_name, blueprint in self.blueprints.items():
            if blueprint_name == "_openapi":
                continue
            _tag = getattr(blueprint, "openapi_tag", None)  # type: Optional[Union[dict, str]]
            if _tag:
                if isinstance(_tag, dict):
                    tag = _tag
                else:
                    tag = {
                        "name": _tag,
                        "description": blueprint.tag_description,
                        "externalDocs": {},
                    }
            else:
                tag = {
                    "name": blueprint_name,
                    "description": blueprint.tag_description,
                    "externalDocs": {},
                }
            tags.append(tag)
        return tags

    def _make_paths(self) -> dict:
        paths = {
            "$ref": "",
            "summary": "",
            "description": "",
            "servers": [],
            "parameters": [],
        }  # type: Dict[str, Union[str, List[Dict], Dict]]
        for rule in self.url_map.iter_rules():
            view_func = self.view_functions[rule.endpoint]
            if hasattr(view_func, "view_class") and issubclass(view_func.view_class, Handler):
                class_ = cast(Type[Handler], view_func.view_class)
                func = getattr(class_, class_.handle_func_name)
                if not func:
                    raise AttributeError(
                        f"{class_.__name__} must have function {class_.handle_func_name}"
                    )
                blueprint = self.blueprints[rule.endpoint.split(".")[0]]  # type: Blueprint
                _rule = cast(str, rule.rule)
                paths[_rule] = paths.get(_rule, {})
                _path_rule = cast(Dict, paths[_rule])
                for method in class_.methods:
                    _path_rule.update(
                        {
                            method.lower(): {
                                "tags": [blueprint.openapi_tag],
                                "summary": func.__doc__,
                                "parameters": class_.parameters,
                                "requestBody": class_.request_body,
                                "responses": class_.responses,
                            },
                            "parameters": getattr(class_, "path", []),
                        }
                    )
        return paths

    def _make_components(self) -> dict:
        components = {
            "schemas": {},
            "responses": {},
            "parameters": {},
            "examples": {},
            "requestBodies": {},
            "headers": {},
            "securitySchemes": {},
            "links": {},
            "callback": {},
        }
        from .args import (
            components_parameters,
            components_request_bodies,
            components_responses,
            components_schemas,
            translate_schema_to_openapi,
        )

        for k, v in components_parameters.items():
            components["parameters"][k] = {
                "name": k.split("$")[-1],
                "in": "query",
                "description": v.__doc__ or "",
                "required": True,
                "deprecated": False,
                "allowEmptyValue": False,
                "schema": translate_schema_to_openapi(v),
            }

        for k, v in components_request_bodies.items():
            components["requestBodies"][k] = {
                "description": v.__doc__ or "",
                "content": {v._content_type: {"schema": translate_schema_to_openapi(v)}},
                "required": True,
            }

        for k, v in components_responses.items():
            components["responses"][k] = {
                "description": v.__doc__ or "",
                "content": {v._content_type: {"schema": translate_schema_to_openapi(v)}},
            }

        while components_schemas:
            k, v = components_schemas.popitem()
            components["schemas"][k] = translate_schema_to_openapi(v)

        return components
