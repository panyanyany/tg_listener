import click
from datetime import timedelta, datetime
import pandas as pd

from tg_listener.repo.arctic_repo.arctic_repo import arctic_db

pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('token')
@click.option('--hours', type=int)
def a(token, hours):
    # token = '0x56aa5cb724cb12c0452ac51094a7ae165202f81e'
    # token = '0xabaf0bcd3a4f6d3bd76edc10ea922d50b751c357'
    # end = dtparse('2022-03-20 21:30')
    token = token.lower()
    end = datetime.now()
    start = end - timedelta(hours=hours)

    data = arctic_db.db_tick.read(f'{token}:tick')
    all_data = data.copy().loc[:end]
    data = data.loc[start:end]
    print(data)

    sellers = []
    for item in data[data['direction'] == 'SELL']['operator']:
        sellers.append(item)
    c_sellers = len(sellers)
    c_uniq_sellers = len(set(sellers))
    print(f"sellers={c_sellers}, uniq={c_uniq_sellers}")

    buyers = []
    c_new_buyers = 0
    for item in data[data['direction'] == 'BUY']['operator']:
        if len(all_data[all_data['operator'] == item]) == 1:
            c_new_buyers += 1
        buyers.append(item)
    c_buyers = len(buyers)
    c_uniq_buyers = len(set(buyers))
    if c_buyers:
        new_rate = c_new_buyers / c_buyers
    else:
        new_rate = 0
    if c_sellers:
        new_rate_2 = c_new_buyers / c_sellers
    else:
        new_rate_2 = 0
    print(
        f"buyers={c_buyers}, uniq={c_uniq_buyers}, new={c_new_buyers}, new/all={new_rate:.2f}, new/sell={new_rate_2:.2f}")

    data = data[data['direction'] == 'SELL']
    print(len(data))
    print(data.tail())

    data = arctic_db.db_tick.read(f'{token}:liq')
    print(data.tail())


if __name__ == '__main__':
    mcli = click.CommandCollection(sources=[cli])
    mcli()
