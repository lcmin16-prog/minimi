import csv
from datetime import datetime, timedelta
import math
import os

from config import PAPER_INITIAL_KRW

TRADES_CSV = "trades.csv"


def parse_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def parse_time(value):
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def load_trades(path):
    if not os.path.exists(path):
        print(f"Missing {path}. Run backtest first.")
        return []

    trades = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = parse_time(row.get("time", ""))
            if not ts:
                continue
            trades.append(
                {
                    "time": ts,
                    "signal": row.get("signal", ""),
                    "price": parse_float(row.get("price")),
                    "qty": parse_float(row.get("qty")),
                    "fee": parse_float(row.get("fee")),
                    "balance": parse_float(row.get("balance")),
                    "position": parse_float(row.get("position")),
                    "pnl": parse_float(row.get("pnl")),
                }
            )
    return trades


def compute_metrics(trades):
    if not trades:
        return {
            "trade_count": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "risk_reward": 0.0,
            "total_fees": 0.0,
            "total_pnl": 0.0,
            "cumulative_return": 0.0,
            "mdd": 0.0,
            "avg_holding": None,
            "final_equity": PAPER_INITIAL_KRW,
        }

    equity_curve = []
    sell_pnls = []
    total_fees = 0.0
    total_pnl = 0.0
    trade_count = 0
    wins = 0
    losses = 0

    prev_position = 0.0
    entry_time = None
    holding_durations = []

    for trade in trades:
        equity = trade["balance"] + trade["position"] * trade["price"]
        equity_curve.append(equity)
        total_fees += trade["fee"]

        if trade["signal"] == "sell":
            trade_count += 1
            pnl = trade["pnl"]
            total_pnl += pnl
            sell_pnls.append(pnl)
            if pnl > 0:
                wins += 1
            elif pnl < 0:
                losses += 1

        if trade["signal"] == "buy" and prev_position == 0 and trade["position"] > 0:
            entry_time = trade["time"]
        if trade["signal"] == "sell" and prev_position > 0 and trade["position"] == 0:
            if entry_time:
                holding_durations.append(trade["time"] - entry_time)
            entry_time = None

        prev_position = trade["position"]

    final_equity = equity_curve[-1] if equity_curve else PAPER_INITIAL_KRW
    cumulative_return = (final_equity - PAPER_INITIAL_KRW) / PAPER_INITIAL_KRW

    peak = -math.inf
    mdd = 0.0
    for equity in equity_curve:
        if equity > peak:
            peak = equity
        if peak > 0:
            drawdown = (equity - peak) / peak
            if drawdown < mdd:
                mdd = drawdown

    win_rate = wins / trade_count if trade_count > 0 else 0.0
    avg_win = sum(p for p in sell_pnls if p > 0) / wins if wins > 0 else 0.0
    avg_loss = (
        abs(sum(p for p in sell_pnls if p < 0)) / losses if losses > 0 else 0.0
    )
    risk_reward = avg_win / avg_loss if avg_loss > 0 else (math.inf if wins > 0 else 0.0)

    avg_holding = None
    if holding_durations:
        total = sum(holding_durations, timedelta())
        avg_holding = total / len(holding_durations)

    return {
        "trade_count": trade_count,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "risk_reward": risk_reward,
        "total_fees": total_fees,
        "total_pnl": total_pnl,
        "cumulative_return": cumulative_return,
        "mdd": mdd,
        "avg_holding": avg_holding,
        "final_equity": final_equity,
    }


def format_duration(td):
    if td is None:
        return "N/A"
    total_minutes = int(td.total_seconds() / 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}h {minutes}m"


def diagnose(metrics):
    reasons = []
    trade_count = metrics["trade_count"]
    win_rate = metrics["win_rate"]
    risk_reward = metrics["risk_reward"]
    total_fees = metrics["total_fees"]
    total_pnl = metrics["total_pnl"]
    avg_holding = metrics["avg_holding"]

    if trade_count == 0:
        return ["No trades occurred; the entry conditions may be too strict."]

    if metrics["cumulative_return"] > 0:
        return ["Cumulative return is positive; focus on fee reduction and stability."]

    if win_rate < 0.45:
        reasons.append("Low win rate suggests too many losing trades.")
    if risk_reward < 1:
        reasons.append("Risk/reward below 1 indicates losses outweigh wins.")

    fee_ratio = 0.0
    gross_move = abs(total_pnl) + total_fees
    if gross_move > 0:
        fee_ratio = total_fees / gross_move
    if trade_count > 30 and fee_ratio > 0.3:
        reasons.append("Fee drag is high relative to trading activity.")

    if avg_holding is not None and avg_holding.total_seconds() < 3600 and trade_count > 20:
        reasons.append("Holding time is short, implying over-trading on noise.")

    if not reasons:
        reasons.append("No clear driver found; test longer periods or more tickers.")

    return reasons


def print_report(metrics):
    print("Backtest Report")
    print("================")
    print(f"Cumulative Return: {metrics['cumulative_return'] * 100:.2f}%")
    print(f"MDD: {metrics['mdd'] * 100:.2f}%")
    print(f"Win Rate: {metrics['win_rate'] * 100:.2f}%")
    print(f"Risk/Reward: {metrics['risk_reward']:.2f}")
    print(f"Trade Count: {metrics['trade_count']}")
    print(f"Average Holding Time: {format_duration(metrics['avg_holding'])}")
    print(f"Total Fees: {metrics['total_fees']:.2f}")
    print("")
    print("Main Reasons for Underperformance")
    for reason in diagnose(metrics):
        print(f"- {reason}")


if __name__ == "__main__":
    trades = load_trades(TRADES_CSV)
    metrics = compute_metrics(trades)
    print_report(metrics)
