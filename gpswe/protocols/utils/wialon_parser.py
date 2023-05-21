def login_parser(data: list):
    return {
        "protocol_version": data[0],
        "imei": data[1],
        "password": data[2],
        "crc16": data[3]
    }

def cut_parser(data: list, imei: str):
    return {
        "imei": imei,
        "date": data[0],
        "time": data[1],
        "lat_deg": data[2],
        "lat_sign": data[3],
        "long_deg": data[4],
        "long_sign": data[5],
        "speed": data[6],
        "course": data[7],
        "alt": data[8],
        "sats": data[9],
        "crc16": data[10]
    }

def extend_parser(data: list, imei: str):
    return {
        "imei": imei,
        "date": data[0],
        "time": data[1],
        "lat_deg": data[2],
        "lat_sign": data[3],
        "long_deg": data[4],
        "long_sign": data[5],
        "speed": data[6],
        "course": data[7],
        "alt": data[8],
        "sats": data[9],
        "hdop": data[10],
        "inputs": data[11],
        "outputs": data[12],
        "adc": data[13],
        "lbutton": data[14],
        "params": data[15],
        "crc16": data[16]
    }
