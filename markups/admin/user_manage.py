from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_user_manage_markup(user_id, is_user_blocked: bool, is_user_admin: bool, is_extended = False):
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Посмотреть анкету", callback_data=f"showform_{user_id}")
            ],
            [
                InlineKeyboardButton(text="История изменения анкеты", callback_data=f"showformh_{user_id}")
            ],
            [
                InlineKeyboardButton(
                    text="Посмотреть автмобили",
                    callback_data=f"showcars_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⛔️ Удалить пользователя",
                    callback_data=f"deluser_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Разблокировать",
                    callback_data=f"unblockuser_{user_id}"
                ) if is_user_blocked else InlineKeyboardButton(
                    text="🚫 Заблокировать",
                    callback_data=f"blockuser_{user_id}"
                )
            ]
        ]
    )

    if is_extended:
        inline_keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text= "Разжаловать" if is_user_admin else"Сделать администратором",
                    callback_data=f"changerights_{user_id}"
                )
            ]
        )
    return inline_keyboard

def get_approve_form_markup(user_id: int, is_moderated: bool):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Анкета уже отмодерирвоана",
                    callback_data=" "
                ) if is_moderated else InlineKeyboardButton(
                    text="✅ Одобрить",
                    callback_data=f"approve_{user_id}"
                )
            ]
        ]
    )

def get_moderate_driver_markup(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Посмотреть анкету", callback_data=f"showform_{user_id}")]
        ]
    )
