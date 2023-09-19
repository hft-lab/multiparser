import requests
import time
import asyncio
import aiohttp

class Coinstore:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
        self.urlOrderbooks = f"https://api.coinstore.com/api/v1/market/depth/"
        self.urlMarket = f"https://api.coinstore.com/api/v1/ticker/price"
        self.fees = {'SPOT': {'Maker': 0.2, 'Taker': 0.2}, 'FUTURES': {'Maker': 0.00025, 'Taker': 0.0006}}
        self.SAF = {'BTCUSDT', 'BOBCUSDT', 'LEGOUSDT', 'DREAMSUSDT', 'FEETUSDT',
                    'CBYUSDT', 'LTCUSDT', 'XRPUSDT', 'ETHUSDT', 'BNBUSDT', 'TRXUSDT', 'LINKUSDT',
                    'ADAUSDT', 'FILUSDT', 'FTMUSDT', 'CELRUSDT', 'MATICUSDT', 'CELOUSDT', 'AVAXUSDT',
                    'SANDUSDT', 'DOTUSDT', 'AXSUSDT', 'BICOUSDT', 'DYDXUSDT', 'RACAUSDT',
                    '1MWAGMIGAMESUSDT', 'DOGEUSDT', 'UNIUSDT'}  # SAF = Spot And Futures
        self.futuresOnly = {'LTCUSDT', 'ETCUSDT', 'EOSUSDT', 'BCHUSDT', 'THETAUSDT', 'ATOMUSDT', 'HBARUSDT',
                        'KSMUSDT', 'ICPUSDT', '1MWAGMIGAMESUSDT', 'SOLUSDT'}
        self.markets = {}
        self.requestLimit = 1876

    def get_markets(self):
        markets = requests.get(url=self.urlMarket, headers=self.headers).json()
        for market in markets['data']:
            if 'USDT' in market['symbol']:
                coin = market['symbol'].split('USDT')[0]
                self.markets.update({coin: market['symbol']})
        return(self.markets)

    def get_coin_fee(self, symbol):
        if symbol in self.markets.values():
            if symbol in self.futuresOnly:
                return {symbol: self.fees['FUTURES']}
            elif symbol in self.SAF:
                return {symbol: self.fees}
            else:
                return {symbol: self.fees['SPOT']}
        else:
            return {}

    async def get_orderbook(self, symbol):
        async with aiohttp.ClientSession() as session:  # менеджер отправления запросов
            async with session.get(self.urlOrderbooks + symbol) as response:
                ob = await response.json()
        return {'top_ask': ob['data']['a'][0][0], 'ask_vol': ob['data']['a'][0][1],
                'top_bid': ob['data']['b'][0][0], 'bid_vol': ob['data']['b'][0][1],
                'ts_exchange': 0}

async def main():
    orderbook = Coinstore()
    # result = await orderbook.get_orderbook('BTCUSDT')
    # print(result)
    while True:
        t0 = time.time()
        result = asyncio.create_task(orderbook.get_orderbook('BTCUSDT'))
        await result
        print(time.time() - t0)

if __name__ == "__main__":
    markets = Coinstore()
    print(markets.get_markets())
    print(markets.get_coin_fee('BTCUSDT'))
    asyncio.run(main())
