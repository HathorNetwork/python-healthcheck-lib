from enum import Enum
from typing import Any


def get_enum_value(enum_member: Enum) -> Any:
    """Return the value a enum member.
    This is needed because some older versions of Python don't support the `value` attribute.
    """
    try:
        return enum_member.value
    except AttributeError:
        return enum_member
