import requests
import aiohttp
import asyncio
import time

class Tidex:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://api.tidex.com/api/v1/public/depth/result?market="
        self.endUrlOrderbook = "&limit=2"
        self.urlMarkets = f"https://api.tidex.com/api/v1/public/markets"
        self.markets = {}
        self.urlfees = f"https://api.tidex.com/api/v1/public/book?market="
        self.endUrlFees = "&side=sell&offset=0&limit=1"
        self.fees = {}
        self.requestLimit = 34  # ban on 35th iteration

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets['result']:
            if ('_USDT' in market['name']) and ('USDC_USDT' not in market['name']):
                coin = market['name'].split('_USDT')[0]
                self.markets.update({coin: market['name']})
        return (self.markets)
        # return(markets)

    def get_coin_fee(self, symbol):
        url = self.urlfees + symbol + self.endUrlFees
        fees = requests.get(url=url, headers=self.headers).json()
        makerFee = fees['result']['orders'][0]['makerFee']
        takerFee = fees['result']['orders'][0]['takerFee']
        self.fees.update({symbol: {"Maker": makerFee, "Taker": takerFee}})
        return self.fees
        # return fees

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urlOrderbooks + symbol + self.endUrlOrderbook) as response:
                ob = await response.json()
                # print(ob)
        return {"top_ask": ob['asks'][0][0], "ask_vol": ob['asks'][0][1],
                "top_bid": ob['bids'][0][0], "bid_vol": ob['bids'][0][1],
                "ts_exchange": 0}

async def main():
    orderbook = Tidex()
    result = await orderbook.get_orderbook('BTC_USDT')
    print(result)
    # while True:
    #     t0 = time.time()
    #     result = asyncio.create_task(orderbook.get_orderbook('SPOT_BTC_USDT'))
    #     await result
    #     print(time.time() - t0)

if __name__ == "__main__":
    markets = Tidex()
    print(markets.get_markets())
    print(markets.get_coin_fee('BTC_USDT'))
    asyncio.run(main())