from datetime import datetime, timedelta, timezone
from uuid import UUID
from jose import jwt

from passlib.context import CryptContext
from config import settings


# настройка контекста, используем bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hash_password(password: str) -> str:
    """Генерация хэш из пароля"""
    return pwd_context.hash(password)

def verify_password(password: str, hash_password: str) -> bool:
    """Проверяем, совпадает ли введенный пароль с хэшом в базе"""
    return pwd_context.verify(secret=password, hash=hash_password)

def create_access_token(user_id: UUID) -> str:
    expires = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "type": "access", "exp": expires}
    return jwt.encode(claims=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(user_id: UUID) -> str:
    expires = datetime.now(tz=timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "type": "access", "exp": expires}
    return jwt.encode(claims=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
