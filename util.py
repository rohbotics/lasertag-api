import json

from typing import Tuple, List

def error_message(message: str, code: int) -> Tuple[str, int]:
    return json.dumps({"msg": message}) + '\r\n', code

def id_to_string(id : int) -> str:
    return hex(id)[2:]

def id_from_string(id: str) -> int:
    return int(id, 16)

