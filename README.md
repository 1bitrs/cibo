## Cibo
![Python Version](https://img.shields.io/badge/python-v3.7.5-brightgreen)
![System Platform](https://img.shields.io/badge/platform-ubuntu-brightgreen.svg)
![Travis CI](https://app.travis-ci.com/yangfan9702/cibo.svg?branch=master&status=unknown)
![Coverage](https://img.shields.io/codecov/c/github/yangfan9702/cibo)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![License](https://img.shields.io/github/license/yangfan9702/cibo)
![Repo Size](https://img.shields.io/github/repo-size/yangfan9702/cibo)


## Installing
```shell
python setup.py install
```

## A Simple Example
```python
from cibo import Handler, SimpleContext, Blueprint, BaseApiQuery, BaseApiBody

api = Blueprint("api")

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

```
Use a custom model and validate function
```python
@api.post("/user")
class UserHandler(Handler):
    class Body(BaseApiBody):
        class User(BaseModel):
            name: str = Field(description="姓名")
            emails: Optional[List[str]] = Field(description="邮箱")

            @classmethod
            def validate(cls, value: Any):
                obj = cls(**value)
                if obj.emails:
                    if not all(
                        [
                            re.match(
                                r"^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$", email
                            )
                            for email in obj.emails
                        ]
                    ):
                        raise ValueError("email is not valid")
                return obj

        user: User
        inviter: str

    def handle(self, context: SimpleContext, body: Body):
        """custom model and validate"""
        return context.success(user=body.user, inviter=body.inviter)
```

## Dev
pull `stubs` files
```shell
git submodule update --init --recursive
```

## Docs
[http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs)

## Contributing Guide
### First time setup
Create a virtual environment and install requirements:
```bash
$ python3 -m venv env
$ source env/bin/activate
$ python -m pip install --upgrade pip setuptools
$ pip install -r requirements/dev.txt
$ pip install -e .
$ pre-commit install
```
