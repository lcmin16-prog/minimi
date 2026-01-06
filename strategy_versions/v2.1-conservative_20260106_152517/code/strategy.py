def calculate_rsi(close_series, period):
    delta = close_series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def get_signal(df, period):
    if df is None or df.empty:
        return "hold", None

    rsi_series = calculate_rsi(df["close"], period)
    latest = rsi_series.iloc[-1]

    if latest != latest:
        return "hold", None

    if latest <= 30:
        return "buy", float(latest)
    if latest >= 70:
        return "sell", float(latest)
    return "hold", float(latest)
