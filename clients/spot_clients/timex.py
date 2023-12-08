import requests
import time
import asyncio
import aiohttp

class Timex:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://plasma-relay-backend.timex.io/public/orderbook?market="
        self.urlMarkets = f"https://plasma-relay-backend.timex.io/public/markets"
        self.markets = {}
        self.urlFees = f"https://plasma-relay-backend.timex.io/public/markets/fees"
        self.fees = {}
        self.rateLimits = 1882

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets:
            if ('/USDT' in market['name']) and ('USDC/USDT' not in market['name']):
                coin = market['baseCurrency']
                self.markets.update({coin: market['name']})
        return (self.markets)
        # return markets


    def get_coin_fee(self, symbol):
        fees = requests.get(url=self.urlFees, headers=self.headers).json()
        for fee in fees:
            if symbol + 'USDT' in fee['symbol']:
                maker_fee = fee['fees'][0]['makerFee']
                taker_fee = fee['fees'][0]['takerFee']
                self.fees.update({symbol: {"Maker": maker_fee, "Taker": taker_fee}})
        return self.fees
        # return fees

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urlOrderbooks + symbol) as response:
                ob = await response.json()
                # print(ob)
        return {"top_ask": ob["ask"][0]["price"], "ask_vol": ob["ask"][0]["baseTokenAmount"],
                "top_bid": ob["bid"][0]["price"], "bid_vol": ob["bid"][0]["baseTokenAmount"],
                "ts_exchange": ob['timestamp']}

async def main():
    orderbook = Timex()
    # result = await orderbook.get_orderbook('BTCUSDT')
    # print(result)
    while True:
        t0 = time.time()
        result = asyncio.create_task(orderbook.get_orderbook('BTCUSDT'))
        await result
        print(time.time() - t0)


if __name__ == "__main__":
    markets = Timex()
    print(markets.get_markets())
    print(markets.get_coin_fee('EOS'))
    asyncio.run(main())
