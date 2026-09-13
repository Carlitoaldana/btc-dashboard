import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Macaly + Alpha Bot v3.0",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
.stApp {background-color:#0b0e14;}
.block-container {padding:10px !important; max-width:450px;}
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATOS REALES BTC
# =========================================================

@st.cache_data(ttl=15)
def get_btc_data():

    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 250
    }

    response = requests.get(url, params=params, timeout=8)
    response.raise_for_status()

    raw = response.json()

    df = pd.DataFrame(raw, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "close_time", "quote_volume",
        "trades", "taker_base", "taker_quote", "ignore"
    ])

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# =========================================================
# INDICADORES
# =========================================================

def calculate_indicators(df):

    close = df["close"]

    # EMA REAL
    df["ema9"] = close.ewm(span=9, adjust=False).mean()
    df["ema21"] = close.ewm(span=21, adjust=False).mean()

    # RSI 14 - Wilder
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

    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    df["sma20"] = close.rolling(20).mean()
    df["std20"] = close.rolling(20).std()

    df["upper"] = df["sma20"] + (2 * df["std20"])
    df["lower"] = df["sma20"] - (2 * df["std20"])

    # Momentum corto
    df["momentum3"] = close.pct_change(3) * 100
    df["momentum5"] = close.pct_change(5) * 100

    # Volumen relativo
    df["volume_avg20"] = df["volume"].rolling(20).mean()
    df["volume_ratio"] = df["volume"] / df["volume_avg20"]

    return df


# =========================================================
# MOTOR DE SEÑALES
# =========================================================

def generate_signal(df):

    last = df.iloc[-1]

    price = float(last["close"])
    ema9 = float(last["ema9"])
    ema21 = float(last["ema21"])
    rsi = float(last["rsi"])
    momentum3 = float(last["momentum3"])
    momentum5 = float(last["momentum5"])
    volume_ratio = float(last["volume_ratio"])

    score = 0.0
    reasons = []

    # Tendencia EMA
    if ema9 > ema21:
        score += 2
        reasons.append("EMA 9 sobre EMA 21")
        ema_status = "ALCISTA 🚀"
    else:
        score -= 2
        reasons.append("EMA 9 debajo de EMA 21")
        ema_status = "BAJISTA 🔴"

    # RSI
    if 52 <= rsi <= 70:
        score += 1.25
        reasons.append("RSI favorece compradores")

    elif 30 <= rsi <= 48:
        score -= 1.25
        reasons.append("RSI favorece vendedores")

    elif rsi > 75:
        score -= 0.50
        reasons.append("RSI sobrecomprado")

    elif rsi < 25:
        score += 0.50
        reasons.append("RSI sobrevendido")

    # Momentum 3 minutos
    if momentum3 > 0.05:
        score += 1.25
        reasons.append("Momentum corto positivo")

    elif momentum3 < -0.05:
        score -= 1.25
        reasons.append("Momentum corto negativo")

    # Momentum 5 minutos
    if momentum5 > 0.10:
        score += 1
    elif momentum5 < -0.10:
        score -= 1

    # Volumen como confirmación
    if volume_ratio > 1.20:
        if momentum3 > 0:
            score += 0.75
            reasons.append("Volumen confirma subida")
        elif momentum3 < 0:
            score -= 0.75
            reasons.append("Volumen confirma bajada")

    # Convertir score a confianza.
    # Es un SCORE del modelo, NO probabilidad garantizada.
    confidence = min(78, 50 + abs(score) * 5)

    if score >= 2.5:
        signal = "UP"
        up = round(confidence)
        down = 100 - up

    elif score <= -2.5:
        signal = "DOWN"
        down = round(confidence)
        up = 100 - down

    else:
        signal = "NO TRADE"
        up = 50
        down = 50

    # Volatilidad usando ancho de Bollinger
    if last["sma20"] and not pd.isna(last["sma20"]):
        band_width = (
            (last["upper"] - last["lower"])
            / last["sma20"]
        ) * 100
    else:
        band_width = 0

    if band_width >= 0.60:
        volatility = "ALTA 🚨"
    elif band_width >= 0.30:
        volatility = "MEDIA ⚠️"
    else:
        volatility = "BAJA"

    return {
        "signal": signal,
        "up": up,
        "down": down,
        "score": score,
        "price": price,
        "rsi": rsi,
        "ema9": ema9,
        "ema21": ema21,
        "ema_status": ema_status,
        "momentum3": momentum3,
        "momentum5": momentum5,
        "volume_ratio": volume_ratio,
        "volatility": volatility,
        "reasons": reasons
    }


# =========================================================
# CARGAR MOTOR
# =========================================================

try:

    df = get_btc_data()
    df = calculate_indicators(df)

    result = generate_signal(df)

    connected = True

