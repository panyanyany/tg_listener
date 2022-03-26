import click
from pathlib import Path

import pandas
import pandas as pd

from tg_listener.repo import tick_maker
from tg_listener.repo.arctic_repo.arctic_repo import arctic_db

pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)


# pd.set_option('display.max_rows', None)


@click.command()
@click.argument('token')
@click.option('--span', default='15min')
def insight(token: str, span='15min'):
    token = token.lower()
    tot_data: pandas.DataFrame = arctic_db.db_tick.read(f'{token}:tick')
    data = tot_data.resample(span)['price'].agg(['first', 'last']).dropna()
    data['times'] = (data['last'] - data['first']) / data['first']

    print(data.iloc[-10:])


if __name__ == '__main__':
    insight()
