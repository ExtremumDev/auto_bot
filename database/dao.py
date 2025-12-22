import datetime
from typing import List, Any, Dict, Sequence

from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, asc, update
from sqlalchemy.orm import joinedload, selectinload

from .models import User, MemberEvent, EventMembership, Initiative, UserProfile, DatingProfile


class BaseDAO:
    model = None

    @classmethod
    async def add(cls, session: AsyncSession, **values):
        new_instance = cls.model(**values)
        session.add(new_instance)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return new_instance

    @classmethod
    async def get_obj(cls, session: AsyncSession, **values):
        query = select(cls.model).filter_by(**values)

        result = await session.execute(query)
        obj = result.scalar_one_or_none()
        return obj

    @classmethod
    async def add_many(cls, session: AsyncSession, instances: List[Dict[str, Any]]):
        new_instances = [cls.model(**values) for values in instances]
        session.add_all(new_instances)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return new_instances

    @classmethod
    async def delete_obj(cls, session: AsyncSession, obj_id):
        query = delete(cls.model).filter_by(id=obj_id)
        await session.execute(query)


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def register_user(
        cls,
        session: AsyncSession,
        telegram_id: int,
        username: str,
        has_bot_chat: bool,
        is_admin: bool = False
    ) -> User:
        return await cls.add(
            session,
            telegram_id=telegram_id,
            telegram_username=username,
            has_private=has_bot_chat,
            is_admin=is_admin
        )

    @classmethod
    async def get_obj(cls, session: AsyncSession, **values):
        query = select(cls.model).options(selectinload(User.profile)).filter_by(**values)

        result = await session.execute(query)
        obj = result.scalar_one_or_none()
        return obj
