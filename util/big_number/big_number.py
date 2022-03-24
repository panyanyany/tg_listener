import decimal

ctx = decimal.Context()


def float_to_str(f):
    ctx.prec = 256
    """
    Convert the given float to a string,
    without resorting to scientific notation
    """
    d1 = ctx.create_decimal(repr(f))
    return format(d1, 'f')
