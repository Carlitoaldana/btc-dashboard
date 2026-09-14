import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone

# =========================================================
# MACALY + ALPHA BOT v4.6
# BTC 15 MIN
# ROUND MEMORY + PROBABILITY + REVERSAL WATCH
# =========================================================

st.set_page_config(
    page_title="Macaly + Alpha Bot v4.6",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CONFIGURACIÓN
# =========================================================

NEW_ROUND_WAIT = 30
NEW_ENTRY_LOCK = 75

UP_THRESHOLD = 4.0
DOWN_THRESHOLD = -4.0

# Para cambiar una señal ya activa a la contraria,
# exigimos más confirmación que para crear la primera.
FLIP_UP_THRESHOLD = 4.75
FLIP_DOWN_THRESHOLD = -4.75
FLIP_CONFIRMATIONS = 2

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

.small-note {
    color:#64748b;
    font-size:12px;
    line-height:1.5;
    text-align:center;
}

.prob-box {
    background:#0d1420;
    border:1px solid #334155;
    border-radius:14px;
    padding:14px;
    margin-top:12px;
}

.warning-box {
    background:#2a2110;
    border:1px solid #f59e0b;
    border-radius:14px;
    padding:14px;
    margin-top:12px;
    color:#fbbf24;
    text-align:center;
    font-weight:800;
}

.round-box {
    background:#0f172a;
    border:1px solid #38bdf8;
    border-radius:14px;
    padding:12px;
    margin-bottom:12px;
    text-align:center;
    color:#7dd3fc;
    font-weight:800;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================

if "rounds" not in st.session_state:
    st.session_state.rounds = {}

if "active_ticker" not in st.session_state:
    st.session_state.active_ticker = None


def new_round_state(ticker, seconds_left):

    now = datetime.now(timezone.utc)

    return {
        "ticker": ticker,
        "detected_at": now,
        "detected_seconds_left": seconds_left,

        "first_direction": None,
        "first_signal_time": None,
        "first_signal_seconds": None,
        "first_signal_price": None,

        "active_direction": None,
        "active_since": None,

        "last_score": 0.0,
        "previous_score": 0.0,

        "opposite_count": 0,

        "last_live_price": None,
        "previous_live_price": None,

        "reversal_warning": False,
        "reversal_text": "",
    }


# =========================================================
# COINBASE - VELAS PARA INDICADORES
# =========================================================

@st.cache_data(ttl=5)
def get_btc_data():

    url = (
        "https://api.exchange.coinbase.com/"
        "products/BTC-USD/candles"
    )

    response = requests.get(
        url,
        params={"granularity": 60},
        headers={"User-Agent": "MacalyAlphaBot/4.6"},
        timeout=10
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

    return (
        df.dropna()
        .sort_values("time")
        .reset_index(drop=True)
    )


# =========================================================
# COINBASE - PRECIO BTC LIVE
# =========================================================

def get_btc_live_price():

    url = (
        "https://api.exchange.coinbase.com/"
        "products/BTC-USD/ticker"
    )

    response = requests.get(
        url,
        headers={
            "User-Agent": "MacalyAlphaBot/4.6",
            "Cache-Control": "no-cache"
        },
        params={
            "_": int(
                datetime.now(timezone.utc).timestamp()
            )
        },
        timeout=6
    )

    response.raise_for_status()

    data = response.json()

    price = data.get("price")

    if price in [None, ""]:
        raise ValueError(
            "Coinbase ticker no devolvió precio."
        )

    return float(price)


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
        headers={"User-Agent": "MacalyAlphaBot/4.6"},
        timeout=10
    )

    response.raise_for_status()

    markets = response.json().get(
        "markets",
        []
    )

    if not markets:
        return None

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
# TARGET
# =========================================================

def get_target_from_market(market):

    if not market:
        return None

    floor_strike = market.get(
        "floor_strike"
    )

    cap_strike = market.get(
        "cap_strike"
    )

    if floor_strike not in [None, ""]:

        try:

            floor_value = float(
                floor_strike
            )

            if floor_value > 1000:
                return floor_value

        except Exception:
            pass

    if cap_strike not in [None, ""]:

        try:

            cap_value = float(
                cap_strike
            )

            if cap_value > 1000:
                return cap_value

        except Exception:
            pass

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
# PRECIOS KALSHI
# =========================================================

def numeric_kalshi_price(
    dollar_value,
    cent_value
):

    if dollar_value not in [None, ""]:

        try:
            return float(dollar_value)
        except Exception:
            pass

    if cent_value not in [None, ""]:

        try:
            return float(cent_value) / 100
        except Exception:
            pass

    return None


def kalshi_price(
    dollar_value,
    cent_value
):

    value = numeric_kalshi_price(
        dollar_value,
        cent_value
    )

    if value is None:
        return "--"

    return f"${value:.2f}"


def get_yes_ask(market):

    if not market:
        return None

    return numeric_kalshi_price(
        market.get("yes_ask_dollars"),
        market.get("yes_ask")
    )


def get_no_ask(market):

    if not market:
        return None

    direct = numeric_kalshi_price(
        market.get("no_ask_dollars"),
        market.get("no_ask")
    )

    if direct is not None:
        return direct

    yes_bid = numeric_kalshi_price(
        market.get("yes_bid_dollars"),
        market.get("yes_bid")
    )

    if yes_bid is not None:
        return max(
            0.0,
            min(
                1.0,
                1.0 - yes_bid
            )
        )

    return None


# =========================================================
# PROBABILIDAD ESTIMADA DEL MOTOR
# =========================================================

def estimated_probabilities(
    final_score,
    distance,
    seconds_left,
    mom3,
    mom5
):

    # Esta NO es una probabilidad garantizada.
    # Es una estimación interna basada en la fuerza
    # de los factores del motor.

    score = float(
        np.clip(
            final_score,
            -10,
            10
        )
    )

    up_prob = (
        50 +
        score * 4.2
    )

    # Pequeño ajuste por aceleración reciente.
    if mom3 > 0.04:
        up_prob += 3

    elif mom3 < -0.04:
        up_prob -= 3

    if mom5 > 0.06:
        up_prob += 2

    elif mom5 < -0.06:
        up_prob -= 2

    # Cerca del cierre, la posición respecto
    # al target pesa más.
    if (
        distance is not None
        and
        seconds_left is not None
        and
        seconds_left <= 180
    ):

        if distance > 0:
            up_prob += 3

        elif distance < 0:
            up_prob -= 3

    # Nunca mostramos 100/0.
    up_prob = float(
        np.clip(
            up_prob,
            5,
            95
        )
    )

    down_prob = 100 - up_prob

    return (
        round(up_prob),
        round(down_prob)
    )


# =========================================================
# MOTOR BASE v4.6
# =========================================================

def build_signal(
    df,
    target,
    seconds_left,
    live_price=None
):

    last = df.iloc[-1]

    candle_price = float(
        last["close"]
    )

    if live_price is not None:
        price = float(live_price)
    else:
        price = candle_price

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

    # MOMENTUM
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

    # VOLUMEN
    if vol_ratio > 1.20:

        if mom3 > 0:
            technical_score += 0.50

        elif mom3 < 0:
            technical_score -= 0.50

    # =====================================================
    # TARGET / TIEMPO
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

        if distance > 0:
            target_score += 2.0

        elif distance < 0:
            target_score -= 2.0

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

            if abs_distance < 10:
                target_score *= 0.60

            elif abs_distance < 20:
                target_score *= 0.80

    final_score = (
        technical_score +
        target_score
    )

    if mom3 > 0.02:
        momentum = "ALCISTA"

    elif mom3 < -0.02:
        momentum = "BAJISTA"

    else:
        momentum = "NEUTRAL"

    up_probability, down_probability = (
        estimated_probabilities(
            final_score,
            distance,
            seconds_left,
            mom3,
            mom5
        )
    )

    return {
        "price": price,
        "candle_price": candle_price,
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
        "momentum": momentum,
        "up_probability": up_probability,
        "down_probability": down_probability
    }


# =========================================================
# CALIDAD DE ENTRADA
# =========================================================

def entry_quality(price, seconds_left):

    if price is None:
        return (
            "PRECIO NO DISPONIBLE",
            "#94a3b8"
        )

    if (
        seconds_left is not None
        and
        seconds_left <= NEW_ENTRY_LOCK
    ):
        return (
            "TARDE ⏰",
            "#fb7185"
        )

    if price <= 0.60:
        return (
            "BUENA 🟢",
            "#34d399"
        )

    if price <= 0.70:
        return (
            "PRECAUCIÓN 🟡",
            "#fbbf24"
        )

    return (
        "CARA / TARDE 🔴",
        "#fb7185"
    )


# =========================================================
# CONTROL DE RONDA + SEÑAL
# =========================================================

def process_round_signal(
    ticker,
    sig,
    market,
    seconds_left
):

    now = datetime.now(
        timezone.utc
    )

    # -----------------------------------------------------
    # NUEVO TICKER = NUEVA RONDA
    # -----------------------------------------------------

    if (
        ticker
        and
        ticker != "--"
        and
        st.session_state.active_ticker != ticker
    ):

        st.session_state.active_ticker = ticker

        st.session_state.rounds[ticker] = (
            new_round_state(
                ticker,
                seconds_left
            )
        )

    if (
        not ticker
        or
        ticker == "--"
    ):

        return {
            "decision": "NO TRADE",
            "signal": "SIN RONDA",
            "icon": "⚠️",
            "color": "#fbbf24",
            "round_state": None,
            "reversal": False,
            "reversal_text": "",
            "entry_price": None,
            "entry_quality": "SIN DATOS",
            "entry_quality_color": "#94a3b8"
        }

    if ticker not in st.session_state.rounds:

        st.session_state.rounds[ticker] = (
            new_round_state(
                ticker,
                seconds_left
            )
        )

    state = st.session_state.rounds[
        ticker
    ]

    # -----------------------------------------------------
    # TIEMPO TRANSCURRIDO DESDE QUE DETECTAMOS RONDA
    # -----------------------------------------------------

    age = (
        now -
        state["detected_at"]
    ).total_seconds()

    score = sig["final_score"]

    # -----------------------------------------------------
    # PRECIO ACTUAL PARA DETECTAR ACELERACIÓN
    # -----------------------------------------------------

    previous_live_price = (
        state["last_live_price"]
    )

    state["previous_live_price"] = (
        previous_live_price
    )

    state["last_live_price"] = (
        sig["price"]
    )

    price_change = 0.0

    if previous_live_price is not None:

        price_change = (
            sig["price"] -
            previous_live_price
        )

    previous_score = (
        state["last_score"]
    )

    state["previous_score"] = (
        previous_score
    )

    score_change = (
        score -
        previous_score
    )

    state["last_score"] = score

    # -----------------------------------------------------
    # NUEVA RONDA
    # -----------------------------------------------------

    if age < NEW_ROUND_WAIT:

        state["reversal_warning"] = False
        state["reversal_text"] = ""

        return {
            "decision": "ANALIZANDO NUEVA RONDA",
            "signal": "ESPERANDO CONFIRMACIÓN",
            "icon": "⏳",
            "color": "#38bdf8",
            "round_state": state,
            "reversal": False,
            "reversal_text": "",
            "entry_price": None,
            "entry_quality": "ESPERANDO",
            "entry_quality_color": "#38bdf8"
        }

    # -----------------------------------------------------
    # BLOQUEO DE NUEVA ENTRADA CERCA DEL FINAL
    # -----------------------------------------------------

    lock_new_entries = (
        seconds_left is not None
        and
        seconds_left <= NEW_ENTRY_LOCK
    )

    # -----------------------------------------------------
    # DIRECCIÓN CANDIDATA
    # -----------------------------------------------------

    candidate = None

    if score >= UP_THRESHOLD:
        candidate = "UP"

    elif score <= DOWN_THRESHOLD:
        candidate = "DOWN"

    # -----------------------------------------------------
    # PRIMERA SEÑAL DE LA RONDA
    # -----------------------------------------------------

    if (
        state["active_direction"] is None
        and
        candidate is not None
        and
        not lock_new_entries
    ):

        direction_price = (
            get_yes_ask(market)
            if candidate == "UP"
            else get_no_ask(market)
        )

        state["active_direction"] = (
            candidate
        )

        state["active_since"] = now

        state["first_direction"] = (
            candidate
        )

        state["first_signal_time"] = (
            now
        )

        state["first_signal_seconds"] = (
            seconds_left
        )

        state["first_signal_price"] = (
            direction_price
        )

        state["opposite_count"] = 0

    # -----------------------------------------------------
    # DETECTOR DE PÉRDIDA DE FUERZA / REVERSIÓN
    # -----------------------------------------------------

    active = state[
        "active_direction"
    ]

    reversal = False
    reversal_text = ""

    if active == "UP":

        weakness_points = 0

        # Score se deteriora.
        if score < 3:
            weakness_points += 1

        if score_change <= -1.25:
            weakness_points += 1

        # Momentum corto cambia contra UP.
        if sig["mom3"] < -0.02:
            weakness_points += 1

        if sig["mom5"] < 0:
            weakness_points += 1

        # Precio live cae entre evaluaciones.
        if price_change < -8:
            weakness_points += 1

        # Cerca del target y cayendo al final.
        if (
            sig["distance"] is not None
            and
            seconds_left is not None
            and
            seconds_left <= 180
            and
            sig["distance"] < 25
            and
            price_change < 0
        ):
            weakness_points += 1

        if weakness_points >= 2:

            reversal = True
            reversal_text = (
                "UP PERDIENDO FUERZA • "
                "POSIBLE REVERSIÓN A DOWN"
            )

    elif active == "DOWN":

        weakness_points = 0

        if score > -3:
            weakness_points += 1

        if score_change >= 1.25:
            weakness_points += 1

        if sig["mom3"] > 0.02:
            weakness_points += 1

        if sig["mom5"] > 0:
            weakness_points += 1

        if price_change > 8:
            weakness_points += 1

        if (
            sig["distance"] is not None
            and
            seconds_left is not None
            and
            seconds_left <= 180
            and
            sig["distance"] > -25
            and
            price_change > 0
        ):
            weakness_points += 1

        if weakness_points >= 2:

            reversal = True
            reversal_text = (
                "DOWN PERDIENDO FUERZA • "
                "POSIBLE REBOTE A UP"
            )

    state["reversal_warning"] = (
        reversal
    )

    state["reversal_text"] = (
        reversal_text
    )

    # -----------------------------------------------------
    # CONFIRMACIÓN PARA CAMBIAR DIRECCIÓN
    # -----------------------------------------------------

    if active == "UP":

        if (
            score <= FLIP_DOWN_THRESHOLD
            and
            sig["mom3"] < 0
        ):

            state["opposite_count"] += 1

        else:

            state["opposite_count"] = 0

        if (
            state["opposite_count"]
            >= FLIP_CONFIRMATIONS
        ):

            # En últimos segundos NO lo mostramos como
            # una nueva entrada. Solo como reversión.
            if not lock_new_entries:

                state["active_direction"] = (
                    "DOWN"
                )

                state["active_since"] = now

            state["opposite_count"] = 0

    elif active == "DOWN":

        if (
            score >= FLIP_UP_THRESHOLD
            and
            sig["mom3"] > 0
        ):

            state["opposite_count"] += 1

        else:

            state["opposite_count"] = 0

        if (
            state["opposite_count"]
            >= FLIP_CONFIRMATIONS
        ):

            if not lock_new_entries:

                state["active_direction"] = (
                    "UP"
                )

                state["active_since"] = now

            state["opposite_count"] = 0

    active = state[
        "active_direction"
    ]

    # -----------------------------------------------------
    # SALIDA VISUAL
    # -----------------------------------------------------

    if active == "UP":

        decision = "POSIBLE UP"
        signal = "SEÑAL UP"
        icon = "🚀"
        color = "#34d399"

        current_entry_price = (
            get_yes_ask(market)
        )

    elif active == "DOWN":

        decision = "POSIBLE DOWN"
        signal = "SEÑAL DOWN"
        icon = "🔻"
        color = "#fb7185"

        current_entry_price = (
            get_no_ask(market)
        )

    else:

        current_entry_price = None

        if lock_new_entries:

            decision = "NO NUEVA ENTRADA"
            signal = "FINAL DE RONDA"
            icon = "⏰"
            color = "#fbbf24"

        else:

            decision = "NO TRADE"
            signal = "ESPERAR"
            icon = "⚪"
            color = "#fbbf24"

    quality, quality_color = (
        entry_quality(
            current_entry_price,
            seconds_left
        )
    )

    return {
        "decision": decision,
        "signal": signal,
        "icon": icon,
        "color": color,
        "round_state": state,
        "reversal": reversal,
        "reversal_text": reversal_text,
        "entry_price": current_entry_price,
        "entry_quality": quality,
        "entry_quality_color": quality_color
    }


# =========================================================
# TÍTULO
# =========================================================

st.markdown(
    '<div class="bot-title">'
    '⚡ MACALY + ALPHA BOT • v4.6'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# DASHBOARD LIVE
# =========================================================

@st.fragment(run_every="2s")
def live_dashboard():

    btc_error = ""
    live_price_error = ""
    kalshi_error = ""

    # =====================================================
    # BTC VELAS
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
    # BTC LIVE
    # =====================================================

    try:

        live_btc_price = (
            get_btc_live_price()
        )

        live_price_ok = True

    except Exception as error:

        live_price_ok = False
        live_price_error = str(error)

        if btc_ok:

            live_btc_price = float(
                btc_df.iloc[-1]["close"]
            )

        else:

            live_btc_price = None

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

        no_ask_display = kalshi_price(
            market.get("no_ask_dollars"),
            market.get("no_ask")
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
        no_ask_display = "--"
        last_display = "--"

    # =====================================================
    # MOTOR
    # =====================================================

    if btc_ok:

        sig = build_signal(
            btc_df,
            target,
            seconds_left,
            live_btc_price
        )

    else:

        sig = {
            "price": (
                live_btc_price
                if live_btc_price is not None
                else 0
            ),
            "candle_price": 0,
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
            "momentum": "NEUTRAL",
            "up_probability": 50,
            "down_probability": 50
        }

    round_signal = process_round_signal(
        ticker,
        sig,
        market,
        seconds_left
    )

    # =====================================================
    # PRINCIPAL
    # =====================================================

    main_html = (
        '<div class="bot-card" style="text-align:center;">'

        '<div class="bot-label">'
        'BITCOIN • KALSHI 15 MIN'
        '</div>'

        f'<div style="font-size:30px;font-weight:900;'
        f'color:{round_signal["color"]};">'
        f'{round_signal["icon"]} '
        f'{round_signal["decision"]}'
        '</div>'

        f'<div style="font-size:19px;margin-top:8px;'
        f'color:#e2e8f0;">'
        f'BTC ${sig["price"]:,.2f}'
        '</div>'

        '</div>'
    )

    st.markdown(
        main_html,
        unsafe_allow_html=True
    )

    # =====================================================
    # PROBABILIDAD
    # =====================================================

    probability_html = (
        '<div class="bot-card">'

        '<div class="bot-label">'
        'PROBABILIDAD ESTIMADA'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">🚀 UP</span>'
        '<span class="bot-right" '
        'style="color:#34d399;">'
        f'{sig["up_probability"]}%'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">🔻 DOWN</span>'
        '<span class="bot-right" '
        'style="color:#fb7185;">'
        f'{sig["down_probability"]}%'
        '</span>'
        '</div>'

        '<div class="small-note" '
        'style="margin-top:12px;">'
        'Estimación interna del motor • '
        'no representa certeza de resultado'
        '</div>'

        '</div>'
    )

    st.markdown(
        probability_html,
        unsafe_allow_html=True
    )

    # =====================================================
    # REVERSIÓN
    # =====================================================

    if round_signal["reversal"]:

        st.markdown(
            '<div class="warning-box">'
            '⚠️ POSIBLE REVERSIÓN / REBOTE'
            '<br><br>'
            f'{round_signal["reversal_text"]}'
            '</div>',
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

            distance_text = "$0.00"
            distance_color = "#fbbf24"

    else:

        distance_text = "--"
        distance_color = "#94a3b8"

    target_html = (
        '<div class="bot-card">'

        '<div class="bot-label">'
        'RONDA ACTUAL'
        '</div>'

        '<div class="round-box">'
        f'{ticker}'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Target</span>'
        f'<span class="bot-right">{target_text}</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">BTC actual</span>'
        f'<span class="bot-right">'
        f'${sig["price"]:,.2f}'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Distancia</span>'
        f'<span class="bot-right" '
        f'style="color:{distance_color};">'
        f'{distance_text}'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'Tiempo restante'
        '</span>'
        f'<span class="bot-right">'
        f'{countdown}'
        '</span>'
        '</div>'

        '</div>'
    )

    st.markdown(
        target_html,
        unsafe_allow_html=True
    )

    # =====================================================
    # HISTORIAL DE ESTA RONDA
    # =====================================================

    state = round_signal[
        "round_state"
    ]

    if state:

        if (
            state["first_signal_time"]
            is not None
        ):

            signal_time_text = (
                state[
                    "first_signal_time"
                ]
                .astimezone()
                .strftime("%H:%M:%S")
            )

        else:

            signal_time_text = "--"

        if (
            state["first_signal_seconds"]
            is not None
        ):

            signal_seconds_text = (
                format_countdown(
                    state[
                        "first_signal_seconds"
                    ]
                )
            )

        else:

            signal_seconds_text = "--:--"

        if (
            state["first_signal_price"]
            is not None
        ):

            first_price_text = (
                f'${state["first_signal_price"]:.2f}'
            )

        else:

            first_price_text = "--"

        first_direction = (
            state["first_direction"]
            if state["first_direction"]
            else "NINGUNA"
        )

        active_direction = (
            state["active_direction"]
            if state["active_direction"]
            else "ESPERANDO"
        )

        history_html = (
            '<div class="bot-card">'

            '<div class="bot-label">'
            'SEÑAL DE ESTA RONDA'
            '</div>'

            '<div class="bot-row">'
            '<span class="bot-left">'
            'Primera señal'
            '</span>'
            f'<span class="bot-right">'
            f'{first_direction}'
            '</span>'
            '</div>'

            '<div class="bot-row">'
            '<span class="bot-left">'
            'Generada'
            '</span>'
            f'<span class="bot-right">'
            f'{signal_time_text}'
            '</span>'
            '</div>'

            '<div class="bot-row">'
            '<span class="bot-left">'
            'Tiempo restante al aparecer'
            '</span>'
            f'<span class="bot-right">'
            f'{signal_seconds_text}'
            '</span>'
            '</div>'

            '<div class="bot-row">'
            '<span class="bot-left">'
            'Kalshi al aparecer'
            '</span>'
            f'<span class="bot-right">'
            f'{first_price_text}'
            '</span>'
            '</div>'

            '<div class="bot-row">'
            '<span class="bot-left">'
            'Estado actual'
            '</span>'
            f'<span class="bot-right">'
            f'{active_direction}'
            '</span>'
            '</div>'

            '</div>'
        )

        st.markdown(
            history_html,
            unsafe_allow_html=True
        )

    # =====================================================
    # CALIDAD DE ENTRADA ACTUAL
    # =====================================================

    if round_signal[
        "entry_price"
    ] is not None:

        entry_price_text = (
            f'${round_signal["entry_price"]:.2f}'
        )

    else:

        entry_price_text = "--"

    entry_html = (
        '<div class="bot-card">'

        '<div class="bot-label">'
        'ENTRADA ACTUAL'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'Precio contrato'
        '</span>'
        f'<span class="bot-right">'
        f'{entry_price_text}'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'Calidad'
        '</span>'
        f'<span class="bot-right" '
        f'style="color:'
        f'{round_signal["entry_quality_color"]};">'
        f'{round_signal["entry_quality"]}'
        '</span>'
        '</div>'

        '</div>'
    )

    st.markdown(
        entry_html,
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

        '<div class="bot-label">'
        'KALSHI • BTC 15 MIN'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">Ticker</span>'
        f'<span class="bot-right">'
        f'{ticker}'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'YES bid'
        '</span>'
        f'<span class="bot-right">'
        f'{yes_bid_display}'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'YES ask'
        '</span>'
        f'<span class="bot-right">'
        f'{yes_ask_display}'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'NO ask'
        '</span>'
        f'<span class="bot-right">'
        f'{no_ask_display}'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'Último'
        '</span>'
        f'<span class="bot-right">'
        f'{last_display}'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'API Kalshi'
        '</span>'
        f'<span class="bot-right">'
        f'{kalshi_status}'
        '</span>'
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
        "LIVE 🟢"
        if live_price_ok
        else
        "FALLBACK VELA 🟡"
    )

    indicators_html = (
        '<div class="bot-card">'

        '<div class="bot-label">'
        'ANÁLISIS TÉCNICO'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'EMA 9 / 21'
        '</span>'
        f'<span class="bot-right">'
        f'{sig["ema"]}'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'RSI 14'
        '</span>'
        f'<span class="bot-right">'
        f'{sig["rsi"]:.1f}'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'Momentum 3m'
        '</span>'
        f'<span class="bot-right">'
        f'{sig["mom3"]:+.3f}%'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'Momentum 5m'
        '</span>'
        f'<span class="bot-right">'
        f'{sig["mom5"]:+.3f}%'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'Momentum 15m'
        '</span>'
        f'<span class="bot-right">'
        f'{sig["mom15"]:+.3f}%'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'Volumen'
        '</span>'
        f'<span class="bot-right">'
        f'{sig["vol_ratio"]:.2f}x'
        '</span>'
        '</div>'

        '<div class="bot-row">'
        '<span class="bot-left">'
        'BTC ticker'
        '</span>'
        f'<span class="bot-right">'
        f'{coinbase_status}'
        '</span>'
        '</div>'

        '</div>'
    )

    st.markdown(
        indicators_html,
        unsafe_allow_html=True
    )

    # =====================================================
    # DECISIÓN DEL MOTOR
    # =====================================================

    decision_html = (
        '<div class="bot-card" '
        'style="text-align:center;">'

        '<div class="bot-label">'
        'DECISIÓN DEL MOTOR'
        '</div>'

        f'<div style="font-size:27px;'
        f'font-weight:900;'
        f'color:{round_signal["color"]};">'
        f'{round_signal["signal"]}'
        '</div>'

        '<div style="margin-top:12px;'
        'color:#94a3b8;">'

        f'Score técnico: '
        f'{sig["technical_score"]:.2f}'

        '<br>'

        f'Score target/tiempo: '
        f'{sig["target_score"]:.2f}'

        '<br>'

        f'Score combinado: '
        f'{sig["final_score"]:.2f}'

        '</div>'

        '<div class="small-note" '
        'style="margin-top:16px;">'

        'Cada ticker = una ronda independiente'
        '<br>'

        'Nueva ronda requiere confirmación'
        '<br>'

        'No crea nuevas entradas en los '
        'últimos 75 segundos'
        '<br>'

        'BTC live / distancia cada ~2 segundos 🔄'
        '<br>'

        'Indicadores con velas Coinbase'
        '<br>'

        'Probabilidades = estimación del motor'
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
            "Error Coinbase velas: " +
            btc_error
        )

    if live_price_error:

        st.warning(
            "Ticker Coinbase live falló temporalmente. "
            "Usando última vela como respaldo: " +
            live_price_error
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
