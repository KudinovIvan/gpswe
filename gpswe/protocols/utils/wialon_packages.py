from ..models.wialon import WialonLogin, WialonCutData, WialonExtendData
from ..models.validators import check_datetime, check_coord, check_speed_course_alt_sats_hdop, check_adc, check_params
from ..models.validators import DataFieldNames
from ..config.settings import settings
from ..utils.wialon_parser import login_parser, cut_parser, extend_parser
from .calculation_data.crc import crc
from ..db.postgres import save_wialon_login, save_wialon_cut_data, save_wialon_extend_data


async def login_check(data: str):
    try:
        login_data = WialonLogin(**login_parser(data[3:].split(";")))
    except Exception:
        return "0", None
    if login_data.protocol_version != settings.WIALON_PROTOCOL_VERSION:
        return "0", None
    if login_data.crc16 != crc(data[3:data.rfind(";")+1], 'crc-16'):
        return "10", None
    #TODO! проверка на пароль будет позже, valid_code 01
    return "1", login_data

async def login_package(dsl: dict, data: WialonLogin):
    await save_wialon_login(dsl, data)

async def cut_check(data: str, imei: str):
    try:
        cut_data = WialonCutData(**cut_parser(data[4:].split(";"), imei))
    except Exception as e:
        return "-1", None
    valid_code, cut_data.date = check_datetime(cut_data.date, DataFieldNames.DATE)
    if valid_code != "1":
        return valid_code, None
    valid_code, cut_data.time = check_datetime(cut_data.time, DataFieldNames.TIME)
    if valid_code != "1":
        return valid_code, None
    valid_code, cut_data.lat_deg = check_coord(cut_data.lat_deg, cut_data.lat_sign, DataFieldNames.LAT)
    if valid_code != "1":
        return valid_code, None
    valid_code, cut_data.long_deg = check_coord(cut_data.long_deg, cut_data.long_sign, DataFieldNames.LON)
    if valid_code != "1":
        return valid_code, None
    valid_code, cut_data.alt = check_speed_course_alt_sats_hdop(cut_data.alt)
    if valid_code != "1":
        return valid_code, None
    valid_code, cut_data.speed = check_speed_course_alt_sats_hdop(cut_data.speed)
    if valid_code != "1":
        return valid_code, None
    valid_code, cut_data.course = check_speed_course_alt_sats_hdop(cut_data.course, DataFieldNames.COURSE)
    if valid_code != "1":
        return valid_code, None
    valid_code, cut_data.sats = check_speed_course_alt_sats_hdop(cut_data.sats, DataFieldNames.SATS)
    if valid_code != "1":
        return valid_code, None
    print(cut_data.crc16)
    print(crc(data[4:data.rfind(";")+1], 'crc-16'))
    if cut_data.crc16 != crc(data[4:data.rfind(";")+1], 'crc-16'):
        return "13", None
    #TODO! проверка на пароль будет позже, valid_code 01
    return "1", cut_data

async def cut_package(dsl: dict, data: WialonCutData):
    await save_wialon_cut_data(dsl, data)

async def extend_check(data: str, imei: str):
    try:
        extend_data = WialonExtendData(**extend_parser(data[3:].split(";"), imei))
    except Exception:
        return "-1", None
    valid_code, extend_data.date = check_datetime(extend_data.date, DataFieldNames.DATE)
    if valid_code != "1":
        return valid_code, None
    valid_code, extend_data.time = check_datetime(extend_data.time, DataFieldNames.TIME)
    if valid_code != "1":
        return valid_code, None
    valid_code, extend_data.lat_deg = check_coord(extend_data.lat_deg, extend_data.lat_sign, DataFieldNames.LAT)
    if valid_code != "1":
        return valid_code, None
    valid_code, extend_data.long_deg = check_coord(extend_data.long_deg, extend_data.long_sign, DataFieldNames.LON)
    if valid_code != "1":
        return valid_code, None
    valid_code, extend_data.alt = check_speed_course_alt_sats_hdop(extend_data.alt)
    if valid_code != "1":
        return valid_code, None
    valid_code, extend_data.speed = check_speed_course_alt_sats_hdop(extend_data.speed)
    if valid_code != "1":
        return valid_code, None
    valid_code, extend_data.course = check_speed_course_alt_sats_hdop(extend_data.course, DataFieldNames.COURSE)
    if valid_code != "1":
        return valid_code, None
    valid_code, extend_data.sats = check_speed_course_alt_sats_hdop(extend_data.sats, DataFieldNames.SATS)
    if valid_code != "1":
        return valid_code, None
    valid_code, extend_data.hdop = check_speed_course_alt_sats_hdop(extend_data.hdop, DataFieldNames.HDOP)
    if valid_code != "1":
        return valid_code, None
    valid_code, extend_data.inputs = check_speed_course_alt_sats_hdop(extend_data.inputs, DataFieldNames.INPUTS)
    if valid_code != "1":
        return valid_code, None
    valid_code, extend_data.outputs = check_speed_course_alt_sats_hdop(extend_data.outputs, DataFieldNames.OUTPUTS)
    if valid_code != "1":
        return valid_code, None
    valid_code, extend_data.adc = check_adc(extend_data.adc)
    if valid_code != "1":
        return valid_code, None
    valid_code, extend_data.params = check_params(extend_data.params)
    if valid_code != "1":
        return valid_code, None
    if extend_data.crc16 != crc(data[4:data.rfind(";")+1], 'crc-16'):
        return "16", None
    #TODO! проверка на пароль будет позже, valid_code 01
    return "1", extend_data

async def extend_package(dsl: dict, data: WialonExtendData):
    await save_wialon_extend_data(dsl, data)
