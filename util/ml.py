from textrank4zh import TextRank4Keyword, TextRank4Sentence


tr4w = TextRank4Keyword()
def kwe_tr4k(text):
    tr4w.analyze(text=text, lower=True, window=2)  # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象
    # keywords
    words = []
    for item in tr4w.get_keywords(20, word_min_len=2):
        words.append(item.word)
    words = ','.join(words)

    return words
