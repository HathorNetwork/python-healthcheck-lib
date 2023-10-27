def get_enum_value(enum_member):
    """Return the value a enum member.
        This is needed because some older versions of Python don't support the `value` attribute.
    """
    try:
        return enum_member.value
    except AttributeError:
        return enum_member
