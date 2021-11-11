from cibo import Handler, SimpleContext

from . import api


@api.get("/ping")
class PingHandler(Handler):
    def handle(self, context: SimpleContext):
        return context.success(msg="pong")
