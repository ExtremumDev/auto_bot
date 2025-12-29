from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

order_type_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Межгород", callback_data="ordertype_1")],
        [InlineKeyboardButton(text="По городу", callback_data="ordertype_2")],
        [InlineKeyboardButton(text="Доставка", callback_data="ordertype_3")],
        [InlineKeyboardButton(text="Трезвый водитель", callback_data="ordertype_4")],
        [InlineKeyboardButton(text="Свободный заказ", callback_data="ordertype_5")],
    ]
)

order_speed_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Срочный", callback_data="orderspeed_0")],
        [InlineKeyboardButton(text="Текущий", callback_data="orderspeed_1")],
        [InlineKeyboardButton(text="Предварительный", callback_data="orderspeed_2")],
    ]
)
