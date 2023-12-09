from abc import ABC, abstractmethod
import telebot
import configparser
import sys
from core.telegram import Telegram, TG_Groups

config = configparser.ConfigParser()
config.read(sys.argv[1], "utf-8")


class ClientState():
    ACTIVE = 'ACTIVE'
    PAUSE = 'PAUSE'


class BaseClient(ABC):
    BASE_URL = None
    BASE_WS = None
    EXCHANGE_NAME = None

    def __init__(self):
        self.chat_id = config['TELEGRAM']['CHAT_ID']
        self.chat_token = config['TELEGRAM']['TOKEN']
        self.alert_id = config['TELEGRAM']['ALERT_CHAT_ID']
        self.alert_token = config['TELEGRAM']['ALERT_BOT_TOKEN']
        self.debug_id = config['TELEGRAM']['DIMA_DEBUG_CHAT_ID']
        self.debug_token = config['TELEGRAM']['DIMA_DEBUG_BOT_TOKEN']
        self.telegram = Telegram()
        self.state = None

    @abstractmethod
    def get_markets(self) -> dict:
        pass

    @abstractmethod
    def get_orderbook(self, symbol) -> dict:
        pass

    def change_state(self, new_state, client_name, text):
        if self.state == new_state:
            pass
        if self.state == ClientState.ACTIVE and new_state == ClientState.PAUSE:
            self.state = ClientState.PAUSE
            print(f'Request Limit Exceeded {client_name=}. {text=}')
            self.telegram.send_message(
                f'Парсер: {client_name} \nПревышен лимит запросов. Клиент поставлен на паузу.\nОшибка от биржи: {text}',
                TG_Groups.Alerts)
        if self.state == ClientState.PAUSE and new_state == ClientState.ACTIVE:
            self.state = ClientState.ACTIVE
            self.telegram.send_message(f'Парсер: {client_name} Снят с паузы', TG_Groups.Alerts)

    def ob_parsing_exception(self, symbol, error):
        print(f'Response Status = 200. OB Parsing Problem. {symbol=}, Error^ {str(error)}')
        return {'Status': 'OB Parse Error', 'Error': str(error)}

    def request_limit_exception(self, code, text):
        return {'Status': 'Request Limit Exceeded', 'Code': code, 'Text': text}

    def exchange_connection_exception(self, symbol, code, text):
        print(f'Response Status != 200. {code=}, {symbol=}, {text=}')
        return {'Status': 'Exchange Conn. Problems', 'Code': code, 'Text': text}
