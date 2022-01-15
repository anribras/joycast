from enum import Enum


class ErrorCode(Enum):
    ok = 0
    table_insert_error = 0x1001
    data_null = 0x1002
    input_error = 0x1003
    data_deleted = 0x1004


def derived_error(item, extra=None):
    return {
        'status': {
            'code': ErrorCode[item.name].value,
            'message': ErrorCode[item.name].name,
            'extra': extra
        }
    }
