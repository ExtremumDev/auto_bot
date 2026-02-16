from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from config import AdminsSettings


def get_main_markup(user_id: int):
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Мой профиль", callback_data="my_profile")],
            [InlineKeyboardButton(text="Создать заказ", callback_data="new_order")],
            [InlineKeyboardButton(text="Активные заказы", callback_data="active_orders")],
            [InlineKeyboardButton(text="ПРАВИЛА", callback_data="rules")],
            [InlineKeyboardButton(text="Образцы оформления заказов", callback_data="orders_rules")]
        ]
    )

    if user_id in AdminsSettings.ADMIN_ID + AdminsSettings.MAIN_ADMIN_ID:
        inline_keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="Админ-панель",
                    callback_data="admin_panel"
                )
            ]
        )

    return inline_keyboard



profile_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Редактировать анкету", callback_data="edit_drive_form")],
        [InlineKeyboardButton(text="Управление моими автомобилями", callback_data="car_manage")]
    ]
)


user_type_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Я пассажир", callback_data="usertype_p")],
        [InlineKeyboardButton(text="Я водитель", callback_data="usertype_d")]
    ]
)

start_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Заполнить анкету", callback_data="fill_form")],
        [InlineKeyboardButton(text="Открыть главное меню", callback_data="main_menu")]
    ]
)

cancel_action_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_action")]
    ]
)

main_reply_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Создать заказ"), KeyboardButton(text="🚖 Стать водителем")],
        [KeyboardButton(text="👤 Личный кабиент")],
    ]
)
