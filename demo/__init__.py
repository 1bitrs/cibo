from cibo import Flask


def create_app():
    app = Flask(__name__, enable_doc=True, title="", version="0.1.0")
    from .handlers import api

    app.register_blueprint(api, url_prefix="/api")
    return app
