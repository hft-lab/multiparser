import traceback
import datetime
import requests

from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini', "utf-8")


class TG_Groups():
    _main_id = int(config['TELEGRAM']['CHAT_ID'])
    _main_token = config['TELEGRAM']['TOKEN']
    # self.daily_chat_id = int(config['TELEGRAM']['DAILY_CHAT_ID'])
    # self.inv_chat_id = int(config['TELEGRAM']['INV_CHAT_ID'])
    _alert_id = int(config['TELEGRAM']['ALERT_CHAT_ID'])
    _alert_token = config['TELEGRAM']['ALERT_BOT_TOKEN']
    _debug_id = int(config['TELEGRAM']['DIMA_DEBUG_CHAT_ID'])
    _debug_token = config['TELEGRAM']['DIMA_DEBUG_BOT_TOKEN']

    MainGroup = {'chat_id': _main_id, 'bot_token': _main_token}
    Alerts = {'chat_id': _alert_id, 'bot_token': _alert_token}
    DebugDima = {'chat_id': _debug_id, 'bot_token': _debug_token}


class Telegram:
    def __init__(self):
        self.tg_url = "https://api.telegram.org/bot"
        self.TG_DEBUG = bool(int(config['TELEGRAM']['TG_DEBUG']))
        self.env = str(config['SETTINGS']['ENV'])

    def send_message(self, message: str, tg_group_obj: TG_Groups = None):
        if (not self.TG_DEBUG) and ((tg_group_obj is None) or (tg_group_obj == TG_Groups.DebugDima)):
            print('TG_DEBUG IS OFF')
        else:
            group = tg_group_obj if tg_group_obj else TG_Groups.DebugDima
            url = self.tg_url + group['bot_token'] + "/sendMessage"
            message_data = {"chat_id": group['chat_id'], "parse_mode": "HTML",
                            "text": f"<pre>ENV: {self.env} \n{str(message)}</pre>"}
            try:
                r = requests.post(url, json=message_data)
                return r.json()
            except Exception as e:
                return e


if __name__ == '__main__':
    tg = Telegram()
    # tg.send_message('Hi Dima')
