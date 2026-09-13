import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone

# =========================================================
# MACALY + ALPHA BOT v4.0
# Coinbase + Kalshi
# =========================================================

st.set_page_config(
    page_title="Macaly + Alpha Bot v4.0",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    header {visibility:hidden;}
    .stApp {background:#0b0e14;}
    .block-container {
        padding:8px !important;
        max-width:460px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# COINBASE - BTC REAL
# =========================================================

@st.cache_data(ttl=15)
def get_btc_candles():

    url = (
        "https://api.exchange.coinbase.com/"
        "products/BTC-USD/candles"
    )

    response = requests.get(
        url,
        params={"granularity": 60},
        headers={
            "User-Agent": "MacalyAlphaBot/4.0"
        },
        timeout=10
    )

    response.raise_for_status()

    raw = response.json()

    if not isinstance(raw, list) or len(raw) < 30:
        raise ValueError("No hay suficientes velas BTC")

    # Coinbase:
    # time, low, high, open, close, volume
    df = pd.DataFrame(
        raw,
        columns=[
            "time",
            "low",
            "high",
            "open",
            "close",
            "volume"
        ]
    )

    for col in [
        "low",
        "high",
        "open",
        "close",
        "volume"
    ]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = (
        df.dropna()
        .sort_values("time")
        .reset_index(drop=True)
    )

    return df


# =========================================================
# KALSHI - MERCADOS BTC
# =========================================================

@st.cache_data(ttl=15)
def get_kalshi_btc_market():

    url = (
        "https://api.elections.kalshi.com/"
        "trade-api/v2/markets"
    )

    # Traemos mercados abiertos y buscamos BTC/Bitcoin.
    response = requests.get(
        url,
        params={
            "limit": 1000,
            "status": "open"
        },
        headers={
            "User-Agent": "MacalyAlphaBot/4.0"
        },
        timeout=12
    )

    response.raise_for_status()

    markets = response.json().get(
        "markets",
        []
    )

    candidates = []

    for market in markets:

        text = " ".join([
            str(market.get("ticker", "")),
            str(market.get("title", "")),
            str(market.get("subtitle", "")),
            str(market.get("yes_sub_title", "")),
            str(market.get("no_sub_title", ""))
        ]).lower()

        if (
            "bitcoin" in text
            or "btc" in text
        ):
            candidates.append(market)

    if not candidates:
        return None

    # Intentamos priorizar mercados que parezcan
    # de duración corta / 15 minutos.
    def market_score(m):

        text = " ".join([
            str(m.get("ticker", "")),
            str(m.get("title", "")),
            str(m.get("subtitle", ""))
        ]).lower()

        score = 0

        if "15" in text:
            score += 5

        if "minute" in text:
            score += 4

        if "bitcoin" in text:
            score += 2

        if "btc" in text:
            score += 2

        # Preferir mercados con precios disponibles
        if m.get("yes_bid") is not None:
            score += 1

        if m.get("yes_ask") is not None:
            score += 1

        return score

    candidates.sort(
        key=market_score,
        reverse=True
    )

    return candidates[0]


# =========================================================
# INDICADORES
# =========================================================

def add_indicators(df):

    df = df.copy()

    close = df["close"]

    # EMA real
    df["ema9"] = close.ewm(
        span=9,
        adjust=False
    ).mean()

    df["ema21"] = close.ewm(
        span=21,
        adjust=False
    ).mean()

    # RSI Wilder 14
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1/14,
        adjust=False,
        min_periods=14
    ).mean()

    avg_loss = loss.ewm(
        alpha=1/14,
        adjust=False,
        min_periods=14
    ).mean()

    rs = avg_gain / avg_loss.replace(
        0,
        np.nan
    )

    df["rsi"] = (
        100 -
        (100 / (1 + rs))
    )

    # Momentum
    df["mom3"] = (
        close.pct_change(3) * 100
    )

    df["mom5"] = (
        close.pct_change(5) * 100
    )

    df["mom15"] = (
        close.pct_change(15) * 100
    )

    # Bollinger
    df["sma20"] = (
        close.rolling(20).mean()
    )

    df["std20"] = (
        close.rolling(20).std()
    )

    df["upper"] = (
        df["sma20"] +
        2 * df["std20"]
    )

    df["lower"] = (
        df["sma20"] -
        2 * df["std20"]
    )

    # Volumen
    df["vol_avg"] = (
        df["volume"]
        .rolling(20)
        .mean()
    )

    df["vol_ratio"] = (
        df["volume"] /
        df["vol_avg"]
    )

    return df


# =========================================================
# MOTOR DE SEÑAL
# =========================================================

def calculate_signal(df):

    last = df.iloc[-1]

    price = float(last["close"])
    ema9 = float(last["ema9"])
    ema21 = float(last["ema21"])
    rsi = float(last["rsi"])
    mom3 = float(last["mom3"])
    mom5 = float(last["mom5"])
    mom15 = float(last["mom15"])
    vol_ratio = float(last["vol_ratio"])

    score = 0.0

    # Tendencia EMA
    if ema9 > ema21:
        score += 2.0
        ema_text = "ALCISTA 🚀"
    else:
        score -= 2.0
        ema_text = "BAJISTA 🔻"

    # RSI
    if 52 <= rsi <= 70:
        score += 1.25

    elif 30 <= rsi <= 48:
        score -= 1.25

    elif rsi > 75:
        score -= 0.50

    elif rsi < 25:
        score += 0.50

    # Momentum 3m
    if mom3 > 0.05:
        score += 1.25

    elif mom3 < -0.05:
        score -= 1.25

    # Momentum 5m
    if mom5 > 0.10:
        score += 1.0

    elif mom5 < -0.10:
        score -= 1.0

    # Momentum 15m
    if mom15 > 0.20:
        score += 1.25

    elif mom15 < -0.20:
        score -= 1.25

    # Volumen confirmando dirección
    if vol_ratio > 1.20:

        if mom3 > 0:
            score += 0.75

        elif mom3 < 0:
            score -= 0.75

    # Volatilidad
    sma20 = float(last["sma20"])
    upper = float(last["upper"])
    lower = float(last["lower"])

    if sma20:
        band_width = (
            (upper - lower)
            / sma20
        ) * 100
    else:
        band_width = 0

    if band_width >= 0.60:
        volatility = "ALTA"

    elif band_width >= 0.30:
        volatility = "MEDIA"

    else:
        volatility = "BAJA"

    # Confianza experimental
    confidence = min(
        78,
        50 + abs(score) * 5
    )

    if score >= 2.5:

        signal = "UP"
        up = int(round(confidence))
        down = 100 - up

    elif score <= -2.5:

        signal = "DOWN"
        down = int(round(confidence))
        up = 100 - down

    else:

        signal = "NO TRADE"
        up = 50
        down = 50

    return {
        "price": price,
        "ema9": ema9,
        "ema21": ema21,
        "ema_text": ema_text,
        "rsi": rsi,
        "mom3": mom3,
        "mom5": mom5,
        "mom15": mom15,
        "vol_ratio": vol_ratio,
        "volatility": volatility,
        "score": score,
        "signal": signal,
        "up": up,
        "down": down
    }


# =========================================================
# LEER TODO
# =========================================================

btc_connected = False
kalshi_connected = False
btc_error = ""
kalshi_error = ""

try:

    btc_df = get_btc_candles()
    btc_df = add_indicators(btc_df)
    result = calculate_signal(btc_df)

    btc_connected = True

except Exception as e:

    btc_error = str(e)

    result = {
        "price": 0,
        "ema9": 0,
        "ema21": 0,
        "ema_text": "SIN DATOS",
        "rsi": 50,
        "mom3": 0,
        "mom5": 0,
        "mom15": 0,
        "vol_ratio": 0,
        "volatility": "SIN DATOS",
        "score": 0,
        "signal": "SIN DATOS",
        "up": 50,
        "down": 50
    }


try:

    kalshi_market = get_kalshi_btc_market()

    if kalshi_market:
        kalshi_connected = True

except Exception as e:

    kalshi_market = None
    kalshi_error = str(e)


# =========================================================
# KALSHI INFO
# =========================================================

if kalshi_market:

    kalshi_title = str(
        kalshi_market.get(
            "title",
            "Mercado BTC"
        )
    )

    kalshi_ticker = str(
        kalshi_market.get(
            "ticker",
            "-"
        )
    )

    yes_bid = kalshi_market.get(
        "yes_bid"
    )

    yes_ask = kalshi_market.get(
        "yes_ask"
    )

    last_price = kalshi_market.get(
        "last_price"
    )

    def cents(value):

        if value is None:
            return "--"

        try:
            return f"{float(value):.0f}¢"
        except:
            return "--"

    kalshi_yes = cents(yes_bid)
    kalshi_ask = cents(yes_ask)
    kalshi_last = cents(last_price)

else:

    kalshi_title = (
        "No se encontró mercado BTC"
    )

    kalshi_ticker = "--"
    kalshi_yes = "--"
    kalshi_ask = "--"
    kalshi_last = "--"


# =========================================================
# VISUAL SIGNAL
# =========================================================

signal = result["signal"]

if signal == "UP":

    signal_label = "POSIBLE UP"
    signal_icon = "🚀"
    signal_color = "#34d399"
    decision = "SEÑAL UP"

elif signal == "DOWN":

    signal_label = "POSIBLE DOWN"
    signal_icon = "🔻"
    signal_color = "#fb7185"
    decision = "SEÑAL DOWN"

elif signal == "NO TRADE":

    signal_label = "NO TRADE"
    signal_icon = "⚠️"
    signal_color = "#fbbf24"
    decision = "ESPERAR"

else:

    signal_label = "SIN DATOS"
    signal_icon = "⚪"
    signal_color = "#9ca3af"
    decision = "SIN CONEXIÓN"


if result["mom3"] > 0.05:

    momentum_text = (
        "MOMENTUM ALCISTA"
    )
    momentum_color = "#34d399"

elif result["mom3"] < -0.05:

    momentum_text = (
        "MOMENTUM BAJISTA"
    )
    momentum_color = "#fb7185"

else:

    momentum_text = (
        "MOMENTUM NEUTRAL"
    )
    momentum_color = "#fbbf24"


btc_status = (
    "CONECTADO 🟢"
    if btc_connected
    else "ERROR 🔴"
)

kalshi_status = (
    "CONECTADO 🟢"
    if kalshi_connected
    else "SIN MERCADO ⚠️"
)


# =========================================================
# DASHBOARD
# =========================================================

html_code = f"""
<!DOCTYPE html>
<html>
<head>

<meta name="viewport"
content="width=device-width,
initial-scale=1.0">

<style>

* {{
    box-sizing:border-box;
}}

body {{
    margin:0;
    background:#0b0e14;
    color:#e6e6e6;
    font-family:
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
}}

.wrap {{
    padding:8px;
}}

.header {{
    border:1px solid #2563eb;
    background:#0f172a;
    border-radius:18px;
    padding:16px;
    text-align:center;
    color:#38bdf8;
    font-size:14px;
    font-weight:900;
    letter-spacing:2px;
    margin-bottom:12px;
}}

.card {{
    background:#11151c;
    border:1px solid #334155;
    border-radius:18px;
    padding:18px;
    margin-bottom:12px;
}}

.title {{
    color:#94a3b8;
    font-size:11px;
    font-weight:800;
    letter-spacing:2px;
    text-align:center;
}}

.signal {{
    color:{signal_color};
    font-size:29px;
    font-weight:900;
    text-align:center;
    margin-top:10px;
}}

.price {{
    text-align:center;
    color:#cbd5e1;
    margin-top:7px;
}}

.grid {{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:10px;
    margin-bottom:12px;
}}

.up {{
    background:#0c2a22;
    border:1px solid #10b981;
    border-radius:18px;
    padding:17px;
    text-align:center;
    color:#34d399;
}}

.down {{
    background:#2a151a;
    border:1px solid #ef4444;
    border-radius:18px;
    padding:17px;
    text-align:center;
    color:#fb7185;
}}

.big {{
    font-size:30px;
    font-weight:900;
}}

.row {{
    display:flex;
    justify-content:space-between;
    gap:10px;
    padding:10px 0;
    border-bottom:1px solid #334155;
    font-size:13px;
}}

.row:last-child {{
    border-bottom:none;
}}

.label {{
    color:#94a3b8;
}}

.value {{
    font-weight:800;
    text-align:right;
}}

.kalshi {{
    color:#a78bfa;
}}

.small {{
    font-size:11px;
    color:#64748b;
    text-align:center;
    line-height:1.5;
}}

.market-title {{
    color:#e2e8f0;
    text-align:center;
    font-size:13px;
    font-weight:700;
    margin:10px 0;
    line-height:1.4;
}}

.decision {{
    color:{signal_color};
    font-size:25px;
    font-weight:900;
    text-align:center;
    margin:10px 0;
}}

</style>
</head>

<body>

<div class="wrap">

<div class="header">
⚡ MACALY + ALPHA BOT • v4.0
</div>


<div class="card">

<div class="title">
SEÑAL TÉCNICA BTC
</div>

<div class="signal">
{signal_icon} {signal_label}
</div>

<div class="price">
BTC ${result["price"]:,.2f}
</div>

</div>


<div class="grid">

<div class="up">
<b>UP</b>
<div class="big">
{result["up"]}%
</div>
</div>

<div class="down">
<b>DOWN</b>
<div class="big">
{result["down"]}%
</div>
</div>

</div>


<div class="card">

<div class="title">
MOMENTUM
</div>

<div style="
color:{momentum_color};
text-align:center;
font-size:19px;
font-weight:900;
margin-top:9px;
">
{momentum_text}
</div>

<div class="small">
3 min:
{result["mom3"]:+.3f}%
&nbsp; • &nbsp;
15 min:
{result["mom15"]:+.3f}%
</div>

</div>


<div class="card">

<div class="title">
INDICADORES
</div>

<div class="row">
<span class="label">
EMA 9 / 21
</span>
<span class="value">
{result["ema_text"]}
</span>
</div>

<div class="row">
<span class="label">
RSI 14
</span>
<span class="value">
{result["rsi"]:.1f}
</span>
</div>

<div class="row">
<span class="label">
Momentum 5m
</span>
<span class="value">
{result["mom5"]:+.3f}%
</span>
</div>

<div class="row">
<span class="label">
Volumen
</span>
<span class="value">
{result["vol_ratio"]:.2f}x
</span>
</div>

<div class="row">
<span class="label">
Volatilidad
</span>
<span class="value">
{result["volatility"]}
</span>
</div>

<div class="row">
<span class="label">
Coinbase
</span>
<span class="value">
{btc_status}
</span>
</div>

</div>


<div class="card">

<div class="title">
KALSHI • BTC
</div>

<div class="market-title">
{kalshi_title}
</div>

<div class="row">
<span class="label">
Ticker
</span>
<span class="value kalshi">
{kalshi_ticker}
</span>
</div>

<div class="row">
<span class="label">
YES bid
</span>
<span class="value">
{kalshi_yes}
</span>
</div>

<div class="row">
<span class="label">
YES ask
</span>
<span class="value">
{kalshi_ask}
</span>
</div>

<div class="row">
<span class="label">
Último
</span>
<span class="value">
{kalshi_last}
</span>
</div>

<div class="row">
<span class="label">
API Kalshi
</span>
<span class="value">
{kalshi_status}
</span>
</div>

</div>


<div class="card">

<div class="title">
DECISIÓN DEL MOTOR
</div>

<div class="decision">
{decision}
</div>

<div class="small">

Score técnico:
{result["score"]:.2f}

<br><br>

Actualización aproximada:
15 segundos.

<br><br>

Modo análisis / paper.
No envía órdenes.

</div>

</div>

</div>

</body>
</html>
"""


st.components.v1.html(
    html_code,
    height=1180,
    scrolling=True
)


# =========================================================
# ERRORES
# =========================================================

if not btc_connected:
    st.error(
        "BTC ERROR: " + btc_error
    )

if kalshi_error:
    st.error(
        "KALSHI ERROR: " + kalshi_error
    )
