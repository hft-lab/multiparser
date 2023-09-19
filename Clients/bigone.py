import requests
import asyncio
import aiohttp
import time

class Bigone:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://big.one/api/v3/asset_pairs/"
        self.endOrderbook = "/depth"
        self.urlMarkets = f"https://big.one/api/v3/asset_pairs"
        self.markets = {}
        self.fees = {'SPOT': {'Maker': {'LMCA': 0.2, 'Altkoins': 0.2}, 'Taker': {'LMCA': 0.2, 'Altkoins': 0.2}},
                     'FUTURES': {'Maker': {'LMCA': 0.2, 'Altkoins': 0.2}, 'Taker': {'LMCA': 0.6, 'Altkoins': 0.6}}}

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets['data']:
            if '-USDT' in market['name']:
                coin = market['name'].split('-USDT')[0]
                self.markets.update({coin: market['name']})
        return(self.markets)

    def get_all_fees(self):
        return {'comission': self.fees}

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urlOrderbooks + symbol + self.endOrderbook) as response:
                ob = await response.json()
                # print(ob)
        return {"top_ask": ob["data"]["asks"][0]["price"], "ask_vol": ob["data"]["asks"][0]["quantity"],
                "top_bid": ob["data"]["bids"][0]["price"], "bid_vol": ob["data"]["bids"][0]["quantity"],
                "ts_exchange": 0}

async def main():
    orderbook = Bigone()
    # result = await orderbook.get_orderbook('BTC-USDT')
    # print(result)
    while True:
        t0 = time.time()
        result = asyncio.create_task(orderbook.get_orderbook('BTC-USDT'))
        await result
        print(time.time() - t0)

if __name__ == "__main__":
    markets = Bigone()
    print(markets.get_markets())
    print(markets.get_all_fees())
    asyncio.run(main())
