import logging
from contextlib import asynccontextmanager
import asyncpg
from .decorator import backoff
from ..models.egts import EGTSData
from ..models.wialon import WialonLogin, WialonCutData, WialonExtendData
from ..models.client import Client

save_wialon_login_sql = """
    INSERT INTO 
    gpswe.wialon_login (imei, protocol_version, 
    password, crc16) 
    VALUES ($1, $2, 
    $3, $4) ON CONFLICT (imei) DO NOTHING RETURNING imei
    
"""

save_wialon_cut_data_sql = """
    INSERT INTO 
    gpswe.wialon_cut_data (imei, date, 
    time, lat_deg, lat_sign, long_deg,
    long_sign, speed, course, alt,
    sats, crc16) 
    VALUES ($1, $2, 
    $3, $4, $5, $6, $7,
    $8, $9, $10, $11, $12)
"""

save_wialon_extend_data_sql = """
    INSERT INTO 
    gpswe.wialon_extend_data (imei, date, 
    time, lat_deg, lat_sign, long_deg,
    long_sign, speed, course, alt,
    sats, crc16, hdop, inputs,
    outputs, adc, lbutton, params) 
    VALUES ($1, $2, 
    $3, $4, $5, $6, $7,
    $8, $9, $10, $11, $12,
    $13, $14, $15, $16, $17, $18)
"""

save_client_sql = """
    INSERT INTO 
    gpswe.client (ip, port, imei) 
    VALUES ($1, $2, $3)
"""

save_egts_data_sql = """
    INSERT INTO 
    gpswe.egts_data (oid, date, 
    time, lat_deg, long_deg, speed,
    course) 
    VALUES ($1, $2, 
    $3, $4, $5, $6, $7)
"""

get_client_sql = """
    SELECT gc.imei
    FROM gpswe.client AS gc
    WHERE gc.ip IN ({1})
"""


@asynccontextmanager
async def conn_context_postgres(dsl: dict):
    """
    Подключение к базе postgres
    """

    @backoff(logger=logging.getLogger("main::conn_context_postgres"))
    async def connect(dsl: dict):
        conn = await asyncpg.connect(**dsl)
        return conn

    conn = await connect(dsl)
    yield conn
    await conn.close()


async def save_wialon_login(dsl: dict, data: WialonLogin):
    """
    Сохранение WialonLogin
    """
    async with conn_context_postgres(dsl) as conn:
        await conn.fetch(save_wialon_login_sql, *list(data.dict().values()))


async def save_wialon_cut_data(dsl: dict, data: WialonCutData):
    """
    Сохранение WialonCutData
    """
    async with conn_context_postgres(dsl) as conn:
        await conn.fetch(save_wialon_cut_data_sql, *list(data.dict().values()))


async def save_wialon_extend_data(dsl: dict, data: WialonExtendData):
    """
    Сохранение WialonExtendData
    """
    async with conn_context_postgres(dsl) as conn:
        await conn.fetch(save_wialon_extend_data_sql, *list(data.dict().values()))


async def save_client(dsl: dict, data: Client):
    """
    Сохранение Client
    """
    async with conn_context_postgres(dsl) as conn:
        await conn.fetch(save_client_sql, *list(data.dict().values()))


async def save_egts_data(dsl: dict, data: EGTSData):
    """
    Сохранение EGTSData
    """
    async with conn_context_postgres(dsl) as conn:
        await conn.fetch(save_egts_data_sql, *list(data.dict().values()))


async def get_client(dsl: dict, ip: str):
    """
    Получение Client по IP
    """
    async with conn_context_postgres(dsl) as conn:
        current_fetch = await conn.fetch(
            get_client_sql.format({}, ", ".join(f"'{arg}'" for arg in [ip]))
        )
        return current_fetch[0].get("imei")
