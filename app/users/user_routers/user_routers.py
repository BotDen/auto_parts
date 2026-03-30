from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import SessionDep
from app.users.crud.crud import CRUDUsers, get_current_user
from app.users.models import UserBase
from app.users.schemas import UserResponseSchema, UserResponseWithAdSchema


router = APIRouter()


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponseSchema)
async def get_me(current_user: UserBase = Depends(get_current_user)):
    """
    Метод получения данных только пользователя, без объявлений
    :param current_user: Авторизованный пользователь через зависимости
    :return: Возвращает объект пользователя по схеме UserResponseSchema
    """
    return current_user


@router.get(path="/user_ads", status_code=status.HTTP_200_OK, response_model=UserResponseWithAdSchema)
async def get_user(session: SessionDep, current_user: UserBase = Depends(get_current_user)):
    """
    Метод получения данных пользователя с объявлениями
    :param session: Асинхронная сессия
    :param current_user: Авторизованный пользователь через зависимости
    :return: Возвращает объект пользователя по схеме UserResponseWithAdSchema
    """
    result = await CRUDUsers.get_user_with_ads(session=session, current_user=current_user)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    if not result.advertisements:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Объявления не найден")
    return result
