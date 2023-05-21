from config.logger import logger
from typing import Optional
import datetime
from enum import Enum

class DataFieldNames(Enum):
    DATE = "date"
    TIME = "time"
    LAT = "lat"
    LON = "lon"
    COURSE = "course"
    SATS = "sats"
    HDOP = "hdop"
    INPUTS = "inputs"
    OUTPUTS = "outputs"

class CoordSignFieldNames(Enum):
    N = "N"
    S = "S"
    E = "E"
    W = "W"

class ErrorData(Enum):
    DATETIME = "0"
    COORD = "10"
    SPEED_COURSE_ALT = "11"
    SATS_HDOP = "12"
    INPUTS_OUTPUTS = "13"
    ADC = "14"
    PARAMS = "15"
    PARAMS_LEN_LIMIT = "15.1"
    PARAMS_SPACE = "15.2"

def check_datetime(value: str, field_name: DataFieldNames):
    if value is None or value == 'NA':
        today = datetime.datetime.now()
        if field_name == DataFieldNames.DATE:
            return "1", today.date()
        if field_name == DataFieldNames.TIME:
            return "1", today.time()
    try:
        if field_name == DataFieldNames.DATE:
            return "1", datetime.datetime.strptime(
                value, "%d%m%y"
            ).date()
        elif field_name == DataFieldNames.TIME:
            return "1", datetime.datetime.strptime(
                value, "%H%M%S.%f"
            ).time()
    except Exception as e:
        return ErrorData.DATETIME.value, None
    return value

def check_coord(value: str, sign: str, field_name: DataFieldNames):
    try:
        if field_name == DataFieldNames.LAT:
            if sign == CoordSignFieldNames.N.value:
                return "1", round(
                    int(value[:2]) + float(value[2:]) / 60, 7
                )
            elif sign == CoordSignFieldNames.S.value:
                return "1", round(
                    int(value[:2]) - float(value[2:]) / 60, 7
                )
            else:
                raise Exception()
        elif field_name == DataFieldNames.LON:
            if sign == CoordSignFieldNames.E.value:
                return "1", round(
                    int(value[:3]) + float(value[3:]) / 60, 7
                )
            elif sign == CoordSignFieldNames.W.value:
                return "1", round(
                    int(value[:3]) - float(value[3:]) / 60, 7
                )
            else:
                raise Exception()
    except Exception as e:
        return ErrorData.COORD.value, None

def check_speed_course_alt_sats_hdop(value: str, field_name:DataFieldNames = None):
    try:
        if value == 'NA':
            return "1", None
        if field_name == DataFieldNames.COURSE and int(value) not in range(359):
            raise Exception()
        if field_name == DataFieldNames.HDOP:
            return "1", float(value)
        return "1", int(value)
    except Exception as e:
        if field_name in [DataFieldNames.SATS, DataFieldNames.HDOP]:
            return ErrorData.SATS_HDOP.value, None
        if field_name in [DataFieldNames.INPUTS, DataFieldNames.OUTPUTS]:
            return ErrorData.INPUTS_OUTPUTS.value, None
        return ErrorData.SPEED_COURSE_ALT.value, None

def check_adc(value):
    try:
        if value == '':
            return "1", None
        if value[0] != "1":
            raise Exception()
        value.split(',')
        return "1", value
    except Exception as e:
        return ErrorData.ADC.value, None

def check_params(value):
    if " " in value:
        return ErrorData.PARAMS_SPACE, None
    try:
        params = value.split(',')
        for param in params:
            param_values = param.split(":")
            if len(param_values[0]) > 40:
                return ErrorData.PARAMS_LEN_LIMIT.value, None
            if int(param_values[1]) not in range(1,3):
                raise Exception()
        return "1", value
    except Exception:
        return ErrorData.PARAMS.value, None
