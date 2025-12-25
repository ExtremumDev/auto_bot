from typing import List

from sqlalchemy.orm import (
    DeclarativeBase, declared_attr, Mapped, mapped_column, relationship
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import BigInteger, func, String, Boolean, ForeignKey

from utils.enums import CarClass


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

    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=True)
    driver: Mapped["Driver"] = relationship("Driver", back_populates="user")

    cars: Mapped[List["Car"]] = relationship(
        "Car",
        back_populates="user"
    )


class Driver(Base):
    user: Mapped["User"] = relationship("User", back_populates="driver")

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



class Car(Base):
    brand: Mapped[str] = mapped_column(String(20))
    model: Mapped[str] = mapped_column(String(30))

    release_year: Mapped[int] = mapped_column()

    car_number: Mapped[str] = mapped_column(String(10))
    sts_series: Mapped[str] = mapped_column(String(15), nullable=True)
    sts_number: Mapped[str] = mapped_column(String(15))

    car_class: Mapped[CarClass] = mapped_column()

    photo: Mapped[str] = mapped_column()
    video: Mapped[str] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship("User")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

