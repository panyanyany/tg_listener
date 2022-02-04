

def str_valid(col_def, val, raise_err=False):
    # val = getattr(md, col_def.name)
    if len(val) > col_def.type.length:
        if raise_err:
            raise ValueError("%s is too long: %s > %s" % (col_def.name, len(val), col_def.type.length))
        return False

    return True

def str_trunc(col_def, val):
    return val[:col_def.type.length]
