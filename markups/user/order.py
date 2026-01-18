from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_accept_order_markup(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Принять заказ", callback_data=f"acceptorder_{order_id}")]
        ]
    )


def get_give_order_markup(order_id: int, user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отдать заказ этому пользователю", callback_data=f"giveorder_{order_id}")]
        ]
    )


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
