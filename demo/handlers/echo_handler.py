from typing import Dict, List, Optional, Set, Tuple

from cibo import BaseApiBody, BaseApiQuery, Handler, SimpleContext
from demo.auth import token_auth
from demo.handlers import api


@api.post("/echo")
class EchoHandler(Handler):

    decorators = [token_auth]

    class Query(BaseApiQuery):
        a: str
        b: Optional[List[int]]
        c: Optional[Dict[str, int]]

    class Body(BaseApiBody):
        d: Set[int]
        e: Tuple[Dict[int, List], Dict[int, List]]

    def handle(self, context: SimpleContext, query: Query, body: Body):
        """echo the recevied params"""
        return context.success(
            data=f"a: {query.a}, b: {query.b}, c: {query.c}, d: {body.d}, e: {body.e}"
        )
