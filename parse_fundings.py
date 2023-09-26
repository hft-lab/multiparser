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

ob_zero = {'top_bid': 0, 'top_ask': 0, 'bid_vol': 0, 'ask_vol': 0, 'ts_exchange': 0, 'ts_start': 0, 'ts_end': 0}


class FundingParser:

    def __init__(self):
        self.clients_list = [DyDx(), Kraken(), Binance()]  # , Bitfinex()]  # , Bitspay(), Ascendex()]
        self.markets = coins_symbols_client(self.clients_list)  # {coin: {symbol:client(),...},...}
        self.clients_data = self.get_clients_data()

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

    @staticmethod
    async def fundings(client):
        try:
            return await client.get_fundings()
        except Exception as error:
            print(f'Exception из fundings, биржа:{client.__class__.__name__}, ошибка: {error}')
            return ob_zero

    async def create_and_await_fundings_requests_tasks(self):
        tasks_dict = {}
        for client in self.clients_list:
            tasks_dict[client.__class__.__name__] = asyncio.create_task(self.fundings(client))
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

    @staticmethod
    def reformat_data(fundings):
        last_results = {}
        for exchange, result in fundings.items():
            last_timeframe = 0
            print(result)
            for timeframe, coins in result.items():
                if float(timeframe) > float(last_timeframe):
                    last_timeframe = timeframe
            last_results.update({exchange: result[last_timeframe]})
            if not last_results.get('next_funding_time'):
                last_results['next_funding_time'] = {}
            last_results['next_funding_time'].update({exchange: last_timeframe})
        return last_results

    def find_funding_AP(self, fundings):
        for exchange_1, funding_1 in fundings:
            for exchange_2, funding_2 in fundings:
                if exchange_2 == exchange_1:
                    continue

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

            results = await self.create_and_await_fundings_requests_tasks()
            results = self.reformat_data(results)

            print(results)

            print(f"Iteration  end. Duration.: {(datetime.utcnow() - time_start_cycle).total_seconds()}")
            iteration += 1


if __name__ == '__main__':
    parser = FundingParser()
    asyncio.run(parser.main())
