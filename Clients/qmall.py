import requests
import asyncio
import aiohttp
import time


class Qmall:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://api.qmall.io/api/v1/public/depth/result?market="
        self.endOrderbook = f"&limit=5"
        self.urlMarkets = f"https://api.qmall.io/api/v1/public/symbols"
        self.markets = {}
        self.urlFees = f"https://api.qmall.io/api/v1/public/book?market="
        self.endUrlFees = "&side=sell&offset=0&limit=1"
        self.fees = {}
        self.requestLimit = 1273

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets['result']:
            if ('_USDT' in market) and ('USDC_USDT' not in market):
                coin = market.split('_USDT')[0]
                self.markets.update({coin: market})
        return (self.markets)
        # return markets

    def get_coin_fee(self, symbol):
        url = self.urlFees + symbol + self.endUrlFees
        fees = requests.get(url=url, headers=self.headers).json()
        for fee in fees['result']['orders']:
            maker_fee = fee['makerFee']
            taker_fee = fee['takerFee']
            self.fees.update({symbol: {"Maker": maker_fee, "Taker": taker_fee}})
        return self.fees

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urlOrderbooks + symbol + self.endOrderbook) as response:
                ob = await response.json()
        return {"top_ask": ob["asks"][0][0], "ask_vol": ob["asks"][0][1],
                "top_bid": ob["bids"][0][0], "bid_vol": ob["bids"][0][1],
                "ts_exchange": 0}
        # return ob

async def main():
    orderbook = Qmall()
    # result = await orderbook.get_orderbook('BTC_USDT')
    # print(result)
    while True:
        t0 = time.time()
        result = asyncio.create_task(orderbook.get_orderbook('BTC_USDT'))
        await result
        print(time.time() - t0)

if __name__ == "__main__":
    markets = Qmall()
    print(markets.get_markets())
    print(markets.get_coin_fee('BTC_USDT'))
    asyncio.run(main())