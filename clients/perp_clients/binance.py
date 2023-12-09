import asyncio
import aiohttp
import requests
from ..core.base_parser_client import BaseClient, ClientState, GetOrderbookErrors
import configparser

config = configparser.ConfigParser()
config.read('config.ini', "utf-8")

# https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#exchange-information
# https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/Exchange-Information

class Binance(BaseClient):
    def __init__(self):
        super().__init__()
        self.client_name = 'BINANCE'
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = "https://fapi.binance.com/fapi/v1/depth?limit=5&symbol="
        self.urlMarkets = "https://fapi.binance.com/fapi/v1/exchangeInfo"
        self.fees = float(config[self.client_name]['FEES'])
        self.requestLimit = int(config[self.client_name]['REQUESTS_LIMIT'])

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets['symbols']:
            if (market['marginAsset'] == 'USDT') & (market['contractType'] == 'PERPETUAL') & (
                    market['underlyingType'] == 'COIN') & (market['status'] == 'TRADING'):
                coin = market['baseAsset']
                self.markets.update({coin: market['symbol']})
        return self.markets

    # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/Order-Book
    async def get_orderbook(self, symbol: str):
        if self.state == ClientState.ACTIVE:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.urlOrderbooks + symbol) as response:
                    if response.status == 200:
                        try:
                            ob = await response.json()
                            return {'top_bid': ob['bids'][0][0], 'top_ask': ob['asks'][0][0],
                                    'bid_vol': ob['bids'][0][1], 'ask_vol': ob['asks'][0][1],
                                    'ts_exchange': ob['E'], 'Status': 'OK'}
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
    client = Binance()
    print(client.get_markets())


if __name__ == '__main__':
    asyncio.run(main())
