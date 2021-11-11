from cibo import BaseApiBody, BaseApiQuery, Handler, SimpleContext

from ..exceptions import AuthException
from . import api


def token_auth(fn):
    def wrapper(*args, **kwargs):
        from flask import request

        if request.headers.get("token", None) != "123":
            raise AuthException("Fail to get access")
        return fn(*args, **kwargs)

    return wrapper


@api.post("/echo")
class EchoHandler(Handler):

    decorators = [token_auth]

    class Query(BaseApiQuery):
        a: str

    class Body(BaseApiBody):
        b: int

    def handle(self, context: SimpleContext, query: Query, body: Body):
        return context.success(data=f"{query.a}, {body.b}")
