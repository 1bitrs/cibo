from typing import Dict, List, Tuple, Union

from flask import Response

TCorsConfig = Dict[str, Union[str, List[str]]]

TFlaskResponse = Union[Tuple[Response, int], Response]
