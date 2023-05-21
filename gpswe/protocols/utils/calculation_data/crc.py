import crcmod.predefined

def crc(data: str, crc_type: str, need_encode = True):
    # Создаем объект CRC с предустановленным параметром
    crc = crcmod.predefined.Crc(crc_type)
    # Кодируем строку в байты, если необходимо
    if need_encode:
        data = data.encode('utf-8')
    # Вычисляем контрольную сумму
    checksum = crc.new(data).hexdigest()
    return int(checksum, 16)
