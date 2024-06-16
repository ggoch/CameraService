from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    password:str = Field(min_length=6)
    name: str  = Field(min_length=3)
    avatar: Optional[str] = Field(min_length=3)
    age: int = Field(gt=0,lt=100)
    email: EmailStr = Field()
    birthday: date = Field()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "password": "123456",
                    "name": "user1",
                    "avatar": "https://i.imgur.com/4M34hi2.png",
                    "age": 18,
                    "email": "user1@email.com",
                    "birthday": "2003-01-01"
                }
            ]
        }
    }

class UserCreateResponse(UserBase):
    name: str
    email: str

class UserUpdate(UserBase):
    avatar: Optional[str] = None
    age: Optional[int] = Field(gt=0,lt=100)
    birthday: Optional[date] = Field()


class UserUpdateResponse(UserBase):
    avatar: Optional[str] = None
    age: Optional[int] = Field(gt=0,lt=100)
    birthday: Optional[date] = Field()

class UserUpdatePassword(BaseModel):
    password: str = Field(min_length=6)

class UserRead(UserBase):
    id: int
    email: str
    avatar: Optional[str] = None

class CurrentUser(BaseModel):
    id: int
    name: str
    email: str

class UserInDB(BaseModel):
    id: int
    name: str
    password: str