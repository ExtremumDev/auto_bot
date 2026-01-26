import datetime
from typing import List

from sqlalchemy.dialects.mysql import TINYINT, DATETIME
from sqlalchemy.orm import (
    DeclarativeBase, declared_attr, Mapped, mapped_column, relationship
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import BigInteger, func, String, Boolean, ForeignKey, Enum

from utils.enums import CarClass, UserType, OrderType, OrderStatus, CrossCityOrderSpeed
from utils.text import get_cross_city_order_description


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        table_name = []
        table_name.append(cls.__name__[0].lower())
        for c in cls.__name__[1:]:
            if c.isupper():
                table_name.append('_')
                table_name.append(c.lower())
            else:
                table_name.append(c)

        return ''.join(table_name) + 's'


class User(Base):
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    telegram_username: Mapped[str] = mapped_column(String(35))

    user_type: Mapped[UserType] = mapped_column(Enum(UserType, name="user_type"), nullable=True)

    is_blocked: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(server_default="0")

    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=True)
    driver: Mapped["Driver"] = relationship("Driver", back_populates="user")

    cars: Mapped[List["Car"]] = relationship(
        "Car",
        back_populates="user"
    )

    created_orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="creator",
        foreign_keys="[Order.creator_id]"
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="executor",
        foreign_keys="[Order.executor_id]"
    )

    accepted_orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="responded",
        secondary="users_accepted_orderss"
    )


class Driver(Base):
    user_id: Mapped[int] = mapped_column(nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="driver")

    date_time: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    full_name: Mapped[str] = mapped_column(String(80))
    phone_number: Mapped[str] = mapped_column(String(12))
    city: Mapped[str] = mapped_column(String(20))

    passport_number: Mapped[str] = mapped_column(String(15))
    passport_photo: Mapped[str] = mapped_column(String(50))

    drive_exp: Mapped[int] = mapped_column()

    license_number: Mapped[str] = mapped_column(String(10))
    license_series: Mapped[str] = mapped_column(String(10), nullable=True)
    license_photo_1: Mapped[str] = mapped_column(String(50))
    license_photo_2: Mapped[str] = mapped_column(String(50))

    is_moderated: Mapped[bool] = mapped_column(default=False)



class Car(Base):
    brand: Mapped[str] = mapped_column(String(20))
    model: Mapped[str] = mapped_column(String(30))

    release_year: Mapped[int] = mapped_column()

    car_number: Mapped[str] = mapped_column(String(30))
    sts_series: Mapped[str] = mapped_column(String(30), nullable=True)
    sts_number: Mapped[str] = mapped_column(String(50))

    car_class: Mapped[CarClass] = mapped_column(String(20), default=CarClass.BASE_CAR, nullable=True)

    photo: Mapped[str] = mapped_column(String(100))
    video: Mapped[str] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship("User")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


class CrossCityOrder(Base):
    from_city: Mapped[str] = mapped_column(String(150))

    destination_city: Mapped[str] = mapped_column(String(150))

    intermediate_points: Mapped[str] = mapped_column(String(100))

    speed: Mapped[CrossCityOrderSpeed] = mapped_column(TINYINT)
    date: Mapped[datetime.date] = mapped_column(nullable=True)
    time: Mapped[str] = mapped_column(String(20))

    passengers_number: Mapped[int] = mapped_column()
    car_class: Mapped[CarClass] = mapped_column(String(20), nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="cross_city")

    new_territory_distance: Mapped[int] = mapped_column(default=0, server_default="0")
    rf_distance: Mapped[int] = mapped_column(default=0, server_default="0")

    description: Mapped[str] = mapped_column(String(100), default="")


class PlaceOrder(Base):
    settlement: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(300))

    order: Mapped["Order"] = relationship("Order", back_populates="place_order")


class DeliveryOrder(Base):
    settlement: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(300))

    order: Mapped["Order"] = relationship("Order", back_populates="delivery_order")


class SoberDriverOrder(Base):
    from_point: Mapped[str] = mapped_column(String(80))
    destination_point: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(200))

    order: Mapped["Order"] = relationship("Order", back_populates="sober_driver")



