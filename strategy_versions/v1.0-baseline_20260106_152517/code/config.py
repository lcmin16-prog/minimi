import os

from dotenv import load_dotenv

load_dotenv()


def _get_str(name, default):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def _get_int(name, default):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_float(name, default):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


TRADE_MODE = _get_str("TRADE_MODE", "paper").strip().lower()
TICKER = _get_str("TICKER", "KRW-BTC")
RSI_PERIOD = _get_int("RSI_PERIOD", 14)
TRADE_AMOUNT_KRW = _get_float("TRADE_AMOUNT_KRW", 10000.0)
PAPER_INITIAL_KRW = _get_float("PAPER_INITIAL_KRW", 1000000.0)
PAPER_STATE_FILE = _get_str("PAPER_STATE_FILE", "paper_account.json")
LOG_FILE = _get_str("LOG_FILE", "trades.log")

UPBIT_ACCESS_KEY = _get_str("UPBIT_ACCESS_KEY", "")
UPBIT_SECRET_KEY = _get_str("UPBIT_SECRET_KEY", "")

CANDLE_INTERVAL = "minute5"

MAX_INVEST_RATIO = 0.30
STOP_LOSS_PCT = 0.03
TAKE_PROFIT_PCT = 0.05
DAILY_LOSS_LIMIT_PCT = 0.05
