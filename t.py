from web3 import Web3
from uniswap import Uniswap
import settings
from util.bsc.multicall import Multicall
from util.bsc.pancake_swap.factory import Factory

address = settings.accounts['default']['address']  # or None if you're not going to make transactions
private_key = settings.accounts['default']['private_key']  # or None if you're not going to make transactions
version = 2  # specify which version of Uniswap to use
provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`
router = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
factory = '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'
wbnb = '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c'
busd = '0xe9e7cea3dedca5984780bafc599bd69add087d56'
usdt = '0x55d398326f99059fF775485246999027B3197955'
wbnb_busd_pair = '0x58F876857a02D6762E0101bb5C46A8c1ED44Dc16'

web3 = Web3(Web3.HTTPProvider(provider))
uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider,
                  factory_contract_addr=factory, router_contract_addr=router)

c_multi_call = Multicall(web3)
c_factory = Factory(web3)

# wei = uniswap.get_eth_balance()
# print(wei)

nftpad = '0x4a72af9609d22bf2ff227aec333c7d0860f3db36'
pair_info = c_factory.get_pair(busd, nftpad)
print('pair_info', pair_info)
token_info = c_multi_call.get_pair_info_with_price(pair_info)
print(token_info.token_0.to_human())
print(token_info.token_1.to_human())

