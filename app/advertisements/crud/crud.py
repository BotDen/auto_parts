from uuid import UUID

from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.advertisements.models import AdvertisementBase
from app.advertisements.schemas import AdvertisementCreateSchema, AdvertisementUpdateSchema
from app.users.models import UserBase


class CRUDAdvertisement:
    @classmethod
    async def create_advertisement(
        cls,
        ad: AdvertisementCreateSchema,
        current_user: UserBase,
        session: AsyncSession,
    ) -> AdvertisementBase:
        model_ad = AdvertisementBase(
            title=ad.title,
            description=ad.description,
            price=ad.price,
            photos_url=ad.photos_url,
            author_id=current_user.id,
        )
        session.add(model_ad)
        await session.commit()
        await session.refresh(model_ad)

        return model_ad

    @classmethod
    async def get_advertisement(cls, ad_id: UUID, session: AsyncSession) -> AdvertisementBase:
        query = select(AdvertisementBase).where(AdvertisementBase.id == ad_id).options(selectinload(AdvertisementBase.author))
        db_item = (await session.execute(query)).scalars().first()

        return db_item

    @classmethod
    async def get_all_advertisements(cls, session: AsyncSession) -> Sequence[AdvertisementBase]:
        query = select(AdvertisementBase).options(selectinload(AdvertisementBase.author))
        db_items = list((await session.execute(query)).scalars().all())

        return db_items

    @classmethod
    async def update_advertisement(
        cls,
        db_item: AdvertisementBase,
        update_ad: AdvertisementUpdateSchema,
        session: AsyncSession
    ) -> AdvertisementBase:
        update_ad_dict = update_ad.model_dump(exclude_unset=True)
        for key, value in update_ad_dict.items():
            setattr(db_item, key, value)
        await session.commit()
        await session.refresh(db_item)

        return db_item

    @classmethod
    async def delete_advertisement(cls, db_item: AdvertisementBase, session: AsyncSession) -> None:
        await session.delete(db_item)
        await session.commit()

        return None
