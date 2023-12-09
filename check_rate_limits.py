import json
import random
import time
from datetime import datetime
import asyncio

from clients.all_clients import ALL_CLIENTS_DICT


class Check_limit():
    def __init__(self):
        self.client = ALL_CLIENTS_DICT['KRAKEN']()
        self.density = 5000  # requests per duration
        self.duration = 60  # in seconds
        print(f"Inputs: Exchange: {self.client.client_name}, Duration - {self.duration}, "
              f"Density - {self.density}, Start DT: {datetime.utcnow()}")

        try:
            self.markets_all = list(self.client.get_markets().values())
        except Exception as error:
            input('We are in BAN already, input smth to continue')

    async def async_request(self, markets):
        tasks = []
        time_list = []
        start_dt = datetime.utcnow()
        # создаем таски с нужной интенсивностью + фиксируем время создания
        for market in markets:
            tasks.append(asyncio.create_task(self.client.get_orderbook(market)))
            time_list.append(datetime.utcnow())
            time.sleep(self.duration / self.density)

        print(f"Full time of requesting exchange: {(datetime.utcnow() - start_dt).total_seconds()}")
        return await asyncio.gather(*tasks, return_exceptions=True)

    def analise_response(self, results):
        success_counter = 0
        for result in results:
            try:
                if 'Status' in result:
                    if result['Status'] == 'OK':
                        success_counter += 1
                    else:
                        print(f'Проблема на запросе # {success_counter + 1}')
                        print(json.dumps(result, indent=2))
                        break
                else:
                    print(f'Проблема на запросе # {success_counter + 1}')
                    print(json.dumps(result, indent=2))
                    break
                    # real_work_time = (time_list[i] - start_dt).total_seconds()
                    # problem_requests.update({'request': i, 'duration': real_work_time, 'result': result}
            except Exception as error:
                print(f'Проблема на запросе # {success_counter + 1}')
                print(f'{json.dumps(result, indent=2)} error: {error}')
                break
        if success_counter == self.density:
            print('Все запросы успешно отработаны')

    async def main(self):
        markets = []
        # заполняем список случайными рынками биржи
        for i in range(self.density):
            markets.append(random.choice(self.markets_all))

        start_dt = datetime.utcnow()
        results = await self.async_request(markets)
        print(f"Full time for all responses: {(datetime.utcnow() - start_dt).total_seconds()}")
        self.analise_response(results)
        await asyncio.sleep(1)

if __name__ == '__main__':
    check_limit = Check_limit()
    asyncio.run(check_limit.main())
