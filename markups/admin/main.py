from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_panel_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Посмотреть статистику", callback_data="statistic"),
            InlineKeyboardButton(text="Изменить правила", callback_data="edit_rules")
         ],
        [
            InlineKeyboardButton(text="Новая рассылка водителям", callback_data="new_mailing")
        ],
        [InlineKeyboardButton(text="Управление пользователями", callback_data="users_manage")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="main_menu")]
    ]
)


return_to_admin_panel_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад в меню", callback_data="admin_panel")]
    ]
)
