
from . import currency


def findCodes(symb):
    codes = []
    for s, c in currency.symbol_and_code:
        if symb in s:
            codes.append(c)

    return codes


def findSymb(code):
    for s, c in currency.symbol_and_code:
        if code == c:
            return s
