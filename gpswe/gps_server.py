import asyncio

from config.settings import settings
from config.logger import logger
from connections import handle_connection
from db.postgres import postgres_init


async def _init_db():
    if settings.POSTGRES_DB and settings.POSTGRES_PORT and settings.POSTGRES_HOST \
        and settings.POSTGRES_PASSWORD and settings.POSTGRES_USER:
        dsl = {
            'database': settings.POSTGRES_DB,
            'user': settings.POSTGRES_USER,
            'password': settings.POSTGRES_PASSWORD,
            'host': settings.POSTGRES_HOST,
            'port': settings.POSTGRES_PORT
        }
        await postgres_init(dsl)
    else:
        logger.warning(f"Not all DB data was provided")


def init_db():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_init_db())


async def _start_server():
    if settings.POSTGRES_DB and settings.POSTGRES_PORT and settings.POSTGRES_HOST \
        and settings.POSTGRES_PASSWORD and settings.POSTGRES_USER:
        server = await asyncio.start_server(handle_connection, settings.HOST, settings.PORT)
        async with server:
            logger.info(f"Server started at: {settings.HOST}:{settings.PORT}")
            await server.serve_forever()
    else:
        logger.warning(f"Not all DB data was provided")

def start_server():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_start_server())


#async def _get_coordinates():
#    if settings.POSTGRES_DB and settings.POSTGRES_PORT and settings.POSTGRES_HOST \
#        and settings.POSTGRES_PASSWORD and settings.POSTGRES_USER:
#        dsl = {
#            'database': settings.POSTGRES_DB,
#            'user': settings.POSTGRES_USER,
#            'password': settings.POSTGRES_PASSWORD,
#            'host': settings.POSTGRES_HOST,
#            'port': settings.POSTGRES_PORT
#        }
#        await postgres_init(dsl)
#    else:
#        logger.warning(f"Not all DB data was provided")


#def get_coordinates():
#    loop = asyncio.new_event_loop()
#    loop.run_until_complete(_get_coordinates())