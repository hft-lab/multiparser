import requests
import aiohttp
import asyncio
import time
from ..core.base_parser_client import BaseClient, ClientState, GetOrderbookErrors
import configparser

config = configparser.ConfigParser()
config.read('config.ini', "utf-8")

class Woo(BaseClient):
    def __init__(self):
        super().__init__()
        self.client_name = 'WOO'
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://api.woo.org/v1/public/orderbook/"
        self.urlMarkets = f"https://api.woo.org/v1/public/info"
        self.fees = float(config[self.client_name]['FEES'])
        self.requestLimit = int(config[self.client_name]['REQUESTS_LIMIT'])


    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()

        for market in markets['rows']:
            split_market_symbol = market['symbol'].split('_')
            if ([split_market_symbol[0], split_market_symbol[2]] == ['PERP', 'USDT']) and (
                    market['status'] == 'TRADING'):
                coin = split_market_symbol[1]
                self.markets.update({coin: market['symbol']})
        return (self.markets)
        # return(markets)

    def get_coin_fee(self, symbol):
        return {symbol: self.fees}

    async def get_orderbook(self, symbol):
        if self.state == ClientState.ACTIVE:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.urlOrderbooks + symbol) as response:
                    if response.status == 200:
                        try:
                            ob = await response.json()
                            return {"top_ask": ob['asks'][0]['price'], "ask_vol": ob['asks'][0]['quantity'],
                                    "top_bid": ob['bids'][0]['price'], "bid_vol": ob['bids'][0]['quantity'],
                                    "ts_exchange": ob['timestamp'], 'Status': 'OK'}
                        except Exception as error:
                            self.error_notification(error=GetOrderbookErrors.OB_PARSING, error_text=str(ob))
                            self.state = ClientState.PAUSE
                            return {'Status': GetOrderbookErrors.OB_PARSING, 'Error': str(error)}
                    else:
                        if response.status == 429:
                            error = GetOrderbookErrors.RATE_LIMIT
                        else:
                            error = GetOrderbookErrors.OTHER_EXCH_ERRORS
                        error_text = await response.json()
                        error_text = str(error_text) + f'\nResponse code: {response.status}'
                        self.error_notification(error, error_text)
                        self.state = ClientState.PAUSE
                        return {'Status': error, 'Code': response.status, 'Text': str(error_text)}
        else:
            return {}

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
    # asyncio.run(main())
