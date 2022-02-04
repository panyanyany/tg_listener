"""
HTML <-> text conversions.
"""
import re
from html.entities import name2codepoint
from html.parser import HTMLParser

from six import unichr

from util.text.cleaner import clean_text


class HTMLToText(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._buf = []
        self.hide_output = False
        self.paragraph_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'title', 'ul', 'ol', 'li', 'tr', 'div']

    def handle_starttag(self, tag, attrs):
        if tag in ('br', *self.paragraph_tags) and not self.hide_output:
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = True

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self._buf.append('\n')

    def handle_endtag(self, tag):
        if tag in self.paragraph_tags:
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = False

    def handle_data(self, text):
        if text and not self.hide_output:
            self._buf.append(re.sub(r'\s+', ' ', text))

    def handle_entityref(self, name):
        if name in name2codepoint and not self.hide_output:
            c = unichr(name2codepoint[name])
            self._buf.append(c)

    def handle_charref(self, name):
        if not self.hide_output:
            n = int(name[1:], 16) if name.startswith('x') else int(name)
            self._buf.append(unichr(n))

    def get_text(self):
        text = re.sub(r' +', ' ', ''.join(self._buf)).strip()
        return clean_text(text, rm_empty_lines=False, rm_sequential_dup_line=False)


def html_to_text(html: str):
    """
    Given a piece of HTML, return the plain text it contains.
    This handles entities and char refs, but not javascript and stylesheets.
    """
    parser = HTMLToText()
    parser.feed(html)
    parser.close()
    return parser.get_text()


def text_to_html(text):
    """
    Convert the given text to html, wrapping what looks like URLs with <a> tags,
    converting newlines to <br> tags and converting confusing chars into html
    entities.
    """

    def f(mo):
        t = mo.group()
        if len(t) == 1:
            return {'&': '&amp;', "'": '&#39;', '"': '&quot;', '<': '&lt;', '>': '&gt;'}.get(t)
        return '<a href="%s">%s</a>' % (t, t)

    return re.sub(r'https?://[^] ()"\';]+|[&\'"<>]', f, text)
