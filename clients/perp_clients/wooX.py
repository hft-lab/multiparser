import requests
import aiohttp
import asyncio
import time

class Woo:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://api.woo.org/v1/public/orderbook/"
        self.urlMarkets = f"https://api.woo.org/v1/public/info"
        self.markets = {}
        self.fees = {"Maker": 0.05, "Taker": 0.05}
        self.requestLimit = 5  # ban on iteration 6

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets['rows']:
            if ('_USDT' in market['symbol']) and ('USDC_USDT' not in market['symbol']):
                coin = market['symbol'].split('_USDT')[0]
                self.markets.update({coin: market['symbol']})
        return (self.markets)
        # return(markets)

    def get_coin_fee(self, symbol):
        return {symbol: self.fees}

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urlOrderbooks + symbol) as response:
                ob = await response.json()
                # print(ob)
        return {"top_ask": ob['asks'][0]['price'], "ask_vol": ob['asks'][0]['quantity'],
                "top_bid": ob['bids'][0]['price'], "bid_vol": ob['bids'][0]['quantity'],
                "ts_exchange": ob['timestamp']}

async def main():
    orderbook = Woo()
    # result = await orderbook.get_orderbook('SPOT_BTC_USDT')
    # print(result)
    while True:
        t0 = time.time()
        result = asyncio.create_task(orderbook.get_orderbook('SPOT_BTC_USDT'))
        await result
        print(time.time() - t0)

if __name__ == "__main__":
    markets = Woo()
    print(markets.get_markets())
    print(markets.get_coin_fee('BTC_USDT'))
    asyncio.run(main())
