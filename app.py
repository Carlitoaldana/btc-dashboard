import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
import base64
import time
import uuid
import math
import subprocess
import tempfile

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



# =========================================================
# SESSION STATE ORIGINAL
# =========================================================

if "rounds" not in st.session_state:
    st.session_state.rounds = {}

if "active_ticker" not in st.session_state:
    st.session_state.active_ticker = None


# =========================================================
# KALSHI AUTO TRADING — CAPA SEPARADA DEL MOTOR v4.6.1
# =========================================================
_AUTO_DEFAULTS = {
    "kalshi_auth_ok": False,
    "kalshi_auth_message": "No conectado",
    "auto_enabled": False,
    "auto_amount": 0.50,
    "auto_limit_cents": 45,
    "auto_take_profit": 90,
    "auto_martingale": True,
    "auto_max_levels": 4,
    "auto_level": 1,
    "auto_stop_after_win": False,
    "auto_last_ticker": None,
    "auto_last_order": None,
    "auto_last_status": "AUTO APAGADO",
    "auto_history": [],
}
for _k, _v in _AUTO_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# UI/strategy preferences (presentation only; signal brain remains v4.6.1)
_UI_DEFAULTS = {
    "amount_mode": "Manual",
    "restart_martingale": False,
    "sound_power": True,
    "sound_order": True,
}
for _k, _v in _UI_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v



KALSHI_API_BASE = "https://external-api.kalshi.com"
KALSHI_API_PREFIX = "/trade-api/v2"

