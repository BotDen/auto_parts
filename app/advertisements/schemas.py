from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.users.models import UserBase
from utility.sql_enum import StatusEnum


class AdvertisementsBaseSchema(BaseModel):
    """Базовый класс для схемы объявления"""

    title: str = Field(..., min_length=1, max_length=255, description="Название объявления")
    description: str = Field(..., min_length=1, max_length=512, description="Описание детали")
    price: float = Field(..., gt=0)
    photos_url: list[str | None]


class AdvertisementCreateSchema(AdvertisementsBaseSchema):
    """Схема для создания объявления"""
    pass


class AdvertisementUpdateSchema(AdvertisementsBaseSchema):
    """Схема для обновления объявления"""
    pass


class AdvertisementShortResponseSchema(BaseModel):
    """Схема для фильтрации объекта объявления по полям"""
    created_at: datetime
    id: UUID
    title: str
    description: str
    price: float
    # author_id: UUID
    status: StatusEnum

    model_config = ConfigDict(from_attributes=True)


class ListAdvertisementResponseSchema(BaseModel):
    """Схема получения списка объявлений"""
    ads: list[AdvertisementShortResponseSchema]
