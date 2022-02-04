import re
from itertools import groupby

win_newline_match_pattern = re.compile(r'(\r\n)+')
newline_match_pattern = re.compile(r'\n+')
multi_line_match_pattern = re.compile(r' *\n+ *')
space_match_pattern = re.compile(r'[\t \xa0　]+')
sentence_split_pattern = re.compile(r'[;；。！!]')
micro_sentence_split_pattern = re.compile(r'[,，]')


def clean_text(text, rm_sequential_dup_line=True, rm_empty_lines=True):
    # print([text])
    text = space_match_pattern.sub(' ', text)
    # print([text])
    text = win_newline_match_pattern.sub('\n', text)
    if rm_empty_lines:
        text = newline_match_pattern.sub('\n', text)
        text = multi_line_match_pattern.sub('\n', text)
        text = newline_match_pattern.sub('\n', text)
    # print([text])
    text = text.strip()

    lines = text.split('\n')
    # 过滤掉连续重复的内容
    if rm_sequential_dup_line:
        lines = [x[0] for x in groupby(lines)]
    text = '\n'.join(lines)
    # print()
    # input('>')
    return text


def clean_lines(lines, merge_number=True):
    new_lines = []
    for line in lines:
        line = clean_text(line)
        if line:
            new_lines.append(line)

    return new_lines


def _split_into_micro_sentences(sentence):
    ms = micro_sentence_split_pattern.split(sentence)
    ms = clean_lines(ms)
    return ms


def split_into_sentences(text, max_length=125, drop_exceeded=True):
    sentences = newline_match_pattern.split(text)
    new_sentences = []
    for s in sentences:
        ss = sentence_split_pattern.split(s)
        ss = clean_lines(ss)
        new_sentences += ss

    # print(1, new_sentences)
    sentences, new_sentences = new_sentences, []
    for s in sentences:
        if len(s) > max_length:
            ss = _split_into_micro_sentences(s)
            new_sentences += ss
        else:
            new_sentences.append(s)

    # print(2, new_sentences)
    sentences, new_sentences = new_sentences, []
    for s in sentences:
        if len(s) > max_length and drop_exceeded:
            continue
        new_sentences.append(s)

    # print(3, new_sentences)
    return new_sentences
