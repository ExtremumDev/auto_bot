from enum import Enum

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class CarClass(Enum):
    BASE_CAR = "base"
    COMPACTVAN = "compactvan"
    MINIVAN = "minivan"

    @property
    def name(self) -> str:
        names = {
            CarClass.BASE_CAR: "Легковой",
            CarClass.COMPACTVAN: "Компактвен",
            CarClass.MINIVAN: "Минивен"
        }
        return names.get(self, "Автомобиль")

    @classmethod
    def get_choice_by_passengers_number(cls, passengers_number: int = 0):
        classes = []

        if passengers_number < 7:
            classes = [cls.BASE_CAR, cls.COMPACTVAN, cls.MINIVAN]
        else:
            classes = [cls.MINIVAN]

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=c.name, callback_data=f"carclass_{c.value}")]
                for c in classes
            ]
        )


class UserType(Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"


class OrderType(int, Enum):
    CROSS_CITY = 1
    CITY = 2
    DELIVERY = 3
    SOBER_DRIVER = 4
    FREE_ORDER = 5
