from Clients.binance import Binance
from Clients.dydx import DyDx
# from Clients.bitfinex import Bitfinex
from Clients.kraken import Kraken
# from Clients.ascendex import Ascendex
from Clients.coinstore import Coinstore
from Clients.bigone import Bigone


def coins_exchanges_symbol(clients_list):
    clients_coins_symbol = dict()
    coin_exception = ['VOLT']
    # Собираем справочник: {client_name:{coin1:symbol1, ...},...}
    for client in clients_list:
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
            input(f"Ошибка 1 в модуле Define_markets: {coin},{client.client_name},{symbol}. Error: {error}")

    # Удаляем монеты с единственным маркетом
    for coin, clients_symbol in coins_clients_symbol.copy().items():
        if len(clients_symbol) == 1:
            del coins_clients_symbol[coin]
    return coins_clients_symbol


def main():
    clients_list = [Binance(), Coinstore(), DyDx(), Kraken(), Bigone()]

    for client in clients_list:
        print(client.__class__.__name__, end=" ")


if __name__ == '__main__':
    main()
