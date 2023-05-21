import logging
from contextlib import asynccontextmanager
import asyncpg
import geopy.distance
import datetime
from .decorator import backoff

init_gpswe = """
    CREATE SCHEMA IF NOT EXISTS gpswe;

    CREATE TABLE IF NOT EXISTS gpswe.wialon_login (
        imei TEXT PRIMARY KEY,
        protocol_version TEXT NOT NULL,
        password TEXT,
        crc16 INTEGER NOT NULL,
        created timestamp with time zone,
        modified timestamp with time zone
    );

    CREATE TABLE IF NOT EXISTS gpswe.wialon_cut_data (
        id SERIAL PRIMARY KEY,
        imei TEXT,
        date DATE,
        time TIME,
        lat_deg DECIMAL,
        lat_sign TEXT,
        long_deg DECIMAL,
        long_sign TEXT,
        speed INTEGER,
        course INTEGER,
        alt INTEGER,
        sats INTEGER,
        crc16 INTEGER NOT NULL,
        created timestamp with time zone,
        modified timestamp with time zone,
        FOREIGN KEY (imei) REFERENCES gpswe.wialon_login(imei) ON DELETE CASCADE
    );
    
    CREATE TABLE IF NOT EXISTS gpswe.wialon_extend_data (
        id SERIAL PRIMARY KEY,
        imei TEXT,
        date DATE,
        time TIME,
        lat_deg DECIMAL,
        lat_sign TEXT,
        long_deg DECIMAL,
        long_sign TEXT,
        speed INTEGER,
        course INTEGER,
        alt INTEGER,
        crc16 INTEGER NOT NULL,
        sats INTEGER,
        hdop DECIMAL,
        inputs INTEGER,
        outputs INTEGER,
        adc TEXT,
        lbutton TEXT,
        params TEXT,
        created timestamp with time zone,
        modified timestamp with time zone,
        FOREIGN KEY (imei) REFERENCES gpswe.wialon_login(imei) ON DELETE CASCADE
    );
    
    CREATE TABLE IF NOT EXISTS gpswe.client (
        ip TEXT PRIMARY KEY,
        port INTEGER,
        imei TEXT, 
        FOREIGN KEY (imei) REFERENCES gpswe.wialon_login(imei) ON DELETE CASCADE
    );
    
    CREATE TABLE IF NOT EXISTS gpswe.egts_data (
        id SERIAL PRIMARY KEY,
        oid INTEGER NOT NULL,
        date DATE NOT NULL,
        time TIME NOT NULL,
        lat_deg DECIMAL NOT NULL,
        long_deg DECIMAL NOT NULL,
        speed INTEGER NOT NULL,
        course INTEGER NOT NULL,
        created timestamp with time zone,
        modified timestamp with time zone
    );
"""

get_cut_wialon_info_sql = """
    SELECT dt.long_deg, dt.lat_deg, dt.speed, dt.datetime 
    FROM (
    SELECT long_deg, lat_deg, speed, date+time::time as datetime 
    FROM gpswe.wialon_cut_data
    WHERE imei = '{imei}'
    ) as dt
    WHERE dt.datetime BETWEEN '{from_datetime}' AND '{to_datetime}'
"""

check_cut_wialon_sql = """
    SELECT EXISTS
    ( SELECT 1
    FROM gpswe.wialon_cut_data as wcd
    WHERE wcd.imei = '{imei}'
    )
"""

get_extend_wialon_info_sql = """
    SELECT dt.long_deg, dt.lat_deg, dt.speed, dt.datetime 
    FROM (
    SELECT long_deg, lat_deg, speed, date+time::time as datetime 
    FROM gpswe.wialon_extend_data
    WHERE imei = '{imei}'
    ) as dt
    WHERE dt.datetime BETWEEN '{from_datetime}' AND '{to_datetime}'
"""

