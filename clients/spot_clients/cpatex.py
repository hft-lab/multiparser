import requests
import asyncio
import aiohttp
import time

class CPatex:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://api.c-patex.com/api/v1/public/depth/result?market="
        self.endOrderbooks = f"&limit=1000"
        self.urlMarkets = f"https://api.c-patex.com/api/v1/public/tickers"
        self.markets = {}
        self.requestLimit = 3  # Ban on 4th iteration
        self.urlFee = f"https://api.c-patex.com/api/v1/public/book?market="
        self.endUrlFee = "&side=sell&offset=0&limit=1"
        self.fees = {}

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets['result']:
            if ('_USDT' in market) and ('USDC_USDT' not in market):
                coin = market.split('_USDT')[0]
                self.markets.update({coin: market})
        return(self.markets)
        # return(markets)

    def get_coin_fee(self, symbol):
        url = self.urlFee + symbol + self.endUrlFee
        fees = requests.get(url=url, headers=self.headers).json()
        for fee in fees['result']['orders']:
            if symbol == fee['market']:
                maker_fee = fee['makerFee']
                taker_fee = fee['takerFee']
                self.fees.update({symbol: {"Maker": maker_fee, "Taker": taker_fee}})
            return self.fees
        # return fees

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urlOrderbooks + symbol + self.endOrderbooks) as response:
                ob = await response.json()
                # print(ob)
        return {"top_ask": ob["asks"][0][0], "ask_vol": ob["asks"][0][1], "top_bid": ob["bids"][0][0],
                "bid_vol": ob["bids"][0][1], "ts_exchange": 0}

async def main():
    orderbook = CPatex()
    # result = await orderbook.get_orderbook('BTC_USDT')
    # print(result)
    while True:
        t0 = time.time()
        result = asyncio.create_task(orderbook.get_orderbook('BTC_USDT'))
        await result
        print(time.time() - t0)

if __name__ == "__main__":
    markets = CPatex()
    print(markets.get_markets())
    print(markets.get_coin_fee('BTC_USDT'))
    asyncio.run(main())