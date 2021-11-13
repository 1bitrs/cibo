## Cibo
![Python Version](https://img.shields.io/badge/python-v3.7.5-brightgreen)
![System Platform](https://img.shields.io/badge/platform-ubuntu-brightgreen.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Install
```shell
python setup.py install
```

## Usage
```python
from cibo import Handler, SimpleContext, Blueprint, BaseApiQuery, BaseApiBody

api = Blueprint("api")

@api.get("/echo")
class EchoHandler(Handler):

    class Query(BaseApiQuery):
        str1: str

    class Body(BaseApiBody):
        str2: str

    def handle(self, context: SimpleContext, query: Query, body: Body):
        return context.success(msg=f"{query.str1}, {body.str2}")

```

## Dev
pull `stubs` files
```shell
git submodule update --init --recursive
```

## Docs
[http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs)

