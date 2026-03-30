from fastapi import APIRouter, HTTPException, status, Response
from sqlalchemy import select

from app.core.database import SessionDep
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.users.crud.crud import CRUDUsers
from app.users.models import UserBase
from app.users.schemas import TokenResponseSchema, UserCreateSchema, UserLoginSchema, UserResponseSchema


router = APIRouter()


@router.post(path="/register", status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema)
async def register_user(user: UserCreateSchema, session: SessionDep):
    """
    Метод регистрации пользователя в системе

    :param user: Данные пользователя в формате UserCreateSchema
    :param session: Асинхронная сессия для работы с базой данных
    :return: Возвращает объект пользователя согласно схеме UserResponseSchema
    """

    # Проверяет наличие переданного email в Базе Данных. True or False
    result = await CRUDUsers.check_existing_email(email=user.email, session=session)
    if result:
        # Поднимает ошибку, если переданных email уже есть в Базе Данных
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Такой email:{user.email} уже зарегистрирован")
    # Сохраняет пользователя в Базе Данных и возвращает объект UserBase
    new_user = await CRUDUsers.create_user(user=user, session=session)
    return new_user


@router.post(path="/login", status_code=status.HTTP_200_OK, response_model=TokenResponseSchema)
async def login(response: Response, user: UserLoginSchema, session: SessionDep):
    """
    Метод авторизации пользователя в системе

    :param user: Данные пользователя в формате UserLoginSchema
    :param session: Асинхронная сессия для работы с базой данных
    :param response: Объект Response для работы с cookies
    :return: Возвращает токены согласно схеме TokenResponseSchema
    """

    # Запрос к Базе Данных
    query = select(UserBase).where(UserBase.email == user.email)
    # Получение записи пользователя из Базы Данных по email.
    result = (await session.execute(query)).scalar_one_or_none()
    # Проверка на наличие пользователя по email и совпадение хэш переданного пароля с хэш паролем из Базы Данных
    if (result is None) or (not verify_password(password=user.password, hash_password=str(result.hashed_password))):
        # Поднимает ошибку если нет такого email в Базе Данных или хэщ пароли не совпали
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")
    # Проверка, что пользователь не удален
    if result.is_deleted:
        # Поднимает ошибку, если is_deleted=True
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь удален")
    access_token = create_access_token(user_id=result.id)
    response.set_cookie(
        key="access_token",
        value=f"Bearer:{access_token}",
        samesite="lax",
    )
    return TokenResponseSchema(
        access_token=access_token,
        refresh_token=create_refresh_token(user_id=result.id),
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response) -> None:
    """
    Метод выхода из системы
    :param response: Объект ответа
    :return: Возвращает None
    """
    response.delete_cookie(key="access_token")
    return None
