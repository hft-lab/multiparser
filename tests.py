from clients.all_clients import ALL_CLIENTS_DICT
import asyncio
import json
from clients.perp_clients.binance import Binance
from clients.perp_clients.wooX import Woo


async def main():
    client = Woo()
    print(json.dumps(client.get_markets(), indent=2))
    symbol = 'SPOT_ZRX_USDT'
    #input('symbol:')
    for i in range(1000):
        ob = await client.get_orderbook(symbol=symbol)
        print(ob)
    await asyncio.sleep(1)

    # # print(json.dumps(ob, indent=2))



    # print(json.dumps(await client.get_orderbook(symbol="NEARUSDT")))


if __name__ == '__main__':
    asyncio.run(main())
