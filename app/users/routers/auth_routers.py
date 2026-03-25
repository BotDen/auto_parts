from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.database import SessionDep
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.users.crud.crud import CRUDUsers
from app.users.models import UserModel
from app.users.schemas import TokenResponseSchema, UserCreateSchema, UserLoginSchema, UserResponseSchema


router = APIRouter()


@router.post(path="/register", status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema)
async def register_user(user: UserCreateSchema, session: SessionDep):
    result = await CRUDUsers.check_existing_email(email=user.email, session=session)
    if not result:
        new_user = await CRUDUsers.create(user=user, session=session)
        return new_user
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Такой email:{user.email} уже зарегистрирован")


@router.post(path="/login", status_code=status.HTTP_200_OK, response_model=UserResponseSchema)
async def login(user: UserLoginSchema, session: SessionDep):
    query = select(UserModel).where(UserModel.email == user.email)
    result = (await session.execute(query)).scalar_one_or_none()
    if result is None or not verify_password(password=user.password, hash_password=str(result.hashed_password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")
    if result.is_deleted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь удален")
    return TokenResponseSchema(
        access_token=create_access_token(user_id=result.id),
        refresh_token=create_refresh_token(user_id=result.id),
    )
