
from pydantic import BaseModel


class QueryContext(BaseModel):
    query: str
    top_k: int = 5


class QueryKeyword(BaseModel):
    query: str
    offset: int = 0
    limit: int = 10


class DocumentContentUpdated(BaseModel):
    name: str | None = None
    content: str | None = None
