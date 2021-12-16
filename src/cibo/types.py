from typing import TYPE_CHECKING, Dict, List, Tuple, Union

from typing_extensions import Literal

if TYPE_CHECKING:

    from flask.wrappers import Response

TCorsConfig = Dict[str, Union[str, List[str]]]

TFlaskResponse = Union[Tuple["Response", int], "Response"]


MediaType = Literal[
    "text/plain; charset=utf-8",
    "application/json",
    "application/vnd.github+json",
    "application/vnd.github.v3+json",
    "application/vnd.github.v3.raw+json",
    "application/vnd.github.v3.text+json",
    "application/vnd.github.v3.html+json",
    "application/vnd.github.v3.full+json",
    "application/vnd.github.v3.diff",
    "application/vnd.github.v3.patch",
]
