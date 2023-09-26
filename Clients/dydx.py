import asyncio
import aiohttp
import requests
import time
from datetime import datetime
from dateutil.parser import parse


class DyDx:
    def __init__(self):
        self.client_name = 'DyDx'
        self.headers = {"Content-Type": "application/json"}
        self.urlMarkets = "https://api.dydx.exchange/v3/markets/"
        self.urlOrderbooks = "https://api.dydx.exchange/v3/orderbook/"
        self.fees = 0.0005
        self.requestLimit = 1050  # 175 за 10 секунд https://dydxprotocol.github.io/v3-teacher/#rate-limit-api
        self.markets = {}
        self.fundings = {}

    async def get_fundings(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        ts = None
        for market, value in markets['markets'].items():
            coin = value['baseAsset']
            if not ts:
                date_obj = parse(value['nextFundingAt'])
                ts = str(date_obj.timestamp())
            if not self.fundings.get(ts):
                self.fundings.update({ts: {}})
            new_record = [float(value['nextFundingRate']), datetime.utcnow().timestamp(), float(value['indexPrice'])]
            if not self.fundings[ts].get(market):
                self.fundings[ts].update({market: [new_record]})
            else:
                self.fundings[ts][market].append(new_record)
        print(self.fundings)
        return self.fundings

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
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


if __name__ == '__main__':
    async def main():
        client = DyDx()
        # symbol = "ETHUSD"
        while True:
            # task = asyncio.create_task(client.get_orderbook(symbol))
            # print(await task)
            client.get_fundings()
            time.sleep(60)

    asyncio.run(main())

