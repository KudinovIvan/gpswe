import logging
from contextlib import asynccontextmanager
import asyncpg
from .decorator import backoff

init_gpswe = '''
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
'''

@asynccontextmanager
async def conn_context_postgres(dsl: dict):
    """
    Подключение к базе postgres
    """

    @backoff(logger=logging.getLogger('main::conn_context_postgres'))
    async def connect(dsl: dict):
        conn = await asyncpg.connect(**dsl)
        return conn

    conn = await connect(dsl)
    yield conn
    await conn.close()


async def postgres_init(dsl):
    async with conn_context_postgres(dsl) as conn:
        await conn.execute(init_gpswe)
