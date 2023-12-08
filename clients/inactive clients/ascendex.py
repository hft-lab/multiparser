import requests
import time
import asyncio
import aiohttp

class Ascendex:
    def __init__(self):
        self.client_name = 'Ascendex'
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://ascendex.com/api/pro/v1/depth?symbol="
        self.urlMarkets = f"https://ascendex.com/api/pro/v1/margin/products"
        self.fees = 0.001
        # self.fees = {'SPOT': {'Maker': {'LMCA': 0.1, 'Altkoins': 0.2}, 'Taker': {'LMCA': 0.1, 'Altkoins': 0.2}},
        #             'FUTURES': {'Maker': {'LMCA': 0.1, 'Altkoins': 0.2}, 'Taker': {'LMCA': 0.1, 'Altkoins': 0.2}}}
        self.markets = {}

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        # ascendex.com/api/pro/v1/depth?symbol=DOGE/USDT
        for market in markets['data']:
            if 'USDT' in market['symbol']:
                coin = market['symbol'].split('/USDT')[0]
                self.markets.update({coin: market['symbol']})
        return self.markets

    def get_all_fees(self):
        return {'comission': self.fees}

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urlOrderbooks + symbol) as response:
                ob = await response.json()
        return {'top_ask': ob["data"]["data"]["asks"][0][0], 'ask_vol': ob["data"]["data"]["asks"][0][1],
                'top_bid': ob["data"]["data"]["bids"][0][0], 'bid_vol': ob["data"]["data"]["bids"][0][1],
                'ts_exchange': ob["data"]["data"]["ts"]}
        # return ob

async def main():
    client = Ascendex()
    # print(client.get_markets())
    symbol = 'DOGE/USDT'
    result = asyncio.create_task(client.get_orderbook(symbol))
    print(await result)
    time.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
