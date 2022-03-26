import dataclasses
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import arrow
import pandas
import pytz

from tg_listener.repo.arctic_repo.arctic_repo import arctic_db
from util.big_number.big_number import float_to_str

db = arctic_db.db_tick


@dataclasses.dataclass
class TickMakerTask:
    span: str
    times: float
    min_count: int = 1

    def gen_key(self):
        return f"T{self.span}_{self.times}_{self.min_count}"


@dataclasses.dataclass
class TickMakerResultItem:
    stat: dict
    ticks: pandas.DataFrame


@dataclasses.dataclass
class TickMakerResult:
    task: TickMakerTask
    items: List[TickMakerResultItem]

    # stat: dict
    # ticks: pandas.DataFrame

    def save(self, dirpath: Path):

        result = []
        for item in self.items:
            stat = dict(item.stat)
            ticks = item.ticks

            ticks['first'] = ticks['first'].apply(float_to_str)
            ticks['last'] = ticks['last'].apply(float_to_str)
            ticks = ticks.tz_localize(pytz.timezone('Asia/Shanghai'))

            stat['ticks'] = json.loads(ticks.to_json(orient='index', date_format='', ))

            result.append(stat)

        save_name = dirpath.joinpath(self.task.gen_key() + '.json')
        if not save_name.parent.exists():
            save_name.parent.mkdir(parents=True)

        result = {'build_time': arrow.now(), 'items': result}
        with save_name.open('w+') as fp:
            json.dump(result, fp, default=str)


class TickMaker:
    # candlestick_span = '1h'  # K线间隔
    # growth_times = 0.1  # 涨幅倍数
    tasks = []
    results: Dict[str, TickMakerResult]

    # 通用配置
    open_min_age = 60  # 开盘时间最小允许多久(min)
    idle_max_span = 15  # 空闲期(上一次交易到现在)最大允许多久(min)

    debug_token = ''

    def __init__(self, tasks):
        # self.candlestick_span = candlestick_span
        # self.growth_times = growth_times
        self.tasks: List[TickMakerTask] = tasks
        self.results: Dict[str, TickMakerResult] = {}

    def check_min_count(self, data, min_count, times):
        if len(data) < min_count:
            return False
        for i in range(min_count):
            pos = i + 1
            if data.iloc[-pos]['times'] < times:
                return False
        return True

    def filter_token(self, stat) -> pandas.DataFrame:
        token = stat['token']
        tot_data: pandas.DataFrame = arctic_db.db_tick.read(f'{token}:tick')
        if len(tot_data[tot_data['direction'] == 'SELL']) < 3:
            return

        for task in self.tasks:
            data = tot_data.resample(task.span)['price'].agg(['first', 'last']).dropna()
            data['times'] = (data['last'] - data['first']) / data['first']
            if self.debug_token:
                print(tot_data.iloc[-20:])
                print(data.iloc[-4:])
            if self.check_min_count(data, task.min_count, task.times):
                if task.gen_key() not in self.results:
                    result = TickMakerResult(task=task, items=[])
                else:
                    result = self.results[task.gen_key()]

                result.items.append(TickMakerResultItem(stat=stat, ticks=data))
                self.results[task.gen_key()] = result

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
            if self.debug_token and self.debug_token != stat['token']:
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
            self.filter_token(stat)
