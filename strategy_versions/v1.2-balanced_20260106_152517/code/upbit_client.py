import pyupbit


class UpbitClient:
    def __init__(self, access_key=None, secret_key=None):
        self.upbit = None
        if access_key and secret_key:
            self.upbit = pyupbit.Upbit(access_key, secret_key)

    def get_ohlcv(self, ticker, interval="minute5", count=200):
        return pyupbit.get_ohlcv(ticker, interval=interval, count=count)

    def buy_market_order(self, ticker, amount_krw):
        if not self.upbit:
            raise RuntimeError("Upbit keys are not set.")
        return self.upbit.buy_market_order(ticker, amount_krw)

    def sell_market_order(self, ticker):
        if not self.upbit:
            raise RuntimeError("Upbit keys are not set.")
        balance = self.upbit.get_balance(ticker)
        if balance is None:
            raise RuntimeError("Failed to fetch balance.")
        if balance <= 0:
            raise RuntimeError("No balance to sell.")
        return self.upbit.sell_market_order(ticker, balance)
