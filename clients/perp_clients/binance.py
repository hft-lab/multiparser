import asyncio
import aiohttp
import time
import requests
from ..core.base_parser_client import BaseClient
from datetime import datetime


# https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#exchange-information
# https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/Exchange-Information

class Binance(BaseClient):
    def __init__(self):
        super().__init__()
        self.client_name = 'Binance'
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = "https://fapi.binance.com/fapi/v1/depth?limit=5&symbol="
        self.urlMarkets = "https://fapi.binance.com/fapi/v1/exchangeInfo"
        self.fees = 0.00036
        self.requestLimit = 1200
        self.markets = {}

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets['symbols']:
            if (market['marginAsset'] == 'USDT') & (market['contractType'] == 'PERPETUAL') & (
                    market['underlyingType'] == 'COIN') & (market['status'] == 'TRADING'):
                coin = market['baseAsset']
                self.markets.update({coin: market['symbol']})
        return self.markets

    # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/Order-Book
    async def get_orderbook(self, symbol: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.urlOrderbooks + symbol) as response:
                if response.status == 200:
                    try:
                        ob = await response.json()
                        return {'top_bid': ob['bids'][0][0], 'top_ask': ob['asks'][0][0],
                                'bid_vol': ob['bids'][0][1], 'ask_vol': ob['asks'][0][1],
                                'ts_exchange': ob['E'], 'Status': 'OK'}
                    except Exception as error:
                        return self.ob_parsing_exception(symbol, error)
                else:
                    return await self.exchange_connection_exception(symbol, code=response.status, text=str(response.json()))


async def main():
    client = Binance()
    print(client.get_markets())


if __name__ == '__main__':
    asyncio.run(main())
