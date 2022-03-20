import asyncio
import logging
import threading
from datetime import datetime
from typing import Any, Optional, Union

from eth_typing import URI
from web3 import AsyncHTTPProvider
from web3._utils.request import async_make_post_request
from web3.types import RPCEndpoint, RPCResponse

logger = logging.getLogger(__name__)


class AsyncConcurrencyHTTPProvider(AsyncHTTPProvider):
    endpoints = [
        # "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.binance.org/",
        "https://bsc-dataseed2.binance.org/",
        "https://bsc-dataseed3.binance.org/",
        "https://bsc-dataseed4.binance.org/",
        "https://bsc-dataseed1.defibit.io/",
        "https://bsc-dataseed2.defibit.io/",
        "https://bsc-dataseed3.defibit.io/",
        "https://bsc-dataseed4.defibit.io/",
        # "https://bsc-dataseed1.ninicoin.io/",
        # "https://bsc-dataseed2.ninicoin.io/",
        # "https://bsc-dataseed3.ninicoin.io/",
        # "https://bsc-dataseed4.ninicoin.io/",
    ]
    last_time = {}
    lock = threading.Lock()
    interval = 0.1

    error_stat = {}

    def __init__(self, endpoint_uri: Optional[Union[URI, str]] = None, request_kwargs: Optional[Any] = None) -> None:
        super().__init__(endpoint_uri, request_kwargs)

    async def pick_endpoint(self):
        while True:
            with self.lock:
                for endpoint_uri in self.endpoints:
                    last_time: datetime = self.last_time.get(endpoint_uri, datetime.fromtimestamp(0))
                    diff = datetime.now() - last_time
                    # self.logger.debug(f"{endpoint_uri}, {diff}, {last_time}")
                    if diff.total_seconds() > self.interval:
                        self.last_time[endpoint_uri] = datetime.now()
                        return endpoint_uri
            # self.logger.debug('---- waiting: no endpoint available')
            await asyncio.sleep(0.05)

    async def make_request(self, method: RPCEndpoint, params: Any) -> RPCResponse:
        self.endpoint_uri = await self.pick_endpoint()

        self.logger.debug("Making request HTTP. URI: %s, Method: %s",
                          self.endpoint_uri, method)
        request_data = self.encode_rpc_request(method, params)
        try:
            raw_response = await async_make_post_request(
                self.endpoint_uri,
                request_data,
                **self.get_request_kwargs()
            )
        # except asyncio.TimeoutError as e:
        except BaseException as e:
            AsyncConcurrencyHTTPProvider.error_stat.setdefault(self.endpoint_uri, 0)
            AsyncConcurrencyHTTPProvider.error_stat[self.endpoint_uri] += 1
            if AsyncConcurrencyHTTPProvider.error_stat[self.endpoint_uri] % 5 == 1:
                logger.warning("endpoint too many errors: %s", AsyncConcurrencyHTTPProvider.error_stat)
            raise

        response = self.decode_rpc_response(raw_response)
        self.logger.debug("Getting response HTTP. URI: %s, "
                          "Method: %s, Response: %s",
                          self.endpoint_uri, method, response)
        return response
