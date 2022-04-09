import dataclasses
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import arrow
import pandas
import pytz

import settings
from tg_listener.db import init_database
from tg_listener.models.models import AddressRecord
from tg_listener.repo.arctic_repo.arctic_repo import arctic_db
from util.big_number.big_number import float_to_str
from util.datetime_util.datetime_util import dtt_parse

mysql_db = init_database()
db = arctic_db.db_tick


@dataclasses.dataclass
class TokenResult:
    stat: dict
    ticks: pandas.DataFrame


@dataclasses.dataclass
class TickMakerRule:
    span: str = ''
    times: float = 0
    token_results: List[TokenResult] = dataclasses.field(default_factory=list)

    def gen_key(self):
        raise NotImplemented

    def add(self, stat, data):
        raise NotImplemented


@dataclasses.dataclass
class TickMakerRuleGrow(TickMakerRule):
    min_count: int = 1

    def gen_key(self):
        return f"T{self.span}_{self.times}_{self.min_count}"

    def check_min_count(self, data, min_count, times):
        if len(data) < min_count:
            return False
        for i in range(min_count):
            pos = i + 1
            if data.iloc[-pos]['times'] < times:
                return False
        return True

    def add(self, stat, tot_data):
        task = self
        data = tot_data.resample(task.span)['price'].agg(['first', 'last']).dropna()
        data['times'] = (data['last'] - data['first']) / data['first']
        if self.check_min_count(data, task.min_count, task.times):
            self.token_results.append(TokenResult(stat=stat, ticks=data))

    def save(self, dirpath: Path):
        result = []
        for item in self.token_results:
            stat = dict(item.stat)
            ticks = item.ticks

            ticks['first'] = ticks['first'].apply(float_to_str)
            ticks['last'] = ticks['last'].apply(float_to_str)
            ticks = ticks.tz_localize(pytz.timezone('Asia/Shanghai'))

            stat['ticks'] = json.loads(ticks.to_json(orient='index', date_format='', ))

            result.append(stat)

        save_name = dirpath.joinpath(self.gen_key() + '.json')
        if not save_name.parent.exists():
            save_name.parent.mkdir(parents=True)

        result = {'build_time': arrow.now(), 'items': result}
        with save_name.open('w+') as fp:
            json.dump(result, fp, default=str)


@dataclasses.dataclass
class TickMakerRuleMostlyGrow(TickMakerRule):
    child_span: str = ''

    def gen_key(self):
        return f"TM{self.span}_{self.times}_{self.child_span}"


@dataclasses.dataclass
class TickMakerResult:
    task: TickMakerRuleGrow

    # stat: dict
    # ticks: pandas.DataFrame


class TickMaker:
    # candlestick_span = '1h'  # K线间隔
    # growth_times = 0.1  # 涨幅倍数
    tasks: List[TickMakerRuleGrow] = []

    # 通用配置
    open_min_age = 1  # 开盘时间最小允许多久(min)
    idle_max_span = 15  # 空闲期(上一次交易到现在)最大允许多久(min)

    debug_token = ''

    def __init__(self, tasks):
        # self.candlestick_span = candlestick_span
        # self.growth_times = growth_times
        self.tasks: List[TickMakerRuleGrow] = tasks

    def filter_token(self, stat) -> pandas.DataFrame:
        token = stat['token']
        tot_data: pandas.DataFrame = arctic_db.db_tick.read(f'{token}:tick')
        if len(tot_data[tot_data['direction'] == 'SELL']) < 3:
            return

        # 这种交易不能要，价格太离谱
        tot_data = tot_data[tot_data['value'] > 0.01]

        for task in self.tasks:
            task.add(stat, tot_data)
            # if not token_result:
            #     continue
            # if task.gen_key() not in self.task_results:
            #     result = TickMakerResult(task=task, token_results=[])
            # else:
            #     result = self.task_results[task.gen_key()]
            #
            # result.token_results.append(token_result)
            # self.task_results[task.gen_key()] = result

    def run(self):
        dt_idle_gte = datetime.now() - timedelta(minutes=self.idle_max_span)
        dt_open_lte = datetime.now() - timedelta(minutes=self.open_min_age)
        query = {"last_tick_at": {"$gte": dt_idle_gte},
                 "recorded_at": {"$lte": dt_open_lte}}
        stats = arctic_db.db_data.stats.find(query)

        # print(stats.count())
        # print(len(db.list_symbols(partial_match=':tick')))
        # exit()

        stats = list(stats)
        for stat in stats[:]:
            if stat['pools']['TOTAL'] < 100:
                continue
            if self.debug_token and self.debug_token != stat['token']:
                continue
            if stat['token'] in settings.make_stat_ignore_tokens:
                continue
            # del stat['_id']
            # print(json.dumps(stat, default=str))
            # return
            sym = f"{stat['token']}:tick"
            if not db.has_symbol(sym):
                continue
            info = db.get_info(sym)
            if info['len'] < 5:
                continue

            # 最后一次 CX 时间
            md_rec: AddressRecord = AddressRecord.get_or_none(AddressRecord.address == stat['token'])
            if md_rec:
                stat['last_cx_at'] = arrow.get(dtt_parse(md_rec.updated_at)).format()
            else:
                stat['last_cx_at'] = None

            self.filter_token(stat)
