import random
import time
from datetime import datetime
import asyncio

from clients.perp_clients.ascendex import Ascendex # все ок, лимиты хорошие


async def main():
    client = Ascendex()
    try:
        markets_all = list(client.get_markets().values())
    except Exception as error:
        input('We are in BAN already, input smth to continue')
    density = 2000  # requests per duration
    duration = 30  # in seconds
    markets = []
    print(
        f"Inputs: Exchange: {client.__class__.__name__}, Duration - {duration}, Density - {density}, Start DT: {datetime.utcnow()}")

    # заполняем список случайными рынками биржи
    for i in range(density):
        markets.append(random.choice(markets_all))

    tasks = []
    time_list = []
    start_dt = datetime.utcnow()
    # создаем таски с нужной интенсивностью + фиксируем время создания
    for market in markets:
        tasks.append(asyncio.create_task(client.get_orderbook(market)))
        time_list.append(datetime.utcnow())
        time.sleep(duration / density)

    real_create_time = (datetime.utcnow() - start_dt).total_seconds()
    print(f"Full time of requesting exchange: {real_create_time}")

    results = await asyncio.gather(*tasks, return_exceptions=True)

    print(
        f"Waiting for response from exchange time: {(datetime.utcnow() - start_dt).total_seconds() - real_create_time}")
    # проверяю на какой итерации мы не получили ответа от биржи, т.е. в этот момент лимит был превышен
    i = 0
    success = 0
    problem_requests = {}

    for result in results:
        try:
            if type(result) not in (dict, IndexError):

                real_work_time = (time_list[i] - start_dt).total_seconds()
                problem_requests.update({'request': i, 'duration': real_work_time, 'result': result})
                break
            else:
                success += 1

        except Exception as error:
            real_work_time = (time_list[i] - start_dt).total_seconds()
            print(
                f'Exception. BAN on iteration: {i}, duration: {real_work_time}, real request per minute limit is {i * 60 / real_work_time}')
            input('Press enter, to see details')
            print(f'{result} error: {error}')
            input('Stop')
        i += 1
    time.sleep(1)
    print(f'Inputs: Duration - {duration}, Density - {density}. Outputs: Success response - {success}. '
          f'Real requests per minute: {round(density * 60 / real_create_time)} is OK. ')

    print(problem_requests)


if __name__ == '__main__':
    asyncio.run(main())
