from pydantic import BaseModel
from typing import Any


class Token(BaseModel):
    access_token: str
    token_type: str


class ResStatus(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


class User(BaseModel):
    name: str
    phone_number: int


class UserInfo(User):
    password: str


class UserRestPasswd(BaseModel):
    name: str | int
    new_password: str
