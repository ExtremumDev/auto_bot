import asyncio


from bot import bot, dp
from handlers import register_all_handlers
from utils.logger import get_bot_logger, setup_logger


async def on_startup():
    register_all_handlers(dp)

    get_bot_logger().info('Бот начал свою работу')


async def on_shutdown():
    get_bot_logger().info('Бот завершил свою работу')


async def main():
    setup_logger()
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
