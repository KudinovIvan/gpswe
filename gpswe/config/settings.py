from typing import Optional
from pydantic import BaseModel


class ServerSettings(BaseModel):
    """
    Пользовательские настройки библиотеки
    """

    BUFF_SIZE: Optional[int]
    HOST: Optional[str]
    PORT: Optional[int]
    WIALON_PROTOCOL_VERSION: Optional[str]
    EGTS_PROTOCOL_VERSION: Optional[str]
    POSTGRES_DB: Optional[str]
    POSTGRES_USER: Optional[str]
    POSTGRES_PASSWORD: Optional[str]
    POSTGRES_HOST: Optional[str]
    POSTGRES_PORT: Optional[str]

settings = ServerSettings()

"""
Инициализация настроек для тестирования
"""

settings.BUFF_SIZE = 8192
settings.HOST = "0.0.0.0"
settings.PORT = 10500
settings.WIALON_PROTOCOL_VERSION = "2.0"
settings.POSTGRES_DB = "gpswe_test"
settings.POSTGRES_USER = "test"
settings.POSTGRES_PASSWORD = "pass"
settings.POSTGRES_HOST = "0.0.0.0"
settings.POSTGRES_PORT = "5432"
