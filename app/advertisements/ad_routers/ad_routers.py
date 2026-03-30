from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.advertisements.crud.crud import CRUDAdvertisement
from app.advertisements.models import AdvertisementBase
from app.advertisements.schemas import (
    AdvertisementCreateSchema,
    AdvertisementShortResponseSchema,
    AdvertisementUpdateSchema,
    ListAdvertisementShortResponseSchema,
)
from app.core.database import SessionDep
from app.users.crud.crud import get_current_user
from app.users.models import UserBase

router = APIRouter()


# Ошибка поиска объявления
ad_404_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Объявление не создано")


@router.post(path="", status_code=status.HTTP_201_CREATED, response_model=AdvertisementShortResponseSchema)
async def create_advertisement(
    ad: AdvertisementCreateSchema,
    session: SessionDep,
    current_user: UserBase = Depends(get_current_user)
):
    """
    Метод создания объявления

    :param ad: Данные объявления по схеме AdvertisementCreateSchema
    :param session: Асинхронная сессия для работы с базой данных
    :param current_user: Авторизованный пользователь в системе
    :return: Возвращает объявление по схеме AdvertisementResponseSchema
    """
    # Создание записи объявления в базе данных и возвращает его
    advertisement = await CRUDAdvertisement.create_advertisement(ad=ad, session=session, current_user=current_user)
    # Проверка наличие объекта объявления
    if not ad:
        # Поднимает ошибку создания объявления
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Объявление не создано")
    return advertisement


@router.get(path="/{advertisement_id}", status_code=status.HTTP_200_OK, response_model=AdvertisementShortResponseSchema)
async def get_advertisement(advertisement_id: UUID, session: SessionDep):
    """
    Метод получения объявления из базы данных

    :param advertisement_id: ID объявления
    :param session: Асинхронная сессия для работы с базой данных
    :return: Возвращает объявление по схеме AdvertisementResponseSchema
    """
    # Получение записи объявления из базы данных
    advertisement = await CRUDAdvertisement.get_advertisement(ad_id=advertisement_id, session=session)
    # Проверка получения объявления из базы данных
    if not advertisement:
        raise ad_404_exception
    return advertisement


@router.get(path="", status_code=status.HTTP_200_OK, response_model=ListAdvertisementShortResponseSchema)
async def get_all_advertisement(session: SessionDep):
    """
    Метод получения всех объявлений без пагинации
    :param session: Асинхронная сессия для работы с базой данных
    :return: Возвращает список объявлений по схеме ListAdvertisementResponseSchema
    """
    # Получение списка всех объявлений из базы данных
    advertisement_list = await CRUDAdvertisement.get_all_advertisements(session=session)
    # Проверка получения списка объявлений из базы данных
    if not advertisement_list:
        raise ad_404_exception
    return ListAdvertisementShortResponseSchema(ads=advertisement_list)


@router.patch(path="/{advertisement_id}", status_code=status.HTTP_200_OK, response_model=AdvertisementShortResponseSchema)
async def update_advertisement(
    advertisement_id: UUID,
    update_ad: AdvertisementUpdateSchema,
    session: SessionDep,
    current_user: UserBase = Depends(get_current_user),
):
    """
    Метод обновления одного объявления

    :param advertisement_id: ID объявления, которое нужно обновить
    :param update_ad: Данные для обновления объявления
    :param session: Асинхронная сессия для работы с базой данных
    :param current_user: Авторизованный пользователь в системе
    :return: Возвращает обновленное объявление по схеме AdvertisementResponseSchema
    """
    # Получение записи объявления по id
    db_item = await CRUDAdvertisement.get_advertisement(ad_id=advertisement_id, session=session)
    # Проверка получения объявления из базы данных
    if not db_item:
        raise ad_404_exception
    # Обновляет запись объявления в базе данных и возвращает ее
    update_db_item = await CRUDAdvertisement.update_advertisement(db_item=db_item, update_ad=update_ad, session=session)
    return update_db_item


@router.delete(path="/{advertisement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_advertisement(
    advertisement_id: UUID,
    session: SessionDep,
    current_user: UserBase = Depends(get_current_user)
) -> None:
    """
    Метод полного удаления объявления

    :param advertisement_id: ID объявления, которое нужно удалить
    :param session: Асинхронная сессия для работы с базой данных
    :param current_user: Авторизованный пользователь в системе
    :return: Возвращает None
    """
    # Получение объявления по id из базы данных
    db_item = await CRUDAdvertisement.get_advertisement(ad_id=advertisement_id, session=session)
    # Проверка получения объявления из базы данных
    if not db_item:
        raise ad_404_exception
    # Полное удаления объявления из базы данных
    result = await CRUDAdvertisement.delete_advertisement(db_item=db_item, session=session)
    return result
