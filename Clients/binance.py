import asyncio
import aiohttp
import time
import requests
from datetime import datetime


# https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#exchange-information
# https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/Exchange-Information

class Binance:
    def __init__(self):
        self.client_name = 'Binance'
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = "https://fapi.binance.com/fapi/v1/depth?limit=5&symbol="
        self.urlMarkets = "https://fapi.binance.com/fapi/v1/exchangeInfo"
        self.fees = 0.00036
        self.requestLimit = 1200
        self.markets = {}
        self.timestamp_diff = datetime.utcnow().timestamp() - time.time()
        self.fundings = {}

    async def get_fundings(self):
        url = f"https://fapi.binance.com/fapi/v1/premiumIndex"
        response = requests.get(url)
        markets = response.json()
        ts = str(round(markets[0]['nextFundingTime'] / 1000 + self.timestamp_diff, 0))
        for market in markets:
            if (market['marginAsset'] == 'USDT') & (market['contractType'] == 'PERPETUAL') & (
                    market['underlyingType'] == 'COIN') & (market['status'] == 'TRADING'):
                if not self.fundings.get(ts):
                    self.fundings.update({ts: {}})
                new_record = [float(market['interestRate']), datetime.utcnow().timestamp(), float(market['indexPrice'])]
                if not self.fundings[ts].get(market['symbol']):
                    self.fundings[ts].update({market['symbol']: [new_record]})
                else:
                    self.fundings[ts][market['symbol']].append(new_record)
        print(self.fundings)
        return self.fundings

    def get_markets(self):
        markets = requests.get(url=self.urlMarkets, headers=self.headers).json()
        for market in markets['symbols']:
            if (market['marginAsset'] == 'USDT') & (market['contractType'] == 'PERPETUAL') & (
                    market['underlyingType'] == 'COIN') & (market['status'] == 'TRADING'):
                coin = market['baseAsset']
                self.markets.update({coin: market['symbol']})
        return self.markets

    # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/Order-Book
    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.urlOrderbooks + symbol) as response:
                ob = await response.json()
                try:
                    return {'top_bid': ob['bids'][0][0], 'top_ask': ob['asks'][0][0],
                            'bid_vol': ob['bids'][0][1], 'ask_vol': ob['asks'][0][1],
                            'ts_exchange': ob['E']}
                except Exception as error:
                    print('Error from Client. Binance Module:', symbol, error)


if __name__ == '__main__':
    client = Binance()

    # async def main():
    #
    #     time.sleep(60)
    #
    # asyncio.run(main())
    asyncio.run(client.get_fundings())
