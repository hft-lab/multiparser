import requests
import aiohttp
import asyncio
import time
from ..core.base_parser_client import BaseClient, ClientState


class Woo(BaseClient):
    def __init__(self):
        super().__init__()
        self.client_name = 'Woo'
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://api.woo.org/v1/public/orderbook/"
        self.urlMarkets = f"https://api.woo.org/v1/public/info"
        self.markets = {}
        self.fees = {"Maker": 0.05, "Taker": 0.05}
        self.requestLimit = 2000  #
        self.state = ClientState.ACTIVE


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
                            return self.ob_parsing_exception(symbol, error)
                    else:
                        error_text = await response.json()
                        if response.status == 429:
                            self.change_state(ClientState.PAUSE, self.client_name,str(error_text))
                            return self.request_limit_exception(code=response.status,text=str(error_text))

                        else:
                            return self.exchange_connection_exception(symbol, code=response.status,
                                                                        text=str(error_text))
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
