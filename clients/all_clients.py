from clients.perp_clients.binance import Binance
from clients.perp_clients.dydx import DyDx
from clients.perp_clients.kraken import Kraken
from clients.perp_clients.wooX import Woo

ALL_CLIENTS_DICT = {
    'DYDX': DyDx,
    'BINANCE': Binance,
    'KRAKEN': Kraken,
    'WOO': Woo
}

ALL_CLIENTS_LIST = [DyDx, Binance, Kraken, Woo]
