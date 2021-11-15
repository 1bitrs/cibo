from demo.exceptions import AuthException


def token_auth(fn):
    def wrapper(*args, **kwargs):
        from flask import request

        if request.headers.get("token", None) != "123":
            raise AuthException("Fail to get access")
        return fn(*args, **kwargs)

    return wrapper
