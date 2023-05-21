import datetime
from typing import Optional, Union
from pydantic import BaseModel, validator


class WialonLogin(BaseModel):
    """
    Пакет логина:
    Предназначен для авторизации устройства на сервере
    """
    imei: str
    protocol_version: str
    password: Optional[str]
    crc16: int


class WialonCutData(BaseModel):
    """
    Сокращенный пакет с данными:
    Содержит только навигационные данные
    """
    imei: Optional[str]
    date: Union[str, datetime.date, None]
    time: Union[str, datetime.time, None]
    lat_deg: Union[str, float, None]
    lat_sign: Union[str, None]
    long_deg: Union[str, float, None]
    long_sign: Union[str, None]
    speed: Union[str, int, None]
    course: Union[str, int, None]
    alt: Union[str, int, None]
    sats: Union[str, int, None]
    crc16: int


class WialonExtendData(WialonCutData):
    """
    Расширенный пакет с данными:
    Содержит дополнительные структуры данных
    """
    hdop: Union[str, float, None]
    inputs: Union[str, int, None]
    outputs: Union[str, int, None]
    adc: Union[str, None]
    lbutton: Union[str, None]
    params: Union[str, None]
