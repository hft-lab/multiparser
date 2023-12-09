from abc import ABC, abstractmethod
import telebot
import configparser
import sys
from core.telegram import Telegram, TG_Groups
from core.wrappers import try_exc_regular, try_exc_async

config = configparser.ConfigParser()
config.read(sys.argv[1], "utf-8")


class ClientState():
    ACTIVE = 'ACTIVE'
    PAUSE = 'PAUSE'


class GetOrderbookErrors():
    OB_PARSING = 'OB Parse Error'
    RATE_LIMIT = 'Request Limit Exceeded'
    OTHER_EXCH_ERRORS = 'Other Exchanges Error'


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
        self.markets = {}
        self.state = ClientState.ACTIVE
        self.client_name = None

    @abstractmethod
    def get_markets(self) -> dict:
        pass

    @abstractmethod
    def get_orderbook(self, symbol) -> dict:
        pass

    def error_notification(self, error,error_text):
        if self.state == ClientState.ACTIVE:
            message = f'Client: {self.client_name}\nError: {error}\nText: {error_text}\nACTION: Клиент исключен из парсинга '
            self.telegram.send_message(message, TG_Groups.Alerts)