check_extend_wialon_sql = """
    SELECT EXISTS
    ( SELECT 1
    FROM gpswe.wialon_extend_data as wed
    WHERE wed.imei = '{imei}'
    )
"""

get_egts_info_sql = """
    SELECT dt.long_deg, dt.lat_deg, dt.speed, dt.datetime 
    FROM (
    SELECT long_deg, lat_deg, speed, date+time::time as datetime 
    FROM gpswe.egts_data
    WHERE oid = '{imei}'
    ) as dt
    WHERE dt.datetime BETWEEN '{from_datetime}' AND '{to_datetime}'
"""

check_egts_sql = """
    SELECT EXISTS
    ( SELECT 1
    FROM gpswe.egts_data as egts
    WHERE egts.oid = '{imei}'
    )
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


async def postgres_init(dsl: dict):
    """
    Создание всех необходимых таблиц
    """
    async with conn_context_postgres(dsl) as conn:
        await conn.execute(init_gpswe)


async def postgres_get_info(
    dsl: dict,
    imei: str,
    from_datetime: datetime.datetime,
    to_datetime: datetime.datetime,
):
    """
    Получение информации по GPS в промежуток времени
    """
    async with conn_context_postgres(dsl) as conn:
        resp = []
        resp_data = {"speed": "", "distance": "", "coordinates": []}
        extend_wialon = await conn.fetchval(check_extend_wialon_sql.format(imei=imei))
        if extend_wialon:
            resp = await conn.fetchval(
                get_extend_wialon_info_sql.format(
                    imei=imei,
                    from_datetime=from_datetime,
                    to_datetime=to_datetime,
                )
            )
        cut_wialon = await conn.fetchval(check_cut_wialon_sql.format(imei=imei))
        if cut_wialon:
            resp = await conn.fetchval(
                get_cut_wialon_info_sql.format(
                    imei=imei,
                    from_datetime=from_datetime,
                    to_datetime=to_datetime,
                )
            )
        egts = await conn.fetchval(check_egts_sql.format(imei=imei))
        if egts:
            resp = await conn.fetch(
                get_egts_info_sql.format(
                    imei=imei,
                    from_datetime=from_datetime,
                    to_datetime=to_datetime,
                )
            )
        if len(resp) > 0:
            resp_data["speed"] = await get_average_speed(
                [item.get("speed") for item in resp]
            )
            resp_data["distance"] = await get_distance(
                [
                    [float(item.get("lat_deg")), float(item.get("long_deg"))]
                    for item in resp
                ]
            )
            resp_data["coordinates"] = [
                {
                    "latitude": float(item.get("lat_deg")),
                    "longitude": float(item.get("long_deg")),
                }
                for item in resp
            ]
        return resp_data


async def get_average_speed(speed_list: list):
    """
    Расчет средней скорости
    """
    speed = 0
    result_speed_list = []
    for speed_item in speed_list:
        if speed_item and speed_item > 0:
            result_speed_list.append(speed_item)
    if len(result_speed_list) > 0:
        speed = round(sum(result_speed_list) / len(result_speed_list), 1)
    return speed


async def get_distance(coordinates: list):
    """
    Расчет пройденного расстояния
    """
    distance = 0
    for i in range(len(coordinates) - 1):
        coords_1 = (
            float(
                coordinates[i][0]
                if coordinates[i][0] is not None and coordinates[i][0] != ""
                else 0
            ),
            float(
                coordinates[i][1]
                if coordinates[i][1] is not None and coordinates[i][1] != ""
                else 0
            ),
        )
        coords_2 = (
            float(
                coordinates[i + 1][0]
                if coordinates[i + 1][0] is not None and coordinates[i + 1][0] != ""
                else 0
            ),
            float(
                coordinates[i + 1][1]
                if coordinates[i + 1][1] is not None and coordinates[i + 1][1] != ""
                else 0
            ),
        )
        distance += geopy.distance.geodesic(coords_1, coords_2).km
    return round(distance, 1)
