import datetime
from typing import List, Any, Dict, Sequence

from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, asc, update
from sqlalchemy.orm import joinedload, selectinload

from utils.enums import OrderType
from .models import User, Driver, Car, CrossCityOrder, Order, PlaceOrder, DeliveryOrder, SoberDriverOrder, FreeOrder


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

    @classmethod
    async def get_many(cls, session: AsyncSession, **kwargs):
        query = select(cls.model).filter_by(**kwargs)
        res = await session.execute(query)
        return res.scalars().all()


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def get_obj(cls, session: AsyncSession, **values):
        query = select(cls.model).options(selectinload(User.driver)).filter_by(**values)

        result = await session.execute(query)
        obj = result.scalar_one_or_none()
        return obj

    @classmethod
    async def get_user_with_cars(cls, session: AsyncSession, **kwargs):
        query = select(cls.model).options(selectinload(User.driver), selectinload(User.cars)).filter_by(
            **kwargs
        )

        result = await session.execute(query)
        obj = result.scalar_one_or_none()
        return obj


    @classmethod
    async def get_drivers(cls, session: AsyncSession):
        query = select(cls.model).filter(
            User.driver_id != None
        )

        res = await session.execute(query)

        return res.scalars().all()


class DriverDAO(BaseDAO):
    model = Driver


    @classmethod
    async def get_all_user_forms(cls, session: AsyncSession, **kwargs):
        query = select(cls.model).filter_by(
            **kwargs
        )
        res = await session.execute(query)
        return res.scalars().all()


    @classmethod
    async def get_driver_form(cls, session: AsyncSession, obj_id):
        query = select(cls.model).options(selectinload(Driver.user)).filter_by(
            id=obj_id
        )
        res = await session.execute(query)
        return res.scalar_one_or_none()

class CarDAO(BaseDAO):
    model = Car


class OrderDAO(BaseDAO):
    model = Order

    @classmethod
    async def add_order(cls, session: AsyncSession, order_type: OrderType, **order_kwargs):

        order = Order(order_type=order_type)

        order_class = None
        order_key = None

        match order_type:
            case OrderType.CROSS_CITY:
                order_class = CrossCityOrder
                order_key = "cross_city"
            case OrderType.CITY:
                order_class = PlaceOrder
                order_key = "place_order"
            case OrderType.DELIVERY:
                order_class = DeliveryOrder
                order_key = "delivery_order"
            case OrderType.SOBER_DRIVER:
                order_class = SoberDriverOrder
                order_key = "sober_driver"
            case OrderType.FREE_ORDER:
                order_class = FreeOrder
                order_key = "free_order"

        sub_order = order_class(**order_kwargs)

        await session.flush()
        await session.refresh(sub_order)

        order.__setattr__(order_key, sub_order)

        await session.commit()

        return order

    @classmethod
    async def get_active_orders(cls, session: AsyncSession, *args) -> Sequence[Order]:
        query = select(Order).filter_by()

        res = await session.execute(query)

        return res.scalars().all()

