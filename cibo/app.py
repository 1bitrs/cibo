import json
from typing import List, Optional

from flask import Blueprint
from flask import Flask as _Flask
from flask import render_template_string

from .ui_templates import DOCS_TEMPLATE, REDOC_TEMPLATE


class Flask(_Flask):
    openapi_version: str
    tags: List

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
        docs_path: str = "/docs",
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

        self.docs_path = docs_path
        self.redoc_path = redoc_path
        self.enable_doc = enable_doc
        self.spec_path = spec_path
        self._register_openapi_blueprint()

    def _register_openapi_blueprint(self):
        bp = Blueprint(
            "openapi",
            __name__,
        )
        if self.spec_path:

            @bp.route(self.spec_path)
            def spec():  # type: ignore
                demo = None
                with open("./cibo/demo.json") as f:
                    demo = json.loads(f.read())
                return demo

        if self.docs_path:

            @bp.route(self.docs_path)
            def docs() -> str:  # type: ignore
                return render_template_string(DOCS_TEMPLATE)

        if self.redoc_path:

            @bp.route(self.redoc_path)
            def redoc() -> str:  # type: ignore
                return render_template_string(REDOC_TEMPLATE)

        if self.enable_doc and (self.docs_path or self.redoc_path):
            self.register_blueprint(bp)
