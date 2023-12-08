import requests
import asyncio
import aiohttp
import time

class Pointpay:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://api.pointpay.io/api/v1/public/depth/result?market="
        self.endOrderbooks = f"&limit=25"
        self.urlMarkets = f"https://api.pointpay.io/api/v1/public/tickers"
        self.markets = {}
        self.urlFees = f"https://api.pointpay.io/api/v1/public/book?market="
        self.urlEndFees = f"&side=sell&offset=0&limit=1"
        self.fees = {}
        self.requestLimit = 1279

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets['result']:
            if ('_USDT' in market) and ('USDC_USDT' not in market):
                coin = market.split('_USDT')[0]
                self.markets.update({coin: market})
        return(self.markets)
        # return(markets)

    def get_coin_fee(self, symbol):
        url = self.urlFees + symbol + self.urlEndFees
        fees = requests.get(url=url, headers=self.headers).json()
        makerFee = fees['result']['orders'][0]['makerFee']
        takerFee = fees['result']['orders'][0]['takerFee']
        self.fees.update({symbol: {"Maker": makerFee, "Taker": takerFee}})
        return self.fees

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urlOrderbooks + symbol + self.endOrderbooks) as response:
                ob = await response.json()
                # print(ob)
        return {"top_ask": ob["asks"][0][0], "ask_vol": ob["asks"][0][1],
                "top_bid": ob["bids"][0][0], "bid_vol": ob["bids"][0][1],
                "ts_exchange": 0}


async def main():
    orderbook = Pointpay()
    # result = await orderbook.get_orderbook('BTC_USDT')
    # print(result)
    while True:
        t0 = time.time()
        result = asyncio.create_task(orderbook.get_orderbook('BTC_USDT'))
        await result
        print(time.time() - t0)

if __name__ == "__main__":
    markets = Pointpay()
    print(markets.get_markets())
    print(markets.get_coin_fee('BTC_USDT'))
    asyncio.run(main())