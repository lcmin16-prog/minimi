import argparse
import csv
from datetime import datetime, timedelta
import sys

import pandas as pd
import pyupbit
from loguru import logger

from config import PAPER_INITIAL_KRW, RSI_PERIOD, TRADE_AMOUNT_KRW
from strategy import get_signal

FEE_RATE = 0.0005
MIN_ORDER_KRW = 5000.0
DEFAULT_DAYS = 90
DEFAULT_INTERVAL = "minute5"
TRADES_CSV = "trades.csv"


def interval_to_minutes(interval):
    if not interval.startswith("minute"):
        raise ValueError("Only minute intervals are supported.")
    return int(interval.replace("minute", ""))


def fetch_ohlcv_days(ticker, interval, days):
    minutes = interval_to_minutes(interval)
    total_needed = int(days * 24 * 60 / minutes)
    remaining = max(total_needed, 1)
    dfs = []
    to = None

    while remaining > 0:
        count = min(200, remaining)
        df = pyupbit.get_ohlcv(ticker, interval=interval, count=count, to=to)
        if df is None or df.empty:
            break
        dfs.append(df)
        remaining -= len(df)

        earliest = df.index[0]
        next_to = earliest - timedelta(seconds=1)
        if hasattr(next_to, "to_pydatetime"):
            next_to = next_to.to_pydatetime()
        to = next_to

        if len(df) < count:
            break

    if not dfs:
        return None

    result = pd.concat(dfs).sort_index()
    result = result[~result.index.duplicated(keep="last")]
    return result


def write_trades_csv(rows, path):
    fields = ["time", "signal", "price", "qty", "fee", "balance", "position", "pnl"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run_backtest(ticker, days, interval):
    try:
        df = fetch_ohlcv_days(ticker, interval, days)
    except Exception as exc:
        logger.error("Failed to fetch OHLCV: {}", exc)
        return 1

    if df is None or df.empty:
        logger.error("No OHLCV data returned.")
        return 1

    krw_balance = float(PAPER_INITIAL_KRW)
    position_qty = 0.0
    position_cost = 0.0
    trades = []

    for idx in range(len(df)):
        window = df.iloc[: idx + 1]
        signal, rsi = get_signal(window, RSI_PERIOD)
        if rsi is None:
            continue

        price = float(window["close"].iloc[-1])
        ts = window.index[-1]
        if hasattr(ts, "to_pydatetime"):
            ts = ts.to_pydatetime()
        time_str = ts.isoformat(sep=" ")

        if signal == "buy":
            available = krw_balance / (1 + FEE_RATE)
            spend = min(TRADE_AMOUNT_KRW, available)
            if spend < MIN_ORDER_KRW:
                continue
            fee = spend * FEE_RATE
            qty = spend / price
            krw_balance -= (spend + fee)
            position_qty += qty
            position_cost += (spend + fee)

            trades.append(
                {
                    "time": time_str,
                    "signal": "buy",
                    "price": f"{price:.4f}",
                    "qty": f"{qty:.8f}",
                    "fee": f"{fee:.2f}",
                    "balance": f"{krw_balance:.2f}",
                    "position": f"{position_qty:.8f}",
                    "pnl": "0.00",
                }
            )
            continue

        if signal == "sell" and position_qty > 0:
            proceeds = position_qty * price
            if proceeds < MIN_ORDER_KRW:
                continue
            fee = proceeds * FEE_RATE
            net = proceeds - fee
            pnl = net - position_cost
            krw_balance += net

            qty = position_qty
            position_qty = 0.0
            position_cost = 0.0

            trades.append(
                {
                    "time": time_str,
                    "signal": "sell",
                    "price": f"{price:.4f}",
                    "qty": f"{qty:.8f}",
                    "fee": f"{fee:.2f}",
                    "balance": f"{krw_balance:.2f}",
                    "position": f"{position_qty:.8f}",
                    "pnl": f"{pnl:.2f}",
                }
            )

    write_trades_csv(trades, TRADES_CSV)
    logger.info("Backtest finished. Trades written to {}", TRADES_CSV)
    return 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", default="KRW-BTC")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--interval", default=DEFAULT_INTERVAL)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sys.exit(run_backtest(args.ticker, args.days, args.interval))
