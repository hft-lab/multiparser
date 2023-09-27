import requests
import aiohttp
import asyncio
import time

class Poloniex:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://api.poloniex.com/markets/"
        self.urlMarkets = f"https://api.poloniex.com/markets/markPrice"
        self.markets = {}
        self.fees = {"Maker": 0.2, "Taker": 0.2}
        self.requestLimit = 0  # ban on first iteration

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets:
            if ('_USDT' in market['symbol']) and ('USDC_USDT' in market['symbol']):
                coin = market['symbol'].split('_USD')[0]
                self.markets.update({coin: market['symbol']})
        return (self.markets)
        # return(markets)

    def get_coin_fee(self, symbol):
        return {symbol: self.fees}

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urlOrderbooks + symbol + '/orderBook') as response:
                ob = await response.json()
                # print(ob)
        return {"top_ask": ob['asks'][0], "ask_vol": ob['asks'][1],
                "top_bid": ob['bids'][0], "bid_vol": ob['bids'][1],
                "ts_exchange": ob['time']}

async def main():
    orderbook = Poloniex()
    # result = await orderbook.get_orderbook('BTC_USDT')
    # print(result)
    while True:
        t0 = time.time()
        result = asyncio.create_task(orderbook.get_orderbook('SPOT_BTC_USDT'))
        await result
        print(time.time() - t0)

if __name__ == "__main__":
    markets = Poloniex()
    print(markets.get_markets())
    print(markets.get_coin_fee('BTC_USDT'))
    asyncio.run(main())