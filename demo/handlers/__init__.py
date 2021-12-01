from pydantic import ValidationError
from werkzeug.exceptions import InternalServerError

from cibo import Blueprint, ErrorContext

from ..exceptions import AuthException

api = Blueprint("api", __name__, openapi_tag="API", tag_description="description of API")


@api.errorhandler(ValidationError)
def handle_validation_error(e: ValidationError):
    return ErrorContext().error(data=dict(errors=e.errors()))


@api.errorhandler(AuthException)
def handle_auth_exception(e: AuthException):
    return ErrorContext().error(e.msg, e.code)


@api.errorhandler(InternalServerError)
def handle_internal_server_error(e: InternalServerError):
    return ErrorContext().error("服务器错误", e.code)


def _binding_route_rule():
    from . import echo_handler, health_check_handler, user_handler  # type: ignore


_binding_route_rule()
