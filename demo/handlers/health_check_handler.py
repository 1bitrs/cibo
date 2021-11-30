from cibo.args import BaseApiSuccessResp
from typing_extensions import Literal
from cibo import Handler, SimpleContext
from demo.handlers import api


@api.get("/ping")
class PingHandler(Handler):
    
    class Resp(BaseApiSuccessResp):
        msg: Literal["pong"]

    def handle(self, context: SimpleContext):
        """return `pong` if service work normally"""
        return context.success(msg="pong")
