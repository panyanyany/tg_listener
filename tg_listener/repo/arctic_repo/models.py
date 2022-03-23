import dataclasses
import datetime

import pandas


@dataclasses.dataclass
class Stat:
    _id: str
    token: str
    recorded_at: datetime.datetime
    last_tick_at: datetime.datetime
    pools: dict

    ticks: pandas.DataFrame = dataclasses.field(default_factory=pandas.DataFrame)
