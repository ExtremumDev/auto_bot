import datetime
from pathlib import Path

from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_only

from database.dao import UserDAO


async def check_user_blocked(telegram_id: int, db_session: AsyncSession):
    """
    :return: True - if user blocked, False - if not
    """
    user = await UserDAO.get_obj(session=db_session, telegram_id=telegram_id)

    if user:
        return user.is_blocked
    return True


async def check_and_save_photo(message: types.Message, save_path: Path, file_name_format: str) -> bool | str:
    """

    :param message:
    :param save_path:
    :param file_name_format:
    :return: if image correct and was saved - file name will be returned, else - false
    """
    if message.photo:
        file = await message.bot.get_file(message.photo[-1].file_id)

        if file.file_path and '.' in file.file_path:
            file_extension = '.' + file.file_path.split('.')[-1].lower()
        else:
            file_extension = ".jpg"

        file_name = file_name_format.format(
            user_id=message.from_user.id,
            datetime=datetime.datetime.now().strftime("%d-%m-%Y_%H-%M"),
        )

        file_name += file_extension

        await message.bot.download_file(
            file.file_path,
            save_path / file_name
        )

        return file_name


    elif message.document:
        await message.answer(
            "Пожалуйста пришлите фотографию не как файл, а как картинку"
        )
    else:
        await message.answer(
            "Необходимо прислать фотографию! Попробуйте еще раз"
        )
    return False


async def check_and_save_video_message(message: types.Message, save_path: Path, file_name_format: str) -> bool | str:
    """

    :param message:
    :param save_path:
    :param file_name_format:
    :return: if vide message correct and was saved - file name will be returned, else - false
    """
    if message.video_note:
        file = await message.bot.get_file(message.video_note.file_id)

        file_name = file_name_format.format(
            user_id=message.from_user.id,
            datetime=datetime.datetime.now().strftime("%d-%m-%Y_%H-%M"),
        )

        file_name += ".mp4"

        await message.bot.download_file(
            file.file_path,
            save_path / file_name,
            timeout=60
        )

        return file_name

    else:
        await message.answer(
            "Необходимо прислать видеосообщение! Попробуйте еще раз"
        )
    return False

