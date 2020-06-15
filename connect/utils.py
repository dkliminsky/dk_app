import struct


def bytes_to_float(data: bytes) -> float:
    return struct.unpack('<f', data)[0]


def bytes_to_uint(data: bytes) -> int:
    return int.from_bytes(data, byteorder='little', signed=False)


def int8_to_bytes(value: int) -> bytes:
    return value.to_bytes(1, byteorder='little')


def int16_to_bytes(value: int) -> bytes:
    return value.to_bytes(2, byteorder='little')


def int32_to_bytes(value: int) -> bytes:
    return value.to_bytes(4, byteorder='little')


def float_to_bytes(value: float) -> bytes:
    return struct.pack("f", value)