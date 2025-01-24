from enum import Enum

PROJECT_NAME = 'ThorpAI'

class Interval(Enum):
    """
    interval of bar data.
    """
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR = "1h"
    DAILY = "1d"
    WEEKLY = "1w"
    TICK = "tick"

class SecurityType(Enum):
    NONE = 0
    EQUITY = 1
    FUTURE = 2
    OPTION = 3
    FOREX = 4
    METAL = 5
    BOND = 6
    REPO = 7
    OPENFUND = 8
    INDEX = 9
    FORWARD = 10


class Exchange(Enum):
    """
    Exchange.
    """
    # Chinese
    SSE = "SSE"  # Shanghai Stock Exchange
    SZSE = "SZSE"  # Shenzhen Stock Exchange

    CFFEX = "CFFEX"  # China Financial Futures Exchange
    SHFE = "SHFE"  # Shanghai Futures Exchange
    CZCE = "CZCE"  # Zhengzhou Commodity Exchange
    DCE = "DCE"  # Dalian Commodity Exchange
    INE = "INE"  # Shanghai International Energy Exchange

    BSE = "BSE"  # Beijing Stock Exchange
    CFETS = "CFETS"  # CFETS Bond Market Maker Trading System
    XBOND = "XBOND"  # CFETS X-Bond Anonymous Trading System

    # Global
    NYSE = "NYSE"  # New York Stock Exchnage
    NASDAQ = "NASDAQ"  # Nasdaq Exchange
    HKEX = "HKEX"  # Stock Exchange of Hong Kong

    # Crypto Currency
    BINANCE = "BINANCE"  # BINANCE Exchange
    OKX = "OKX"  # OKX Exchange


