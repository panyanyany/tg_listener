from util.bsc.constants import busd, usdt, wbnb

canonicals = [busd, usdt, wbnb]


def has_canonical(tokens):
    for token in tokens:
        token = token.lower()
        if token in canonicals:
            return True
    return False
