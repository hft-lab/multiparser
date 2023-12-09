import requests
import asyncio
import aiohttp
import time
import datetime
from ..core.base_parser_client import BaseClient


# docs.futures.kraken.com
class Kraken(BaseClient):
    def __init__(self):
        super().__init__()
        self.client_name = 'Kraken'
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = "https://futures.kraken.com/derivatives/api/v3/orderbook?symbol="
        self.urlMarkets = "https://futures.kraken.com/derivatives/api/v3/tickers"
        self.fees = 0.0005
        self.requestLimit = 1200
        self.markets = {}

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets['tickers']:
            if market.get('tag') is not None:
                if (market['tag'] == 'perpetual') & (market['pair'].split(":")[1] == 'USD'):
                    coin = market['pair'].split(":")[0]
                    self.markets.update({coin: market['symbol']})
        return self.markets

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.urlOrderbooks + symbol) as response:
                if response.status == 200:
                    try:
                        full_response = await response.json()
                        ob = full_response['orderBook']
                        ts_exchange = int(
                            datetime.datetime.strptime(full_response['serverTime'], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp() * 1000)
                        return {'top_bid': ob['bids'][0][0], 'top_ask': ob['asks'][0][0],
                                'bid_vol': ob['bids'][0][1], 'ask_vol': ob['asks'][0][1],
                                'ts_exchange': ts_exchange,'Status':'OK'}
                    except Exception as error:
                        return self.ob_parsing_exception(symbol, error)
                else:
                    return await self.exchange_connection_exception(symbol, code=response.status, text=str(response.json()))

async def main():
    client = Kraken()
    symbol = 'pi_ethusd'
    #print(client.get_markets())
    task = asyncio.create_task(client.get_orderbook(symbol))
    print(await task)
    time.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
