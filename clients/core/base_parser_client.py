import aiohttp
from abc import ABC, abstractmethod
import telebot
import configparser
import sys
config = configparser.ConfigParser()
config.read(sys.argv[1], "utf-8")


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

    @abstractmethod
    def get_orderbook(self, symbol) -> dict:
        pass


