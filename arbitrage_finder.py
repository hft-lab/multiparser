import time
from datetime import datetime
import telebot


class ArbitrageFinder:

    def __init__(self, coins, clients_list):
        self.chat_id = -807300930
        self.telegram_bot = telebot.TeleBot('6037890725:AAHSKzK9aazvOYU2AiBSDO8ZLE5bJaBNrBw')
        self.coins = coins
        self.clients_list = clients_list
        self.exchanges = [x.client_name for x in self.clients_list]
        self.fees = {x.client_name: x.fees for x in self.clients_list}

    def arbitrage(self, data):
        possibilities = []
        for coin in self.coins:

            for exchange_1 in self.exchanges:
                for exchange_2 in self.exchanges:
                    if exchange_1 == exchange_2:
                        continue
                    if compare_1:= data.get(exchange_1 + '__' + coin):
                        if compare_2:= data.get(exchange_2 + '__' + coin):
                            profit = (float(compare_2['top_bid']) - float(compare_1['top_ask'])) / float(compare_1['top_ask'])
                            profit = profit - self.fees[exchange_1] - self.fees[exchange_2]
                            if profit > 0:
                                # print(f"AP! {coin}: S.E: {exchange_2} | B.E: {exchange_1} | Profit: {profit}")
                                expect_profit_abs = profit * min(float(compare_1['bid_vol']), float(compare_2['ask_vol']))
                                expect_profit_abs *= float(compare_2['top_bid'])
                                possibility = {
                                    'buy_exchange': exchange_1,
                                    'sell_exchange': exchange_2,
                                    'buy_fee': self.fees[exchange_1],
                                    'sell_fee': self.fees[exchange_2],
                                    'sell_price': float(compare_2['top_bid']),
                                    'buy_price': float(compare_1['top_ask']),
                                    'sell_size': float(compare_1['bid_vol']),
                                    'buy_size': float(compare_2['ask_vol']),
                                    'expect_profit_rel': round(profit, 5),
                                    'expect_profit_abs_usd': round(expect_profit_abs, 3),
                                    'datetime': datetime.utcnow(),
                                    'timestamp': round(datetime.utcnow().timestamp(), 3)}
                                message = '\n'.join([x + ': ' + str(y) for x, y in possibility.items()])
                                # print(message)
                                self.telegram_bot.send_message(self.chat_id,
                                                               '<pre>' + message + '</pre>',
                                                               parse_mode='HTML')
                                possibilities.append(possibility)

        # print(possibilities)


if __name__ == '__main__':
    from datetime import datetime
    from Define_markets import coins_symbols_client
    from Clients.kraken import Kraken
    from Clients.binance import Binance
    from Clients.dydx import DyDx

    clients_list = [DyDx(), Kraken(), Binance()]  # , Bitfinex()]  # , Bitspay(), Ascendex()]
    markets = coins_symbols_client(clients_list)  # {coin: {symbol:client(),...},...}
    finder = ArbitrageFinder([x for x in markets.keys()], clients_list)
    data = {}
    finder.arbitrage(data)

