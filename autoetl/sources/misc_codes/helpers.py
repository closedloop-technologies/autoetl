import hashlib
import json
from datetime import datetime
import numpy as np


async def object_to_coroutine(obj):
    return obj


async def collect_coroutines(async_generator):
    coroutines = []
    async for coroutine in async_generator:
        coroutines.append(coroutine)
    return coroutines


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.isoformat() if isinstance(obj, datetime) else super().default(obj)


def hash_dictionary(d, kind="dict"):
    serialized_dict = f"{kind}({json.dumps(d, sort_keys=True, cls=DateTimeEncoder)})"
    hash_object = hashlib.sha256()
    hash_object.update(serialized_dict.encode())
    return hash_object.hexdigest()
