from typing import TYPE_CHECKING, Dict, List, Tuple, Union

if TYPE_CHECKING:

    from flask.wrappers import Response

TCorsConfig = Dict[str, Union[str, List[str]]]

TFlaskResponse = Union[Tuple["Response", int], "Response"]
