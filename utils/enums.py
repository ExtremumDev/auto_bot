from enum import Enum


class CarClass(Enum):
    BASE_CAR = 1
    COMPACTVAN = 2
    MINIVAN = 3

    @property
    def name(self) -> str:
        names = {
            CarClass.BASE_CAR: "Легковой",
            CarClass.COMPACTVAN: "Компактвен",
            CarClass.MINIVAN: "Минивен"
        }
        return names.get(self, "Автомобиль")