def _kalshi_sign(message):
    """RSA-PSS/SHA256 signature using system OpenSSL; no Python crypto package required."""
    pem = st.session_state.get("kalshi_private_key_input", "")
    if not pem:
        raise ValueError("Falta la Private Key.")
    key_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False) as f:
            f.write(pem.strip() + "\n")
            key_path = f.name
        proc = subprocess.run(
            [
                "openssl", "dgst", "-sha256",
                "-sigopt", "rsa_padding_mode:pss",
                "-sigopt", "rsa_pss_saltlen:digest",
                "-sign", key_path,
            ],
            input=message,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        if proc.returncode != 0:
            raise ValueError("Private Key inválida o OpenSSL no pudo firmar.")
        return proc.stdout
    finally:
        if key_path:
            try:
                Path(key_path).unlink(missing_ok=True)
            except Exception:
                pass

def _kalshi_headers(method, path):
    key_id = st.session_state.get("kalshi_key_id_input", st.session_state.get("kalshi_api_key_input", "")).strip()
    if not key_id:
        raise ValueError("Falta el API Key ID.")
    ts = str(int(time.time() * 1000))
    clean_path = path.split("?", 1)[0]
    msg = f"{ts}{method.upper()}{clean_path}".encode("utf-8")
    signature = _kalshi_sign(msg)
    return {
        "KALSHI-ACCESS-KEY": key_id,
        "KALSHI-ACCESS-TIMESTAMP": ts,
        "KALSHI-ACCESS-SIGNATURE": base64.b64encode(signature).decode("ascii"),
        "Content-Type": "application/json",
    }

def kalshi_private_request(method, endpoint, payload=None, params=None):
    path = KALSHI_API_PREFIX + endpoint
    headers = _kalshi_headers(method, path)
    r = requests.request(
        method.upper(),
        KALSHI_API_BASE + path,
        headers=headers,
        json=payload,
        params=params,
        timeout=8,
    )
    if r.status_code >= 400:
        try:
            detail = r.json()
        except Exception:
            detail = r.text[:300]
        raise RuntimeError(f"Kalshi {r.status_code}: {detail}")
    return r.json() if r.text else {}

def kalshi_test_connection():
    data = kalshi_private_request("GET", "/portfolio/balance")
    dollars = data.get("balance_dollars")
    if dollars is None and data.get("balance") is not None:
        dollars = f"{float(data['balance']) / 100:.2f}"
    return data, dollars

def _market_contract_prices(market):
    """Returns current YES/NO asks as dollars when Kalshi exposes them."""
    if not market:
        return None, None
    def f(name):
        try:
            v = market.get(name)
            return float(v) if v not in (None, "") else None
        except Exception:
            return None
    yes_ask = f("yes_ask_dollars")
    no_ask = f("no_ask_dollars")
    # Compatibility with older payloads still returned by some endpoints.
    if yes_ask is None:
        y = f("yes_ask")
        yes_ask = y / 100.0 if y and y > 1 else y
    if no_ask is None:
        n = f("no_ask")
        no_ask = n / 100.0 if n and n > 1 else n
    return yes_ask, no_ask

def _automatic_base_amount():
    """90% of available Kalshi cash distributed across selected martingale levels."""
    try:
        _, dollars = kalshi_test_connection()
        balance = max(0.0, float(dollars or 0.0))
    except Exception:
        return 0.0
    levels = max(1, int(st.session_state.auto_max_levels))
    weights = sum(2 ** i for i in range(levels)) if st.session_state.auto_martingale else levels
    return math.floor(((balance * 0.90) / max(weights, 1)) * 100) / 100.0

def _amount_for_level():
    if st.session_state.get("amount_mode") == "Automático":
        base = _automatic_base_amount()
    else:
        base = max(0.01, float(st.session_state.auto_amount))
    level = max(1, int(st.session_state.auto_level))
    return base * (2 ** (level - 1)) if st.session_state.auto_martingale else base

def _direction_for_level(signal_direction):
    level = max(1, int(st.session_state.auto_level))
    choice = st.session_state.get(f"auto_level_direction_{level}", "Seguir señal")
    if choice == "Solo UP":
        return "UP"
    if choice == "Solo DOWN":
        return "DOWN"
    return signal_direction

def _contracts_for_amount(amount, contract_price):
    if contract_price is None or contract_price <= 0:
        return 0.0
    # Fixed-point quantity; never intentionally exceeds configured premium.
    return math.floor((amount / contract_price) * 100) / 100.0

def kalshi_place_entry(ticker, direction, market):
    limit = max(1, min(99, int(st.session_state.auto_limit_cents))) / 100.0
    yes_ask, no_ask = _market_contract_prices(market)
    observed = yes_ask if direction == "UP" else no_ask
    if observed is not None and observed > limit:
        return {"skipped": True, "reason": f"{direction} está a {observed*100:.1f}¢ > límite {limit*100:.0f}¢"}

    amount = _amount_for_level()
    contract_price = min(observed, limit) if observed is not None else limit
    count = _contracts_for_amount(amount, contract_price)
    if count < 0.01:
        return {"skipped": True, "reason": "Monto demasiado pequeño para el precio actual."}

    # V2 is a single YES book:
    # UP = buy YES -> bid at max YES price.
    # DOWN = buy NO -> economically equivalent to ask YES at 1 - max NO price.
    if direction == "UP":
        side = "bid"
        yes_price = limit
    else:
        side = "ask"
        yes_price = 1.0 - limit

    client_id = f"btc461-{ticker}-{direction}-L{st.session_state.auto_level}"
    payload = {
        "ticker": ticker,
        "client_order_id": client_id[:64],
        "side": side,
        "count": f"{count:.2f}",
        "price": f"{yes_price:.4f}",
        "time_in_force": "immediate_or_cancel",
        "self_trade_prevention_type": "taker_at_cross",
        "cancel_order_on_pause": True,
    }
    result = kalshi_private_request("POST", "/portfolio/events/orders", payload)
    result["_direction"] = direction
    result["_requested_count"] = count
    result["_amount_level"] = amount
    result["_entry_contract_price"] = contract_price
    result["_ticker"] = ticker
    result["_level"] = int(st.session_state.auto_level)
    return result

def kalshi_place_take_profit(entry):
    try:
        filled = float(entry.get("fill_count") or entry.get("fill_count_fp") or 0)
    except Exception:
        filled = 0.0
    if filled <= 0:
        return None

    direction = entry["_direction"]
    p = float(entry["_entry_contract_price"])
    tp = max(0, float(st.session_state.auto_take_profit)) / 100.0
    desired_contract_exit = min(0.99, p * (1.0 + tp))

    if direction == "UP":
        # Close long YES by selling YES.
        side = "ask"
        yes_exit = desired_contract_exit
    else:
        # Close long NO / short YES by buying YES back at complement.
        side = "bid"
        yes_exit = max(0.01, 1.0 - desired_contract_exit)

    payload = {
        "ticker": entry["_ticker"],
        "client_order_id": (f"tp-{entry['_ticker']}-{entry['_direction']}-L{entry['_level']}")[:64],
        "side": side,
        "count": f"{filled:.2f}",
        "price": f"{yes_exit:.4f}",
        "time_in_force": "good_till_canceled",
        "self_trade_prevention_type": "taker_at_cross",
        "reduce_only": True,
        "cancel_order_on_pause": True,
    }
    return kalshi_private_request("POST", "/portfolio/events/orders", payload)

def _public_market_by_ticker(ticker):
    r = requests.get(
        f"{KALSHI_API_BASE}{KALSHI_API_PREFIX}/markets/{ticker}",
        timeout=6,
        headers={"User-Agent": "BTCSignal/4.6.1"},
    )
    r.raise_for_status()
    j = r.json()
    return j.get("market", j)

def auto_check_previous_result(current_ticker):
    prev = st.session_state.get("auto_last_order")
    if not prev or prev.get("_resolved"):
        return
    old_ticker = prev.get("_ticker")
    if not old_ticker or old_ticker == current_ticker:
        return
    try:
        old_market = _public_market_by_ticker(old_ticker)
        result = str(old_market.get("result", "")).lower()
        if result not in ("yes", "no"):
            return
        won = (prev.get("_direction") == "UP" and result == "yes") or \
              (prev.get("_direction") == "DOWN" and result == "no")
        prev["_resolved"] = True
        prev["_won"] = won
        if won:
            st.session_state.auto_level = 1
            st.session_state.auto_last_status = "WIN · MARTINGALA REINICIADA"
            if st.session_state.auto_stop_after_win:
                st.session_state.auto_enabled = False
                st.session_state.auto_last_status = "WIN · AUTO APAGADO"
        else:
            if st.session_state.auto_martingale:
                st.session_state.auto_level = min(
                    int(st.session_state.auto_level) + 1,
                    int(st.session_state.auto_max_levels),
                )
            st.session_state.auto_last_status = f"LOSS · NIVEL {st.session_state.auto_level}"
    except Exception:
        pass

def auto_trade_tick(ticker, market, round_signal):
    if not st.session_state.get("auto_enabled"):
        return
    if not st.session_state.get("kalshi_auth_ok"):
        st.session_state.auto_enabled = False
        st.session_state.auto_last_status = "AUTO APAGADO · KALSHI NO CONECTADO"
        return
    if not ticker or ticker == "--":
        return

    auto_check_previous_result(ticker)

    direction = round_signal.get("decision")
    if direction not in ("UP", "DOWN"):
        return
    direction = _direction_for_level(direction)

    # One entry maximum per Kalshi round.
    if st.session_state.get("auto_last_ticker") == ticker:
        return

    try:
        result = kalshi_place_entry(ticker, direction, market)
        if result.get("skipped"):
            st.session_state.auto_last_status = "ESPERANDO · " + result["reason"]
            return

        st.session_state.auto_last_ticker = ticker
        st.session_state.auto_last_order = result
        st.session_state.auto_history.append({
            "ticker": ticker,
            "direction": direction,
            "level": int(st.session_state.auto_level),
            "time": datetime.now(timezone.utc).isoformat(),
            "order_id": result.get("order_id"),
        })
        filled = float(result.get("fill_count") or 0)
        if filled > 0:
            st.session_state.auto_last_status = f"FILLED {direction} · {filled:.2f} contratos"
            try:
                tp_order = kalshi_place_take_profit(result)
                if tp_order:
                    result["_tp_order_id"] = tp_order.get("order_id")
            except Exception as e:
                result["_tp_error"] = str(e)
        else:
            st.session_state.auto_last_status = f"ORDEN {direction} ENVIADA · SIN FILL"
    except Exception as e:
        st.session_state.auto_last_status = "ERROR AUTO · " + str(e)[:180]

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


# CLEAN MOBILE FRONTEND — MOTOR v4.6.1 INTACTO
# =========================================================

def _page():
    if 'ui_page' not in st.session_state: st.session_state.ui_page='Bot'
    return st.session_state.ui_page

def _go(name):
    st.session_state.ui_page=name
    st.rerun()

def _closed_markets_real():
    """Últimos mercados KXBTC15M resueltos; nunca fabrica resultados."""
    try:
        r=requests.get(KALSHI_API_BASE+KALSHI_API_PREFIX+'/markets',params={'series_ticker':'KXBTC15M','status':'settled','limit':10},timeout=8)
        r.raise_for_status(); ms=r.json().get('markets',[])
        out=[]
        for m in reversed(ms):
            res=str(m.get('result','')).lower()
            if res=='yes': out.append('UP')
            elif res=='no': out.append('DOWN')
        return out[-10:]
    except Exception:
        return []

def _round_times(market):
    if not market: return '--'
    raw=market.get('close_time') or market.get('expected_expiration_time') or market.get('expiration_time')
    if not raw: return '--'
    try:
        close_dt=pd.to_datetime(raw,utc=True).to_pydatetime().astimezone()
        start_dt=close_dt-pd.Timedelta(minutes=15)
        return f"{start_dt.strftime('%-I:%M %p')} → {close_dt.strftime('%-I:%M %p')}"
    except Exception: return '--'

def _line_chart(df, live, target, seconds_left):
    if df is None or len(df)==0 or live is None: return '<div class="chart-empty">Esperando datos BTC…</div>'
    d=df.tail(16).copy(); vals=[float(x) for x in d['close'].tolist()]
    if vals: vals[-1]=float(live)
    allv=vals+([float(target)] if target else [])
    lo,hi=min(allv),max(allv); pad=max((hi-lo)*.12,8); lo-=pad; hi+=pad
    W,H=720,430; L,R,T,B=18,94,24,34; cw=W-L-R; ch=H-T-B
    # mobile chart: samples always fill the plot width.
    frac=1.0
    n=len(vals); pts=[]
    for i,v in enumerate(vals):
        x=L+(cw*frac)*(i/max(1,n-1)); y=T+(hi-v)/(hi-lo)*ch; pts.append((x,y))
    path=' '.join(('M' if i==0 else 'L')+f'{x:.1f},{y:.1f}' for i,(x,y) in enumerate(pts))
    ex,ey=pts[-1]; base=T+ch
    area=path+f' L{ex:.1f},{base:.1f} L{pts[0][0]:.1f},{base:.1f} Z'
    below=live < target if target else False; c='#ff626b' if below else '#31d995'; fill='rgba(255,98,107,.25)' if below else 'rgba(49,217,149,.22)'
    ty=T+(hi-target)/(hi-lo)*ch if target else None
    ticks=[]
    for j in range(4):
        v=hi-(hi-lo)*j/3; y=T+ch*j/3; ticks.append(f'<text x="{W-4}" y="{y+5:.1f}" text-anchor="end">${v:,.0f}</text>')
    tline=f'<line x1="{L}" y1="{ty:.1f}" x2="{L+cw}" y2="{ty:.1f}" class="targetline"/><rect x="292" y="{ty-16:.1f}" width="105" height="30" rx="3" class="targetbg"/><text x="344" y="{ty+5:.1f}" text-anchor="middle" class="targettxt">TARGET ⌃</text>' if target else ''
    return f'''<div class="chartwrap"><svg viewBox="0 0 {W} {H}" preserveAspectRatio="none"><g class="axis">{''.join(ticks)}</g>{tline}<path d="{area}" fill="{fill}"/><path d="{path}" fill="none" stroke="{c}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/><circle cx="{ex}" cy="{ey}" r="20" fill="none" stroke="{c}" opacity=".18" stroke-width="5"/><circle cx="{ex}" cy="{ey}" r="10" fill="{c}" stroke="#08110e" stroke-width="4"/></svg><div class="times"><span>Inicio</span><span>+5 min</span><span>+10 min</span><span>Ahora</span></div></div>'''

def _nav():
    cols=st.columns(4,gap='small')
    for c,name,ico in zip(cols,['Bot','Operaciones','Saldo','Ajustes'],['⚙','↗','▣','⚙']):
        with c:
            if st.button(f'{ico}\n{name}',key='nav_'+name,use_container_width=True): _go(name)

def _fetch_state():
    btc_df=market=live=None; err=''
    try: btc_df=add_indicators(get_btc_data())
    except Exception as e: err=str(e)
    try: market=get_kalshi_btc_market()
    except Exception: pass
    try:
        live=get_kalshi_live_btc(market) if market else None
    except Exception: live=None
    if live is None:
        try: live=get_btc_live_price()
        except Exception: live=float(btc_df.iloc[-1]['close']) if btc_df is not None else None
    target=get_target_from_market(market) if market else None
    sec=get_seconds_remaining(market) if market else None
    ticker=market.get('ticker','--') if market else '--'
    sig=build_signal(btc_df,target,sec,live) if btc_df is not None else {'price':live or 0,'final_score':0,'up_probability':50,'down_probability':50,'mom3':0,'distance':None,'distance_pct':None,'ema':'N/A','rsi':50}
    rs=process_round_signal(ticker,sig,market,sec)
    auto_trade_tick(ticker,market,rs)
    return btc_df,market,live,target,sec,ticker,sig,rs,err

st.markdown('''<style>
/* SINGLE CLEAN MOBILE LAYOUT */
html,body,[data-testid="stAppViewContainer"],.stApp{background:#020806!important;color:#eef3f0!important}
[data-testid="stHeader"],#MainMenu,footer{display:none!important}
.block-container{max-width:430px!important;padding:10px 12px 105px!important}
*{box-sizing:border-box}.c2{font-family:Arial,sans-serif}.c2top{display:flex;justify-content:space-between;align-items:flex-start;margin:8px 2px 20px}.coin{display:flex;gap:12px;align-items:center}.btcball{width:48px;height:48px;border-radius:50%;background:#ff9418;color:#080b09;display:grid;place-items:center;font-size:31px;font-weight:900}.pair small,.autohead small{display:block;color:#8c9a94;font-weight:800;letter-spacing:.7px;font-size:10px}.pair b{font-size:25px}.autohead{text-align:center}.autostat{font-size:10px;color:#ff626b;font-weight:900;margin-top:4px}.stats{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:0 2px 8px}.stat:first-child{border-right:1px solid #52605b}.stat label{display:block;color:#8c9a94;font-weight:900;font-size:11px;letter-spacing:.5px}.stat .price{font-size:28px;font-weight:900;margin:10px 0 7px}.stat .sub{font-size:12px;font-weight:800}.red{color:#ff626b}.green{color:#32d995}.count{font-size:22px;font-weight:900;margin-top:15px}.live-dot{float:right;color:#dce5e1;font-size:11px}.live-dot i{display:inline-block;width:9px;height:9px;border-radius:50%;background:#24c987;margin-right:6px}.chartwrap{height:315px;margin-top:0}.chartwrap svg{width:100%;height:282px;overflow:visible}.axis text{fill:#81908a;font-size:13px;font-weight:700}.targetline{stroke:#91a09b;stroke-width:2;stroke-dasharray:5 7}.targetbg{fill:#020806}.targettxt{fill:#91a09b;font-size:14px;font-weight:900}.times{display:flex;justify-content:space-between;color:#78867f;font-size:9px;padding:0 12px}.past{display:flex;align-items:center;gap:7px;margin:4px 2px 12px;color:#89968f;font-size:10px;font-weight:900}.tri.up{color:#31d995}.tri.down{color:#ff626b}.signalcard{border:1px solid #075c3c;border-radius:14px;background:#03130e;padding:14px 12px;margin:0 2px 16px}.sighead{display:flex;align-items:center;gap:10px}.sigicon{width:42px;height:42px;border:1px solid #00a967;border-radius:11px;display:grid;place-items:center;color:#26d98e}.sigtitle small{color:#28d894;font-size:9px;font-weight:900;letter-spacing:1.4px}.sigtitle b{display:block;font-size:23px}.sigbody{border:1px solid #34453f;border-radius:12px;padding:13px;margin-top:10px}.sigbody small{color:#8b9892;font-size:9px;font-weight:900}.sigword{font-size:25px;font-weight:900;margin:12px 0 8px}.sigdesc{color:#aab5b0;font-size:10px;font-weight:700}.page-title{font-size:22px;font-weight:900;margin:12px 0 28px}.section-title{font-size:16px;font-weight:900;letter-spacing:1px;margin:26px 0 14px}.settingrow{display:grid;grid-template-columns:1.5fr .8fr;gap:14px;align-items:center;margin:15px 0}.settingrow b{font-size:13px}.settingrow p{font-size:9px;color:#84928c;margin:4px 0}.profile{display:flex;align-items:center;gap:16px;margin:30px 0 55px}.avatar{width:66px;height:66px;border-radius:50%;border:1px solid #9ba6a2;display:grid;place-items:center;color:#2ed18b;font-size:20px;font-weight:900}.menurow{font-size:17px;font-weight:800;padding:21px 5px;border-bottom:0}.menurow span{float:right;color:#2ed18b;font-size:26px}.balancebox{border:1px solid #39433f;border-radius:16px;padding:22px 16px;height:410px;background:#070d0b}.balancebig{font-size:42px;font-weight:900}.risk{border:1px solid #665100;border-radius:10px;padding:12px;color:#c9b55a;font-size:9px;margin-top:14px}.connbox{border:1px solid #34433d;border-radius:14px;padding:18px;margin-bottom:12px}.connected{color:#2bd18b;font-weight:900}.latency{border:1px solid #08754a;border-radius:12px;padding:18px;height:160px;background:linear-gradient(#062018,#06110d)}
/* native controls: dark mobile look */
.stButton>button{background:transparent!important;border:0!important;color:#dfe8e4!important;border-radius:10px!important;min-height:40px!important;font-weight:800!important}.stButton>button:hover{color:#2bd18b!important;border:0!important}.st-key-auto_power{position:absolute!important;top:42px!important;right:38px!important;width:58px!important;z-index:30}.st-key-auto_power button{width:58px!important;height:58px!important;min-height:58px!important;border-radius:50%!important;border:1.5px solid #8d3f43!important;background:#0b1110!important;color:#ff626b!important;font-size:28px!important;padding:0!important}.st-key-auto_power button:hover{border:1.5px solid #ff626b!important;color:#ff626b!important}.st-key-nav_Bot,.st-key-nav_Operaciones,.st-key-nav_Saldo,.st-key-nav_Ajustes{position:fixed!important;bottom:16px!important;z-index:9999!important;width:24%!important;background:#020806!important;border-top:1px solid #26312d!important;padding-top:8px!important}.st-key-nav_Bot{left:2%!important}.st-key-nav_Operaciones{left:26%!important}.st-key-nav_Saldo{left:50%!important}.st-key-nav_Ajustes{left:74%!important}.st-key-nav_Bot button,.st-key-nav_Operaciones button,.st-key-nav_Saldo button,.st-key-nav_Ajustes button{font-size:11px!important;line-height:1.25!important;color:#87928e!important;min-height:54px!important}.st-key-nav_Bot button{color:#27d991!important}.stSelectbox>div>div,.stNumberInput>div>div>input,.stTextInput input,.stTextArea textarea{background:#070b0a!important;color:#eef3f0!important;border-color:#343d39!important}.stToggle label{color:#eef3f0!important}.navfix{height:1px}

/* mobile corrections */
.block-container{max-width:430px!important;padding:10px 12px 132px!important;overflow-x:hidden!important}
.chartwrap{height:328px!important;margin-top:2px!important}.chartwrap svg{height:294px!important}
.signalcard{position:relative!important;margin:8px 2px 22px!important;padding:12px!important;background:#03130e!important;border:1px solid #0a6446!important;border-radius:14px!important}
.st-key-signal_card_real{border:1px solid #075c3c!important;border-radius:14px!important;background:#03130e!important;padding:13px 12px 14px!important;margin:0 2px 16px!important;overflow:visible!important}
.st-key-signal_card_real [data-testid="stHorizontalBlock"]{align-items:center!important;gap:8px!important}
.st-key-signal_card_real .stToggle{display:flex!important;justify-content:flex-end!important;margin:0!important}
.st-key-signal_card_real .stToggle>label{margin:0!important}
.signal-title-real{display:flex;align-items:center;gap:10px;min-height:48px}.signal-title-real small{display:block;color:#28d894;font-size:9px;font-weight:900;letter-spacing:1.4px}.signal-title-real b{display:block;font-size:23px;line-height:1.05}.sigicon-real{width:42px;height:42px;flex:0 0 42px;border:1px solid #00a967;border-radius:11px;display:grid;place-items:center;color:#26d98e;font-size:20px}.sigbody-real{background:#020a08;border:1px solid #33453f;border-radius:12px;padding:13px 12px;margin-top:9px}.sigbody-real small{color:#8b9892;font-size:9px;font-weight:900}
.st-key-nav_Bot,.st-key-nav_Operaciones,.st-key-nav_Saldo,.st-key-nav_Ajustes{position:fixed!important;bottom:0!important;z-index:9999!important;width:25%!important;height:78px!important;background:#020806!important;border-top:1px solid #26312d!important;padding:7px 2px 10px!important;margin:0!important}
.st-key-nav_Bot{left:0!important}.st-key-nav_Operaciones{left:25%!important}.st-key-nav_Saldo{left:50%!important}.st-key-nav_Ajustes{left:75%!important}
.st-key-nav_Bot button,.st-key-nav_Operaciones button,.st-key-nav_Saldo button,.st-key-nav_Ajustes button{width:100%!important;min-width:0!important;height:58px!important;min-height:58px!important;padding:3px 0!important;font-size:9px!important;line-height:1.10!important;white-space:pre-line!important;word-break:normal!important;overflow:visible!important;text-overflow:clip!important;border:0!important;background:transparent!important}
.st-key-auto_power{top:38px!important;right:40px!important;width:54px!important}.st-key-auto_power button{width:54px!important;height:54px!important;min-height:54px!important;font-size:24px!important}


/* screenshot-verified fixes */
.st-key-signal_card_real .st-key-signal_mode{height:auto!important;min-height:44px!important;display:flex!important;align-items:center!important;justify-content:flex-end!important;position:static!important;overflow:visible!important}
.st-key-signal_card_real .st-key-signal_mode>div{position:static!important;width:auto!important;display:flex!important;justify-content:flex-end!important}
.st-key-signal_card_real [data-testid="stToggle"]{visibility:visible!important;opacity:1!important;display:flex!important;justify-content:flex-end!important}
.sigbody-top{display:flex;align-items:center;justify-content:space-between}.minusbtn{width:28px;height:28px;border:1px solid #33453f;border-radius:9px;display:grid;place-items:center;color:#89968f;font-size:18px}.sigdesc{line-height:1.35!important}

/* FINAL iPHONE LOCK — keep signal header on ONE ROW */
@media (max-width: 640px){
  .st-key-signal_card_real [data-testid="stHorizontalBlock"]{
    display:flex!important;
    flex-direction:row!important;
    flex-wrap:nowrap!important;
    align-items:center!important;
    width:100%!important;
    gap:8px!important;
  }
  .st-key-signal_card_real [data-testid="column"]:first-child{
    width:calc(100% - 76px)!important;
    flex:1 1 auto!important;
    min-width:0!important;
  }
  .st-key-signal_card_real [data-testid="column"]:last-child{
    width:68px!important;
    flex:0 0 68px!important;
    min-width:68px!important;
  }
  .st-key-signal_card_real .st-key-signal_mode,
  .st-key-signal_card_real .st-key-signal_mode>div,
  .st-key-signal_card_real [data-testid="stToggle"]{
    width:68px!important;
    min-width:68px!important;
    height:44px!important;
    min-height:44px!important;
    display:flex!important;
    position:static!important;
    align-items:center!important;
    justify-content:flex-end!important;
    visibility:visible!important;
    opacity:1!important;
    margin:0!important;
    padding:0!important;
  }
  .st-key-signal_card_real{padding:12px!important;}
  .sigbody-real{margin-top:8px!important;}
  .signal-title-real b{font-size:22px!important;white-space:nowrap!important;}
}
.levelcard{display:flex;gap:16px;align-items:center;border:1px solid #21483a;border-radius:12px;padding:12px 14px;background:#06110d;margin-top:8px}.levelcard small,.levelcard b{display:block}.levelcard b{font-size:18px}.levelnum{width:38px;height:38px;border:2px solid #20dc95;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:900}.progressbox{border:1px solid #21483a;border-radius:12px;padding:14px;margin-top:14px;background:#06110d}.pnodes{display:flex;align-items:center;gap:7px;overflow-x:auto;padding:8px 0}.pnode{min-width:34px;height:34px;border:2px solid #5d6d67;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-weight:900}.pnode.current{border-color:#ffd34f;color:#ffd34f;box-shadow:0 0 14px rgba(255,211,79,.45)}.pnode.done{border-color:#20dc95;color:#20dc95}.parrow{color:#65736e}.progressmeta{display:flex;justify-content:space-between;margin-top:14px;color:#8f9c97}.progressmeta b{color:#f4f7f5;font-size:20px}
</style>''',unsafe_allow_html=True)

@st.fragment(run_every='1s')
def bot_page():
    btc_df,market,live,target,sec,ticker,sig,rs,err=_fetch_state()
    state=rs.get('round_state') or {}; active=state.get('active_direction'); enabled=bool(st.session_state.get('signal_mode',False))
    delta=(live-target) if live is not None and target is not None else 0; pct=(delta/target*100) if target else 0
    auto=bool(st.session_state.auto_enabled)
    st.markdown(f'''<div class="c2"><div class="c2top"><div class="coin"><div class="btcball">₿</div><div class="pair"><small>BTC · 15 MIN</small><b>BTC/USD ▼</b></div></div><div class="autohead"><small>TRADING AUTOMÁTICO</small></div></div>''',unsafe_allow_html=True)
    # real auto button, positioned visually just below heading on right
    if st.button('⏻',key='auto_power'):
        if auto: st.session_state.auto_enabled=False
        elif st.session_state.kalshi_auth_ok: st.session_state.auto_enabled=True
        else: st.toast('Conecta Kalshi primero')
        st.rerun()
    auto=bool(st.session_state.auto_enabled)
    st.markdown(f'''<div style="text-align:right;margin-top:-7px;margin-bottom:2px" class="autostat">● {'ENCENDIDO' if auto else 'OFF'}</div><div class="stats"><div class="stat"><label>TARGET</label><div class="price">{('$'+format(target,',.2f')) if target else '--'}</div><div class="sub">Cierre {_round_times(market)}</div><div class="count">⌛ {format_countdown(sec)}</div></div><div class="stat"><label class="{'red' if delta<0 else 'green'}">CURRENT {'↓' if delta<0 else '↑'}</label><div class="price {'red' if delta<0 else 'green'}">{('$'+format(live,',.2f')) if live else '--'}</div><div class="sub {'red' if delta<0 else 'green'}">{delta:+,.2f} ({pct:+.3f}%)</div><div class="live-dot"><i></i>En vivo</div></div></div>{_line_chart(btc_df,live,target,sec)}''',unsafe_allow_html=True)
    hist=_closed_markets_real(); tris=''.join(f'<span class="tri {"up" if x=="UP" else "down"}">{"▲" if x=="UP" else "▼"}</span>' for x in hist) or '<span style="color:#66736e">Esperando resultados reales…</span>'
    st.markdown(f'<div class="past">PAST MARKETS {tris}</div>',unsafe_allow_html=True)
    # Modo Señales: componente REAL. El switch vive dentro del mismo contenedor,
    # no se posiciona encima de HTML separado (eso era lo que desaparecía en iPhone).
    with st.container(border=True, key='signal_card_real'):
        left, right = st.columns([4.6, 1.15], vertical_alignment='center')
        with left:
            st.markdown('<div class="signal-title-real"><div class="sigicon-real">⌁</div><div><small>GUÍA MANUAL</small><b>Modo Señales</b></div></div>', unsafe_allow_html=True)
        with right:
            enabled = st.toggle('Modo Señales', key='signal_mode', label_visibility='collapsed')

        if enabled and active in ('UP','DOWN'):
            prob=int(sig['up_probability'] if active=='UP' else sig['down_probability'])
            word=active
            desc=f'PROBABILIDAD DEL MOTOR v4.6.1 · {prob}%'
            col='green' if active=='UP' else 'red'
        elif enabled:
            word='ESPERANDO'
            desc='El motor v4.6.1 está analizando la ronda.'
            col=''
        else:
            word='DESACTIVADO'
            desc='Actívalo con el bot y Copy Trading apagados. La señal se confirma al iniciar el minuto 3, después de cerrar las dos primeras velas.'
            col=''
        st.markdown(f'<div class="sigbody-real"><div class="sigbody-top"><small>MERCADO ACTUAL · SEÑAL 2 VELAS</small><span class="minusbtn">−</span></div><div class="sigword {col}">{word}</div><div class="sigdesc">{desc}</div></div>', unsafe_allow_html=True)
    _nav()

def operations_page():
    st.markdown('<div class="page-title">Operaciones</div>',unsafe_allow_html=True)
    hist=st.session_state.get('auto_history',[])
    if not hist: st.info('Aún no hay operaciones automáticas registradas.')
    for x in reversed(hist[-20:]): st.write(x)
    _nav()

def balance_page():
    bal='--'
    if st.session_state.kalshi_auth_ok:
        try:
            _,b=kalshi_test_connection(); bal=b or '0.00'
        except Exception: pass
    st.markdown(f'<div class="page-title">Saldo en Kalshi</div><div class="balancebox"><small>SALDO DISPONIBLE</small><div class="balancebig">${bal}</div><div class="green" style="font-size:18px;font-weight:900">+$0.00 (+0.00%) &nbsp; <span style="color:#8b9892">Hoy</span></div></div><div class="risk">⚠ &nbsp; <b>ADVERTENCIA DE RIESGO</b><br>Los mercados de predicciones implican riesgo y pueden ocasionar pérdidas. Opera únicamente con fondos que puedas permitirte perder.</div>',unsafe_allow_html=True); _nav()

def connection_page():
    st.markdown('<div class="page-title">Conexión Kalshi</div>',unsafe_allow_html=True)
    status='CONECTADO' if st.session_state.kalshi_auth_ok else 'NO CONECTADO'
    st.markdown(f'<div class="connbox"><b>API DE OPERACIONES</b><h2>Kalshi Live</h2><span class="connected">● {status}</span></div><div class="latency"><small>LATENCIA DE API</small><h2 class="green">Diagnóstico en vivo</h2></div>',unsafe_allow_html=True)
    st.text_input('API Key ID',key='kalshi_key_id_input',placeholder='Solo para conectar o reemplazar credenciales')
    st.text_area('Clave privada PEM',key='kalshi_private_key_input',placeholder='Solo para conectar o reemplazar credenciales',height=130)
    c1,c2=st.columns(2)
    with c1:
        if st.button('Verificar y guardar',use_container_width=True):
            try:
                _,bal=kalshi_test_connection(); st.session_state.kalshi_auth_ok=True; st.session_state.kalshi_auth_message=f'Conectado · ${bal}' if bal else 'Conectado'; st.success('Kalshi conectado')
            except Exception as e: st.session_state.kalshi_auth_ok=False; st.error(str(e))
    with c2:
        if st.button('Eliminar credenciales',use_container_width=True): st.session_state.kalshi_auth_ok=False; st.session_state.auto_enabled=False
    if st.button('✕ Cerrar',use_container_width=True): _go('Ajustes')

def bot_settings_page():
    st.markdown('<div class="page-title">Ajustes del bot</div><div class="section-title">INDICADORES</div>',unsafe_allow_html=True)
    st.selectbox('Generación de señal',['Motor v4.6.1'],disabled=True, help='Conserva el cerebro original v4.6.1.')
    st.markdown('<div class="section-title">SELECCIONAR ESTRATEGIA</div>',unsafe_allow_html=True)
    st.selectbox('Administración de la operación',['Motor v4.6.1 + Martingala'],disabled=True)

    st.markdown('<div class="section-title">MONTO POR OPERACIÓN</div>',unsafe_allow_html=True)
    st.session_state.amount_mode = st.selectbox('Cálculo del monto',['Manual','Automático'], index=0 if st.session_state.amount_mode=='Manual' else 1)
    if st.session_state.amount_mode == 'Manual':
        st.session_state.auto_amount=st.number_input('Monto inicial manual ($)',min_value=.01,value=float(st.session_state.auto_amount),step=.25)
    else:
        auto_base=_automatic_base_amount() if st.session_state.kalshi_auth_ok else 0.0
        st.caption(f'Monto inicial automático (90% / niveles): ${auto_base:.2f}')

    st.session_state.auto_martingale=st.toggle('Martingala',value=bool(st.session_state.auto_martingale))
    limit_opts=[35,40,45,50,55,60]
    current_limit=int(st.session_state.auto_limit_cents)
    st.session_state.auto_limit_cents=st.selectbox('Precio de orden límite (¢)',limit_opts,index=limit_opts.index(current_limit) if current_limit in limit_opts else 2)
    tp_opts=[50,70,90,100]
    current_tp=int(st.session_state.auto_take_profit)
    st.session_state.auto_take_profit=st.selectbox('Tomar profit (%)',tp_opts,index=tp_opts.index(current_tp) if current_tp in tp_opts else 2)
    level_opts=list(range(1,13))
    current_levels=int(st.session_state.auto_max_levels)
    st.session_state.auto_max_levels=st.selectbox('Máximo de niveles',level_opts,index=level_opts.index(current_levels) if current_levels in level_opts else 2)

    if st.session_state.kalshi_auth_ok:
        try:
            _,bal=kalshi_test_connection(); balf=float(bal or 0)
        except Exception:
            balf=0.0
    else:
        balf=0.0
    auto_base=_automatic_base_amount() if st.session_state.amount_mode=='Automático' and st.session_state.kalshi_auth_ok else 0.0
    st.info(f'Saldo disponible: ${balf:.2f} · Monto inicial automático (90% / {st.session_state.auto_max_levels} niveles): ${auto_base:.2f}')

    st.markdown('<div class="section-title">ELIGE LA DIRECCIÓN</div>',unsafe_allow_html=True)
    for i in range(1,int(st.session_state.auto_max_levels)+1):
        k=f'auto_level_direction_{i}'
        st.session_state.setdefault(k,'Seguir señal')
        amount = (_automatic_base_amount() if st.session_state.amount_mode=='Automático' else float(st.session_state.auto_amount)) * (2 ** (i-1) if st.session_state.auto_martingale else 1)
        st.selectbox(('Entrada inicial' if i==1 else f'Martingala {i-1}') + f' · Nivel {i} · ${amount:.2f}',['Seguir señal','Solo UP','Solo DOWN'],key=k)

    st.markdown('<div class="section-title">CONTINUIDAD</div>',unsafe_allow_html=True)
    st.session_state.restart_martingale=st.toggle('Reiniciar martingala',value=bool(st.session_state.restart_martingale),help='Al guardar, vuelve al nivel 1 y se desactiva automáticamente.')
    st.markdown('<div class="section-title">FINALIZACIÓN</div>',unsafe_allow_html=True)
    st.session_state.auto_stop_after_win=st.toggle('Apagar bot en la próxima operación ganadora',value=bool(st.session_state.auto_stop_after_win))
    st.markdown('<div class="section-title">SONIDOS Y ALERTAS</div>',unsafe_allow_html=True)
    st.session_state.sound_power=st.toggle('Sonido al encender el bot',value=bool(st.session_state.sound_power))
    st.session_state.sound_order=st.toggle('Sonido al abrir una operación',value=bool(st.session_state.sound_order))

    c1,c2,c3=st.columns([1.25,.75,1])
    with c1:
        if st.button('RESTAURAR CONFIGURACIÓN ORIGINAL',use_container_width=True):
            st.session_state.amount_mode='Manual'; st.session_state.auto_amount=.50; st.session_state.auto_martingale=True
            st.session_state.auto_limit_cents=45; st.session_state.auto_take_profit=90; st.session_state.auto_max_levels=4
            st.session_state.auto_stop_after_win=False; st.session_state.restart_martingale=False
            st.session_state.sound_power=True; st.session_state.sound_order=True
            for i in range(1,13): st.session_state[f'auto_level_direction_{i}']='Seguir señal'
            st.session_state.auto_level=1
            st.rerun()
    with c2:
        if st.button('CANCELAR',use_container_width=True): _go('Ajustes')
    with c3:
        if st.button('GUARDAR CAMBIOS',use_container_width=True):
            if st.session_state.restart_martingale:
                st.session_state.auto_level=1
                st.session_state.restart_martingale=False
                st.session_state.auto_last_status='PROGRESIÓN REINICIADA'
            st.success('Cambios guardados')


def progression_page():
    st.markdown('<div class="page-title">Progresión y niveles</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        levels=st.selectbox('Niveles activos', list(range(1,13)), index=max(0,min(11,int(st.session_state.auto_max_levels)-1)), key='progress_levels')
        st.session_state.auto_max_levels=int(levels)
    with c2: st.metric('Total disponible','12')
    base=_automatic_base_amount() if st.session_state.amount_mode=='Automático' else max(.01,float(st.session_state.auto_amount))
    total=0.0
    for i in range(1,int(st.session_state.auto_max_levels)+1):
        amount=base*(2**(i-1) if st.session_state.auto_martingale else 1); total+=amount
        st.markdown(f'<div class="levelcard"><span class="levelnum">{i}</span><span><small>Nivel {i}</small><b>${amount:.2f}</b></span></div>',unsafe_allow_html=True)
        k=f'auto_level_direction_{i}'; st.session_state.setdefault(k,'Seguir señal')
        st.selectbox(f'Dirección nivel {i}',['Seguir señal','Solo UP','Solo DOWN'],key=k,label_visibility='collapsed')
    current=max(1,min(int(st.session_state.auto_level),int(st.session_state.auto_max_levels)))
    parts=[]
    for i in range(1,int(st.session_state.auto_max_levels)+1):
        cls='current' if i==current else ('done' if i<current else '')
        parts.append(f'<span class="pnode {cls}">{i}</span>')
        if i<int(st.session_state.auto_max_levels): parts.append('<span class="parrow">→</span>')
    nodes=''.join(parts)
    st.markdown(f'<div class="progressbox"><h3>Vista de progresión</h3><div class="pnodes">{nodes}</div><div class="progressmeta"><span>Monto total posible<br><b>${total:.2f}</b></span><span>Nivel actual<br><b>{current}/{st.session_state.auto_max_levels}</b></span></div></div>',unsafe_allow_html=True)
    if st.button('RESTAURAR PROGRESIÓN',use_container_width=True):
        st.session_state.auto_level=1; st.session_state.auto_last_status='PROGRESIÓN REINICIADA'; st.rerun()
    if st.button('← Volver a Ajustes',use_container_width=True): _go('Ajustes')


def settings_page():
    st.markdown('<div class="page-title">Ajustes</div><div class="profile"><div class="avatar">CA</div><div><span class="green"><b>Mi perfil</b></span><h2 style="margin:4px 0">Mi perfil</h2><span style="color:#83908a">Editar perfil</span></div></div>',unsafe_allow_html=True)
    if st.button('⚙  Ajustes del bot     ›',use_container_width=True): _go('AjustesBot')
    st.markdown('<div class="menurow">📈 &nbsp; Top Traders <span>›</span></div>',unsafe_allow_html=True)
    if st.button('🔗  Conexión Kalshi     ›',use_container_width=True): _go('Conexion')
    if st.button('◉  Progresión y niveles     ›',use_container_width=True): _go('Progresion')
    st.markdown('<div class="menurow">✈ &nbsp; Alertas Telegram <span>›</span></div><div class="menurow">▣ &nbsp; Suscripción <span>›</span></div><div class="menurow">▤ &nbsp; Términos y Condiciones <span>›</span></div><div class="menurow">ⓘ &nbsp; Acerca del bot <span>›</span></div>',unsafe_allow_html=True)
    _nav()

p=_page()
if p=='Bot': bot_page()
elif p=='Operaciones': operations_page()
elif p=='Saldo': balance_page()
elif p=='Ajustes': settings_page()
elif p=='Conexion': connection_page()
elif p=='AjustesBot': bot_settings_page()
elif p=='Progresion': progression_page()

# NOTE: final mobile CSS is injected above page rendering in the source; this marker is intentionally inert.
