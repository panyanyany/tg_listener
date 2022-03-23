import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas

from tg_listener.repo.arctic_repo.arctic_repo import arctic_db

db = arctic_db.db_tick


class TickMaker:
    candlestick_span = '1h'  # K线间隔
    growth_times = 0.1  # 涨幅倍数

    # 通用配置
    open_min_age = 60  # 开盘时间最小允许多久(min)
    idle_max_span = 15  # 空闲期(上一次交易到现在)最大允许多久(min)

    def __init__(self, candlestick_span, growth_times):
        self.candlestick_span = candlestick_span
        self.growth_times = growth_times

    def filter_token(self, stat, token, times=0.5, span='30min') -> pandas.DataFrame:
        # stat = arctic_db.get_stat(token)
        # last_dt: datetime = stat['last_tick_at']
        # idle = (datetime.now() - last_dt).total_seconds() / 60
        # if idle > 15:
        #     return
        data: pandas.DataFrame = arctic_db.db_tick.read(f'{token}:tick')
        if len(data[data['direction'] == 'SELL']) < 3:
            return None
        # print(data[['price', 'hash', 'value']].tail())
        # print(token)
        data = data.resample(span)['price'].agg(['first', 'last']).dropna()
        data['times'] = (data['last'] - data['first']) / data['first']
        if data.iloc[-1]['times'] > times:
            print(data)
            return data

        return None

    def run(self, save_name: Path):
        dt_idle_gte = datetime.now() - timedelta(minutes=self.idle_max_span)
        dt_open_lte = datetime.now() - timedelta(minutes=self.open_min_age)
        query = {"last_tick_at": {"$gte": dt_idle_gte},
                 "recorded_at": {"$lte": dt_open_lte}}
        stats = arctic_db.db_data.stats.find(query)

        # print(stats.count())
        # print(len(db.list_symbols(partial_match=':tick')))
        # exit()

        results = []
        stats = list(stats)
        print(len(stats))
        for stat in stats[:500]:
            # del stat['_id']
            # print(json.dumps(stat, default=str))
            # return
            sym = f"{stat['token']}:tick"
            if not db.has_symbol(sym):
                continue
            info = db.get_info(sym)
            if info['len'] < 5:
                continue
            token = sym.split(':')[0]
            ticks = self.filter_token(stat, token, span=self.candlestick_span, times=self.growth_times)
            if ticks is None:
                continue
            stat['ticks'] = json.loads(ticks.to_json(orient='index', date_format=''))
            results.append(stat)

        print(len(results))
        if not save_name.parent.exists():
            save_name.parent.mkdir(parents=True)

        with save_name.open('w+') as fp:
            json.dump(results, fp, default=str)
