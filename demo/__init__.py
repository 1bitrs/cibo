from cibo import Flask


def create_app():
    app = Flask(__name__, enable_doc=True, docs_path="")
    from .handlers import api

    app.register_blueprint(api, url_prefix="/api")
    app.config["SWAGGER"] = {
        "openapi_version": "3.0",
        "specs_route": "/docs/",
        "info": {
            "title": "MPA Server API 文档",
            "version": "1.0.0",
            "description": f"123",
        },
        "basePath": "/",
        "schemes": ["http"],
    }

    # from flasgger import Swagger

    # Swagger(app)
    return app
