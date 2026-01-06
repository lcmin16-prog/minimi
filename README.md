# Upbit RSI Paper Trading MVP

Single-run RSI strategy on 5-minute candles with paper trading by default.

## Setup
1. Create and activate a venv:
   - `python -m venv .venv`
   - `.venv\Scripts\activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Create `.env`:
   - `copy .env.example .env`
   - Fill `UPBIT_ACCESS_KEY` and `UPBIT_SECRET_KEY` for real trading.

## Run
- `python main.py`

## Verification Flow (Run -> Backtest -> Report -> Improve)
1. Verify normal run
   - `python main.py`
2. Run backtest
   - `python backtest.py --ticker KRW-BTC --days 90 --interval minute5`
   - Results are saved to `trades.csv`.
3. Review report
   - `python report.py`
4. Improve
   - Adjust RSI settings, trade size, and risk parameters, then re-run

## Notes
- Each run performs: fetch data -> signal -> trade -> log.
- Paper mode uses a persisted JSON state file between runs.
- Switch to real trading with `TRADE_MODE=real` in `.env`.
- Logs are written to `trades.log`.
