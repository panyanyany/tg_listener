from util.bsc.constants import busd, usdt, wbnb, usdc, cake

canonicals = [busd, usdt, wbnb, usdc, cake]


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


StdToken = {
    wbnb: 'BNB',
    busd: 'BUSD',
    usdt: 'USDT',
    usdc: 'USDC',
    cake: 'CAKE',
}


def get_token_name(token):
    return StdToken.get(token.lower(), token.lower())
