from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from app.core.database import SessionDep
from app.core.security import decode_access_token, get_hash_password, oauth2_scheme
from app.users.models import UserBase
from app.users.schemas import UserCreateSchema, UserLoginSchema, UserUpdateSchema


class CRUDUsers:
    """Базовый класс методов работы с Базой Данных"""

    @classmethod
    async def create_user(cls, user: UserCreateSchema, session: AsyncSession) -> UserBase:
        """
        Метод записи User в Базу Данных

        :param user: Объект пользователя для создания записи в базе данных в формате UserCreateSchema
        :param session: Асинхронная сессия для работы с базой данных AsyncSession
        :return: Объект пользователя в формате UserBase
        """

        # Создание объекта UserBase
        model_user = UserBase(
            username=user.username,
            email=str(user.email),
            hashed_password=get_hash_password(user.password),
        )
        # Добавление объекта UserBase в Базу Данных
        session.add(model_user)
        # Сохранение изменений в Базе Данных
        await session.commit()
        # Обновление объекта UserBase из Базы Данных
        await session.refresh(model_user)

        return model_user


    @classmethod
    async def check_is_deleted_user(cls, user: UserLoginSchema, session: AsyncSession) -> bool:
        """
        Метод проверки пользователя на удаление

        :param user: Объект пользователя для авторизации в системе в формате UserLoginSchema
        :param session: Асинхронная сессия для работы с базой данных AsyncSession
        :return: Возвращает булево значение
        """

        # Запрос к Базе Данных
        query = select(UserBase).where(UserBase.email == user.email)
        # Получение пользователя из Базы Данных по email
        result = (await session.execute(query)).scalar_one_or_none()
        # Проверка флага is_deleted у пользователя
        if result.is_deleted:
            return False
        return True


    @classmethod
    async def check_existing_email(cls, email: EmailStr, session: AsyncSession) -> bool:
        """
        Метод проверяет наличие записи email в базе данных

        :param email: Электронный адрес пользователя EmailStr
        :param session: Асинхронная сессия работы с базой данных AsyncSession
        :return: Возвращает булево значение
        """

        # Параметры запроса к Базе Данных
        query = select(UserBase).where(UserBase.email == email)
        # Получение записи пользователя из Базы Данных по email
        result = (await session.execute(query)).scalars().first()
        # Проверка наличия записи
        if result:
            return True

        return False

    @classmethod
    async def get_one_user(cls, user_id: UUID, session: AsyncSession) -> UserBase:
        """
        Метод получения пользователя по id пользователя

        :param user_id: ID пользователя UUID
        :param session: Асинхронная сессия для работы с базой данных AsyncSession
        :return: Возвращает объект пользователя в формате UserBase
        """
        # Параметры запроса к базе данных
        query = select(UserBase).where(UserBase.id == user_id)
        # Получение записи пользователя из базы данных
        db_item = (await session.execute(query)).scalars().first()

        return db_item

    @classmethod
    async def get_user_by_email(cls, user_email: EmailStr, session: AsyncSession) -> UserBase:
        """
        Метод получения пользователя по email
        :param user_email: Электронная почну пользователя, которого надо получить из бд
        :param session: Асинхронная сессия для работы с бд
        :return: Возращает объект пользователя в формате UserBase
        """
        query = select(UserBase).where(UserBase.email == user_email)
        result = (await session.execute(query)).scalars().first()

        return result

    @classmethod
    async def get_user_with_ads(cls, session: AsyncSession, current_user: UserBase) -> UserBase:
        """
        Метод получения пользователя с объявлениями
        :param session: Асинхронная сессия
        :param current_user: Авторизованный пользователь
        :return: Возвращает объект пользователя с объявлениями
        """
        query = select(UserBase).where(UserBase.id == current_user.id).options(selectinload(UserBase.advertisements))
        result = (await session.execute(query)).unique().scalar_one_or_none()

        return result

    @classmethod
    async def update_one_user(cls, db_user: UserBase, user: UserUpdateSchema, session: AsyncSession) -> UserBase:
        """
        Метод обновления записи пользователя в базе данных

        :param db_user: Объект пользователя из базы данных в формате UserBase
        :param user: Данные для обновления записи пользователя в формате UserUpdateSchema
        :param session: Асинхронная сессия для работы с базой данных AsyncSession
        :return: Возвращает обновленную запись пользователя в формате UserBase
        """

        # Получение словаря из модели UserUpdateSchema с пропуском пустых полей
        user_dict = user.model_dump(exclude_unset=True)
        # Обновление объекта db_user из словаря по key=value
        for kye, value in user_dict.items():
            setattr(db_user, kye, value)
        # Сохранение изменений в базе данных
        await session.commit()
        # Обновление объекта db_user после изменений
        await session.refresh(db_user)

        return db_user

    @classmethod
    async def soft_delete_user(cls, db_user: UserBase, session: AsyncSession) -> None:
        """
        Метод мягкого удаления пользователя

        :param db_user: Объект пользователя из базы данных в формате UserBase
        :param session: Асинхронная сессия для работы с базой данных AsyncSession
        :return: Возвращает None
        """

        db_user.is_deleted = True
        db_user.deleted_at = datetime.now(tz=timezone.utc)
        await session.commit()

        return None

async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)) -> UserBase:
    """
    Метод получения текущего пользователя
    :param session: Асинхронная сессия
    :param token: Токен полученный из запроса пользователя
    :return: Возвращает объект пользователя из бд в формате UserBase
    """
    payload = decode_access_token(token)
    # Получение пользователя из бд
    user = await CRUDUsers.get_one_user(user_id=payload.get("sub"), session=session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    if user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь удален")
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь заблокирован")

    return user
