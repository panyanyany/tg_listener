import re


def msub(match, text, repl=''):
    """将 re.search 的结果作为目标，以 repl 替换其在 text 中的内容"""

    if not match:
        return text
    return ssub(match.span(), text, repl)

def ssub(span, text, repl=''):
    """s for span, 将 text 内以 span 指代的区间用 repl 替换掉"""
    beg, end = span
    text = text[:beg] + repl + text[end:]
    return text
