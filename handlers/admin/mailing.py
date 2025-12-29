from aiogram import types, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import PhotoSize
from sqlalchemy.ext.asyncio import AsyncSession

from bot import bot
from database.dao import UserDAO
from database.utils import connection
from filters.users import AdminFilter
from fsm.admin.admin import MailingFSM


async def ask_mailing_text(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(MailingFSM.text_state)
    await c.message.answer(
        "Введите текст сообщения рассылки"
    )

    await c.answer()


async def handle_text(m: types.Message, state: FSMContext):
    await state.set_state(MailingFSM.photo_state)
    if m.photo:
        await state.update_data(text=m.caption)
        await handle_photo(m, state)
    else:
        await state.update_data(text=m.text)

        await m.answer(
            "Если хотите сделать рассылку с картинкой, пришлите ее, если нет - пришлите любой текст, чтобы пропустить"
        )


async def handle_photo(m: types.Message, state: FSMContext):

    photo = None
    if m.photo:
        photo = m.photo[0]


    await state.update_data(photo=photo)

    s_data = await state.get_data()

    await send_mailing(text=s_data['text'], photo=s_data['photo'])


@connection
async def send_mailing(text: str, db_session: AsyncSession, photo: PhotoSize | None = None, *args):
    users = await UserDAO.get_drivers(session=db_session)

    if photo:
        method = bot.send_photo
        kwargs = {"photo": photo, "caption": text}
    else:
        method = bot.send_message()
        kwargs = {"text": text}

    for u in users:
        try:
            await method(kwargs)
        except TelegramBadRequest:
            continue


def register_mailing_handlers(dp: Dispatcher):
    dp.callback_query.register(ask_mailing_text, F.data == "new_mailing", AdminFilter())
    dp.message.register(handle_text, StateFilter(MailingFSM.text_state))
    dp.message.register(handle_photo, StateFilter(MailingFSM.photo_state))
