import streamlit as st
import requests
import pandas as pd
import numpy as np

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Macaly + Alpha Bot v3.1",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {background-color: #0b0e14;}
    .block-container {
        padding: 8px !important;
        max-width: 460px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATOS REALES DE BTC
# =========================================================

@st.cache_data(ttl=15)
def get_btc_data():

    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 250
    }

    response = requests.get(
        url,
        params=params,
        timeout=8
    )

    response.raise_for_status()

    raw = response.json()

    df = pd.DataFrame(
        raw,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trades",
            "taker_base",
            "taker_quote",
            "ignore"
        ]
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna().reset_index(drop=True)

    return df


# =========================================================
# INDICADORES
# =========================================================

def calculate_indicators(df):

    df = df.copy()

    close = df["close"]

    # EMA REAL 9 y 21
    df["ema9"] = close.ewm(
        span=9,
        adjust=False
    ).mean()

    df["ema21"] = close.ewm(
        span=21,
        adjust=False
    ).mean()

    # RSI 14 - Wilder
    delta = close.diff()

    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    avg_gain = gains.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14
    ).mean()

    avg_loss = losses.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    df["rsi"] = 100 - (
        100 / (1 + rs)
    )

    # Bollinger Bands
    df["sma20"] = close.rolling(20).mean()

    df["std20"] = close.rolling(20).std()

    df["upper_band"] = (
        df["sma20"] +
        (2 * df["std20"])
    )

    df["lower_band"] = (
        df["sma20"] -
        (2 * df["std20"])
    )

    # Momentum
    df["momentum3"] = (
        close.pct_change(3) * 100
    )

    df["momentum5"] = (
        close.pct_change(5) * 100
    )

    # Volumen relativo
    df["volume_average"] = (
        df["volume"]
        .rolling(20)
        .mean()
    )

    df["volume_ratio"] = (
        df["volume"] /
        df["volume_average"]
    )

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

    # -----------------------------------------------------
    # EMA
    # -----------------------------------------------------

    if ema9 > ema21:

        score += 2.0

        ema_status = "ALCISTA"

        reasons.append(
            "EMA 9 sobre EMA 21"
        )

    else:

        score -= 2.0

        ema_status = "BAJISTA"

        reasons.append(
            "EMA 9 debajo de EMA 21"
        )

    # -----------------------------------------------------
    # RSI
    # -----------------------------------------------------

    if 52 <= rsi <= 70:

        score += 1.25

        reasons.append(
            "RSI favorece compradores"
        )

    elif 30 <= rsi <= 48:

        score -= 1.25

        reasons.append(
            "RSI favorece vendedores"
        )

    elif rsi > 75:

        score -= 0.50

        reasons.append(
            "RSI sobrecomprado"
        )

    elif rsi < 25:

        score += 0.50

        reasons.append(
            "RSI sobrevendido"
        )

    # -----------------------------------------------------
    # MOMENTUM 3 MIN
    # -----------------------------------------------------

    if momentum3 > 0.05:

        score += 1.25

        reasons.append(
            "Momentum corto positivo"
        )

    elif momentum3 < -0.05:

        score -= 1.25

        reasons.append(
            "Momentum corto negativo"
        )

    # -----------------------------------------------------
    # MOMENTUM 5 MIN
    # -----------------------------------------------------

    if momentum5 > 0.10:

        score += 1.0

    elif momentum5 < -0.10:

        score -= 1.0

    # -----------------------------------------------------
    # VOLUMEN
    # -----------------------------------------------------

    if volume_ratio > 1.20:

        if momentum3 > 0:

            score += 0.75

            reasons.append(
                "Volumen confirma movimiento alcista"
            )

        elif momentum3 < 0:

            score -= 0.75

            reasons.append(
                "Volumen confirma movimiento bajista"
            )

    # -----------------------------------------------------
    # SCORE / CONFIANZA
    # -----------------------------------------------------

    confidence = min(
        78,
        50 + abs(score) * 5
    )

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

    # -----------------------------------------------------
    # VOLATILIDAD
    # -----------------------------------------------------

    sma20 = float(last["sma20"])
    upper = float(last["upper_band"])
    lower = float(last["lower_band"])

    if sma20 != 0:

        band_width = (
            (upper - lower) /
            sma20
        ) * 100

    else:

        band_width = 0

    if band_width >= 0.60:

        volatility = "ALTA"

    elif band_width >= 0.30:

        volatility = "MEDIA"

    else:

        volatility = "BAJA"

    return {
        "signal": signal,
        "up": up,
        "down": down,
        "score": score,
        "price": price,
        "ema9": ema9,
        "ema21": ema21,
        "ema_status": ema_status,
        "rsi": rsi,
        "momentum3": momentum3,
        "momentum5": momentum5,
        "volume_ratio": volume_ratio,
        "volatility": volatility,
        "reasons": reasons
    }


