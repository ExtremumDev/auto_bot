from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.enums import CarClass


def get_car_manage_menu_markup():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить автомобиль", callback_data="add_car")]
        ]
    )

car_class_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=c.name, callback_data=f"carclass_{c.value}")]
        for c in CarClass
    ]
)
