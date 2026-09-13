import streamlit as st
import requests
import pandas as pd
import numpy as np

# =========================================================
# MACALY + ALPHA BOT v4.3
# AUTO REFRESH + COINBASE + KALSHI BTC 15 MIN
# =========================================================

st.set_page_config(
    page_title="Macaly + Alpha Bot v4.3",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# DISEÑO
# =========================================================

st.markdown("""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.stApp {
    background-color:#0b0e14;
}

.block-container {
    padding:10px !important;
    max-width:460px;
}

.bot-card {
    background:#11161f;
    border:1px solid #334155;
    border-radius:18px;
    padding:20px;
    margin-bottom:12px;
    color:#e8edf5;
}

.bot-title {
    background:#111a2e;
    border:1px solid #2563eb;
    border-radius:18px;
    padding:18px;
    margin-bottom:12px;
    text-align:center;
    color:#38bdf8;
    font-weight:900;
    letter-spacing:3px;
}

.bot-label {
    text-align:center;
    color:#94a3b8;
    font-size:13px;
    font-weight:800;
    letter-spacing:3px;
    margin-bottom:12px;
}

.bot-row {
    display:flex;
    justify-content:space-between;
    gap:15px;
    padding:11px 0;
    border-bottom:1px solid #334155;
}

.bot-row:last-child {
    border-bottom:none;
}

.bot-left {
    color:#94a3b8;
}

.bot-right {
    color:#e8edf5;
    font-weight:800;
    text-align:right;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# COINBASE
# =========================================================

@st.cache_data(ttl=8)
def get_btc_data():

    url = (
        "https://api.exchange.coinbase.com/"
        "products/BTC-USD/candles"
    )

    response = requests.get(
        url,
        params={
            "granularity": 60
        },
        headers={
            "User-Agent": "MacalyAlphaBot/4.3"
        },
        timeout=12
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError("Respuesta Coinbase inválida.")

    if len(data) < 30:
        raise ValueError("Coinbase no devolvió suficientes velas.")

    df = pd.DataFrame(
        data,
        columns=[
            "time",
            "low",
            "high",
            "open",
            "close",
            "volume"
        ]
    )

    for column in [
        "low",
        "high",
        "open",
        "close",
        "volume"
    ]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df["time"] = pd.to_datetime(
        df["time"],
        unit="s",
        utc=True
    )

    df = (
        df
        .dropna()
        .sort_values("time")
        .reset_index(drop=True)
    )

    return df


# =========================================================
# KALSHI BTC 15 MIN
# =========================================================

@st.cache_data(ttl=8)
def get_kalshi_btc_market():

    url = (
        "https://external-api.kalshi.com/"
        "trade-api/v2/markets"
    )

    response = requests.get(
        url,
        params={
            "limit": 100,
            "status": "open",
            "series_ticker": "KXBTC15M"
        },
        headers={
            "User-Agent": "MacalyAlphaBot/4.3"
        },
        timeout=12
    )

    response.raise_for_status()

    payload = response.json()

    markets = payload.get(
        "markets",
        []
    )

    if not markets:
        return None

    markets.sort(
        key=lambda market: str(
            market.get("close_time") or "9999"
        )
    )

    return markets[0]


# =========================================================
# INDICADORES
# =========================================================

def add_indicators(df):

    df = df.copy()

    close = df["close"]

    # EMA 9
    df["ema9"] = close.ewm(
        span=9,
        adjust=False
    ).mean()

    # EMA 21
    df["ema21"] = close.ewm(
        span=21,
        adjust=False
    ).mean()

    # RSI 14
    delta = close.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14
    ).mean()

    rs = (
        avg_gain /
        avg_loss.replace(0, np.nan)
    )

    df["rsi"] = (
        100 -
        (100 / (1 + rs))
    ).fillna(50)

    # BOLLINGER
    middle = close.rolling(20).mean()

    std = close.rolling(20).std()

    df["bb_upper"] = (
        middle +
        (2 * std)
    )

    df["bb_lower"] = (
        middle -
        (2 * std)
    )

    # MOMENTUM
    df["mom3"] = (
        close.pct_change(3) * 100
    )

    df["mom5"] = (
        close.pct_change(5) * 100
    )

    df["mom15"] = (
        close.pct_change(15) * 100
    )

    # VOLUMEN
    avg_volume = (
        df["volume"]
        .rolling(20)
        .mean()
    )

    df["vol_ratio"] = (
        df["volume"] /
        avg_volume.replace(0, np.nan)
    )

    return df


# =========================================================
# MOTOR DE SEÑALES
# =========================================================

def build_signal(df):

    last = df.iloc[-1]

    score = 0.0

    # EMA
    if last["ema9"] > last["ema21"]:

        score += 2.0
        ema_text = "ALCISTA 🚀"

    else:

        score -= 2.0
        ema_text = "BAJISTA 🔻"

    # RSI
    rsi = float(last["rsi"])

    if 52 <= rsi <= 68:
        score += 1.25

    elif 32 <= rsi <= 48:
        score -= 1.25

    elif rsi > 75:
        score -= 0.50

    elif rsi < 25:
        score += 0.50

    # MOMENTUM
    if pd.notna(last["mom3"]):
        mom3 = float(last["mom3"])
    else:
        mom3 = 0.0

    if pd.notna(last["mom5"]):
        mom5 = float(last["mom5"])
    else:
        mom5 = 0.0

    if pd.notna(last["mom15"]):
        mom15 = float(last["mom15"])
    else:
        mom15 = 0.0

    if mom3 > 0.02:
        score += 1.25

    elif mom3 < -0.02:
        score -= 1.25

    if mom5 > 0.03:
        score += 1.00

    elif mom5 < -0.03:
        score -= 1.00

    if mom15 > 0.05:
        score += 0.75

    elif mom15 < -0.05:
        score -= 0.75

    # VOLUMEN
    if pd.notna(last["vol_ratio"]):
        vol_ratio = float(last["vol_ratio"])
    else:
        vol_ratio = 0.0

    if vol_ratio > 1.15:

        if mom5 > 0:
            score += 0.50

        elif mom5 < 0:
            score -= 0.50

    # PRECIO
    price = float(last["close"])

    # VOLATILIDAD
    if (
        pd.notna(last["bb_upper"])
        and
        pd.notna(last["bb_lower"])
    ):

        width = (
            (
                float(last["bb_upper"])
                -
                float(last["bb_lower"])
            )
            /
            price
            *
            100
        )

    else:
        width = 0.0

    if width > 0.8:
        volatility = "ALTA"

    elif width > 0.4:
        volatility = "MEDIA"

    else:
        volatility = "BAJA"

    # DECISIÓN
    if score >= 2.5:

        signal = "POSIBLE UP"
        decision = "SEÑAL UP"
        signal_class = "up"
        icon = "🚀"

        up = int(
            round(
                min(
                    78,
                    50 + abs(score) * 5
                )
            )
        )

        down = 100 - up

    elif score <= -2.5:

        signal = "POSIBLE DOWN"
        decision = "SEÑAL DOWN"
        signal_class = "down"
        icon = "🔻"

        down = int(
            round(
                min(
                    78,
                    50 + abs(score) * 5
                )
            )
        )

        up = 100 - down

    else:

        signal = "NO TRADE"
        decision = "ESPERAR"
        signal_class = "neutral"
        icon = "⚪"

        up = 50
        down = 50

    # MOMENTUM VISUAL
    if mom3 > 0.02:
        momentum = "MOMENTUM ALCISTA"

    elif mom3 < -0.02:
        momentum = "MOMENTUM BAJISTA"

    else:
        momentum = "MOMENTUM NEUTRAL"

    return {
        "price": price,
        "score": score,
        "signal": signal,
        "decision": decision,
        "signal_class": signal_class,
        "icon": icon,
        "up": up,
        "down": down,
        "ema": ema_text,
        "rsi": rsi,
        "mom3": mom3,
        "mom5": mom5,
        "mom15": mom15,
        "vol_ratio": vol_ratio,
        "volatility": volatility,
        "momentum": momentum
    }


# =========================================================
# PRECIO KALSHI
# =========================================================

def kalshi_price(dollar_value, cent_value):

    if dollar_value not in [None, ""]:

        try:
            value = float(dollar_value)
            return f"${value:.2f}"

        except Exception:
            return str(dollar_value)

    if cent_value is not None:

        try:
            value = float(cent_value)
            return f"{value:g}¢"

        except Exception:
            return str(cent_value)

    return "--"


# =========================================================
# TITULO
# =========================================================

st.markdown(
    '<div class="bot-title">⚡ MACALY + ALPHA BOT • v4.3</div>',
    unsafe_allow_html=True
)


# =========================================================
# TODO LO DE AQUÍ SE ACTUALIZA CADA 10 SEGUNDOS
# =========================================================

@st.fragment(run_every="10s")
def live_dashboard():

    # -----------------------------------------
    # COINBASE
    # -----------------------------------------

    btc_ok = False
    btc_error = ""

    try:

        btc_df = get_btc_data()

        btc_df = add_indicators(
            btc_df
        )

        sig = build_signal(
            btc_df
        )

        btc_ok = True

    except Exception as error:

        btc_error = str(error)

        sig = {
            "price": 0.0,
            "score": 0.0,
            "signal": "SIN DATOS",
            "decision": "SIN CONEXIÓN",
            "signal_class": "neutral",
            "icon": "⚪",
            "up": 50,
            "down": 50,
            "ema": "SIN DATOS",
            "rsi": 50.0,
            "mom3": 0.0,
            "mom5": 0.0,
            "mom15": 0.0,
            "vol_ratio": 0.0,
            "volatility": "SIN DATOS",
            "momentum": "MOMENTUM NEUTRAL"
        }

    # -----------------------------------------
    # KALSHI
    # -----------------------------------------

    kalshi_ok = False
    kalshi_error = ""
    market = None

    try:

        market = get_kalshi_btc_market()

        if market is not None:
            kalshi_ok = True

    except Exception as error:

        kalshi_error = str(error)

    # -----------------------------------------
    # DATOS DEL MERCADO
    # -----------------------------------------

    if market:

        ticker = market.get(
            "ticker",
            "--"
        )

        yes_bid_dollars = market.get(
            "yes_bid_dollars"
        )

        yes_ask_dollars = market.get(
            "yes_ask_dollars"
        )

        last_price_dollars = market.get(
            "last_price_dollars"
        )

        yes_bid = market.get(
            "yes_bid"
        )

        yes_ask = market.get(
            "yes_ask"
        )

        last_price = market.get(
            "last_price"
        )

    else:

        ticker = "--"

        yes_bid_dollars = None
        yes_ask_dollars = None
        last_price_dollars = None

        yes_bid = None
        yes_ask = None
        last_price = None

    kalshi_bid_display = kalshi_price(
        yes_bid_dollars,
        yes_bid
    )

    kalshi_ask_display = kalshi_price(
        yes_ask_dollars,
        yes_ask
    )

    kalshi_last_display = kalshi_price(
        last_price_dollars,
        last_price
    )

    # -----------------------------------------
    # ESTADOS
    # -----------------------------------------

    if kalshi_ok:

        kalshi_status = "CONECTADO 🟢"
        market_status = "MERCADO ENCONTRADO ✅"

    else:

        kalshi_status = "SIN MERCADO ⚠️"
        market_status = "NO SE ENCONTRÓ MERCADO"

    if btc_ok:
        coinbase_status = "CONECTADO 🟢"

    else:
        coinbase_status = "SIN CONEXIÓN 🔴"

    # -----------------------------------------
    # COLORES
    # -----------------------------------------

    if sig["signal_class"] == "up":

        signal_color = "#34d399"

    elif sig["signal_class"] == "down":

        signal_color = "#fb7185"

    else:

        signal_color = "#fbbf24"

    if "ALCISTA" in sig["momentum"]:

        momentum_color = "#34d399"

    elif "BAJISTA" in sig["momentum"]:

        momentum_color = "#fb7185"

    else:

        momentum_color = "#fbbf24"

    # =====================================================
    # SEÑAL PRINCIPAL
    # =====================================================

    signal_html = (
        '<div class="bot-card" style="text-align:center;">'
        '<div class="bot-label">SEÑAL TÉCNICA BTC</div>'
        f'<div style="font-size:30px;font-weight:900;color:{signal_color};">'
        f'{sig["icon"]} {sig["signal"]}'
        '</div>'
        '<div style="color:#cbd5e1;font-size:19px;margin-top:8px;">'
        f'BTC ${sig["price"]:,.2f}'
        '</div>'
        '</div>'
    )

    st.markdown(
        signal_html,
        unsafe_allow_html=True
    )

    # =====================================================
    # UP / DOWN
    # =====================================================

    col_up, col_down = st.columns(2)

    with col_up:

        up_html = (
            '<div style="'
            'background:#073326;'
            'border:1px solid #10b981;'
            'border-radius:18px;'
            'padding:20px 8px;'
            'text-align:center;'
            'color:#34d399;'
            'font-weight:900;'
            '">'
            'UP'
            '<div style="font-size:34px;margin-top:5px;">'
            f'{sig["up"]}%'
            '</div>'
            '</div>'
        )

        st.markdown(
            up_html,
            unsafe_allow_html=True
        )

    with col_down:

        down_html = (
            '<div style="'
            'background:#35171d;'
            'border:1px solid #ef4444;'
            'border-radius:18px;'
            'padding:20px 8px;'
            'text-align:center;'
            'color:#fb7185;'
            'font-weight:900;'
            '">'
            'DOWN'
            '<div style="font-size:34px;margin-top:5px;">'
            f'{sig["down"]}%'
            '</div>'
            '</div>'
        )

        st.markdown(
            down_html,
            unsafe_allow_html=True
        )

    st.write("")

    # =====================================================
    # MOMENTUM
    # =====================================================

    momentum_html = (
        '<div class="bot-card" style="text-align:center;">'
        '<div class="bot-label">MOMENTUM</div>'
        f'<div style="font-size:21px;font-weight:900;color:{momentum_color};">'
        f'{sig["momentum"]}'
        '</div>'
        '<div style="color:#64748b;margin-top:7px;">'
        f'3 min: {sig["mom3"]:+.3f}%'
        '&nbsp;&nbsp; • &nbsp;&nbsp;'
        f'15 min: {sig["mom15"]:+.3f}%'
        '</div>'
        '</div>'
    )

    st.markdown(
        momentum_html,
        unsafe_allow_html=True
    )

    # =====================================================
    # INDICADORES
    # =====================================================

    indicators_html = (
        '<div class="bot-card">'
        '<div class="bot-label">INDICADORES</div>'

        '<div class="bot-row">'
        '<span class="bot-left">EMA 9 / 21</span>'
        f'<span class="bot-right">{sig["ema"]}</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">RSI 14</span>'
        f'<span class="bot-right">{sig["rsi"]:.1f}</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Momentum 3m</span>'
        f'<span class="bot-right">{sig["mom3"]:+.3f}%</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Momentum 5m</span>'
        f'<span class="bot-right">{sig["mom5"]:+.3f}%</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Momentum 15m</span>'
        f'<span class="bot-right">{sig["mom15"]:+.3f}%</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Volumen</span>'
        f'<span class="bot-right">{sig["vol_ratio"]:.2f}x</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Volatilidad</span>'
        f'<span class="bot-right">{sig["volatility"]}</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Coinbase</span>'
        f'<span class="bot-right">{coinbase_status}</span>'
        '</div>'

        '</div>'
    )

    st.markdown(
        indicators_html,
        unsafe_allow_html=True
    )

    # =====================================================
    # KALSHI
    # =====================================================

    kalshi_html = (
        '<div class="bot-card">'
        '<div class="bot-label">KALSHI • BTC 15 MIN</div>'

        '<div style="text-align:center;font-weight:900;margin-bottom:15px;">'
        f'{market_status}'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Ticker</span>'
        f'<span class="bot-right">{ticker}</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">YES bid</span>'
        f'<span class="bot-right">{kalshi_bid_display}</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">YES ask</span>'
        f'<span class="bot-right">{kalshi_ask_display}</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Último</span>'
        f'<span class="bot-right">{kalshi_last_display}</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">API Kalshi</span>'
        f'<span class="bot-right">{kalshi_status}</span>'
        '</div>'

        '</div>'
    )

    st.markdown(
        kalshi_html,
        unsafe_allow_html=True
    )

    # =====================================================
    # DECISIÓN
    # =====================================================

    decision_html = (
        '<div class="bot-card" style="text-align:center;">'
        '<div class="bot-label">DECISIÓN DEL MOTOR</div>'

        f'<div style="font-size:28px;font-weight:900;color:{signal_color};">'
        f'{sig["decision"]}'
        '</div>'

        '<div style="color:#64748b;margin-top:10px;">'
        f'Score técnico: {sig["score"]:.2f}'
        '</div>'

        '<div style="color:#64748b;font-size:12px;line-height:1.6;margin-top:15px;">'
        'Coinbase + Kalshi BTC 15 min'
        '<br>'
        'Actualización automática cada 10 segundos 🔄'
        '<br>'
        'Modo análisis / paper'
        '<br>'
        'No envía órdenes reales'
        '<br><br>'
        'UP/DOWN es un score técnico experimental.'
        '<br>'
        'No representa la probabilidad oficial de Kalshi.'
        '</div>'

        '</div>'
    )

    st.markdown(
        decision_html,
        unsafe_allow_html=True
    )

    # =====================================================
    # ERRORES
    # =====================================================

    if btc_error:

        st.error(
            "Error Coinbase: "
            +
            btc_error
        )

    if kalshi_error:

        st.error(
            "Error Kalshi: "
            +
            kalshi_error
        )


# =========================================================
# ARRANCAR DASHBOARD
# =========================================================

live_dashboard()
