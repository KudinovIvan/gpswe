from asgiref.sync import sync_to_async
from .utils.egts_packages import headers_package, data_encode_package, data_package, data_response
from .utils.egts_parser import egts_parser
from .models.egts import EGTSData

async def egts_protocol(item: str, dsl: dict):
    result_code, pid, offset_data = await headers_package(item)
    if offset_data:
        encoded_data = await data_encode_package(
            item,
            offset_data.get("current_offset"),
            offset_data.get("header_length"),
            offset_data.get("frame_data_length")
        )
        for encoded_data_item in encoded_data:
            validated_data = EGTSData(**egts_parser(encoded_data_item))
            await data_package(validated_data, dsl)
    return await data_response(pid, result_code)
