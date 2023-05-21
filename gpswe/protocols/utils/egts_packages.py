import datetime
import logging
from ctypes import c_uint8, c_uint16, c_uint32
from .calculation_data.crc import crc
from ..models.egts import EGTSData
from enum import Enum
import pickle
from ..db.postgres import save_egts_data

logging.basicConfig(level=logging.DEBUG)

EGTS_SR_RECORD_RESPONSE = 0
EGTS_SR_POS_DATA = 16


class ResultCodes(Enum):
    """
    Список кодов для ответа на EGTS
    """

    EGTS_PC_OK = 0
    EGTS_PC_UNS_PROTOCOL = 128
    EGTS_PC_DECRYPT_ERROR = 129
    EGTS_PC_INC_HEADERFORM = 131
    EGTS_PC_INC_DATAFORM = 132
    EGTS_PC_HEADERCRC_ERROR = 137
    EGTS_PC_DATACRC_ERROR = 138
    EGTS_PC_TTLEXPIRED = 144


async def headers_package(data: bytearray):
    """
    Парсинг заголовка
    """
    logger = logging.getLogger("gpswe::headers_package")
    protocol_version = c_uint16(data[0]).value
    prefix = c_uint16(data[2] << 8 * 7).value + c_uint16(data[2] << 8 * 6).value
    rte = c_uint16(data[2] << 8 * 5).value
    ena = str(c_uint16(data[2] << 8 * 4).value) + str(c_uint16(data[2] << 8 * 3).value)
    cmp = c_uint16(data[2] << 8 * 3).value
    pid = c_uint16(data[7] << 8 * 0).value + c_uint16(data[8] << 8 * 1).value
    if protocol_version != 1 or prefix != 0:
        return ResultCodes.EGTS_PC_UNS_PROTOCOL.value, pid, None
    header_length = c_uint16(data[3]).value
    if header_length not in [11, 16]:
        return ResultCodes.EGTS_PC_INC_HEADERFORM.value, pid, None
    frame_data_length = (
        c_uint16(data[5] << 8 * 0).value + c_uint16(data[6] << 8 * 1).value
    )
    ttl = c_uint16(data[14]).value
    hcs = c_uint16(data[15]).value
    if hcs != crc(data[:15], "crc-8", False):
        logger.warning("EGTS_PC_HEADERCRC_ERROR")
        return ResultCodes.EGTS_PC_HEADERCRC_ERROR.value, pid, None
    if rte != 0:
        if ttl > 0:
            logger.warning("Plug on the router")
            # Заглушка на маршрутизатор
            return None, None, None
        else:
            logger.warning("EGTS_PC_TTLEXPIRED")
            return ResultCodes.EGTS_PC_TTLEXPIRED.value, pid, None
        pass
    if frame_data_length <= 0:
        logger.warning("EGTS_PC_OK")
        return ResultCodes.EGTS_PC_OK.value, pid, None
    sfrcs = c_uint16(data[-2] << 8 * 0).value + c_uint16(data[-1] << 8 * 1).value
    if sfrcs != crc(data[header_length:-2], "crc-ccitt-false", False):
        logger.warning("EGTS_PC_DATACRC_ERROR")
        return ResultCodes.EGTS_PC_DATACRC_ERROR.value, pid, None
    if ena != "00":
        logger.warning("EGTS_PC_DECRYPT_ERROR")
        return ResultCodes.EGTS_PC_DECRYPT_ERROR.value, pid, None
    if cmp != 0:
        logger.warning("EGTS_PC_INC_DATAFORM")
        return ResultCodes.EGTS_PC_INC_DATAFORM.value, pid, None
    current_offset = header_length
    return (
        ResultCodes.EGTS_PC_OK.value,
        pid,
        {
            "current_offset": current_offset,
            "header_length": header_length,
            "frame_data_length": frame_data_length,
        },
    )


