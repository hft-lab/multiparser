import asyncio
import aiohttp
import requests
from datetime import datetime

class DyDx():
    def __init__(self):
        self.client_name = 'DyDx'
        self.headers = {"Content-Type": "application/json"}
        self.urlMarkets = "https://api.dydx.exchange/v3/markets/"
        self.urlOrderbooks = "https://api.dydx.exchange/v3/orderbook/"
        self.fees = 0.0005
        self.requestLimit = 1050 #175 за 10 секунд https://dydxprotocol.github.io/v3-teacher/#rate-limit-api

        self.markets = {}
    def get_markets(self):
        markets = requests.get(url = self.urlMarkets, headers= self.headers).json()
        for market, value in markets['markets'].items():
            if value['quoteAsset'] == 'USD':
                coin = value['baseAsset']
                self.markets.update({coin: market})
        return self.markets


    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urlOrderbooks + symbol) as response:
                ob = await response.json()
                try:
                    return {'top_bid': ob['bids'][0]['price'], 'top_ask': ob['asks'][0]['price'],
                            'bid_vol': ob['bids'][0]['size'], 'ask_vol': ob['asks'][0]['size'],
                            'ts_exchange': 0}
                except Exception as error:
                    print(f"Error from DyDx Module, symbol: {symbol}, error: {error}")

async def main():
    pass

   # client = Bitfinex()
   #  symbol = "tETHF0:USTF0"
   #  while True:
   #      task = asyncio.create_task(client.get_orderbook(symbol))
   #      print(await task)
   #      time.sleep(1)
if __name__ == '__main__':
    asyncio.run(main())

