import json
from collections import OrderedDict

import hanlp
from hanlp.common.component import Component

from util.text.cleaner import split_into_sentences


class Store:
    hanlp_loaded = False
    Recoginzer: Component = False


RecognizeRecord = None


def load_hanlp(record_class):
    global RecognizeRecord
    RecognizeRecord = record_class
    if not Store.hanlp_loaded:
        Store.Recognizer = hanlp.load(hanlp.pretrained.ner.MSRA_NER_BERT_BASE_ZH)
        Store.hanlp_loaded = True


def recognize(line):
    # print([line])
    md: RecognizeRecord = RecognizeRecord.get_or_none(RecognizeRecord.line == line)
    if md:
        return json.loads(md.result)

    load_hanlp()
    rec = Store.Recognizer(list(line))

    md = RecognizeRecord()
    md.line = line
    md.result = json.dumps(rec, ensure_ascii=False)
    md.save()
    return rec


def get_names(line):
    names = []
    recs = recognize_text(line)
    recs = recs.values()
    for line_recs in recs:
        for rec in line_recs:
            # print('--- rec', rec)
            if rec[1] == 'NR':
                names.append(rec[0])
    return names


def get_first_name(line, min_length=2):
    names, orgs = get_names_n_orgs(line[:15])
    for name in names:
        if len(name) >= min_length:
            return name
    return None


def get_orgs(line, min_length=2):
    _, orgs = get_names_n_orgs(line, min_length)
    return orgs


def get_names_n_orgs(line, min_length=0):
    names = []
    orgs = []
    recs = recognize_text(line)
    recs = recs.values()
    for line_recs in recs:
        for rec in line_recs:
            # print('--- rec', rec)
            if rec[1] == 'NR' and len(rec[0]) >= min_length:
                names.append(rec[0])
            elif rec[1] == 'NT' and len(rec[0]) >= min_length:
                orgs.append(rec[0])

    names = list(map(lambda e: e.replace(' ', ''), names))
    names = list(map(lambda e: e.replace('　', ''), names))
    for i, name in enumerate(names):
        if any(c.isalpha() for c in name):
            continue
        name = name.replace(' ', '')
        name = name.replace('　', '')
        names[i] = name
    return names, orgs


def recognize_text(text):
    lines = split_into_sentences(text)
    records = OrderedDict()
    for line in lines:
        records[line] = recognize(line)
    return records
