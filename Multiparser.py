import asyncio
import time
from Logger import Logging
from datetime import datetime

from Define_markets import coins_symbols_client

from Core import timeit
from Core import gather_dict

from Clients.kraken import Kraken
from Clients.binance import Binance
from Clients.bitfinex import Bitfinex
from Clients.dydx import DyDx
from Clients.bitspay import Bitspay
from Clients.ascendex import Ascendex

ob_zero = {'top_bid': 0, 'top_ask': 0, 'bid_vol': 0, 'ask_vol': 0, 'ts_exchange': 0, 'ts_start': 0, 'ts_end': 0}


class MultiParser:

    def __init__(self):
        self.clients_list = [DyDx(), Kraken(), Binance()]#, Bitfinex()]  # , Bitspay(), Ascendex()]
        self.markets = coins_symbols_client(self.clients_list)  # {coin: {symbol:client(),...},...}
        self.clients_data = self.get_clients_data()

    @staticmethod
    @timeit
    async def ob_top(client, symbol):
        try:
            return await client.get_orderbook(symbol)
        except Exception as error:
            print(f'Exception из ob_top, биржа:{client.__class__.__name__}, рынок: {symbol}, ошибка: {error}')
            return ob_zero

    def get_clients_data(self):
        clients_data = dict()
        for client in self.clients_list:
            clients_data[client] = {'markets_amt': 0,
                                    'rate_per_minute': client.requestLimit,
                                    'delay': round(60 / client.requestLimit, 3)}
        for coin, symbols_client in self.markets.items():
            for symbol, client in symbols_client.items():
                clients_data[client]['markets_amt'] += 1
        return clients_data



    async def create_and_await_ob_requests_tasks(self):
        tasks_dict = {}
        iter_start = datetime.utcnow()
        total_delay = 0
        for coin, symbols_client in self.markets.items():
            coin_start = datetime.utcnow()
            local_delay = 0
            for symbol, client in symbols_client.items():
                tasks_dict[client.__class__.__name__ + '__' + coin] = asyncio.create_task(self.ob_top(client, symbol))

            delays = [self.clients_data[client]['delay'] for client in symbols_client.values()]
            local_delay += max(delays)
            total_delay += max(delays)
            time.sleep(max(delays))
            coin_end = datetime.utcnow()
            # Лог для отладки:
            # print(coin, '# clients:', len(symbols_client.values()), 'coin. delay: ', max(delays),
            #       'Real Delay:', (coin_end - coin_start).total_seconds(), 'Sum of delays: ', local_delay)
        iter_end = datetime.utcnow()
        print('#Coins: ', len(self.markets), '# Clients - Markets: ', len(tasks_dict), 'Total real dur.:',
              (iter_end - iter_start).total_seconds(),
              'Total sum of delay: ', total_delay)

        return await gather_dict(tasks_dict)

    @staticmethod
    def add_status(results):
        for exchange_coin_key, value in results.items():
            if results[exchange_coin_key] != {}:
                results[exchange_coin_key]['Status'] = 'Ok'
                # counter_success += 1
            else:
                results[exchange_coin_key] = ob_zero
                results[exchange_coin_key]['Status'] = 'Timeout'
        return results

    # @staticmethod
    # def calculate_parse_time_and_sort(results):
    #     parsing_time = dict()
    #     for exchange_coin_key, value in results.items():
    #         parsing_time[exchange_coin_key] = float(value['ts_end'] - value['ts_start']) / 1000
    #     return sorted(parsing_time.items(), key=lambda item: item[1], reverse=True)

    async def main(self):
        logger = Logging()
        logger.log_launch_params(self.clients_list)

        # Количество рынков для парсинга в разрезе клиента
        for client, value in self.clients_data.items():
            print(f"{client.__class__.__name__} : {value}")

        iteration = 0

        while True:
            time_start_cycle = datetime.utcnow()
            print(f"Iteration {iteration} start. ", end=" ")

            results = await self.create_and_await_ob_requests_tasks()
            results = self.add_status(results)
            logger.log_rates(iteration, results)
            # parsing_time = self.calculate_parse_time_and_sort(results)
            print(results)
            print(f"Iteration  end. Duration.: {(datetime.utcnow() - time_start_cycle).total_seconds()}")
            iteration += 1


if __name__ == '__main__':
    parser = MultiParser()
    asyncio.run(parser.main())
