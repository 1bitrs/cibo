from typing import List
import pytest
from pydantic.error_wrappers import ValidationError
from cibo.args import BaseApiBody, BaseApiQuery

def test_auto_trans_raise_base_api_body():
    class Body(BaseApiBody):
        age: int
    with pytest.raises(ValidationError) as excinfo:
        Body(age="a")
    assert excinfo._excinfo[1].errors()[0]["msg"] == "value is not a valid integer"

def test_auto_trans_type_base_api_query():
    class Query(BaseApiQuery):
        ids: List[str]

    query = Query(ids=["a", 2])
    assert query.ids[1] == "2"

