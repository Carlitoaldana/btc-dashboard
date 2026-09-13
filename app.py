import streamlit as st
import requests
import pandas as pd
import numpy as np

# =========================================================
# MACALY + ALPHA BOT v4.1
# BTC 15 MIN • COINBASE + KALSHI
# =========================================================

st.set_page_config(
    page_title="Macaly + Alpha Bot v4.1",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #0b0e14;
    }

    .block-container {
        padding: 10px !important;
        max-width: 460px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# COINBASE - BTC EN VIVO
# =========================================================

@st.cache_data(ttl=15)
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
            "User-Agent": "MacalyAlphaBot/4.1"
        },
        timeout=12
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list) or len(data) < 30:
        raise ValueError(
            "Coinbase no devolvió suficientes datos."
        )

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
# KALSHI - BTC 15 MIN
# =========================================================

@st.cache_data(ttl=15)
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
            "User-Agent": "MacalyAlphaBot/4.1"
        },
        timeout=12
    )

    response.raise_for_status()

    markets = response.json().get(
        "markets",
        []
    )

    if not markets:
        return None

    # Elegir el contrato abierto que cierra primero.
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

    # EMA
    df["ema9"] = close.ewm(
        span=9,
        adjust=False
    ).mean()

    df["ema21"] = close.ewm(
        span=21,
        adjust=False
    ).mean()

    # RSI
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

    # Bollinger Bands
    middle = close.rolling(20).mean()

    std = close.rolling(20).std()

    df["bb_upper"] = (
        middle + (2 * std)
    )

    df["bb_lower"] = (
        middle - (2 * std)
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

    # Volumen
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

    # Momentum
    mom3 = (
        float(last["mom3"])
        if pd.notna(last["mom3"])
        else 0.0
    )

    mom5 = (
        float(last["mom5"])
        if pd.notna(last["mom5"])
        else 0.0
    )

    mom15 = (
        float(last["mom15"])
        if pd.notna(last["mom15"])
        else 0.0
    )

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

    # Volumen
    vol_ratio = (
        float(last["vol_ratio"])
        if pd.notna(last["vol_ratio"])
        else 0.0
    )

    if vol_ratio > 1.15:

        if mom5 > 0:

            score += 0.50

        elif mom5 < 0:

            score -= 0.50

    # Volatilidad
    price = float(last["close"])

    if (
        pd.notna(last["bb_upper"])
        and
        pd.notna(last["bb_lower"])
    ):

        width = (
            (
                float(last["bb_upper"]) -
                float(last["bb_lower"])
            )
            / price
            * 100
        )

    else:

        width = 0.0

    if width > 0.8:

        volatility = "ALTA"

    elif width > 0.4:

        volatility = "MEDIA"

    else:

        volatility = "BAJA"

    # Señal final
    if score >= 2.5:

        signal = "POSIBLE UP"

        decision = "SEÑAL UP"

        up = int(
            round(
                min(
                    78,
                    50 + abs(score) * 5
                )
            )
        )

        down = 100 - up

        signal_class = "up"

        icon = "🚀"

    elif score <= -2.5:

        signal = "POSIBLE DOWN"

        decision = "SEÑAL DOWN"

        down = int(
            round(
                min(
                    78,
                    50 + abs(score) * 5
                )
            )
        )

        up = 100 - down

        signal_class = "down"

        icon = "🔻"

    else:

        signal = "NO TRADE"

        decision = "ESPERAR"

        up = 50

        down = 50

        signal_class = "neutral"

        icon = "⚪"

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
        "up": up,
        "down": down,
        "signal_class": signal_class,
        "icon": icon,
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
# CARGAR DATOS
# =========================================================

btc_ok = False

btc_error = ""

kalshi_ok = False

kalshi_error = ""

market = None


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
        "up": 50,
        "down": 50,
        "signal_class": "neutral",
        "icon": "⚪",
        "ema": "SIN DATOS",
        "rsi": 50.0,
        "mom3": 0.0,
        "mom5": 0.0,
        "mom15": 0.0,
        "vol_ratio": 0.0,
        "volatility": "SIN DATOS",
        "momentum": "MOMENTUM NEUTRAL"
    }


