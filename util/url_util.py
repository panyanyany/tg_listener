

def toFileName(s):
    s =  s.replace('.', '_')
    return ''.join(list(filter(lambda e: e.isalnum() or e == '_', s)))