async def data_encode_package(
    data: bytearray, current_offset: int, header_length: int, frame_data_length: int
):
    """
    Парсинг тела запроса
    """
    logger = logging.getLogger("gpswe::data_encode_package")
    encoded_data = []
    while current_offset < header_length + frame_data_length - 7:
        record_len = (
            c_uint16(data[current_offset] << 8 * 0).value
            + c_uint16(data[current_offset + 1] << 8 * 1).value
        )
        current_offset += 2
        current_offset += 2
        rfl = c_uint16(data[current_offset]).value
        current_offset += 1
        oid = None
        if rfl & 1:
            oid = (
                c_uint32(data[current_offset] << 8 * 0).value
                + c_uint32(data[current_offset + 1] << 8 * 1).value
                + c_uint32(data[current_offset + 2] << 8 * 2).value
                + c_uint32(data[current_offset + 3] << 8 * 3).value
            )
            current_offset += 4
        if rfl & 2:
            current_offset += 4
        if rfl & 4:
            current_offset += 4
        current_offset += 2
        srd_offset = current_offset
        if oid:
            while srd_offset < record_len:
                subrecord_type = c_uint16(data[srd_offset]).value
                srd_offset += 3
                if subrecord_type == EGTS_SR_RECORD_RESPONSE:
                    logger.info("parsing EGTS_SR_RECORD_RESPONSE section")
                    break
                elif subrecord_type == EGTS_SR_POS_DATA:
                    logger.info("parsing EGTS_SR_POS_DATA section")
                    navigate_time = (
                        c_uint32(data[srd_offset] << 8 * 0).value
                        + c_uint32(data[srd_offset + 1] << 8 * 1).value
                        + c_uint32(data[srd_offset + 2] << 8 * 2).value
                        + c_uint32(data[srd_offset + 3] << 8 * 3).value
                    )
                    navigate_time += 1262304000
                    date_time = datetime.datetime.utcfromtimestamp(navigate_time)
                    date = date_time.date()
                    time = date_time.time()
                    lat_deg = (
                        (
                            c_uint32(data[srd_offset + 4] << 8 * 0).value
                            + c_uint32(data[srd_offset + 5] << 8 * 1).value
                            + c_uint32(data[srd_offset + 6] << 8 * 2).value
                            + c_uint32(data[srd_offset + 7] << 8 * 3).value
                        )
                        * 90
                        / 0xFFFFFFFF
                    )
                    long_deg = (
                        (
                            c_uint32(data[srd_offset + 8] << 8 * 0).value
                            + c_uint32(data[srd_offset + 9] << 8 * 1).value
                            + c_uint32(data[srd_offset + 10] << 8 * 2).value
                            + c_uint32(data[srd_offset + 11] << 8 * 3).value
                        )
                        * 180
                        / 0xFFFFFFFF
                    )
                    flags = [
                        int(x)
                        for x in "{:08b}".format(c_uint8(data[srd_offset + 12]).value)
                    ]
                    if flags[2]:
                        lat_deg = round(-lat_deg, 7)
                    else:
                        lat_deg = round(lat_deg, 7)
                    if flags[1]:
                        long_deg = round(-long_deg, 7)
                    else:
                        long_deg = round(long_deg, 7)
                    speed = (
                        c_uint16(data[srd_offset + 13] << 14 * 0).value
                        + c_uint16(data[srd_offset + 14] << 2 * 1).value
                    )
                    dir_higest_bit = speed >> 15
                    speed <<= 2
                    speed >>= 2
                    speed = speed / 10
                    direction = c_uint16(data[srd_offset + 15]).value
                    srd_offset += 15
                    course = direction | dir_higest_bit << 7
                    encoded_data_item = [
                        oid,
                        date,
                        time,
                        lat_deg,
                        long_deg,
                        speed,
                        course,
                    ]
                    encoded_data.append(encoded_data_item)
                else:
                    logger.warning(f"Unknown section type: {subrecord_type}")
                current_offset += srd_offset
    return encoded_data


async def data_response(pid: int, result_code: int):
    """
    Формирование ответа для EGTS
    """
    response = []
    body_len = 3
    response.append(0x01)
    response.append(0x00)
    response.append(0x00)
    response.append(0x0B)
    response.append(0x00)
    response.append(body_len & 0xFF)
    response.append(body_len >> 8)
    response.append((pid + 1) & 0xFF)
    response.append((pid + 1) >> 8)
    response.append(0x00)
    resp_crc = crc(bytearray(pickle.dumps(response)), "crc-8", False)
    response.append(hex(resp_crc))
    response.append(pid & 0xFF)
    response.append(pid >> 8)
    response.append(hex(result_code))
    return bytearray(pickle.dumps(response))


async def data_package(data: EGTSData, dsl: dict):
    """
    Сохранение данных с EGTS
    """
    await save_egts_data(dsl, data)
