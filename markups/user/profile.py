from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.models import Driver

def get_profile_markup():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="История редактирования анкеты", callback_data="forms_history")],
            [InlineKeyboardButton(text="Редактировтаь анкету", callback_data="edit_form")],
            [InlineKeyboardButton(text="Управление моими автомобилями", callback_data="car_manage")]
        ]
    )


def get_forms_list_markup(forms_list: list[Driver], is_for_admin: bool = True):

    if is_for_admin:
        callback_data_format = "showformvers_{id}"
    else:
        callback_data_format = "showmyform_{id}"
    if forms_list:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=d.date_time.strftime("%d-%m-%Y"), callback_data=callback_data_format.format(id=d.id))]

                for d in forms_list
            ]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Пользователь еще не заполнял анкету",
                        callback_data=" "
                    )
                ]
            ]
        )


form_edition_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="ФИО", callback_data="formedit_name"),
            InlineKeyboardButton(text="Номер Телефона", callback_data="formedit_phone")
        ],
        [
            InlineKeyboardButton(text="Данные паспорта", callback_data="formedit_passport"),
        ],
        [
            InlineKeyboardButton(text="Данные водительских прав", callback_data="formedit_license")

        ]
    ]
)
