import requests
import asyncio
import time
import aiohttp

class Difx:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
        self.symbol = "BTCUSDT"
        self.urlOrderbooks = f"https://api-v2.difx.com/open/api/v1/orderbook?symbol="
        self.endOrderbooks = f"&level=2&depth=50"
        self.urlMarkets = f"https://api-v2.difx.com/open/api/v1/ticker"
        self.markets = {}
        self.urlFees = f"https://api-v2.difx.com/open/api/v1/pairs?symbol="
        self.fees = {}
        self.requestLimit = 532  # BAN on 533rd request

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets:
            if ('_USDT' in market) and ('USDC_USDT' not in market):
                coin = market.split('_USDT')[0]
                self.markets.update({coin: market})
        return (self.markets)
        # return (markets)

    def get_coin_fee(self, symbol):
        url = self.urlFees + symbol
        fees = requests.get(url=url, headers=self.headers).json()
        for fee in fees['data']:
            maker_fee = fee['mfee']
            taker_fee = fee['tfee']
            self.fees.update({symbol: {"Maker": maker_fee, "Taker": taker_fee}})
        return self.fees
        # return fees

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urlOrderbooks + symbol + self.endOrderbooks) as response:
                ob = await response.json()
                # print(ob)
        return {"top_ask": ob["asks"][0][0], "ask_vol": ob["asks"][0][1],
                "top_bid": ob["bids"][0][0], "bid_vol": ob["bids"][0][1], "ts_exchange": ob['timestamp']}

async def main():
    orderbook = Difx()
    # result = await orderbook.get_orderbook('BTC_USDT')
    # print(result)
    while True:
        t0 = time.time()
        result = asyncio.create_task(orderbook.get_orderbook('BTC_USDT'))
        await result
        print(time.time() - t0)


if __name__ == "__main__":
    markets = Difx()
    print(markets.get_markets())
    print(markets.get_coin_fee('BTCUSDT'))
    asyncio.run(main())