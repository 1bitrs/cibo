from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Contact:
    name: Optional[str]
    url: Optional[str]
    email: Optional[str]


@dataclass
class License:
    name: str
    url: Optional[str]


@dataclass
class Info:
    title: str
    description: Optional[str]
    terms_of_service: Optional[str]
    contact: Optional[Contact]
    license: Optional[License]
    version: str


@dataclass
class ServerVariable:
    enum: Optional[List[str]]
    default: str
    description: Optional[str]


@dataclass
class Server:
    url: str
    description: Optional[str]
    variables: Dict[str, ServerVariable]


@dataclass
class ExternalDocs:
    description: Optional[str]
    url: str


@dataclass
class Tag:
    name: str
    description: Optional[str]
    external_docs: Optional[ExternalDocs]
