app_id = ''
app_id_hash = ''

DB_USERNAME = ''
DB_PASSWORD = ''
DB_NAME = 'tg_listener'

BLOCK_ADDRESSES = {'0x67d14015992b4832839c2c3bdeee27150d9de4c1', '0xcfc9321e3aa3a15bbbc4c4390da7407f3ec84145'}

proxy = None

airtable = {
    'api_key': '这里填 API KEY'
}

accounts = {
    'default': {
        'private_key': '0x....',
        'address': '0x....',
    }
}

load_receipt_timeout = 5  # 加载 receipt 的等待时间，量大，如果网络不好就设置多一点

endpoints = [
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed1.binance.org/",
    "https://bsc-dataseed2.binance.org/",
    "https://bsc-dataseed3.binance.org/",
    "https://bsc-dataseed4.binance.org/",
    "https://bsc-dataseed1.defibit.io/",
    "https://bsc-dataseed2.defibit.io/",
    "https://bsc-dataseed3.defibit.io/",
    "https://bsc-dataseed4.defibit.io/",
    "https://bsc-dataseed1.ninicoin.io/",
    "https://bsc-dataseed2.ninicoin.io/",
    "https://bsc-dataseed3.ninicoin.io/",
    "https://bsc-dataseed4.ninicoin.io/",
]

make_stat_ignore_tokens = {
    '0x2e74ee4fc4466d0883ef5e12a0ce344bfe15be8d',  # PumpETH
}
