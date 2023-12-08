import random
import time
from datetime import datetime
import asyncio

from clients.bigone import Bigone # все ок, лимиты хорошие


async def main():
    client = Bigone()
    try:
        markets_all = list(client.get_markets().values())
    except Exception as error:
        input('We are in BAN already, input smth to continue')
    density = 100  # requests per duration
    duration = 5  # in seconds
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
        i += 1
        try:
            if type(result) not in (dict, IndexError):
                real_work_time = (time_list[i] - start_dt).total_seconds()
                problem_requests.update({'request': i, 'duration': real_work_time, 'result': result})
            else:
                success += 1

        except Exception as error:
            real_work_time = (time_list[i] - start_dt).total_seconds()
            print(
                f'Exception. BAN on iteration: {i}, duration: {real_work_time}, real request per minute limit is {i * 60 / real_work_time}')
            input('Press enter, to see details')
            print(f'{result} error: {error}')
            input('Stop')
    time.sleep(1)
    print(f'Inputs: Duration - {duration}, Density - {density}. Outputs: Success response - {success}. '
          f'Real requests per minute: {round(density * 60 / real_create_time)} is OK. ')
    j = 0
    if len(problem_requests)>0:
        print('Have following problems (top)')
        for problem in problem_requests:
            if j < 3:
                print(problem)
            j += 1


if __name__ == '__main__':
    asyncio.run(main())
