from datetime import datetime, timezone
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_hash_password, verify_password
from app.users.models import UserModel
from app.users.schemas import UserCreateSchema, UserLoginSchema, UserUpdateSchema


class CRUDUsers:
    @classmethod
    async def create(cls, user: UserCreateSchema, session: AsyncSession) -> UserModel:
        user_dict = user.model_dump()
        model_user = UserModel(**user_dict)
        model_user.hashed_password = get_hash_password(user_dict["password"])
        session.add(model_user)
        await session.commit()
        await session.refresh(model_user)

        return model_user


    @classmethod
    async def check_is_deleted(cls, user: UserLoginSchema, session: AsyncSession) -> bool:
        query = select(UserModel).where(UserModel.email == user.email)
        result = (await session.execute(query)).scalar_one_or_none()
        if result.is_deleted:
            return False
        return True


    @classmethod
    async def check_existing_email(cls, email: EmailStr, session: AsyncSession) -> bool:
        query = select(UserModel).where(UserModel.email == email)
        result = (await session.execute(query)).scalars().first()
        if result:
            return True

        return False

    @classmethod
    async def get_one(cls, user_id: UUID, session: AsyncSession) -> UserModel:
        query = select(UserModel).where(UserModel.id == user_id)
        db_item = (await session.execute(query)).scalars().first()

        return db_item

    @classmethod
    async def update_one(cls, db_user: UserModel, user: UserUpdateSchema, session: AsyncSession) -> UserModel:
        user_dict = user.model_dump(exclude_unset=True)
        for kye, value in user_dict.items():
            setattr(db_user, kye, value)
        await session.commit()
        await session.refresh(db_user)

        return db_user

    @classmethod
    async def soft_delete(cls, db_user: UserModel, session: AsyncSession) -> None:
        db_user.is_deleted = True
        db_user.deleted_at = datetime.now(tz=timezone.utc)
        await session.commit()

        return None
