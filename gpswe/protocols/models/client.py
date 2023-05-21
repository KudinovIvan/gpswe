from typing import Optional
from pydantic import BaseModel


class Client(BaseModel):
    """
    Данные подключенного клиента
    """

    ip: Optional[str]
    port: Optional[int]
    imei: Optional[str]
