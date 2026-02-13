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

        if passengers_number >= 7:
            classes = [cls.MINIVAN]
        elif passengers_number > 4:
            classes = [cls.COMPACTVAN, cls.MINIVAN]
        else:
            classes = [cls.BASE_CAR, cls.COMPACTVAN, cls.MINIVAN]

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=c.name, callback_data=f"carclass_{c.value}")]
                for c in classes
            ]
        )


class CrossCityOrderSpeed(Enum):
    FAST = 0
    CURRENT = 1
    PRE = 2

    def __str__(self):
        match self:
            case CrossCityOrderSpeed.FAST:
                return "Срочный"
            case CrossCityOrderSpeed.CURRENT:
                return "Текущий"
            case CrossCityOrderSpeed.PRE:
                return "Предварительный"
            case _:
                return ""


class UserType(Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"


class OrderType(int, Enum):
    CROSS_CITY = 1
    CITY = 2
    DELIVERY = 3
    SOBER_DRIVER = 4
    FREE_ORDER = 5


class OrderStatus(int, Enum):
    SEARCHING = 0
    ACCEPTED = 1
    FINISHED = 2
