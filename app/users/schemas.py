from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.advertisements.schemas import AdvertisementShortResponseSchema


class UserBaseSchema(BaseModel):
    """Базовая схема объекта User"""

    user_name: str = Field(..., min_length=1, max_length=128, description="Имя или логин пользователя", alias="username")
    email: EmailStr = Field(..., max_length=128, description="Электронная почта пользователя")
    avatar_url: str | None = None


class UserLoginSchema(BaseModel):
    """Схема объекта User для входа в систему"""

    email: EmailStr = Field(..., max_length=128, description="Электронная почта пользователя")
    password: str = Field(..., min_length=8, max_length=128, description="Пароль пользователя")


class UserCreateSchema(UserBaseSchema):
    """Схема создания объекта User"""
    password: str = Field(..., min_length=8, max_length=128, description="Пароль пользователя")


class UserUpdateSchema(UserBaseSchema):
    """Схема для обновления объекта User"""
    pass


class UserResponseSchema(BaseModel):
    """Схема для обработки ответа по API"""

    id: UUID
    user_name: str = Field(alias="username")
    email: EmailStr
    avatar_url: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserResponseWithAdSchema(UserResponseSchema):
    """Схема ответа пользователя с объявлениями"""

    ads: list[AdvertisementShortResponseSchema] | None = Field(alias="advertisements")


class TokenResponseSchema(BaseModel):
    """Схема объекта Token"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
