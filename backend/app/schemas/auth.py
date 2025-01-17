from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str
    expires_in: int | None = None


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

class GoogleUserData(BaseModel):
    age: int