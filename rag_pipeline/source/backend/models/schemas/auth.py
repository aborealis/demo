from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class DecodedToken(BaseModel):
    sub: str
    exp: int
