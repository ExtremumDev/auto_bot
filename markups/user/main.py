from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_markup(is_admin: bool = False):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Управление автомобилями", callback_data="car_manage")]
        ]
    )