class FreeOrder(Base):
    description: Mapped[str] = mapped_column(String(100))

    order: Mapped["Order"] = relationship("Order", back_populates="free_order")

class UsersAcceptedOrders(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))


class Order(Base):
    order_type: Mapped[OrderType] = mapped_column(TINYINT)
    price: Mapped[int] = mapped_column(default=0, server_default="0")
    date: Mapped[str] = mapped_column(String(30), nullable=True)
    order_status: Mapped[OrderStatus] = mapped_column(TINYINT, default=0, server_default="0")

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    creator: Mapped["User"] = relationship(
        "User",
        lazy="joined",
        back_populates="created_orders",
        foreign_keys=[creator_id],
    )

    executor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    executor: Mapped["User"] = relationship(
        "User",
        back_populates="orders",
        foreign_keys=[executor_id],
        lazy="joined"
    )

    responded: Mapped[List["User"]] = relationship(
        "User",
        back_populates="accepted_orders",
        secondary="users_accepted_orderss",
    )

    cross_city_id: Mapped[int] = mapped_column(ForeignKey("cross_city_orders.id"), nullable=True)
    cross_city: Mapped["CrossCityOrder"] = relationship("CrossCityOrder", lazy="joined", back_populates="order")

    place_order_id: Mapped[int] = mapped_column(ForeignKey("place_orders.id"), nullable=True)
    place_order: Mapped["PlaceOrder"] = relationship("PlaceOrder", lazy="joined", back_populates="order")

    delivery_order_id: Mapped[int] = mapped_column(ForeignKey("delivery_orders.id"), nullable=True)
    delivery_order: Mapped["DeliveryOrder"] = relationship("DeliveryOrder", lazy="joined", back_populates="order")

    sober_driver_id: Mapped[int] = mapped_column(ForeignKey("sober_driver_orders.id"), nullable=True)
    sober_driver: Mapped["SoberDriverOrder"] = relationship("SoberDriverOrder", lazy="joined", back_populates="order")

    free_order_id: Mapped[int] = mapped_column(ForeignKey("free_orders.id"), nullable=True)
    free_order: Mapped["FreeOrder"] = relationship("FreeOrder", lazy="joined", back_populates="order")

    @property
    def full_date(self):
        if self.date:
            return self.date
        else:
            return "Без даты"


    @property
    def full_price(self):
        return f"{self.price} руб" if self.price else ""

    def get_order_name(self) -> str:
        match self.order_type:
            case OrderType.CROSS_CITY:
                return f"{self.full_price} руб {self.cross_city.from_city} - {self.cross_city.destination_city}"
            case OrderType.CITY:
                return f"{self.full_price} {self.full_date} По городу: {self.place_order.settlement}"
            case OrderType.DELIVERY:
                return f"{self.full_price} Доставка: {self.delivery_order.settlement} {self.full_date} "
            case OrderType.SOBER_DRIVER:
                return f"{self.price} Трезвый водитель {self.full_date}"
            case _:
                return "Заказ"

    def get_description(self) -> str:
        match self.order_type:
            case OrderType.CROSS_CITY:
                return get_cross_city_order_description(
                    from_city=self.cross_city.from_city,
                    dest_city=self.cross_city.destination_city,
                    intermediate_points=self.cross_city.intermediate_points,
                    passengers_number=self.cross_city.passengers_number,
                    nt_distance=self.cross_city.new_territory_distance,
                    rf_distance=self.cross_city.rf_distance,
                    price=self.price,
                    description=self.cross_city.description,
                    speed=self.cross_city.speed
                )
            case OrderType.CITY:
                return f"""
Заказ по городу {self.full_price}

{self.full_date}

Город: {self.place_order.settlement}

Описание: {self.place_order.description}
"""
            case OrderType.DELIVERY:
                return f"""
Доставка {self.full_price}

{self.full_date}

Город: {self.delivery_order.settlement}
Описание: {self.delivery_order.description}
"""
            case OrderType.SOBER_DRIVER:
                return f"""
Трезвый водитель {self.full_price}

{self.full_date}

Откуда: {self.sober_driver.from_point}
Куда: {self.sober_driver.destination_point}

Описание: {self.sober_driver.description}
"""
            case _:
                return "Заказ"