# =========================================================
# EJECUTAR MOTOR
# =========================================================

try:

    btc = get_btc_data()

    btc = calculate_indicators(btc)

    result = generate_signal(btc)

    data_connected = True

    error_message = ""

except Exception as error:

    data_connected = False

    error_message = str(error)

    result = {
        "signal": "SIN DATOS",
        "up": 50,
        "down": 50,
        "score": 0,
        "price": 0,
        "ema9": 0,
        "ema21": 0,
        "ema_status": "SIN DATOS",
        "rsi": 50,
        "momentum3": 0,
        "momentum5": 0,
        "volume_ratio": 0,
        "volatility": "SIN DATOS",
        "reasons": []
    }


# =========================================================
# VARIABLES VISUALES
# =========================================================

signal = result["signal"]

up = result["up"]

down = result["down"]


if signal == "UP":

    signal_text = "POSIBLE UP"

    signal_color = "#34d399"

    signal_icon = "🚀"

    decision = "SEÑAL UP"


elif signal == "DOWN":

    signal_text = "POSIBLE DOWN"

    signal_color = "#f87171"

    signal_icon = "🔴"

    decision = "SEÑAL DOWN"


elif signal == "NO TRADE":

    signal_text = "NO TRADE"

    signal_color = "#fbbf24"

    signal_icon = "⚠️"

    decision = "ESPERAR"


else:

    signal_text = "SIN DATOS"

    signal_color = "#9ca3af"

    signal_icon = "⚪"

    decision = "SIN CONEXIÓN"


if data_connected:

    connection_text = "DATOS BTC CONECTADOS"

    connection_color = "#34d399"

else:

    connection_text = "SIN CONEXIÓN"

    connection_color = "#f87171"


# =========================================================
# DESCRIPCIÓN DE MOMENTUM
# =========================================================

if result["momentum3"] > 0.05:

    momentum_text = "MOMENTUM ALCISTA"

    momentum_color = "#34d399"

elif result["momentum3"] < -0.05:

    momentum_text = "MOMENTUM BAJISTA"

    momentum_color = "#f87171"

else:

    momentum_text = "MOMENTUM NEUTRAL"

    momentum_color = "#fbbf24"


# =========================================================
# HTML
# =========================================================

