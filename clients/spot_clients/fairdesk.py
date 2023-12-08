import requests
import asyncio
import aiohttp
import time

# requestLimit has to be counted

class Fairdesk:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://api.fairdesk.com/api/v1/public/md/orderbook?symbol="
        self.urlMarkets = f"https://api.fairdesk.com/api/v1/public/products"
        self.urlFees = f"https://api.fairdesk.com/api/v1/public/md/contracts"
        self.markets = {}
        self.fees = {}
        self.requestLimit = 0

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets['data']:
            if ('/USDT' in market['displayName']) and ('USDC/USDT' not in market['displayName']):
                coin = market['displayName'].split('/USDT')[0]
                self.markets.update({coin: market['displayName']})
        return(self.markets)
        # return(markets)

    def get_coin_fee(self, symbol):
        fees = requests.get(url=self.urlFees, headers=self.headers).json()
        for fee in fees['result']:
            if symbol == fee['index_name']:
                self.fees.update({symbol: {"Maker": fee['maker_fee'], "Taker": fee['taker_fee']}})
        return self.fees


    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.urlOrderbooks + symbol) as response:
                ob = await response.json()
                # return(ob)
        return {"top_ask": ob['data']["asks"][0][0], "ask_vol": ob['data']['asks'][0][1],
                "top_bid": ob['data']["bids"][0][0], "bid_vol": ob['data']["bids"][0][1],
                "ts_exchange": ob['data']['timestamp']}

async def main():
    orderbook = Fairdesk()
    # result = await orderbook.get_orderbook('BTC/USDT')
    # print(result)
    while True:
        t0 = time.time()
        result = asyncio.create_task(orderbook.get_orderbook('BTC/USDT'))
        await result
        print(time.time() - t0)


if __name__ == "__main__":
    markets = Fairdesk()
    print(markets.get_markets())
    print(markets.get_coin_fee('BTC/USDT'))
    asyncio.run(main())