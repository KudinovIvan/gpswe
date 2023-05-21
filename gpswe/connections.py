from config.logger import logger
from protocols.wialon import wialon_protocol
from protocols.egts import egts_protocol
from config.settings import settings

async def handle_connection(reader, writer):
    # Получение ip клиента
    addr = writer.get_extra_info("peername")
    # Сохраняем данные БД
    dsl = {
        'database': settings.POSTGRES_DB,
        'user': settings.POSTGRES_USER,
        'password': settings.POSTGRES_PASSWORD,
        'host': settings.POSTGRES_HOST,
        'port': settings.POSTGRES_PORT
    }
    logger.info(f"Connected by {addr}")
    while True:
        try:
            # Получаем данные с клиента
            data = await reader.read(settings.BUFF_SIZE)
        except ConnectionError:
            logger.info(f"Client suddenly closed while receiving from {addr}")
            break
        if not data:
            break
        data = data.upper()
        try:
            answer = data.decode("utf-8").split("\r\n")
            for item in answer:
                send_data = await wialon_protocol(item, addr, dsl)
                # Отправление ответа клиенту
                try:
                    writer.write(bytearray(send_data.encode("utf-8")))
                    await writer.drain()
                except ConnectionError:
                    logger.info("Client suddenly closed, cannot send")
                    break
        except UnicodeDecodeError:
            answer = data
            send_data = await egts_protocol(answer, dsl)
            # Отправление ответа клиенту
            try:
                writer.write(send_data)
                await writer.drain()
            except ConnectionError:
                logger.info("Client suddenly closed, cannot send")
                break
    writer.close()
    await writer.wait_closed()
    logger.info(f"Disconnected by: {addr}")
