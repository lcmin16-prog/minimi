from loguru import logger

from config import (
    CANDLE_INTERVAL,
    DAILY_LOSS_LIMIT_PCT,
    LOG_FILE,
    MAX_INVEST_RATIO,
    PAPER_INITIAL_KRW,
    PAPER_STATE_FILE,
    RSI_PERIOD,
    STOP_LOSS_PCT,
    TAKE_PROFIT_PCT,
    TICKER,
    TRADE_AMOUNT_KRW,
    TRADE_MODE,
    UPBIT_ACCESS_KEY,
    UPBIT_SECRET_KEY,
)
from logger_setup import setup_logger
from paper_broker import PaperBroker
from strategy import get_signal
from upbit_client import UpbitClient


def run_once():
    setup_logger(LOG_FILE)
    logger.info("Start run | mode={} ticker={}", TRADE_MODE, TICKER)

    client = UpbitClient(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)

    try:
        df = client.get_ohlcv(
            TICKER, interval=CANDLE_INTERVAL, count=max(200, RSI_PERIOD * 3)
        )
    except Exception as exc:
        logger.exception("Failed to fetch OHLCV: {}", exc)
        return

    if df is None or df.empty:
        logger.error("No OHLCV data returned.")
        return

    signal, rsi = get_signal(df, RSI_PERIOD)
    if rsi is None:
        logger.warning("RSI not ready; skipping trade.")
        return

    last_price = float(df["close"].iloc[-1])
    logger.info("Signal={} RSI={:.2f} Price={:.2f}", signal, rsi, last_price)

    if TRADE_MODE == "paper":
        broker = PaperBroker(
            initial_krw=PAPER_INITIAL_KRW, state_path=PAPER_STATE_FILE
        )
        broker.refresh_day(last_price)
        logger.info("Paper start: {}", broker.get_status())

        daily_loss_pct = broker.get_daily_loss_pct(last_price)
        if daily_loss_pct <= -DAILY_LOSS_LIMIT_PCT:
            logger.warning(
                "Daily loss limit reached ({:.2f}%), trading blocked.",
                daily_loss_pct * 100,
            )
            return

        if broker.coin_amount > 0 and broker.avg_buy_price > 0:
            change_pct = (last_price - broker.avg_buy_price) / broker.avg_buy_price
            if change_pct <= -STOP_LOSS_PCT:
                logger.warning(
                    "Stop-loss triggered at {:.2f}% (avg={:.2f}, price={:.2f}).",
                    change_pct * 100,
                    broker.avg_buy_price,
                    last_price,
                )
                result = broker.sell_all(price=last_price)
                logger.info("Paper result: {}", result)
                logger.info("Paper end: {}", broker.get_status())
                return
            if change_pct >= TAKE_PROFIT_PCT:
                logger.warning(
                    "Take-profit triggered at {:.2f}% (avg={:.2f}, price={:.2f}).",
                    change_pct * 100,
                    broker.avg_buy_price,
                    last_price,
                )
                result = broker.sell_all(price=last_price)
                logger.info("Paper result: {}", result)
                logger.info("Paper end: {}", broker.get_status())
                return

        if signal == "buy":
            total_equity = broker.get_total_equity(last_price)
            current_coin_value = broker.coin_amount * last_price
            spend = min(TRADE_AMOUNT_KRW, broker.krw_balance)
            max_coin_value = total_equity * MAX_INVEST_RATIO

            if current_coin_value >= max_coin_value or (
                current_coin_value + spend > max_coin_value
            ):
                logger.warning(
                    "Max invest ratio reached; buy skipped. "
                    "holding={:.2f} max={:.2f} spend={:.2f}",
                    current_coin_value,
                    max_coin_value,
                    spend,
                )
                result = {"status": "skipped", "reason": "max_invest_ratio"}
            else:
                result = broker.buy(price=last_price, amount_krw=TRADE_AMOUNT_KRW)
        elif signal == "sell":
            result = broker.sell_all(price=last_price)
        else:
            result = {"status": "skipped", "reason": "hold"}

        logger.info("Paper result: {}", result)
        logger.info("Paper end: {}", broker.get_status())
        return

    if TRADE_MODE == "real":
        try:
            if signal == "buy":
                result = client.buy_market_order(TICKER, TRADE_AMOUNT_KRW)
            elif signal == "sell":
                result = client.sell_market_order(TICKER)
            else:
                logger.info("Hold signal; no order sent.")
                return
        except Exception as exc:
            logger.exception("Order failed: {}", exc)
            return

        logger.info("Order response: {}", result)
        return

    logger.error("Unknown TRADE_MODE: {}", TRADE_MODE)


if __name__ == "__main__":
    run_once()
