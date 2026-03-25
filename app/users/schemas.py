from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBaseSchema(BaseModel):
    username: str = Field(..., min_length=1, max_length=128, description="Имя или логин пользователя")
    email: EmailStr = Field(..., max_length=128, description="Электронная почта пользователя")
    avatar_url: str | None


class UserLoginSchema(UserBaseSchema):
    password: str = Field(..., min_length=8, max_length=128, description="Пароль пользователя")


class UserCreateSchema(UserBaseSchema):
    password: str = Field(..., min_length=8, max_length=128, description="Пароль пользователя")


class UserUpdateSchema(UserBaseSchema):
    pass


class UserResponseSchema(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    avatar_url: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
