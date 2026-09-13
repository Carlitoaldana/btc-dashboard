import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone

# =========================================================
# MACALY + ALPHA BOT v4.4
# BTC 15 MIN + TARGET AUTO + COUNTDOWN
# =========================================================

st.set_page_config(
    page_title="Macaly + Alpha Bot v4.4",
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
    letter-spacing:2px;
}

.bot-label {
    text-align:center;
    color:#94a3b8;
    font-size:13px;
    font-weight:800;
    letter-spacing:2px;
    margin-bottom:12px;
}

.bot-row {
    display:flex;
    justify-content:space-between;
    gap:12px;
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

.target-box {
    background:#101827;
    border:1px solid #475569;
    border-radius:16px;
    padding:15px;
    margin-bottom:12px;
    text-align:center;
}

.small-note {
    color:#64748b;
    font-size:12px;
    line-height:1.5;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# COINBASE
# =========================================================

@st.cache_data(ttl=2)
def get_btc_data():

    url = (
        "https://api.exchange.coinbase.com/"
        "products/BTC-USD/candles"
    )

    response = requests.get(
        url,
        params={"granularity": 60},
        headers={"User-Agent": "MacalyAlphaBot/4.4"},
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list) or len(data) < 30:
        raise ValueError("Coinbase no devolvió suficientes datos.")

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

    return (
        df.dropna()
        .sort_values("time")
        .reset_index(drop=True)
    )


# =========================================================
# KALSHI BTC 15 MIN
# =========================================================

@st.cache_data(ttl=2)
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
        headers={"User-Agent": "MacalyAlphaBot/4.4"},
        timeout=10
    )

    response.raise_for_status()

    markets = response.json().get(
        "markets",
        []
    )

    if not markets:
        return None

    # Elegir la ronda BTC 15m que cierra primero.
    markets.sort(
        key=lambda m: str(
            m.get("close_time") or "9999"
        )
    )

    return markets[0]


# =========================================================
# INDICADORES
# =========================================================

def add_indicators(df):

    df = df.copy()

    close = df["close"]

    df["ema9"] = close.ewm(
        span=9,
        adjust=False
    ).mean()

    df["ema21"] = close.ewm(
        span=21,
        adjust=False
    ).mean()

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

    df["mom3"] = close.pct_change(3) * 100
    df["mom5"] = close.pct_change(5) * 100
    df["mom15"] = close.pct_change(15) * 100

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
# TARGET AUTOMÁTICO
# =========================================================

def get_target_from_market(market):

    if not market:
        return None

    strike_type = str(
        market.get("strike_type") or ""
    ).lower()

    floor_strike = market.get(
        "floor_strike"
    )

    cap_strike = market.get(
        "cap_strike"
    )

    # Contratos de tipo "greater" / arriba de un precio.
    if floor_strike not in [None, ""]:

        try:
            floor_value = float(floor_strike)

            if floor_value > 1000:
                return floor_value

        except Exception:
            pass

    # Fallback solamente si el contrato usa cap strike.
    if cap_strike not in [None, ""]:

        try:
            cap_value = float(cap_strike)

            if cap_value > 1000:
                return cap_value

        except Exception:
            pass

    # No inventamos un target.
    return None


# =========================================================
# COUNTDOWN
# =========================================================

def get_seconds_remaining(market):

    if not market:
        return None

    close_time = market.get(
        "close_time"
    )

    if not close_time:
        return None

    try:

        close_dt = datetime.fromisoformat(
            str(close_time).replace(
                "Z",
                "+00:00"
            )
        )

        now = datetime.now(
            timezone.utc
        )

        seconds = int(
            (
                close_dt -
                now
            ).total_seconds()
        )

        return max(
            0,
            seconds
        )

    except Exception:
        return None


def format_countdown(seconds):

    if seconds is None:
        return "--:--"

    minutes = seconds // 60
    secs = seconds % 60

    return f"{minutes:02d}:{secs:02d}"


# =========================================================
# KALSHI PRICE
# =========================================================

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

        except Exception:
            return str(dollar_value)

    if cent_value is not None:

        try:
            return (
                f"${float(cent_value) / 100:.2f}"
            )

        except Exception:
            return str(cent_value)

    return "--"


# =========================================================
# MOTOR v4.4
# =========================================================

def build_signal(
    df,
    target,
    seconds_left
):

    last = df.iloc[-1]

    price = float(
        last["close"]
    )

    rsi = float(
        last["rsi"]
    )

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

    vol_ratio = (
        float(last["vol_ratio"])
        if pd.notna(last["vol_ratio"])
        else 0.0
    )

    technical_score = 0.0

    # EMA
    if last["ema9"] > last["ema21"]:

        technical_score += 2.0
        ema_text = "ALCISTA 🚀"

    else:

        technical_score -= 2.0
        ema_text = "BAJISTA 🔻"

    # RSI
    if rsi >= 55:
        technical_score += 1.0

    elif rsi <= 45:
        technical_score -= 1.0

    # Momentum corto
    if mom3 > 0.02:
        technical_score += 1.25

    elif mom3 < -0.02:
        technical_score -= 1.25

    if mom5 > 0.03:
        technical_score += 1.0

    elif mom5 < -0.03:
        technical_score -= 1.0

    if mom15 > 0.05:
        technical_score += 0.75

    elif mom15 < -0.05:
        technical_score -= 0.75

    # Volumen confirma dirección
    if vol_ratio > 1.20:

        if mom3 > 0:
            technical_score += 0.50

        elif mom3 < 0:
            technical_score -= 0.50

    # =====================================================
    # TARGET
    # =====================================================

    distance = None
    distance_pct = None

    target_score = 0.0

    if target is not None:

        distance = (
            price -
            target
        )

        distance_pct = (
            distance /
            target *
            100
        )

        # Peso base por estar arriba/abajo.
        if distance > 0:
            target_score += 2.0

        elif distance < 0:
            target_score -= 2.0

        # Cuanto más cerca del cierre,
        # más importante es la posición frente al target.
        if seconds_left is not None:

            abs_distance = abs(
                distance
            )

            if seconds_left <= 30:

                if distance > 0:
                    target_score += 4.0

                elif distance < 0:
                    target_score -= 4.0

            elif seconds_left <= 60:

                if distance > 0:
                    target_score += 3.0

                elif distance < 0:
                    target_score -= 3.0

            elif seconds_left <= 180:

                if distance > 0:
                    target_score += 2.0

                elif distance < 0:
                    target_score -= 2.0

            elif seconds_left <= 300:

                if distance > 0:
                    target_score += 1.0

                elif distance < 0:
                    target_score -= 1.0

            # Muy cerca del target = más incertidumbre.
            if abs_distance < 10:
                target_score *= 0.60

            elif abs_distance < 20:
                target_score *= 0.80

    final_score = (
        technical_score +
        target_score
    )

    # =====================================================
    # DECISIÓN
    # =====================================================

    if target is None:

        decision = "NO TRADE"
        signal = "TARGET NO DISPONIBLE"
        icon = "⚠️"
        color = "#fbbf24"

    elif (
        seconds_left is not None
        and
        seconds_left <= 15
        and
        abs(distance) < 20
    ):

        decision = "NO TRADE"
        signal = "DEMASIADO CERRADO"
        icon = "⚠️"
        color = "#fbbf24"

    elif final_score >= 4:

        decision = "POSIBLE UP"
        signal = "SEÑAL UP"
        icon = "🚀"
        color = "#34d399"

    elif final_score <= -4:

        decision = "POSIBLE DOWN"
        signal = "SEÑAL DOWN"
        icon = "🔻"
        color = "#fb7185"

    else:

        decision = "NO TRADE"
        signal = "ESPERAR"
        icon = "⚪"
        color = "#fbbf24"

    # Momentum visual
    if mom3 > 0.02:
        momentum = "ALCISTA"

    elif mom3 < -0.02:
        momentum = "BAJISTA"

    else:
        momentum = "NEUTRAL"

    return {
        "price": price,
        "rsi": rsi,
        "mom3": mom3,
        "mom5": mom5,
        "mom15": mom15,
        "vol_ratio": vol_ratio,
        "ema": ema_text,
        "technical_score": technical_score,
        "target_score": target_score,
        "final_score": final_score,
        "distance": distance,
        "distance_pct": distance_pct,
        "decision": decision,
        "signal": signal,
        "icon": icon,
        "color": color,
        "momentum": momentum
    }


# =========================================================
# TÍTULO
# =========================================================

st.markdown(
    '<div class="bot-title">⚡ MACALY + ALPHA BOT • v4.4</div>',
    unsafe_allow_html=True
)


# =========================================================
# DASHBOARD LIVE
# =========================================================

@st.fragment(run_every="3s")
def live_dashboard():

    btc_error = ""
    kalshi_error = ""

    # =====================================================
    # BTC
    # =====================================================

    try:

        btc_df = get_btc_data()

        btc_df = add_indicators(
            btc_df
        )

        btc_ok = True

    except Exception as error:

        btc_ok = False
        btc_error = str(error)
        btc_df = None

    # =====================================================
    # KALSHI
    # =====================================================

    try:

        market = get_kalshi_btc_market()

        kalshi_ok = (
            market is not None
        )

    except Exception as error:

        kalshi_ok = False
        kalshi_error = str(error)
        market = None

    # =====================================================
    # MARKET INFO
    # =====================================================

    if market:

        ticker = market.get(
            "ticker",
            "--"
        )

        target = get_target_from_market(
            market
        )

        seconds_left = (
            get_seconds_remaining(
                market
            )
        )

        countdown = (
            format_countdown(
                seconds_left
            )
        )

        yes_bid_display = kalshi_price(
            market.get("yes_bid_dollars"),
            market.get("yes_bid")
        )

        yes_ask_display = kalshi_price(
            market.get("yes_ask_dollars"),
            market.get("yes_ask")
        )

        last_display = kalshi_price(
            market.get("last_price_dollars"),
            market.get("last_price")
        )

    else:

        ticker = "--"
        target = None
        seconds_left = None
        countdown = "--:--"

        yes_bid_display = "--"
        yes_ask_display = "--"
        last_display = "--"

    # =====================================================
    # SIGNAL
    # =====================================================

    if btc_ok:

        sig = build_signal(
            btc_df,
            target,
            seconds_left
        )

    else:

        sig = {
            "price": 0,
            "rsi": 50,
            "mom3": 0,
            "mom5": 0,
            "mom15": 0,
            "vol_ratio": 0,
            "ema": "SIN DATOS",
            "technical_score": 0,
            "target_score": 0,
            "final_score": 0,
            "distance": None,
            "distance_pct": None,
            "decision": "NO TRADE",
            "signal": "SIN DATOS",
            "icon": "⚠️",
            "color": "#fbbf24",
            "momentum": "NEUTRAL"
        }

    # =====================================================
    # PRINCIPAL
    # =====================================================

    main_html = (
        '<div class="bot-card" style="text-align:center;">'
        '<div class="bot-label">BITCOIN • KALSHI 15 MIN</div>'
        f'<div style="font-size:30px;font-weight:900;color:{sig["color"]};">'
        f'{sig["icon"]} {sig["decision"]}'
        '</div>'
        f'<div style="font-size:19px;margin-top:8px;color:#e2e8f0;">'
        f'BTC ${sig["price"]:,.2f}'
        '</div>'
        '</div>'
    )

    st.markdown(
        main_html,
        unsafe_allow_html=True
    )

    # =====================================================
    # TARGET
    # =====================================================

    if target is not None:

        target_text = (
            f"${target:,.2f}"
        )

    else:

        target_text = (
            "NO DISPONIBLE"
        )

    if sig["distance"] is not None:

        distance = sig["distance"]

        if distance > 0:

            distance_text = (
                f"+${abs(distance):,.2f} ARRIBA"
            )

            distance_color = (
                "#34d399"
            )

        elif distance < 0:

            distance_text = (
                f"-${abs(distance):,.2f} ABAJO"
            )

            distance_color = (
                "#fb7185"
            )

        else:

            distance_text = (
                "$0.00"
            )

            distance_color = (
                "#fbbf24"
            )

    else:

        distance_text = "--"
        distance_color = "#94a3b8"

    target_html = (
        '<div class="bot-card">'
        '<div class="bot-label">RONDA ACTUAL</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Target</span>'
        f'<span class="bot-right">{target_text}</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">BTC actual</span>'
        f'<span class="bot-right">${sig["price"]:,.2f}</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Distancia</span>'
        f'<span class="bot-right" style="color:{distance_color};">'
        f'{distance_text}'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Tiempo restante</span>'
        f'<span class="bot-right">{countdown}</span>'
        '</div>'

        '</div>'
    )

    st.markdown(
        target_html,
        unsafe_allow_html=True
    )

    # =====================================================
    # KALSHI
    # =====================================================

    kalshi_status = (
        "CONECTADO 🟢"
        if kalshi_ok
        else
        "SIN MERCADO ⚠️"
    )

    kalshi_html = (
        '<div class="bot-card">'
        '<div class="bot-label">KALSHI • BTC 15 MIN</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Ticker</span>'
        f'<span class="bot-right">{ticker}</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">YES bid</span>'
        f'<span class="bot-right">{yes_bid_display}</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">YES ask</span>'
        f'<span class="bot-right">{yes_ask_display}</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Último</span>'
        f'<span class="bot-right">{last_display}</span>'
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
    # INDICADORES
    # =====================================================

    coinbase_status = (
        "CONECTADO 🟢"
        if btc_ok
        else
        "SIN CONEXIÓN 🔴"
    )

    indicators_html = (
        '<div class="bot-card">'
        '<div class="bot-label">ANÁLISIS TÉCNICO</div>'

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
    # DECISIÓN
    # =====================================================

    decision_html = (
        '<div class="bot-card" style="text-align:center;">'
        '<div class="bot-label">DECISIÓN DEL MOTOR</div>'

        f'<div style="font-size:27px;font-weight:900;color:{sig["color"]};">'
        f'{sig["signal"]}'
        '</div>'

        '<div style="margin-top:12px;color:#94a3b8;">'
        f'Score técnico: {sig["technical_score"]:.2f}'
        '<br>'
        f'Score target/tiempo: {sig["target_score"]:.2f}'
        '<br>'
        f'Score combinado: {sig["final_score"]:.2f}'
        '</div>'

        '<div class="small-note" style="margin-top:16px;">'
        'Actualización automática cada 3 segundos 🔄'
        '<br>'
        'Siempre BTC 15 min'
        '<br>'
        'Modo análisis / paper'
        '<br>'
        'No envía órdenes reales'
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

    if target is None and kalshi_ok:

        st.warning(
            "Kalshi está conectado, pero esta ronda no "
            "entregó un strike numérico utilizable como "
            "target. El bot NO inventará uno."
        )

    if btc_error:

        st.error(
            "Error Coinbase: " +
            btc_error
        )

    if kalshi_error:

        st.error(
            "Error Kalshi: " +
            kalshi_error
        )


# =========================================================
# INICIAR
# =========================================================

live_dashboard()
