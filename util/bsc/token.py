from util.bsc.constants import busd, usdt, wbnb, usdc

canonicals = [busd, usdt, wbnb, usdc]


def has_canonical(tokens):
    for token in tokens:
        token = token.lower()
        if token in canonicals:
            return True
    return False


def all_canonical(tokens):
    for token in tokens:
        token = token.lower()
        if token not in canonicals:
            return False
    return True
