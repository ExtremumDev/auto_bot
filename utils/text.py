from typing import List



def get_user_profile_descr(is_drive: bool, is_drive_confirmed: bool, cars: list) -> str:
    profile_descr = """Профиль пользователя:
{drive_form}
{drive_form_status}

Зарегистрировано автомобилей: {cars_count}

"""

    return profile_descr.format(
        drive_form="✅ Анкета водителя заполнена" if is_drive else "❌ Анкета водителя не заполнена",
        drive_form_status="✅ Анкета водителя подтверждена" if is_drive_confirmed else "⏳ Анкета водителя ожидает модерации",
        cars_count=len(cars) if cars else 0
    )


def get_driver_form_text(driver):
    return f"""
ФИО: {driver.full_name}
Номер телефона: {driver.phone_number}

Опыт вождения: {driver.drive_exp}

Паспорт: {driver.passport_number}

Водительские права: {driver.license_number}
"""

def get_cross_city_order_description(
        from_city, dest_city, intermediate_points, passengers_number, nt_distance, rf_distance, price, description,
        speed, time, date = None
):
    return f"""
Заказ межгород. {speed.name}

{'Дата: ' + date if date else ''}
Время: {time}

Откуда: {from_city}
Куда: {dest_city}

Промежуточные точки: {intermediate_points}

Число пассажиров - {passengers_number}

Километраж по НТ(новые территории) - {nt_distance} км
Километраж по РФ - {rf_distance} км

{price} руб. на руки

Описание: {description}
"""


main_menu_message = """
Открыто главное меню
Минимальные тарифы:

Новые территории (НТ):
• Легковая – 50 руб/км
• Компактвен - 60 руб/км
• Минивен – 70 руб/км

Российская Федерация (РФ):
• Легковая - 20 руб/км
• Компактвен - 25 руб/км
• Минивен - 30 руб/км
"""
