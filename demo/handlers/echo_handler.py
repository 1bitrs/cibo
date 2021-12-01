from typing import Dict, List, Optional, Set, Tuple

from pydantic.fields import Field

from cibo import BaseApiBody, BaseApiQuery, Handler, SimpleContext
from cibo.args import BaseApiSuccessResp
from demo.auth import token_auth
from demo.handlers import api


@api.post("/echo")
class EchoHandler(Handler):

    decorators = [token_auth]

    class Query(BaseApiQuery):
        """description of Query"""

        a: str = Field(description="description of parameter a", max_length=20)
        b: Optional[List[int]] = Field(description="description of parameter b")
        c: Optional[Dict[str, int]] = Field(description="description of parameter c")

    class Body(BaseApiBody):
        """description of Body"""

        d: Set[int] = Field(description="description of parameter d")
        e: Tuple[Dict[int, List], Dict[int, List]]
        f: Optional[int] = Field(default=0, gt=-1, lt=10)

    class Resp(BaseApiSuccessResp):
        """description of Response"""

        a: str = Field(description="description of a")
        b: Optional[List[int]] = Field(description="description of b")
        c: Optional[Dict[str, int]] = Field(description="description of c")
        d: Set[int] = Field(description="description of d")
        e: Tuple[Dict[int, List], Dict[int, List]] = Field(description="description of e")

    def handle(self, context: SimpleContext, query: Query, body: Body):
        """echo the recevied params"""
        return context.success(
            data=f"a: {query.a}, b: {query.b}, c: {query.c}, d: {body.d}, e: {body.e}, f: {body.f}"
        )
