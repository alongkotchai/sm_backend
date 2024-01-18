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
import utils


class UserCreate(BaseModel):
    email: EmailStr = Field()
    password: str = Field(min_length=8, max_length=64)
    role: Role = Field(Role.USER)
    is_activate: bool = Field(False)

    @field_validator('password')
    def validate_pass(cls, password: str):
        utils.validate_pass(password)
        return password

    model_config = ConfigDict(
        str_strip_whitespace=True)


class UserModify(UserCreate):
    email: Optional[EmailStr] = Field(None)
    password: Optional[str] = Field(None,
                                    min_length=8,
                                    max_length=64)
    role: Optional[Role] = Field(None)
    is_activate: Optional[bool] = Field(None)

    @field_validator('password')
    def validate_pass(cls, password: str):
        if password == None:
            return
        utils.validate_pass(password)
        return password


class UserDisplay(BaseModel):
    id: UUID = Field()
    email: EmailStr = Field()
    last_login: Optional[datetime] = Field(None)
    create_at: datetime = Field()
    role: Role = Field(Role.USER)
    is_activate: bool = Field(False)

    model_config = ConfigDict(
        from_attributes=True)


class UserList(BaseModel):
    users: list[UserDisplay]

    model_config = ConfigDict(
        from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr = Field()
    password: str = Field(min_length=8, max_length=64)

    model_config = ConfigDict(
        str_strip_whitespace=True)


class UserContext(BaseModel):
    user: UserDisplay
    access_token: str

    model_config = ConfigDict(
        from_attributes=True)
