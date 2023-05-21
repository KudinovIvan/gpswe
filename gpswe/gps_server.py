import asyncio
import datetime
from config.settings import settings
import logging
from connections import handle_connection
from db.postgres import postgres_init, postgres_get_info

logging.basicConfig(level=logging.DEBUG)


async def _init_db():
    """
    Инициализация БД
    """
    logger = logging.getLogger("gpswe::init_db")
    if (
        settings.POSTGRES_DB
        and settings.POSTGRES_PORT
        and settings.POSTGRES_HOST
        and settings.POSTGRES_PASSWORD
        and settings.POSTGRES_USER
    ):
        dsl = {
            "database": settings.POSTGRES_DB,
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD,
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
        }
        logger.info("Start initialized db")
        await postgres_init(dsl)
    else:
        logger.warning("Not all DB data was provided")


def init_db():
    """
    Ассинхронный запуск инициализации БД
    """
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_init_db())


async def _start_server():
    """
    Запуск сервера
    """
    logger = logging.getLogger("gpswe::start_server")
    if (
        settings.POSTGRES_DB
        and settings.POSTGRES_PORT
        and settings.POSTGRES_HOST
        and settings.POSTGRES_PASSWORD
        and settings.POSTGRES_USER
    ):
        server = await asyncio.start_server(
            handle_connection, settings.HOST, settings.PORT
        )
        async with server:
            logger.info(f"Server started at: {settings.HOST}:{settings.PORT}")
            await server.serve_forever()
    else:
        logger.warning("Not all DB data was provided")


def start_server():
    """
    Ассинхронный запуск сервера
    """
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_start_server())


async def _get_coordinates(
    imei: str, from_datetime: datetime.datetime, to_datetime: datetime.datetime
):
    """
    Получение доп. данных в промежутке дат
    """
    logger = logging.getLogger("gpswe::get_coordinates")
    if (
        settings.POSTGRES_DB
        and settings.POSTGRES_PORT
        and settings.POSTGRES_HOST
        and settings.POSTGRES_PASSWORD
        and settings.POSTGRES_USER
    ):
        dsl = {
            "database": settings.POSTGRES_DB,
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD,
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
        }
        logger.info("Get extend GPS data")
        return await postgres_get_info(dsl, imei, from_datetime, to_datetime)
    else:
        logger.warning("Not all DB data was provided")


def get_coordinates(
    imei: str, from_datetime: datetime.datetime, to_datetime: datetime.datetime
):
    """
    Ассинхронный запуск получение доп. данных в промежутке дат
    """
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(_get_coordinates(imei, from_datetime, to_datetime))
