import re
from itertools import groupby

import bs4
import lxml
import lxml.html
from bs4 import BeautifulSoup

from helpers import hanlp_helper, text_clean_helper

from util.html.bs4_util import get_text


class CommonParentFinder:
    def __init__(self, soup, keywords: [str]):
        # soup = BeautifulSoup(self.html, 'lxml')
        self.soup = soup
        self.html = str(soup)
        self.text = soup.get_text('\n')
        self.keywords = keywords
        self.intro_els = []
        self.parent_el = None

    def find(self):
        # 根据 keywords 找它们的 node
        els = []
        # print(f'---- keywords={self.keywords}')
        for keyword in self.keywords:
            el = self.find_common_el_by_word(keyword)
            # print(keyword, [t.name for t in el.parents])
            # print([keyword, el])
            if not el:
                # print('*' * 8, keyword, el)
                continue
            els.append(el)
        # print('els ----- ', '\n---\n'.join(map(str, els)))
        if not els:
            return

        # for el in els:
        #     print([tag.name for tag in el.parents])
        # 合并相同节点
        _els = []
        _els_exists = {}
        for el in els:
            if str(el) in _els_exists:
                continue
            _els.append(el)
            _els_exists[str(el)] = True
        els = _els
        if len(els) == 1:
            # 所有人名分布在同一节点下
            self.intro_els = els
            return

        # print('els', len(els))
        # 统计出最大公共父节点数量
        parents_cnt = {}
        for el in els:
            cnt = len(list(el.parents))
            parents_cnt.setdefault(cnt, 0)
            parents_cnt[cnt] += 1

        pairs = sorted(parents_cnt.items(), key=lambda pair: pair[1], reverse=True)
        max_pair = pairs[0]
        max_cnt = max_pair[0]

        # 移除不在同一层级的元素
        new_els = []
        for el in els:
            if len(list(el.parents)) == max_cnt:
                new_els.append(el)

        last_parent = None
        # 找出公共父节点
        while len(new_els) > 1:
            for i, el in enumerate(new_els):
                new_els[i] = el.parent

            if new_els[0] == new_els[1]:
                break
        max_parent_el = new_els[0]
        self.parent_el = max_parent_el

        # 遍历子孙，找到所有简介节点
        intro_els = []
        tmp_max_cnt = max_cnt
        # print(f'---- tmp_max_cnt={tmp_max_cnt}, max_parent_el={max_parent_el.name}')
        while True:
            intro_els = self.find_intro_els(tmp_max_cnt, max_parent_el)
            # print('=' * 10, tmp_max_cnt, len(list(max_parent_el.parents)), len(intro_els))
            if len(list(max_parent_el.parents)) + 1 == tmp_max_cnt:
                break
            retry = False
            for el in intro_els:
                if not hasattr(el, 'get_text') or el.get_text().strip() == '':
                    tmp_max_cnt -= 1
                    retry = True
                    break
            if not retry:
                break

        # print('=' * 10, len(intro_els))
        # for el in intro_els:
        #     parents = list(filter(None, el.parents))
        #     parents = list(map(lambda e: e.name, parents))
        #     parents.reverse()
        #     print(parents)
        intro_els = self.shift_up_els(intro_els)
        self.intro_els = intro_els

        if len(intro_els) == 0:
            return max_parent_el

        # 判断下 intro_els 是否包含了比较多的「无人名」段落
        too_many_empty_names = False
        name_cnt = 0
        test_el_cnt = min(5, len(intro_els))
        for i in range(test_el_cnt):
            el = intro_els[i]
            if hasattr(el, 'get_text'):
                text = el.get_text()
            else:
                text = str(el)
            text = text_clean_helper.clean_text(text)
            name = hanlp_helper.get_first_name(text)
            if name:
                name_cnt += 1
            else:
                pass
                # print('^^^^^^^^^^', names, text)

        if float(name_cnt) / test_el_cnt >= 0.7:
            too_many_empty_names = False
        else:
            too_many_empty_names = True

        # print('%%%%%%%%%%%%', len(intro_els), too_many_empty_names)
        if too_many_empty_names:
            if self.more_text_in_parent(intro_els):
                # print('44444444, more_text_in_parent')
                intro_els = [intro_els[0].parent]
            elif self.more_text_between_names(intro_els):
                # print('33333333')
                intro_els = [intro_els[0].parent]
            elif self.name_els_fewer_than_detect(intro_els):
                # print('22222222')
                intro_els = [intro_els[0].parent]
            # intro_els = [intro_els[0].parent]
        else:
            if self.more_text_between_names(intro_els):
                intro_els = [intro_els[0].parent]

        self.intro_els = intro_els

        return max_parent_el

    def name_els_fewer_than_detect(self, intro_els):
        name_els = []
        for el in intro_els:
            line = get_text(el).strip()
            name = hanlp_helper.get_first_name(line)
            if name:
                name_els.append(el)

        return len(name_els) + 2 < len(self.keywords)

    def more_text_between_names(self, intro_els):
        text_els = []
        for el in intro_els:
            text = get_text(el).strip()
            if not text:
                continue
            if not hanlp_helper.get_first_name(text):
                continue
            text_els.append(el)

        total_check_cnt = 3
        if len(text_els) < total_check_cnt + 1:
            return False
        check_hit_cnt = 0
        existed_index = {-1: True}

        for i in range(total_check_cnt):
            # beg_text = end_text = ''
            beg_el = text_els[i]
            end_el = text_els[i + 1]

            beg_text = get_text(beg_el).strip()
            end_text = get_text(end_el).strip()

            existed_index[i] = True
            # print('beg', beg_text)
            # print('end', end_text)

            beg_text_idx = self.text.index(beg_text)
            end_text_idx = self.text.index(end_text)

            mid_text = self.text[beg_text_idx + len(beg_text): end_text_idx]
            # print('--- mid_text', len(mid_text))

            if len(mid_text) >= 100:
                check_hit_cnt += 1

        return check_hit_cnt >= 2

    def more_text_in_parent(self, intro_els):
        text_els = []
        for el in intro_els:
            text = get_text(el).strip()
            text = text_clean_helper.clean_text(text)
            if not text:
                continue
            name = hanlp_helper.get_first_name(text)
            if not name:
                continue
            text_els.append(el)

        el_text_cnt = 0
        parent_el_text_cnt = 0
        href_cnt = 0
        p_text_list = []
        for i, el in enumerate(text_els):
            text = get_text(el).strip()
            text = text_clean_helper.clean_text(text)
            el_text_cnt += len(text)

            a_el = None
            if el.name and el.name.lower() == 'a':
                a_el = el
            elif hasattr(el, 'select_one'):
                a_el = el.select_one('a')
            if a_el and a_el.get('href'):
                href_cnt += 1

            p_text = get_text(el.parent).strip()
            p_text = text_clean_helper.clean_text(p_text)
            parent_el_text_cnt += len(p_text)
            p_text_list.append(p_text)

        # print(p_text_list)
        # print('iiiiiiiii', parent_el_text_cnt, len(text_els), el_text_cnt)
        return parent_el_text_cnt > 2 * len(text_els) * el_text_cnt and href_cnt < len(text_els) / 3

    def shift_up_els(self, els):
        if len(els) == 0:
            return els
        parent_els = []
        existed = {}
        for el in els:
            if not el.parent:
                return els
            parent_str = str(el.parent)
            if parent_str in existed:
                # print('existed', str(el).replace('\n', ''), '***'*2, parent_str.replace('\n', ''))
                # print()
                # input('>')
                continue
            existed[parent_str] = True
            parent_els.append(el.parent)

        if len(parent_els) == len(els):
            return self.shift_up_els(parent_els)
        return els

    def find_intro_els(self, max_cnt, root_el):
        if not hasattr(root_el, 'children'):
            return []
        intro_els = []
        for el in root_el.children:
            if len(list(el.parents)) == max_cnt:
                intro_els.append(el)
            else:
                intro_els += self.find_intro_els(max_cnt, el)
        return intro_els

    def find_common_el_by_word(self, keyword: str):
        """同一个 keyword 可能分布在多个 node 里面，找到这些 node 的公共父node"""
        el = self.find_el_by_word(keyword)
        if not el:
            return

        el_index = self.html.index(str(el))
        next_find_index = el_index + len(str(el))

        el2 = self.find_el_by_word(keyword, next_find_index)
        if not el2:
            return el

        # print(keyword)
        # print([tag.name for tag in el.parents])
        # print([tag.name for tag in el2.parents])
        # print()
        min_cnt = min(len(list(el2.parents)), len(list(el.parents)))
        els = [el, el2]
        for i, _ in enumerate(els):
            while len(list(els[i].parents)) > min_cnt:
                els[i] = els[i].parent

        while els[0] != els[1]:
            for i, _ in enumerate(els):
                els[i] = els[i].parent
        return els[0]

    def find_el_by_word(self, keyword: str, start: int = 0):
        # print('keyword', keyword)
        key_index = self.html.find(keyword, start)
        if key_index < 0:
            return
        tag_index = self.html[:key_index].rindex('<')
        matches = re.findall(r'<(\w+)[> ]', self.html[:key_index])
        # print(self.html[:key_index])
        # print(matches)
        # input('>')

        matches.reverse()
        tag_name = ''

        for m in matches:
            if m.lower() not in ['img', 'br', 'hr']:
                tag_name = m
                break
        deepest_cnt = 0
        deepest_el = None
        for el in self.soup.select(tag_name):
            if keyword not in str(el):
                continue
            p_depth = len(list(el.parents))
            if p_depth > deepest_cnt:
                deepest_cnt = p_depth
                deepest_el = el

        if deepest_el:
            return deepest_el
        # tree = lxml.html.fromstring(str(self.soup))
        # for el in tree.xpath(f'//{tag_name}[contains(text(), "{keyword}")]'):
        #     return el

        # 找不到，找上一级
        deepest_cnt = 0
        deepest_el = None
        for el in self.soup.select(tag_name):
            if keyword not in str(el.parent):
                continue
            p_depth = len(list(el.parents))
            if p_depth > deepest_cnt:
                deepest_cnt = p_depth
                deepest_el = el.parent
        return deepest_el

    def find_last_el_by_word(self, keyword: str):
        key_index = self.html.rfind(keyword)
        if key_index < 0:
            return
        tag_index = self.html[:key_index].rindex('<')
        matches = re.findall(r'<(\w+)[> ]', self.html[:key_index])
        # print(self.html[:key_index])
        # print(matches)
        # input('>')

        matches.reverse()
        tag_name = ''

        for m in matches:
            if m.lower() not in ['img', 'br', 'hr', 'b']:
                tag_name = m
                break
        for el in self.soup.select(tag_name):
            if keyword in str(el):
                # print('*' * 10, el)
                # break
                return el
