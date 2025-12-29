from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_car_manage_menu_markup():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить автомобиль", callback_data="add_car")]
        ]
    )
