import requests
import asyncio
import aiohttp
import time


class Bittrex:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://api.bittrex.com/v3/markets/"
        self.endOrderbook = f"/orderbook?depth=25"
        self.urlMarkets = f"https://api.bittrex.com/v3/markets"
        self.markets = {}
        self.fees = {'Maker': 0.10, 'Taker': 0.15}
        self.requestLimit = 576

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets:
            if ('-USDT' in market['symbol']) and ('USDC-USDT' not in market['symbol']):
                coin = market['symbol'].split('-USDT')[0]
                self.markets.update({coin: market['symbol']})
        return (self.markets)

    def get_coin_fee(self, symbol):
        if symbol in self.markets.values():
            return {symbol: self.fees}
        else:
            return {}

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urlOrderbooks + symbol + self.endOrderbook) as response:
                ob = await response.json()
        return {"top_ask": ob["ask"][0]["rate"], "ask_vol": ob["ask"][0]["quantity"],
                "top_bid": ob["bid"][0]["rate"], "bid_vol": ob["bid"][0]["quantity"],
                "ts_exchange": 0}

async def main():
    orderbook = Bittrex()
    # result = await orderbook.get_orderbook('BTC-USDT')
    # print(result)
    while True:
        t0 = time.time()
        result = asyncio.create_task(orderbook.get_orderbook('BTC-USDT'))
        await result
        print(time.time() - t0)

if __name__ == "__main__":
    markets = Bittrex()
    print(markets.get_markets())
    print(markets.get_coin_fee('BTC-USDT'))
    asyncio.run(main())