import bs4


def get_text(el):
    if isinstance(el, bs4.element.Comment):
        return ''
    if hasattr(el, 'get_text'):
        text = el.get_text('\n')
    else:
        text = str(el)

    return text
