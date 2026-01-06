import json
import os
from datetime import datetime

from loguru import logger

DEFAULT_INITIAL_KRW = 1_000_000.0
DEFAULT_STATE_PATH = "paper_account.json"


class PaperBroker:
    def __init__(self, initial_krw=DEFAULT_INITIAL_KRW, state_path=DEFAULT_STATE_PATH):
        self.state_path = state_path or DEFAULT_STATE_PATH
        self.default_krw = float(initial_krw)
        self.krw_balance = self.default_krw
        self.coin_amount = 0.0
        self.avg_buy_price = 0.0
        self.last_day = None
        self.day_start_equity = 0.0
        self._load_or_initialize()

    def _default_state(self):
        today = datetime.now().date().isoformat()
        return {
            "krw_balance": self.default_krw,
            "coin_amount": 0.0,
            "avg_buy_price": 0.0,
            "last_day": today,
            "day_start_equity": self.default_krw,
        }

    def _apply_state(self, data):
        try:
            krw_balance = float(data["krw_balance"])
            coin_amount = float(data["coin_amount"])
            avg_buy_price = float(data["avg_buy_price"])
        except Exception as exc:
            raise ValueError("Invalid paper account state") from exc

        last_day = data.get("last_day")
        day_start_equity_raw = data.get("day_start_equity")
        if last_day and day_start_equity_raw is not None:
            try:
                day_start_equity = float(day_start_equity_raw)
            except Exception as exc:
                raise ValueError("Invalid daily loss state") from exc
        else:
            last_day = None
            day_start_equity = 0.0

        self.krw_balance = krw_balance
        self.coin_amount = coin_amount
        self.avg_buy_price = avg_buy_price
        self.last_day = last_day
        self.day_start_equity = day_start_equity

    def _load_or_initialize(self):
        if not os.path.exists(self.state_path):
            self._reset_to_defaults()
            return

        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._apply_state(data)
        except Exception as exc:
            logger.warning("Failed to load paper account; resetting: {}", exc)
            self._reset_to_defaults()

    def _reset_to_defaults(self):
        self._apply_state(self._default_state())
        self.save()

    def _state_payload(self):
        data = self.get_status()
        data["last_day"] = self.last_day
        data["day_start_equity"] = self.day_start_equity
        return data

    def save(self):
        data = self._state_payload()
        try:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as exc:
            logger.warning("Failed to save paper account: {}", exc)

    def buy(self, price, amount_krw):
        price = float(price)
        amount_krw = float(amount_krw)

        if price <= 0 or amount_krw <= 0:
            return {"status": "rejected", "reason": "invalid_amount"}

        spend = min(amount_krw, self.krw_balance)
        if spend <= 0:
            return {"status": "rejected", "reason": "insufficient_krw"}

        qty = spend / price
        total_cost = self.avg_buy_price * self.coin_amount + spend
        total_qty = self.coin_amount + qty

        self.avg_buy_price = total_cost / total_qty
        self.coin_amount = total_qty
        self.krw_balance -= spend

        self.save()
        return {
            "status": "filled",
            "side": "buy",
            "price": price,
            "qty": qty,
            "krw_spent": spend,
        }

    def sell_all(self, price):
        price = float(price)

        if price <= 0:
            return {"status": "rejected", "reason": "invalid_price"}
        if self.coin_amount <= 0:
            return {"status": "rejected", "reason": "no_position"}

        qty = self.coin_amount
        proceeds = qty * price

        self.krw_balance += proceeds
        self.coin_amount = 0.0
        self.avg_buy_price = 0.0

        self.save()
        return {
            "status": "filled",
            "side": "sell",
            "price": price,
            "qty": qty,
            "krw_received": proceeds,
        }

    def get_status(self):
        return {
            "krw_balance": self.krw_balance,
            "coin_amount": self.coin_amount,
            "avg_buy_price": self.avg_buy_price,
        }

    def snapshot(self):
        return self.get_status()

    def get_total_equity(self, current_price):
        return self.krw_balance + self.coin_amount * float(current_price)

    def refresh_day(self, current_price, now=None):
        if now is None:
            now = datetime.now()
        today = now.date().isoformat()
        if self.last_day != today:
            self.last_day = today
            self.day_start_equity = self.get_total_equity(current_price)
            self.save()

    def get_daily_loss_pct(self, current_price):
        if self.day_start_equity <= 0:
            return 0.0
        equity = self.get_total_equity(current_price)
        return (equity - self.day_start_equity) / self.day_start_equity
