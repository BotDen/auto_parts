from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


from utility.sql_enum import StatusEnum


class AdvertisementsBaseSchema(BaseModel):
    """Базовый класс для схемы объявления"""

    title: str = Field(..., min_length=1, max_length=255, description="Название объявления")
    description: str = Field(..., min_length=1, max_length=512, description="Описание детали")
    price: float = Field(..., gt=0)
    photos_url: list[str | None]

    model_config = ConfigDict(populate_by_name=True)


class AdvertisementCreateSchema(AdvertisementsBaseSchema):
    """Схема для создания объявления"""
    author_id: UUID


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
    status: StatusEnum

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdvertisementLongResponseSchema(AdvertisementShortResponseSchema):
    author_id: UUID


class ListAdvertisementShortResponseSchema(BaseModel):
    """Схема получения списка объявлений"""
    ads: list[AdvertisementLongResponseSchema] | None = Field(alias="advertisements")

    model_config = ConfigDict(populate_by_name=True)
