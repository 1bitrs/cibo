class AuthException(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg
        self.code = 10000