except Exception as e:

    connected = False
    error_message = str(e)

    result = {
        "signal": "SIN DATOS",
        "up": 50,
        "down": 50,
        "score": 0,
        "price": 0,
        "rsi": 50,
        "ema9": 0,
        "ema21": 0,
        "ema_status": "SIN DATOS",
        "momentum3": 0,
        "momentum5": 0,
        "volume_ratio": 0,
        "volatility": "SIN DATOS",
        "reasons": []
    }


signal = result["signal"]
up = result["up"]
down = result["down"]


if signal == "UP":
    signal_color = "#34d399"
    signal_text = "POSIBLE UP 🚀"
    action = "SEÑAL UP"

elif signal == "DOWN":
    signal_color = "#f87171"
    signal_text = "POSIBLE DOWN 🔴"
    action = "SEÑAL DOWN"

else:
    signal_color = "#fbbf24"
    signal_text = "NO TRADE ⚠️"
    action = "ESPERAR"


# =========================================================
# INTERFAZ
# =========================================================

st.markdown(
    f"""
    <div style="
        background:#0b0e14;
        color:#e6e6e6;
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    ">

        <div style="
            background:#0f172a;
            border:1px solid #2563eb;
            border-radius:16px;
            padding:14px;
            text-align:center;
            margin-bottom:12px;
        ">
            <b style="color:#38bdf8;">
                ⚡ BTC SIGNAL ENGINE • 15 MIN
            </b>
        </div>


        <div style="
            background:#11151c;
            border:1px solid #1f293d;
            border-radius:16px;
            padding:18px;
            text-align:center;
            margin-bottom:12px;
        ">

            <div style="
                color:#8a99ad;
                font-size:12px;
                letter-spacing:2px;
            ">
                SEÑAL ACTUAL
            </div>

            <div style="
                color:{signal_color};
                font-size:28px;
                font-weight:800;
                margin-top:8px;
            ">
                {signal_text}
            </div>

            <div style="
                color:#9ca3af;
                margin-top:6px;
            ">
                BTC ${result["price"]:,.2f}
            </div>

        </div>


        <div style="
            display:flex;
            gap:10px;
            margin-bottom:12px;
        ">

            <div style="
                flex:1;
                background:#0d231d;
                border:1px solid #059669;
                border-radius:14px;
                padding:16px;
                text-align:center;
            ">
                <div style="color:#34d399;">UP</div>

                <div style="
                    color:#34d399;
                    font-size:28px;
                    font-weight:800;
                ">
                    {up}%
                </div>
            </div>


            <div style="
                flex:1;
                background:#261519;
                border:1px solid #dc2626;
                border-radius:14px;
                padding:16px;
                text-align:center;
            ">
                <div style="color:#f87171;">DOWN</div>

                <div style="
                    color:#f87171;
                    font-size:28px;
                    font-weight:800;
                ">
                    {down}%
                </div>
            </div>

        </div>


        <div style="
            background:#11151c;
            border:1px solid #1f293d;
            border-radius:16px;
            padding:16px;
            margin-bottom:12px;
        ">

            <div style="
                text-align:center;
                color:#8a99ad;
                letter-spacing:2px;
                margin-bottom:12px;
            ">
                INDICADORES
            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                padding:8px 0;
                border-bottom:1px solid #1f293d;
            ">
                <span>EMA 9 / EMA 21</span>
                <b>{result["ema_status"]}</b>
            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                padding:8px 0;
                border-bottom:1px solid #1f293d;
            ">
                <span>RSI (14)</span>
                <b>{result["rsi"]:.1f}</b>
            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                padding:8px 0;
                border-bottom:1px solid #1f293d;
            ">
                <span>Momentum 3m</span>
                <b>{result["momentum3"]:+.3f}%</b>
            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                padding:8px 0;
                border-bottom:1px solid #1f293d;
            ">
                <span>Volumen relativo</span>
                <b>{result["volume_ratio"]:.2f}x</b>
            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                padding:8px 0;
            ">
                <span>Volatilidad</span>
                <b>{result["volatility"]}</b>
            </div>

        </div>


        <div style="
            background:#11151c;
            border:1px solid #1f293d;
            border-radius:16px;
            padding:16px;
            text-align:center;
        ">

            <div style="color:#8a99ad;">
                DECISIÓN DEL MOTOR
            </div>

            <div style="
                color:{signal_color};
                font-size:22px;
                font-weight:800;
                margin:7px;
            ">
                {action}
            </div>

            <div style="
                color:#6b7280;
                font-size:11px;
            ">
                Score técnico: {result["score"]:.2f}<br>
                Actualización de datos cada ~15 segundos<br>
                Señal experimental • No garantiza resultados
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


if not connected:
    st.error("No se pudieron obtener datos de BTC: " + error_message)