try:

    market = (
        get_kalshi_btc_market()
    )

    kalshi_ok = (
        market is not None
    )

except Exception as error:

    kalshi_error = str(error)


# =========================================================
# DATOS KALSHI
# =========================================================

if market:

    ticker = market.get(
        "ticker",
        "--"
    )

    # Compatibilidad con campos nuevos y anteriores
    yes_bid_dollars = market.get(
        "yes_bid_dollars"
    )

    yes_ask_dollars = market.get(
        "yes_ask_dollars"
    )

    last_dollars = market.get(
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

    last_dollars = None

    yes_bid = None

    yes_ask = None

    last_price = None


def kalshi_price(
    dollar_value,
    cent_value
):

    if dollar_value not in [
        None,
        ""
    ]:

        try:

            return (
                f"${float(dollar_value):.2f}"
            )

        except:

            return str(
                dollar_value
            )

    if cent_value is not None:

        try:

            return (
                f"{float(cent_value):g}¢"
            )

        except:

            return str(
                cent_value
            )

    return "--"


kalshi_bid_display = kalshi_price(
    yes_bid_dollars,
    yes_bid
)

kalshi_ask_display = kalshi_price(
    yes_ask_dollars,
    yes_ask
)

kalshi_last_display = kalshi_price(
    last_dollars,
    last_price
)


if kalshi_ok:

    kalshi_status = (
        "CONECTADO 🟢"
    )

else:

    kalshi_status = (
        "SIN MERCADO ⚠️"
    )


# =========================================================
# COLORES
# =========================================================

if sig["signal_class"] == "up":

    signal_color = "#34d399"

elif sig["signal_class"] == "down":

    signal_color = "#fb7185"

else:

    signal_color = "#a7b0c0"


if "ALCISTA" in sig["momentum"]:

    momentum_color = "#34d399"

elif "BAJISTA" in sig["momentum"]:

    momentum_color = "#fb7185"

else:

    momentum_color = "#fbbf24"


# =========================================================
# INTERFAZ
# =========================================================

st.markdown(
    """
    <div style="
        background:#111a2e;
        border:1px solid #2563eb;
        border-radius:18px;
        padding:18px;
        text-align:center;
        color:#38bdf8;
        font-weight:900;
        letter-spacing:3px;
        margin-bottom:12px;
    ">
        ⚡ MACALY + ALPHA BOT • v4.1
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    f"""
    <div style="
        background:#11161f;
        border:1px solid #334155;
        border-radius:18px;
        padding:22px;
        text-align:center;
        margin-bottom:12px;
    ">

        <div style="
            color:#94a3b8;
            font-size:13px;
            font-weight:800;
            letter-spacing:3px;
        ">
            SEÑAL TÉCNICA BTC
        </div>

        <div style="
            color:{signal_color};
            font-size:30px;
            font-weight:900;
            margin-top:12px;
        ">
            {sig["icon"]}
            {sig["signal"]}
        </div>

        <div style="
            color:#cbd5e1;
            font-size:19px;
            margin-top:8px;
        ">
            BTC ${sig["price"]:,.2f}
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


col1, col2 = st.columns(2)


with col1:

    st.markdown(
        f"""
        <div style="
            background:#073326;
            border:1px solid #10b981;
            border-radius:18px;
            padding:20px 8px;
            text-align:center;
            color:#34d399;
            font-weight:900;
        ">
            UP
            <div style="
                font-size:34px;
                margin-top:5px;
            ">
                {sig["up"]}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div style="
            background:#35171d;
            border:1px solid #ef4444;
            border-radius:18px;
            padding:20px 8px;
            text-align:center;
            color:#fb7185;
            font-weight:900;
        ">
            DOWN
            <div style="
                font-size:34px;
                margin-top:5px;
            ">
                {sig["down"]}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown("<br>", unsafe_allow_html=True)


st.markdown(
    f"""
    <div style="
        background:#11161f;
        border:1px solid #334155;
        border-radius:18px;
        padding:20px;
        text-align:center;
        margin-bottom:12px;
    ">

        <div style="
            color:#94a3b8;
            font-size:13px;
            font-weight:800;
            letter-spacing:3px;
        ">
            MOMENTUM
        </div>

        <div style="
            color:{momentum_color};
            font-size:21px;
            font-weight:900;
            margin-top:12px;
        ">
            {sig["momentum"]}
        </div>

        <div style="
            color:#64748b;
            margin-top:7px;
        ">
            3 min:
            {sig["mom3"]:+.3f}%
            &nbsp; • &nbsp;
            15 min:
            {sig["mom15"]:+.3f}%
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# INDICADORES VISUALES
# =========================================================

st.markdown(
    f"""
    <div style="
        background:#11161f;
        border:1px solid #334155;
        border-radius:18px;
        padding:20px;
        margin-bottom:12px;
    ">

        <div style="
            text-align:center;
            color:#94a3b8;
            font-size:13px;
            font-weight:800;
            letter-spacing:3px;
            margin-bottom:15px;
        ">
            INDICADORES
        </div>

        <div>
            EMA 9 / 21:
            <b>{sig["ema"]}</b>
        </div>

        <hr>

        <div>
            RSI 14:
            <b>{sig["rsi"]:.1f}</b>
        </div>

        <hr>

        <div>
            Momentum 5m:
            <b>{sig["mom5"]:+.3f}%</b>
        </div>

        <hr>

        <div>
            Volumen:
            <b>{sig["vol_ratio"]:.2f}x</b>
        </div>

        <hr>

        <div>
            Volatilidad:
            <b>{sig["volatility"]}</b>
        </div>

        <hr>

        <div>
            Coinbase:
            <b>
                {"CONECTADO 🟢" if btc_ok else "SIN CONEXIÓN 🔴"}
            </b>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# KALSHI VISUAL
# =========================================================

st.markdown(
    f"""
    <div style="
        background:#11161f;
        border:1px solid #334155;
        border-radius:18px;
        padding:20px;
        margin-bottom:12px;
    ">

        <div style="
            text-align:center;
            color:#94a3b8;
            font-size:13px;
            font-weight:800;
            letter-spacing:3px;
            margin-bottom:15px;
        ">
            KALSHI • BTC 15 MIN
        </div>

        <div style="
            text-align:center;
            font-weight:900;
            margin-bottom:15px;
        ">
            {
                "Mercado encontrado"
                if kalshi_ok
                else
                "No se encontró mercado BTC 15m"
            }
        </div>

        <div>
            Ticker:
            <b>{ticker}</b>
        </div>

        <hr>

        <div>
            YES bid:
            <b>{kalshi_bid_display}</b>
        </div>

        <hr>

        <div>
            YES ask:
            <b>{kalshi_ask_display}</b>
        </div>

        <hr>

        <div>
            Último:
            <b>{kalshi_last_display}</b>
        </div>

        <hr>

        <div>
            API Kalshi:
            <b>{kalshi_status}</b>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DECISIÓN
# =========================================================

st.markdown(
    f"""
    <div style="
        background:#11161f;
        border:1px solid #334155;
        border-radius:18px;
        padding:22px;
        text-align:center;
        margin-bottom:12px;
    ">

        <div style="
            color:#94a3b8;
            font-size:13px;
            font-weight:800;
            letter-spacing:3px;
        ">
            DECISIÓN DEL MOTOR
        </div>

        <div style="
            color:{signal_color};
            font-size:28px;
            font-weight:900;
            margin-top:12px;
        ">
            {sig["decision"]}
        </div>

        <div style="
            color:#64748b;
            margin-top:10px;
        ">
            Score técnico:
            {sig["score"]:.2f}
        </div>

        <div style="
            color:#64748b;
            font-size:12px;
            line-height:1.5;
            margin-top:15px;
        ">
            Actualización aproximada: 15 segundos.
            <br>
            Modo análisis / paper.
            No envía órdenes reales.
            <br>
            UP/DOWN es un score técnico experimental;
            no representa la probabilidad de Kalshi.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ERRORES
# =========================================================

if btc_error:

    st.error(
        "Error Coinbase: "
        + btc_error
    )


if kalshi_error:

    st.error(
        "Error Kalshi: "
        + kalshi_error
    )
