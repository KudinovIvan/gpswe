import datetime
from typing import Optional
from pydantic import BaseModel


class EGTSData(BaseModel):
    """
    Пакет с данными с EGTS
    """
    oid: Optional[int]
    date: Optional[datetime.date]
    time: Optional[datetime.time]
    lat_deg: Optional[float]
    long_deg: Optional[float]
    speed: Optional[int]
    course: Optional[int]
