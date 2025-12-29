import datetime
from typing import List

from sqlalchemy.orm import (
    DeclarativeBase, declared_attr, Mapped, mapped_column, relationship
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import BigInteger, func, String, Boolean, ForeignKey, Enum

from utils.enums import CarClass, UserType


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

    car_number: Mapped[str] = mapped_column(String(10))
    sts_series: Mapped[str] = mapped_column(String(15), nullable=True)
    sts_number: Mapped[str] = mapped_column(String(15))

    car_class: Mapped[CarClass] = mapped_column(Enum(CarClass, name="car_class"), default=CarClass.BASE_CAR, nullable=False)

    photo: Mapped[str] = mapped_column(String(100))
    video: Mapped[str] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship("User")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


class CrossCityOrder(Base):
    from_city: Mapped[str] = mapped_column(String(50))
    from_add: Mapped[str] = mapped_column(String(100))

    destination_city: Mapped[str] = mapped_column(String(50))
    destination_add: Mapped[str] = mapped_column(String(100))

    intermediate_points: Mapped[str] = mapped_column(String(100))

    speed: Mapped[int] = mapped_column()
    date: Mapped[datetime.date] = mapped_column(nullable=True)
    time: Mapped[str] = mapped_column(String(20))

    passengers_number: Mapped[int] = mapped_column()
    car_class: Mapped[CarClass] = mapped_column(String(10))

