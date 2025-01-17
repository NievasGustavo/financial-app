from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    age: int


class UserCreate(UserBase):
    password: str

    model_config = {
        "from_attributes": True
    }


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    password: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class UserResponse(UserBase):
    id: UUID4

    model_config = {
        "from_attributes": True
    }
