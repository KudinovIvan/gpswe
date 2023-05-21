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


settings = ServerSettings()
settings.BUFF_SIZE = 8192
settings.HOST = "0.0.0.0"
settings.PORT = 10500
settings.WIALON_PROTOCOL_VERSION = "2.0"
