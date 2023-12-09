import asyncio
import time
from logger import Logging
from datetime import datetime
from core.wrappers import timeit
from core.telegram import Telegram
import configparser

config = configparser.ConfigParser()
config.read('config.ini', "utf-8")

from clients.all_clients import ALL_CLIENTS_DICT

ob_zero = {'top_bid': 0, 'top_ask': 0, 'bid_vol': 0, 'ask_vol': 0, 'ts_exchange': 0, 'ts_start': 0, 'ts_end': 0}


class MultiParser:

    def __init__(self):
        self.logger = Logging()
        self.exchanges = config['SETTINGS']['EXCHANGES'].split(',')
        self.clients = []
        for exchange in self.exchanges:
            client = ALL_CLIENTS_DICT[exchange]()
            self.clients.append(client)
        self.logger.log_launch_params(self.clients)
        self.markets = self.coins_exchanges_symbol()
        self.clients_data = self.get_clients_data()
        self.telegram = Telegram()



    def get_clients_data(self):
        clients_data = dict()
        for client in self.clients:
            clients_data[client] = {'markets_amt': 0,'min_duration':0,
                                    'rate_per_minute': client.requestLimit,
                                    'delay': round(60 / client.requestLimit, 3)}
        for coin, clients_symbol in self.markets.items():
            for client in clients_symbol:
                clients_data[client]['markets_amt'] += 1
        for client in self.clients:
            clients_data[client]['min_duration'] = round(clients_data[client]['markets_amt']*clients_data[client]['delay'],2)
        return clients_data

    @timeit
    async def ob_top(self, client, symbol):
        try:
            return await client.get_orderbook(symbol)
        except Exception as error:
            message = f'Exception из ob_top, биржа:{client.__class__.__name__}, рынок: {symbol}, ошибка: {str(error)}'
            print(message)
            self.telegram.send_message(message)
            return {}


    async def create_and_await_ob_requests_tasks(self):
        tasks_dict = {}
        iter_start = datetime.utcnow()
        total_delay = 0
        for coin, clients_symbol in self.markets.items():

            coin_start = datetime.utcnow()
            local_delay = 0
            for client,symbol in clients_symbol.items():
                tasks_dict[client.__class__.__name__ + '__' + coin] = asyncio.create_task(self.ob_top(client, symbol))

            delays = [self.clients_data[client]['delay'] for client in clients_symbol]
            local_delay += max(delays)
            total_delay += max(delays)
            time.sleep(max(delays))
            coin_end = datetime.utcnow()
            # Лог для отладки:
            # print(coin, '# clients:', len(symbols_client.values()), 'coin. delay: ', max(delays),
            #       'Real Delay:', (coin_end - coin_start).total_seconds(), 'Sum of delays: ', local_delay)
        iter_end = datetime.utcnow()
        print('#Coins: ', len(self.markets), '# clients - Markets: ', len(tasks_dict), 'Total real dur.:',
              (iter_end - iter_start).total_seconds(),
              'Total sum of delay: ', round(total_delay,2))

        return await self.gather_dict(tasks_dict)


    def coins_exchanges_symbol(self)-> dict:
        clients_coins_symbol = dict()
        coin_exception = ['VOLT']
        # Собираем справочник: {client_name:{coin1:symbol1, ...},...}
        for client in self.clients:
            try:
                clients_coins_symbol[client] = client.get_markets()
            except Exception as error:
                print(
                    f'Ошибка 0 в модуле Define_markets, client: {client.client_name}, error: {error}')

        # Меняем порядок ключей в справочнике
        coins_clients_symbol = dict()
        for client, coins_symbol in clients_coins_symbol.items():
            try:
                for coin, symbol in coins_symbol.items():
                    if coin in coin_exception:
                        pass
                    elif coin in coins_clients_symbol.keys():
                        coins_clients_symbol[coin].update({client: symbol})
                    else:
                        coins_clients_symbol[coin] = {client: symbol}
            except Exception as error:
                input(f"Ошибка 1 в модуле Define_markets: {coins_symbol},{client.client_name}. Error: {error}")

        # Удаляем монеты с единственным маркетом
        for coin, clients_symbol in coins_clients_symbol.copy().items():
            if len(clients_symbol) == 1:
                del coins_clients_symbol[coin]
        return coins_clients_symbol # Output format {coin: {client:symbol,...},...}
    @staticmethod
    async def gather_dict(tasks: dict):
        async def mark(key, coro):
            try:
                return key, await coro
            except:
                return key, dict()

        return {
            key: result
            for key, result in await asyncio.gather(*(mark(key, coro) for key, coro in tasks.items()))
        }

    async def main(self):


        # Принтим показатели клиентов - справочно
        for client, value in self.clients_data.items():
            print(f"{client.client_name} : {value}")
        iteration = 0

        while True:
            time_start_cycle = datetime.utcnow()
            print(f"Iteration {iteration} start. ", end=" ")
            results = await self.create_and_await_ob_requests_tasks()
            #self.logger.log_rates(iteration, results)
            print(f"Iteration  end. Duration.: {(datetime.utcnow() - time_start_cycle).total_seconds()}")
            iteration += 1


if __name__ == '__main__':
    parser = MultiParser()
    asyncio.run(parser.main())