html_code = f"""
<!DOCTYPE html>

<html lang="es">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<style>

* {{
    box-sizing: border-box;
}}

html,
body {{

    margin: 0;
    padding: 0;

    background: #0b0e14;

    color: #e6e6e6;

    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Helvetica,
        Arial,
        sans-serif;
}}

.container {{

    width: 100%;

    max-width: 430px;

    margin: 0 auto;

    padding: 8px;
}}


.card {{

    background: #11151c;

    border: 1px solid #263247;

    border-radius: 18px;

    padding: 18px;

    margin-bottom: 12px;
}}


.header {{

    background: #0f172a;

    border: 1px solid #2563eb;

    border-radius: 18px;

    padding: 16px;

    text-align: center;

    margin-bottom: 12px;

    color: #38bdf8;

    font-size: 13px;

    font-weight: 800;

    letter-spacing: 1.5px;
}}


.section-title {{

    text-align: center;

    color: #8a99ad;

    font-size: 11px;

    font-weight: 700;

    letter-spacing: 2px;

    text-transform: uppercase;
}}


.signal {{

    text-align: center;

    color: {signal_color};

    font-size: 28px;

    font-weight: 900;

    margin-top: 8px;
}}


.price {{

    text-align: center;

    color: #9ca3af;

    font-size: 13px;

    margin-top: 7px;
}}


.grid {{

    display: grid;

    grid-template-columns: 1fr 1fr;

    gap: 10px;

    margin-bottom: 12px;
}}


.up-box {{

    background: #0d231d;

    border: 1px solid #059669;

    border-radius: 16px;

    padding: 16px;

    text-align: center;
}}


.down-box {{

    background: #261519;

    border: 1px solid #dc2626;

    border-radius: 16px;

    padding: 16px;

    text-align: center;
}}


.percent {{

    font-size: 29px;

    font-weight: 900;

    margin-top: 4px;
}}


.row {{

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 12px;

    padding: 10px 0;

    border-bottom: 1px solid #263247;

    font-size: 13px;
}}


.row:last-child {{

    border-bottom: none;
}}


.label {{

    color: #8a99ad;
}}


.value {{

    color: #e6e6e6;

    font-weight: 800;

    text-align: right;
}}


.momentum {{

    background: #171b22;

    border: 1px solid #374151;

    border-radius: 16px;

    padding: 15px;

    margin-bottom: 12px;

    text-align: center;
}}


.decision {{

    color: {signal_color};

    font-size: 23px;

    font-weight: 900;

    text-align: center;

    margin: 8px 0;
}}


.note {{

    color: #6b7280;

    font-size: 11px;

    text-align: center;

    line-height: 1.6;
}}


.connection {{

    color: {connection_color};

    font-weight: 800;
}}


.footer {{

    text-align: center;

    color: #4b5563;

    font-size: 10px;

    padding: 8px;
}}

</style>

</head>


<body>

<div class="container">


<div class="header">

⚡ MACALY + ALPHA BOT • BTC 15M

</div>


<div class="card">

<div class="section-title">

Señal actual

</div>

<div class="signal">

{signal_icon} {signal_text}

</div>

<div class="price">

BTC ${result["price"]:,.2f}

</div>

</div>


<div class="grid">

<div class="up-box">

<div style="
    color:#34d399;
    font-weight:800;
">

UP

</div>

<div
    class="percent"
    style="color:#34d399;"
>

{up}%

</div>

</div>


<div class="down-box">

<div style="
    color:#f87171;
    font-weight:800;
">

DOWN

</div>

<div
    class="percent"
    style="color:#f87171;"
>

{down}%

</div>

</div>

</div>


<div class="momentum">

<div class="section-title">

Momentum detectado

</div>

<div style="
    color:{momentum_color};
    font-size:18px;
    font-weight:900;
    margin-top:7px;
">

{momentum_text}

</div>

<div class="note">

Cambio 3 min:
{result["momentum3"]:+.3f}%

</div>

</div>


<div class="card">

<div
    class="section-title"
    style="margin-bottom:8px;"
>

Indicadores clave

</div>


<div class="row">

<span class="label">

EMA 9 / EMA 21

</span>

<span class="value">

{result["ema_status"]}

</span>

</div>


<div class="row">

<span class="label">

RSI (14)

</span>

<span class="value">

{result["rsi"]:.1f}

</span>

</div>


<div class="row">

<span class="label">

Momentum 3m

</span>

<span class="value">

{result["momentum3"]:+.3f}%

</span>

</div>


<div class="row">

<span class="label">

Momentum 5m

</span>

<span class="value">

{result["momentum5"]:+.3f}%

</span>

</div>


<div class="row">

<span class="label">

Volumen relativo

</span>

<span class="value">

{result["volume_ratio"]:.2f}x

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

Fuente de precio

</span>

<span class="connection">

{connection_text}

</span>

</div>

</div>


<div class="card">

<div class="section-title">

Decisión del motor

</div>

<div class="decision">

{decision}

</div>

<div class="note">

Score técnico:
{result["score"]:.2f}

<br>

Datos actualizados aproximadamente
cada 15 segundos.

<br><br>

UP/DOWN es un score experimental
del modelo técnico.

<br>

Todavía NO representa
la probabilidad de Kalshi.

</div>

</div>


<div class="footer">

Macaly + Alpha Bot v3.1

<br>

Signal Engine • Paper Mode

</div>


</div>

</body>

</html>
"""


# =========================================================
# RENDERIZAR CORRECTAMENTE EL HTML
# =========================================================

st.components.v1.html(
    html_code,
    height=850,
    scrolling=True
)


if not data_connected:

    st.error(
        "Error obteniendo datos BTC: "
        + error_message
    )
