import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone

# =========================================================
# MACALY + ALPHA BOT v4.6.1 • MOBILE PRO UI
# BTC 15 MIN • SAME v4.6.1 SIGNAL ENGINE
# =========================================================

st.set_page_config(
    page_title="BTC Signal v4.6.1",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =========================================================
# CONFIGURACIÓN ORIGINAL
# =========================================================

NEW_ROUND_WAIT = 30
NEW_ENTRY_LOCK = 75

UP_THRESHOLD = 4.0
DOWN_THRESHOLD = -4.0

FLIP_UP_THRESHOLD = 4.75
FLIP_DOWN_THRESHOLD = -4.75
FLIP_CONFIRMATIONS = 2

# =========================================================
# DISEÑO MOBILE — BASADO EN LA REFERENCIA APROBADA
# =========================================================

st.markdown(
    """
<style>
#MainMenu, footer, header {visibility:hidden;}
[data-testid="stToolbar"] {display:none;}
[data-testid="stDecoration"] {display:none;}
[data-testid="stStatusWidget"] {display:none;}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background:
      radial-gradient(circle at 50% -12%, rgba(31,65,104,.24), transparent 30%),
      #070b11;
    color:#f4f7fb;
}

.block-container {
    max-width:410px !important;
    padding:8px 10px 24px !important;
}

div[data-testid="stVerticalBlock"] {gap:.55rem;}

.topbar {
    position:relative;
    min-height:45px;
    padding:3px 2px 4px;
    text-align:center;
}
.brand {
    color:#f8fafc;
    font-size:13px;
    line-height:1.05;
    font-weight:950;
    letter-spacing:.15px;
}
.version {
    color:#647184;
    font-size:7px;
    font-weight:800;
    margin-top:2px;
}
.live {
    position:absolute;
    right:3px;
    top:27px;
    display:flex;
    align-items:center;
    gap:5px;
    color:#91a0b3;
    font-size:7.5px;
    font-weight:800;
}
.live-dot {
    width:7px;
    height:7px;
    border-radius:50%;
    background:#2ee67b;
    box-shadow:0 0 10px rgba(46,230,123,.8);
}

.hero {
    text-align:center;
    padding:0 4px 8px;
}
.hero-signal {
    font-size:58px;
    line-height:.96;
    font-weight:1000;
    letter-spacing:-3px;
    text-shadow:0 0 28px var(--glow);
}
.hero-wait {
    font-size:31px;
    line-height:1.03;
    font-weight:1000;
    letter-spacing:-1.2px;
    color:#51bff3;
    text-shadow:0 0 22px rgba(56,189,248,.20);
}
.confidence {
    display:inline-block;
    margin-top:10px;
    padding:5px 12px;
    border-radius:7px;
    font-size:10px;
    font-weight:1000;
    letter-spacing:.4px;
    border:1px solid var(--accent);
    color:var(--accent);
    background:var(--soft);
}

.two {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:8px;
    margin-top:7px;
}
.mini {
    min-height:61px;
    background:linear-gradient(180deg,#101722,#0c121b);
    border:1px solid #1b2735;
    border-radius:10px;
    padding:8px 9px;
}
.mini-label {
    color:#69778a;
    font-size:8px;
    font-weight:900;
    letter-spacing:.8px;
    text-transform:uppercase;
    margin-bottom:5px;
}
.mini-value {
    color:#f4f7fb;
    font-size:18px;
    font-weight:950;
    letter-spacing:-.4px;
}
.mini-sub {
    color:#7e8b9e;
    font-size:9px;
    font-weight:800;
    margin-top:3px;
}
.green {color:#36e985;}
.red {color:#ff5363;}
.blue {color:#54c6f5;}
.amber {color:#f7bd4d;}

.section {
    background:linear-gradient(180deg,#0f1620,#0b1119);
    border:1px solid #1b2735;
    border-radius:11px;
    padding:11px;
    margin-top:8px;
}
.section-title {
    color:#8b98aa;
    font-size:9px;
    font-weight:1000;
    letter-spacing:.8px;
    text-transform:uppercase;
    margin-bottom:8px;
}
.prob-row {
    display:flex;
    align-items:center;
    gap:7px;
}
.prob-up, .prob-down {
    height:12px;
    border-radius:4px;
    min-width:2px;
}
.prob-up {
    background:linear-gradient(90deg,#1bcf6a,#53ef8d);
    box-shadow:0 0 10px rgba(46,230,123,.18);
}
.prob-down {
    background:linear-gradient(90deg,#ff3d50,#ff6876);
    box-shadow:0 0 10px rgba(255,76,91,.18);
}
.prob-labels {
    display:flex;
    justify-content:space-between;
    margin-top:7px;
    font-size:10px;
    font-weight:900;
}

.close-reader {
    border-radius:11px;
    padding:12px;
    margin-top:8px;
    border:1px solid var(--reader-border);
    background:var(--reader-bg);
    box-shadow:inset 0 0 25px rgba(0,0,0,.10);
}
.reader-top {
    display:flex;
    justify-content:space-between;
    align-items:center;
    color:#e9eef5;
    font-size:9px;
    font-weight:1000;
    letter-spacing:.7px;
}
.reader-active {
    padding:3px 7px;
    border-radius:8px;
    color:#57ee91;
    border:1px solid rgba(69,231,129,.55);
    background:rgba(28,153,78,.15);
    font-size:8px;
}
.reader-main {
    display:grid;
    grid-template-columns:1fr 70px;
    align-items:center;
    gap:8px;
    margin-top:12px;
}
.reader-text {
    color:#f6f8fb;
    font-size:15px;
    line-height:1.15;
    font-weight:1000;
}
.reader-note {
    color:#8390a2;
    font-size:8px;
    line-height:1.35;
    margin-top:6px;
}
.ring {
    --p:50;
    --ring:#36e985;
    width:66px;
    height:66px;
    border-radius:50%;
    display:grid;
    place-items:center;
    background:conic-gradient(var(--ring) calc(var(--p)*1%), #27313e 0);
    position:relative;
}
.ring:after {
    content:"";
    position:absolute;
    width:51px;
    height:51px;
    border-radius:50%;
    background:#0b1119;
}
.ring span {
    position:relative;
    z-index:1;
    color:#f7fafc;
    font-size:15px;
    font-weight:1000;
}

.tech-grid {
    display:grid;
    grid-template-columns:repeat(5,1fr);
    gap:3px;
    text-align:center;
}
.tech-label {
    color:#637084;
    font-size:6.5px;
    font-weight:900;
    letter-spacing:.25px;
    text-transform:uppercase;
}
.tech-value {
    color:#eef3f9;
    font-size:10px;
    font-weight:1000;
    margin-top:5px;
    overflow:hidden;
    white-space:nowrap;
}

.ticker {
    text-align:center;
    color:#4f5c6f;
    font-size:7.5px;
    font-weight:800;
    margin-top:8px;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}

.footer-nav {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    text-align:center;
    padding:10px 2px 1px;
    margin-top:7px;
    border-top:1px solid #182331;
}
.nav-item {
    color:#5f6c7e;
    font-size:8px;
    font-weight:800;
}
.nav-active {color:var(--accent);}

.alert {
    border-radius:10px;
    padding:10px;
    margin-top:8px;
    text-align:center;
    color:#ffd260;
    background:rgba(116,78,7,.18);
    border:1px solid rgba(247,189,77,.42);
    font-size:10px;
    font-weight:900;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# SESSION STATE ORIGINAL
# =========================================================

if "rounds" not in st.session_state:
    st.session_state.rounds = {}

if "active_ticker" not in st.session_state:
    st.session_state.active_ticker = None

if "micro_prices" not in st.session_state:
    st.session_state.micro_prices = []

if "micro_ticker" not in st.session_state:
    st.session_state.micro_ticker = None


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
# COINBASE — VELAS ORIGINALES DE 1 MINUTO
# =========================================================

@st.cache_data(ttl=5)
def get_btc_data():
    response = requests.get(
        "https://api.exchange.coinbase.com/products/BTC-USD/candles",
        params={"granularity": 60},
        headers={"User-Agent": "MacalyAlphaBot/4.6.1"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list) or len(data) < 30:
        raise ValueError("Coinbase no devolvió suficientes datos.")

    df = pd.DataFrame(
        data, columns=["time", "low", "high", "open", "close", "volume"]
    )

    for column in ["low", "high", "open", "close", "volume"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df.dropna().sort_values("time").reset_index(drop=True)


def get_btc_live_price():
    response = requests.get(
        "https://api.exchange.coinbase.com/products/BTC-USD/ticker",
        headers={
            "User-Agent": "MacalyAlphaBot/4.6.1",
            "Cache-Control": "no-cache",
        },
        params={"_": int(datetime.now(timezone.utc).timestamp())},
        timeout=6,
    )
    response.raise_for_status()
    price = response.json().get("price")
    if price in [None, ""]:
        raise ValueError("Coinbase ticker no devolvió precio.")
    return float(price)


# =========================================================
# KALSHI BTC 15 MIN
# =========================================================

@st.cache_data(ttl=2)
def get_kalshi_btc_market():
    response = requests.get(
        "https://external-api.kalshi.com/trade-api/v2/markets",
        params={
            "limit": 100,
            "status": "open",
            "series_ticker": "KXBTC15M",
        },
        headers={"User-Agent": "MacalyAlphaBot/4.6.1"},
        timeout=10,
    )
    response.raise_for_status()
    markets = response.json().get("markets", [])
    if not markets:
        return None
    markets.sort(key=lambda m: str(m.get("close_time") or "9999"))
    return markets[0]


def get_event_ticker_from_market(market):
    if not market:
        return None
    event_ticker = market.get("event_ticker")
    if event_ticker:
        return str(event_ticker)
    ticker = market.get("ticker")
    if not ticker:
        return None
    parts = str(ticker).split("-")
    return "-".join(parts[:-1]) if len(parts) >= 2 else None


def extract_kalshi_btc_price(data):
    if not isinstance(data, dict):
        return None

    live_data = data.get("live_data", data)
    details = live_data.get("details", {}) if isinstance(live_data, dict) else {}
    candidates = []

    preferred_keys = {
        "price", "value", "index_value", "indexvalue",
        "current_price", "currentprice", "current_value", "currentvalue",
        "last_price", "lastprice", "close",
    }

    def walk_preferred(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                normalized_key = str(key).lower().replace("-", "_")
                if normalized_key in preferred_keys:
                    try:
                        number = float(value)
                        if 10000 < number < 1000000:
                            candidates.append(number)
                    except (TypeError, ValueError):
                        pass
                walk_preferred(value)
        elif isinstance(obj, list):
            for item in obj:
                walk_preferred(item)

    walk_preferred(details)
    if candidates:
        return float(candidates[-1])

    pair_candidates = []

    def walk_pairs(obj):
        if isinstance(obj, list):
            if len(obj) >= 2:
                try:
                    possible_price = float(obj[-1])
                    if 10000 < possible_price < 1000000:
                        pair_candidates.append(possible_price)
                except (TypeError, ValueError):
                    pass
            for item in obj:
                walk_pairs(item)
        elif isinstance(obj, dict):
            for value in obj.values():
                walk_pairs(value)

    walk_pairs(details)
    return float(pair_candidates[-1]) if pair_candidates else None


def get_kalshi_live_btc(market):
    event_ticker = get_event_ticker_from_market(market)
    if not event_ticker:
        raise ValueError("La ronda no entregó event_ticker.")

    response = requests.get(
        "https://external-api.kalshi.com/trade-api/v2/live_data/events/"
        f"{event_ticker}",
        params={
            "range": "15min",
            "_": int(datetime.now(timezone.utc).timestamp()),
        },
        headers={
            "User-Agent": "MacalyAlphaBot/4.6.1",
            "Cache-Control": "no-cache",
        },
        timeout=6,
    )
    response.raise_for_status()
    price = extract_kalshi_btc_price(response.json())
    if price is None:
        raise ValueError("Kalshi live respondió sin precio BTC válido.")
    return float(price)


# =========================================================
# INDICADORES ORIGINALES
# =========================================================

def add_indicators(df):
    df = df.copy()
    close = df["close"]

    df["ema9"] = close.ewm(span=9, adjust=False).mean()
    df["ema21"] = close.ewm(span=21, adjust=False).mean()

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / 14, adjust=False, min_periods=14
    ).mean()
    avg_loss = loss.ewm(
        alpha=1 / 14, adjust=False, min_periods=14
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"] = (100 - (100 / (1 + rs))).fillna(50)

    df["mom3"] = close.pct_change(3) * 100
    df["mom5"] = close.pct_change(5) * 100
    df["mom15"] = close.pct_change(15) * 100

    avg_volume = df["volume"].rolling(20).mean()
    df["vol_ratio"] = df["volume"] / avg_volume.replace(0, np.nan)
    return df


def get_target_from_market(market):
    if not market:
        return None

    for key in ("floor_strike", "cap_strike"):
        value = market.get(key)
        if value not in [None, ""]:
            try:
                number = float(value)
                if number > 1000:
                    return number
            except Exception:
                pass
    return None


def get_seconds_remaining(market):
    if not market or not market.get("close_time"):
        return None
    try:
        close_dt = datetime.fromisoformat(
            str(market["close_time"]).replace("Z", "+00:00")
        )
        seconds = int(
            (close_dt - datetime.now(timezone.utc)).total_seconds()
        )
        return max(0, seconds)
    except Exception:
        return None


def format_countdown(seconds):
    if seconds is None:
        return "--:--"
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def numeric_kalshi_price(dollar_value, cent_value):
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


def get_yes_ask(market):
    if not market:
        return None
    return numeric_kalshi_price(
        market.get("yes_ask_dollars"), market.get("yes_ask")
    )


def get_no_ask(market):
    if not market:
        return None

    direct = numeric_kalshi_price(
        market.get("no_ask_dollars"), market.get("no_ask")
    )
    if direct is not None:
        return direct

    yes_bid = numeric_kalshi_price(
        market.get("yes_bid_dollars"), market.get("yes_bid")
    )
    if yes_bid is not None:
        return max(0.0, min(1.0, 1.0 - yes_bid))
    return None


# =========================================================
# PROBABILIDAD ORIGINAL
# =========================================================

def estimated_probabilities(
    final_score, distance, seconds_left, mom3, mom5
):
    score = float(np.clip(final_score, -10, 10))
    up_prob = 50 + score * 4.2

    if mom3 > 0.04:
        up_prob += 3
    elif mom3 < -0.04:
        up_prob -= 3

    if mom5 > 0.06:
        up_prob += 2
    elif mom5 < -0.06:
        up_prob -= 2

    if (
        distance is not None
        and seconds_left is not None
        and seconds_left <= 180
    ):
        if distance > 0:
            up_prob += 3
        elif distance < 0:
            up_prob -= 3

    up_prob = float(np.clip(up_prob, 5, 95))
    return round(up_prob), round(100 - up_prob)


# =========================================================
# MOTOR ORIGINAL v4.6.1
# =========================================================

def build_signal(df, target, seconds_left, live_price=None):
    last = df.iloc[-1]
    candle_price = float(last["close"])
    price = float(live_price) if live_price is not None else candle_price

    rsi = float(last["rsi"])
    mom3 = float(last["mom3"]) if pd.notna(last["mom3"]) else 0.0
    mom5 = float(last["mom5"]) if pd.notna(last["mom5"]) else 0.0
    mom15 = float(last["mom15"]) if pd.notna(last["mom15"]) else 0.0
    vol_ratio = (
        float(last["vol_ratio"]) if pd.notna(last["vol_ratio"]) else 0.0
    )

    technical_score = 0.0

    if last["ema9"] > last["ema21"]:
        technical_score += 2.0
        ema_text = "BULL"
    else:
        technical_score -= 2.0
        ema_text = "BEAR"

    if rsi >= 55:
        technical_score += 1.0
    elif rsi <= 45:
        technical_score -= 1.0

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

    if vol_ratio > 1.20:
        if mom3 > 0:
            technical_score += 0.50
        elif mom3 < 0:
            technical_score -= 0.50

    distance = None
    distance_pct = None
    target_score = 0.0

    if target is not None:
        distance = price - target
        distance_pct = distance / target * 100

        if distance > 0:
            target_score += 2.0
        elif distance < 0:
            target_score -= 2.0

        if seconds_left is not None:
            abs_distance = abs(distance)

            if seconds_left <= 30:
                target_score += 4.0 if distance > 0 else -4.0 if distance < 0 else 0
            elif seconds_left <= 60:
                target_score += 3.0 if distance > 0 else -3.0 if distance < 0 else 0
            elif seconds_left <= 180:
                target_score += 2.0 if distance > 0 else -2.0 if distance < 0 else 0
            elif seconds_left <= 300:
                target_score += 1.0 if distance > 0 else -1.0 if distance < 0 else 0

            if abs_distance < 10:
                target_score *= 0.60
            elif abs_distance < 20:
                target_score *= 0.80

    final_score = technical_score + target_score

    if mom3 > 0.02:
        momentum = "ALCISTA"
    elif mom3 < -0.02:
        momentum = "BAJISTA"
    else:
        momentum = "NEUTRAL"

    up_probability, down_probability = estimated_probabilities(
        final_score, distance, seconds_left, mom3, mom5
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
        "down_probability": down_probability,
    }


def entry_quality(price, seconds_left):
    if price is None:
        return "PRECIO NO DISPONIBLE", "#94a3b8"
    if seconds_left is not None and seconds_left <= NEW_ENTRY_LOCK:
        return "TARDE", "#fb7185"
    if price <= 0.60:
        return "BUENA", "#34d399"
    if price <= 0.70:
        return "PRECAUCIÓN", "#fbbf24"
    return "CARA / TARDE", "#fb7185"


# =========================================================
# CONTROL DE RONDA ORIGINAL
# =========================================================

def process_round_signal(ticker, sig, market, seconds_left):
    now = datetime.now(timezone.utc)

    if (
        ticker
        and ticker != "--"
        and st.session_state.active_ticker != ticker
    ):
        st.session_state.active_ticker = ticker
        st.session_state.rounds[ticker] = new_round_state(
            ticker, seconds_left
        )

    if not ticker or ticker == "--":
        return {
            "decision": "NO TRADE",
            "signal": "SIN RONDA",
            "icon": "•",
            "color": "#fbbf24",
            "round_state": None,
            "reversal": False,
            "reversal_text": "",
            "entry_price": None,
            "entry_quality": "SIN DATOS",
            "entry_quality_color": "#94a3b8",
        }

    if ticker not in st.session_state.rounds:
        st.session_state.rounds[ticker] = new_round_state(
            ticker, seconds_left
        )

    state = st.session_state.rounds[ticker]
    age = (now - state["detected_at"]).total_seconds()
    score = sig["final_score"]

    previous_live_price = state["last_live_price"]
    state["previous_live_price"] = previous_live_price
    state["last_live_price"] = sig["price"]

    price_change = (
        sig["price"] - previous_live_price
        if previous_live_price is not None
        else 0.0
    )

    previous_score = state["last_score"]
    state["previous_score"] = previous_score
    score_change = score - previous_score
    state["last_score"] = score

    if age < NEW_ROUND_WAIT:
        state["reversal_warning"] = False
        state["reversal_text"] = ""
        return {
            "decision": "ANALIZANDO NUEVA RONDA",
            "signal": "ESPERANDO CONFIRMACIÓN",
            "icon": "⌛",
            "color": "#38bdf8",
            "round_state": state,
            "reversal": False,
            "reversal_text": "",
            "entry_price": None,
            "entry_quality": "ESPERANDO",
            "entry_quality_color": "#38bdf8",
        }

    lock_new_entries = (
        seconds_left is not None and seconds_left <= NEW_ENTRY_LOCK
    )

    candidate = None
    if score >= UP_THRESHOLD:
        candidate = "UP"
    elif score <= DOWN_THRESHOLD:
        candidate = "DOWN"

    if (
        state["active_direction"] is None
        and candidate is not None
        and not lock_new_entries
    ):
        direction_price = (
            get_yes_ask(market)
            if candidate == "UP"
            else get_no_ask(market)
        )

        state["active_direction"] = candidate
        state["active_since"] = now
        state["first_direction"] = candidate
        state["first_signal_time"] = now
        state["first_signal_seconds"] = seconds_left
        state["first_signal_price"] = direction_price
        state["opposite_count"] = 0

    active = state["active_direction"]
    reversal = False
    reversal_text = ""

    if active == "UP":
        weakness_points = 0

        if score < 3:
            weakness_points += 1
        if score_change <= -1.25:
            weakness_points += 1
        if sig["mom3"] < -0.02:
            weakness_points += 1
        if sig["mom5"] < 0:
            weakness_points += 1
        if price_change < -8:
            weakness_points += 1
        if (
            sig["distance"] is not None
            and seconds_left is not None
            and seconds_left <= 180
            and sig["distance"] < 25
            and price_change < 0
        ):
            weakness_points += 1

        if weakness_points >= 2:
            reversal = True
            reversal_text = "UP PERDIENDO FUERZA • POSIBLE REVERSIÓN A DOWN"

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
            and seconds_left is not None
            and seconds_left <= 180
            and sig["distance"] > -25
            and price_change > 0
        ):
            weakness_points += 1

        if weakness_points >= 2:
            reversal = True
            reversal_text = "DOWN PERDIENDO FUERZA • POSIBLE REBOTE A UP"

    state["reversal_warning"] = reversal
    state["reversal_text"] = reversal_text

    if active == "UP":
        if score <= FLIP_DOWN_THRESHOLD and sig["mom3"] < 0:
            state["opposite_count"] += 1
        else:
            state["opposite_count"] = 0

        if state["opposite_count"] >= FLIP_CONFIRMATIONS:
            if not lock_new_entries:
                state["active_direction"] = "DOWN"
                state["active_since"] = now
            state["opposite_count"] = 0

    elif active == "DOWN":
        if score >= FLIP_UP_THRESHOLD and sig["mom3"] > 0:
            state["opposite_count"] += 1
        else:
            state["opposite_count"] = 0

        if state["opposite_count"] >= FLIP_CONFIRMATIONS:
            if not lock_new_entries:
                state["active_direction"] = "UP"
                state["active_since"] = now
            state["opposite_count"] = 0

    active = state["active_direction"]

    if active == "UP":
        decision = "UP"
        signal = "SEÑAL UP"
        icon = "⬆"
        color = "#34e982"
        current_entry_price = get_yes_ask(market)
    elif active == "DOWN":
        decision = "DOWN"
        signal = "SEÑAL DOWN"
        icon = "⬇"
        color = "#ff4e5f"
        current_entry_price = get_no_ask(market)
    else:
        current_entry_price = None
        if lock_new_entries:
            decision = "NO NUEVA ENTRADA"
            signal = "FINAL DE RONDA"
            icon = "⏱"
            color = "#fbbf24"
        else:
            decision = "ESPERANDO"
            signal = "ESPERAR"
            icon = "•"
            color = "#38bdf8"

    quality, quality_color = entry_quality(
        current_entry_price, seconds_left
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
        "entry_quality_color": quality_color,
    }


# =========================================================
# LECTOR DE CIERRE PRO — MICRO LECTURA ~2 SEGUNDOS
# Mantiene intacto el motor v4.6.1 y sus señales.
# No inventa velas REST de 1 segundo: construye una cinta
# de muestras del BTC live que ya recibe el dashboard.
# =========================================================

def update_micro_tape(ticker, live_price):
    if not ticker or ticker == "--" or live_price is None:
        return

    # Cada ronda empieza con su propia cinta.
    if st.session_state.micro_ticker != ticker:
        st.session_state.micro_ticker = ticker
        st.session_state.micro_prices = []

    now_ts = datetime.now(timezone.utc).timestamp()
    tape = st.session_state.micro_prices

    # Evita duplicar muestras dentro del mismo refresco.
    if not tape or now_ts - tape[-1]["t"] >= 1.0:
        tape.append({"t": now_ts, "p": float(live_price)})

    # Conserva aproximadamente los últimos 90 segundos.
    cutoff = now_ts - 90
    st.session_state.micro_prices = [
        x for x in tape if x["t"] >= cutoff
    ]


def micro_reading():
    tape = st.session_state.micro_prices

    if len(tape) < 4:
        return {
            "ready": False,
            "change_10s": 0.0,
            "change_30s": 0.0,
            "slope": 0.0,
            "up_ratio": 0.5,
            "pressure": "NEUTRAL",
        }

    now_t = tape[-1]["t"]
    current = tape[-1]["p"]

    def price_ago(seconds):
        target_t = now_t - seconds
        candidates = [x for x in tape if x["t"] <= target_t]
        if candidates:
            return candidates[-1]["p"]
        return tape[0]["p"]

    p10 = price_ago(10)
    p30 = price_ago(30)

    changes = [
        tape[i]["p"] - tape[i - 1]["p"]
        for i in range(1, len(tape))
    ]
    nonzero = [x for x in changes if x != 0]
    up_ratio = (
        sum(1 for x in nonzero if x > 0) / len(nonzero)
        if nonzero else 0.5
    )

    # Regresión simple precio/tiempo para medir dirección micro.
    xs = np.array([x["t"] - tape[0]["t"] for x in tape], dtype=float)
    ys = np.array([x["p"] for x in tape], dtype=float)
    slope = float(np.polyfit(xs, ys, 1)[0]) if len(xs) >= 3 and xs[-1] > 0 else 0.0

    c10 = current - p10
    c30 = current - p30

    if slope > 0.35 and up_ratio >= 0.58:
        pressure = "ALCISTA"
    elif slope < -0.35 and up_ratio <= 0.42:
        pressure = "BAJISTA"
    else:
        pressure = "NEUTRAL"

    return {
        "ready": True,
        "change_10s": c10,
        "change_30s": c30,
        "slope": slope,
        "up_ratio": up_ratio,
        "pressure": pressure,
    }


def closing_reader(sig, round_signal, seconds_left, micro):
    direction = None
    state = round_signal.get("round_state")
    if state:
        direction = state.get("active_direction")

    if direction not in ("UP", "DOWN"):
        return {
            "percent": 50,
            "headline": "ESPERANDO SEÑAL",
            "note": "El motor todavía no confirmó una dirección.",
            "micro": "MICROLECTURA PREPARÁNDOSE",
            "color": "#38bdf8",
            "border": "rgba(56,189,248,.45)",
            "bg": "linear-gradient(135deg,rgba(11,64,91,.30),rgba(9,23,34,.72))",
        }

    base = sig["up_probability"] if direction == "UP" else sig["down_probability"]
    confidence = float(base)

    # Contexto del motor de 1 minuto.
    if sig["distance"] is not None:
        aligned = sig["distance"] > 0 if direction == "UP" else sig["distance"] < 0
        confidence += 4 if aligned else -7

    aligned_momentum = sig["mom3"] > 0 if direction == "UP" else sig["mom3"] < 0
    confidence += 3 if aligned_momentum else -5

    if round_signal.get("reversal"):
        confidence -= 12

    # Microestructura: muestras live aproximadamente cada 2 s.
    micro_text = "MICROLECTURA REUNIENDO DATOS"
    if micro.get("ready"):
        wanted = 1 if direction == "UP" else -1
        c10 = micro["change_10s"] * wanted
        c30 = micro["change_30s"] * wanted
        slope = micro["slope"] * wanted
        ratio = micro["up_ratio"] if direction == "UP" else 1 - micro["up_ratio"]

        micro_score = 0
        micro_score += 6 if c10 > 8 else (3 if c10 > 2 else (-7 if c10 < -8 else (-4 if c10 < -2 else 0)))
        micro_score += 7 if c30 > 15 else (4 if c30 > 5 else (-9 if c30 < -15 else (-5 if c30 < -5 else 0)))
        micro_score += 4 if slope > 0.45 else (-5 if slope < -0.45 else 0)
        micro_score += 4 if ratio >= 0.62 else (-5 if ratio <= 0.38 else 0)

        weight = 1.0
        if seconds_left is not None:
            if seconds_left <= 60:
                weight = 1.55
            elif seconds_left <= 120:
                weight = 1.35
            elif seconds_left <= 180:
                weight = 1.20

        confidence += float(np.clip(micro_score * weight, -28, 20))

        strong_contradiction = (c10 < -5 and c30 < -10)
        if strong_contradiction:
            confidence = min(confidence, 69)

        micro_text = (
            f"MICRO {micro['pressure']} • "
            f"10s {micro['change_10s']:+.1f} • "
            f"30s {micro['change_30s']:+.1f}"
        )

    # Cerca del cierre, la microlectura pesa más porque importa la presión inmediata.
    if seconds_left is not None and seconds_left <= 180:
        confidence += 2

    confidence = int(round(np.clip(confidence, 5, 95)))

    if round_signal.get("reversal"):
        headline = "SEÑAL PERDIENDO FUERZA"
        note = round_signal.get("reversal_text") or "Posible cambio de dirección."
    elif micro.get("ready") and 'strong_contradiction' in locals() and strong_contradiction:
        headline = f"{direction} PERDIENDO FUERZA"
        note = "La presión live de 10s y 30s va contra la señal activa."
    elif confidence >= 75:
        headline = f"ALTA PROBABILIDAD DE CIERRE EN {direction}"
        note = "Motor + presión live de segundos alineados."
    elif confidence >= 60:
        headline = f"VENTAJA MODERADA PARA {direction}"
        note = "La dirección sigue activa, pero la presión inmediata aún puede cambiar."
    else:
        headline = f"CIERRE {direction} SIN VENTAJA CLARA"
        note = "La microlectura no confirma con fuerza la señal activa."

    if direction == "UP":
        color = "#34e982"
        border = "rgba(52,233,130,.48)"
        bg = "linear-gradient(135deg,rgba(4,86,43,.46),rgba(7,36,25,.78))"
    else:
        color = "#ff4e5f"
        border = "rgba(255,78,95,.48)"
        bg = "linear-gradient(135deg,rgba(102,20,31,.48),rgba(43,10,17,.80))"

    return {
        "percent": confidence,
        "headline": headline,
        "note": note,
        "micro": micro_text,
        "color": color,
        "border": border,
        "bg": bg,
    }


@st.fragment(run_every="2s")
def live_dashboard():
    btc_error = ""
    live_price_error = ""
    kalshi_error = ""
    kalshi_live_error = ""

    try:
        btc_df = add_indicators(get_btc_data())
        btc_ok = True
    except Exception as error:
        btc_ok = False
        btc_error = str(error)
        btc_df = None

    try:
        market = get_kalshi_btc_market()
        kalshi_ok = market is not None
    except Exception as error:
        kalshi_ok = False
        kalshi_error = str(error)
        market = None

    try:
        coinbase_live_price = get_btc_live_price()
        coinbase_live_ok = True
    except Exception as error:
        coinbase_live_ok = False
        live_price_error = str(error)
        coinbase_live_price = (
            float(btc_df.iloc[-1]["close"]) if btc_ok else None
        )

    kalshi_live_price = None
    kalshi_live_ok = False

    if market:
        try:
            kalshi_live_price = get_kalshi_live_btc(market)
            kalshi_live_ok = True
        except Exception as error:
            kalshi_live_error = str(error)

    if kalshi_live_price is not None:
        live_btc_price = kalshi_live_price
        source = "KALSHI LIVE"
    else:
        live_btc_price = coinbase_live_price
        source = (
            "COINBASE"
            if coinbase_live_ok or live_btc_price is not None
            else "SIN DATOS"
        )

    if market:
        ticker = market.get("ticker", "--")
        target = get_target_from_market(market)
        seconds_left = get_seconds_remaining(market)
    else:
        ticker = "--"
        target = None
        seconds_left = None

    if btc_ok:
        sig = build_signal(
            btc_df, target, seconds_left, live_btc_price
        )
    else:
        sig = {
            "price": live_btc_price if live_btc_price is not None else 0,
            "candle_price": 0,
            "rsi": 50,
            "mom3": 0,
            "mom5": 0,
            "mom15": 0,
            "vol_ratio": 0,
            "ema": "N/A",
            "technical_score": 0,
            "target_score": 0,
            "final_score": 0,
            "distance": None,
            "distance_pct": None,
            "momentum": "NEUTRAL",
            "up_probability": 50,
            "down_probability": 50,
        }

    round_signal = process_round_signal(
        ticker, sig, market, seconds_left
    )

    # Cinta live de segundos para el Lector de Cierre.
    update_micro_tape(ticker, live_btc_price)
    micro = micro_reading()
    reader = closing_reader(sig, round_signal, seconds_left, micro)

    state = round_signal.get("round_state")
    active = (
        state.get("active_direction")
        if state
        else None
    )

    if active == "UP":
        accent = "#34e982"
        glow = "rgba(52,233,130,.46)"
        soft = "rgba(52,233,130,.10)"
        hero = "↑ UP"
        confidence = sig["up_probability"]
    elif active == "DOWN":
        accent = "#ff4e5f"
        glow = "rgba(255,78,95,.45)"
        soft = "rgba(255,78,95,.10)"
        hero = "↓ DOWN"
        confidence = sig["down_probability"]
    else:
        accent = "#38bdf8"
        glow = "rgba(56,189,248,.30)"
        soft = "rgba(56,189,248,.09)"
        hero = None
        confidence = max(
            sig["up_probability"], sig["down_probability"]
        )

    market_live = kalshi_ok and live_btc_price is not None

    st.markdown(
        f"""
<div style="--accent:{accent};--glow:{glow};--soft:{soft};">
  <div class="topbar">
    <div class="brand">BTC Signal</div>
    <div class="version">v4.6.1</div>
    <div class="live">
      <span class="live-dot" style="background:{'#2ee67b' if market_live else '#f7bd4d'}"></span>
      {'Mercado en vivo' if market_live else 'Conexión parcial'}
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if hero:
        hero_html = f"""
<div style="--accent:{accent};--glow:{glow};--soft:{soft};">
  <div class="hero">
    <div class="hero-signal" style="color:{accent};">{hero}</div>
    <div class="confidence">CONFIANZA {confidence}%</div>
  </div>
</div>
"""
    else:
        hero_html = f"""
<div style="--accent:{accent};--glow:{glow};--soft:{soft};">
  <div class="hero">
    <div class="hero-wait">{round_signal["decision"]}</div>
    <div class="confidence">{round_signal["signal"]}</div>
  </div>
</div>
"""

    st.markdown(hero_html, unsafe_allow_html=True)

    distance = sig["distance"]
    distance_pct = sig.get("distance_pct")

    if distance is None:
        distance_text = "--"
        distance_sub = "sin target"
        distance_class = ""
    else:
        distance_text = f"${abs(distance):,.0f}"
        distance_sub = (
            f"{abs(distance_pct):.2f}% • "
            + ("ARRIBA" if distance > 0 else "ABAJO")
        )
        distance_class = "green" if distance > 0 else "red"

    target_text = f"${target:,.0f}" if target is not None else "--"
    countdown = format_countdown(seconds_left)

    st.markdown(
        f"""
<div class="two">
  <div class="mini">
    <div class="mini-label">₿ BTC</div>
    <div class="mini-value">${sig["price"]:,.0f}</div>
    <div class="mini-sub">{source}</div>
  </div>
  <div class="mini">
    <div class="mini-label">◎ Target</div>
    <div class="mini-value">{target_text}</div>
    <div class="mini-sub">KALSHI 15 MIN</div>
  </div>
</div>

<div class="two">
  <div class="mini">
    <div class="mini-label">▥ Distancia al target</div>
    <div class="mini-value {distance_class}">{distance_text}</div>
    <div class="mini-sub">{distance_sub}</div>
  </div>
  <div class="mini">
    <div class="mini-label">◷ Tiempo restante</div>
    <div class="mini-value">{countdown}</div>
    <div class="mini-sub">{round_signal["entry_quality"]}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    up = int(sig["up_probability"])
    down = int(sig["down_probability"])

    st.markdown(
        f"""
<div class="section">
  <div class="section-title">Probabilidades</div>
  <div class="prob-row">
    <div class="prob-up" style="width:{up}%"></div>
    <div class="prob-down" style="width:{down}%"></div>
  </div>
  <div class="prob-labels">
    <span class="green">● UP&nbsp; {up}%</span>
    <span class="red">● DOWN&nbsp; {down}%</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="close-reader"
     style="--reader-border:{reader['border']};--reader-bg:{reader['bg']};">
  <div class="reader-top">
    <span style="color:{reader['color']};">⌁ &nbsp; LECTOR DE CIERRE</span>
    <span class="reader-active">ACTIVO</span>
  </div>
  <div class="reader-main">
    <div>
      <div class="reader-text">{reader['headline']}</div>
      <div class="reader-note">{reader['note']}</div>
    </div>
    <div class="ring" style="--p:{reader['percent']};--ring:{reader['color']};">
      <span>{reader['percent']}%</span>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    first_signal = (
        state.get("first_direction") if state else None
    ) or "--"
    first_time = "--"
    if state and state.get("first_signal_time"):
        first_time = (
            state["first_signal_time"]
            .astimezone()
            .strftime("%H:%M")
        )

    ema_class = (
        "green" if sig["ema"] == "BULL" else "red"
    )
    rsi_class = (
        "green"
        if sig["rsi"] >= 55
        else "red"
        if sig["rsi"] <= 45
        else ""
    )
    mom_class = (
        "green"
        if sig["mom3"] > 0
        else "red"
        if sig["mom3"] < 0
        else ""
    )

    st.markdown(
        f"""
<div class="section">
  <div class="section-title">Detalles técnicos</div>
  <div class="tech-grid">
    <div>
      <div class="tech-label">1ª señal</div>
      <div class="tech-value" style="color:{accent};">{first_signal}</div>
      <div class="tech-label">{first_time}</div>
    </div>
    <div>
      <div class="tech-label">Kalshi</div>
      <div class="tech-value">{confidence}%</div>
      <div class="tech-label">{round_signal["entry_quality"]}</div>
    </div>
    <div>
      <div class="tech-label">EMA</div>
      <div class="tech-value {ema_class}">{sig["ema"]}</div>
      <div class="tech-label">9 / 21</div>
    </div>
    <div>
      <div class="tech-label">RSI</div>
      <div class="tech-value {rsi_class}">{sig["rsi"]:.0f}</div>
      <div class="tech-label">14</div>
    </div>
    <div>
      <div class="tech-label">Momentum</div>
      <div class="tech-value {mom_class}">{sig["mom3"]:+.2f}</div>
      <div class="tech-label">3 min</div>
    </div>
  </div>
</div>

<div class="ticker">{ticker} • SCORE {sig["final_score"]:+.2f}</div>

<div style="--accent:{accent};">
  <div class="footer-nav">
    <div class="nav-item nav-active">●<br>Señal</div>
    <div class="nav-item">⌁<br>Gráfico</div>
    <div class="nav-item">▣<br>Kalshi</div>
    <div class="nav-item">⚙<br>Ajustes</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if round_signal["reversal"]:
        st.markdown(
            f'<div class="alert">⚠ {round_signal["reversal_text"]}</div>',
            unsafe_allow_html=True,
        )

    if target is None and kalshi_ok:
        st.warning(
            "Kalshi está conectado, pero esta ronda no entregó un target numérico."
        )
    if btc_error:
        st.error("Error Coinbase velas: " + btc_error)
    if live_price_error and live_btc_price is None:
        st.warning("Coinbase live: " + live_price_error)
    if kalshi_live_error and coinbase_live_price is not None:
        st.warning(
            "Kalshi BTC live falló temporalmente; usando Coinbase."
        )
    if kalshi_error:
        st.error("Error Kalshi: " + kalshi_error)


live_dashboard()
