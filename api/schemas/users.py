from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import (
    Field,
    EmailStr,
    BaseModel,
    ConfigDict,
    field_validator)
from core.security import Role
from schemas.base import (
    InputModel,
    OutputModel,
    BaseList)
import utils


class UserCreate(InputModel):
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8,
                          max_length=64)
    role: Role = Field(Role.USER)
    is_active: bool = Field(False)

    @field_validator('password')
    def validate_pass(cls, password: str):
        utils.validate_pass(password)
        return password


class UserModify(InputModel):
    email: Optional[EmailStr] = Field(None)
    password: Optional[str] = Field(None,
                                    min_length=8,
                                    max_length=64)
    role: Optional[Role] = Field(None)
    is_active: Optional[bool] = Field(None)

    @field_validator('password')
    def validate_pass(cls, password: str):
        if password == None:
            return
        utils.validate_pass(password)
        return password


class UserDisplay(OutputModel):
    uid: UUID
    email: EmailStr
    last_login: Optional[datetime]
    create_at: datetime
    role: Role
    is_active: bool


class UserList(BaseList):
    users: list[UserDisplay]


class UserLogin(InputModel):
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8,
                          max_length=64)


class UserContext(OutputModel):
    user: UserDisplay
    access_token: str
