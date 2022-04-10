import dataclasses
from datetime import datetime, timedelta
from typing import List

import arrow
import pandas

import settings
from tg_listener.db import init_database
from tg_listener.models.models import AddressRecord
from tg_listener.repo.analysis_repo.tick_rules.TickMakerRuleGrow import TickMakerRuleGrow
from tg_listener.repo.arctic_repo.arctic_repo import arctic_db
from util.datetime_util.datetime_util import dtt_parse

init_database()
db = arctic_db.db_tick


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
