import re
from typing import Callable

from cuid2 import cuid_wrapper

cuid_generator: Callable[[], str] = cuid_wrapper()


def make_valid_folder_name(name: str) -> str:
    """Makes a valid folder name"""
    name = re.sub("[^a-zA-Z0-9]", "_", name)
    name = re.sub("_+", "_", name)
    # remove leading and trailing underscores
    name = re.sub("_+$", "", name)
    name = re.sub("^_+", "", name)
    return name
