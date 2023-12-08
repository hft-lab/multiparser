import asyncio
import time
import aiohttp
import requests

class Bitfinex:
    # Terminal: https://trading.bitfinex.com/t/ETHF0:USTF0
    def __init__(self):
        self.client_name = 'Bitfinex'
        self.headers = {"Content-Type": "application/json"}
        # urlTopOBAll = "https://api-pub.bitfinex.com/v2/tickers?symbols=ALL" выдает лучшие bid и ask по всем рынкам сразу
        # url = "https://api-pub.bitfinex.com/v2/conf/pub:map:currency:undl" - тоже полезный метод
        self.urlOrderbooks = "https://api-pub.bitfinex.com/v2/book/"
        # Order book method https://docs.bitfinex.com/reference/rest-public-book
        self.urlMarkets = "https://api-pub.bitfinex.com/v2/conf/pub:list:pair:futures"
        self.fees = 0.00065

        self.requestLimit = 600
        self.markets = {}
    def get_markets(self):
        markets = requests.get(url = self.urlMarkets, headers=self.headers)
        for market in markets.json()[0]:
            if market.split(":")[1] == "USTF0":
                coin = market.split(":")[0][:-2]
                self.markets.update({coin: "t"+ market})
        return self.markets

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            #api-pub.bitfinex.com/v2/book/tETHF0:USTF0/P0?len=1
            async with session.get(url = self.urlOrderbooks + symbol + "/P0?len=1") as response:
                ob = await response.json()
                try:
                    return {'top_bid': ob[0][0], 'top_ask': ob[1][0],
                            'bid_vol': abs(ob[0][1]), 'ask_vol': abs(ob[1][1]),
                            'ts_exchange': 0} #ts стакана от биржи недоступно
                except Exception as error:
                    print(f"Error from Client. Bitfinex Module, symbol: {symbol}, ob: {ob}, error: {error}")



async def main():
    client = Bitfinex()
    symbol = "tETHF0:USTF0"
    while True:
        task = asyncio.create_task(client.get_orderbook(symbol))
        print(await task)
        time.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())



