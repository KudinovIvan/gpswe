import logging

from .utils.wialon_packages import (
    login_package,
    login_check,
    cut_package,
    cut_check,
    extend_package,
    extend_check,
)
from .db.postgres import get_client, save_client
from .models.client import Client

logging.basicConfig(level=logging.DEBUG)


async def wialon_protocol(data: str, addr: list, dsl: dict):
    """
    Парсинг данных протокола Wialon
    """
    logger = logging.getLogger("gpswe::wialon_protocol")
    if len(data) >= 1:
        if data[1] == "L":
            # Обработка пакета логина
            logger.info("Processing the login package")
            valid_code, validated_data = await login_check(data)
            if valid_code == "1":
                await login_package(dsl, validated_data)
                logger.info("Save the client's address and IMEI")
                await save_client(
                    dsl, Client(ip=addr[0], port=addr[1], imei=validated_data.imei)
                )
            return f"#AL#{valid_code}\r\n"
        elif data[1] == "S" and data[2] == "D":
            # Обработка сокращенного пакета с данными
            logger.info("Processing a shortened data packet")
            logger.info("Get the client's address and IMEI")
            imei = await get_client(dsl, addr[0])
            valid_code, validated_data = await cut_check(data, imei)
            if valid_code == "1":
                await cut_package(dsl, validated_data)
            return f"#ASD#{valid_code}\r\n"
        elif data[1] == "D":
            # Обработка расширенного пакета с данными
            logger.info("Processing an extended data package")
            logger.info("Get the client's address and IMEI")
            imei = await get_client(dsl, addr[0])
            valid_code, validated_data = await extend_check(data, imei)
            if valid_code == "1":
                await extend_package(dsl, validated_data)
            return f"#AD#{valid_code}\r\n"
