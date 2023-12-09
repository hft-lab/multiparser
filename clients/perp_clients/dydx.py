import asyncio
import aiohttp
import requests
from ..core.base_parser_client import BaseClient, ClientState, GetOrderbookErrors
import configparser

config = configparser.ConfigParser()
config.read('config.ini', "utf-8")

class DyDx(BaseClient):
    def __init__(self):
        super().__init__()
        self.client_name = 'DYDX'
        self.headers = {"Content-Type": "application/json"}
        self.urlMarkets = "https://api.dydx.exchange/v3/markets/"
        self.urlOrderbooks = "https://api.dydx.exchange/v3/orderbook/"
        self.fees = float(config[self.client_name]['FEES'])
        self.requestLimit = int(config[self.client_name]['REQUESTS_LIMIT'])

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market, value in markets['markets'].items():
            if value['quoteAsset'] == 'USD':
                coin = value['baseAsset']
                self.markets.update({coin: market})
        return self.markets

    async def get_orderbook(self, symbol):
        if self.state == ClientState.ACTIVE:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.urlOrderbooks + symbol) as response:
                    if response.status == 200:
                        try:
                            ob = await response.json()
                            return {'top_bid': ob['bids'][0]['price'], 'top_ask': ob['asks'][0]['price'],
                                    'bid_vol': ob['bids'][0]['size'], 'ask_vol': ob['asks'][0]['size'],
                                    'ts_exchange': 0, 'Status': 'OK'}
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
    pass


# client = Bitfinex()
#  symbol = "tETHF0:USTF0"
#  while True:
#      task = asyncio.create_task(client.get_orderbook(symbol))
#      print(await task)
#      time.sleep(1)
if __name__ == '__main__':
    asyncio.run(main())
