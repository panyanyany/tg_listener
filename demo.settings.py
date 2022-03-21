app_id = ''
app_id_hash = ''

DB_USERNAME = ''
DB_PASSWORD = ''
DB_NAME = 'tg_listener'

BLOCK_ADDRESSES = set([
    '0x67d14015992b4832839c2c3bdeee27150d9de4c1',  # TAC
    '0xcfc9321e3aa3a15bbbc4c4390da7407f3ec84145',  # TAC
])

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
max_load_receipt = 50
