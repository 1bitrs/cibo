from cibo import Handler, SimpleContext
from demo.handlers import api


@api.get("/ping")
class PingHandler(Handler):
    def handle(self, context: SimpleContext):
        """return `pong` if service work normally"""
        return context.success(msg="pong")
