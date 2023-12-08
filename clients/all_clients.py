from clients.perp_clients.binance import Binance
from clients.perp_clients.dydx import DyDx
from clients.perp_clients.kraken import Kraken

ALL_CLIENTS_DICT = {
    'DYDX': DyDx,
    'BINANCE': Binance,
    'KRAKEN': Kraken
}

ALL_CLIENTS_LIST = [DyDx, Binance, Kraken]
