def egts_parser(data: list):
    """
    Парсер пакета EGTS для модели EGTSData
    """
    return {
        "oid": data[0],
        "date": data[1],
        "time": data[2],
        "lat_deg": data[3],
        "long_deg": data[4],
        "speed": data[5],
        "course": data[6],
    }
