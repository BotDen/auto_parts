from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from config import settings


# Создаем объект хешера
ph = PasswordHasher()


def get_hash_password(password: str) -> str:
    """
    Генерация хэш из пароля
    :param password: Пароль пользователя в формате str
    :return: Возвращает хэш в формате строки
    """
    return ph.hash(password)


def verify_password(password: str, hash_password: str) -> bool:
    """
    Проверяет, совпадает ли хэш введенного пароля с хэшом хранящимся в базе
    :param password: Пароль введенный пользователем без преобразования
    :param hash_password: Хэш пароля из базы данных
    :return: Возвращает булево значение
    """
    try:
        return ph.verify(password=password, hash=hash_password)
    except VerifyMismatchError:
        return False


def create_access_token(user_id: UUID) -> str:
    """
    Метод получения access token

    :param user_id: ID пользователя из базы данных
    :return: Возвращает сгенерированный access token в формате str
    """
    # Получение времени жизни access token
    expires = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Формирование JSON с данными для токена
    payload = {"sub": str(user_id), "type": "access", "exp": expires}
    # Возвращает закодированный token
    return jwt.encode(claims=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """
    Метод получения refresh token

    :param user_id: ID пользователя из базы данных
    :return: Возвращает сгенерированный refresh token в формате str
    """
    # Получение времени жизни refresh token
    expires = datetime.now(tz=timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    # Формирование JSON с данными для токена
    payload = {"sub": str(user_id), "type": "access", "exp": expires}
    # Возвращает закодированный token
    return jwt.encode(claims=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)


class OAuth2(OAuth2PasswordBearer):
    """
    Класс для получения токена
    """
    def __call__(self, request: Request) -> str | None:
        """
        Метод по получения токена из запроса
        :param request: Объект запроса
        :return: Возвращает строку с токеном
        """
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Вы не авторизованы")
        return token.replace("Bearer:", "")


# Объект класс OAuth2. URL для автоматической работы документации в swagger
oauth2_scheme = OAuth2(tokenUrl="/auth/login")


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Метод декодирует и проверяет токен
    :param token: Токен полученный из запроса
    :return: Возвращает payload токена
    """
    # Декодирование полученного токена
    try:
        payload = jwt.decode(token=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен")

    return payload
