import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import base64
import time
import uuid
import math
import subprocess
import tempfile

# =========================================================
# ALPHA AUTÓNOMO • ALPHA ENGINE v4.6.1
# BTC 15 MIN • SAME v4.6.1 SIGNAL ENGINE
# =========================================================

st.set_page_config(
    page_title="Alpha Autónomo",
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


MIAMI_TZ = ZoneInfo("America/New_York")

def _page():
    if "ui_page" not in st.session_state: st.session_state.ui_page = "Bot"
    return st.session_state.ui_page

def _go(name):
    st.session_state.ui_page=name; st.rerun()

def _round_window(market):
    if not market: return "--", "--"
    raw=market.get("close_time") or market.get("expected_expiration_time") or market.get("expiration_time")
    if not raw: return "--", "--"
    try:
        close_dt=pd.to_datetime(raw,utc=True).to_pydatetime().astimezone(MIAMI_TZ)
        start_dt=close_dt-pd.Timedelta(minutes=15)
        fmt=lambda d:d.strftime("%I:%M %p").lstrip("0")
        return fmt(start_dt),fmt(close_dt)
    except Exception: return "--", "--"

def _fetch_state():
    btc_df=market=live=None; err=""
    try: btc_df=add_indicators(get_btc_data())
    except Exception as e: err=str(e)
    try: market=get_kalshi_btc_market()
    except Exception: market=None
    try: live=get_kalshi_live_btc(market) if market else None
    except Exception: live=None
    if live is None:
        try: live=get_btc_live_price()
        except Exception: live=float(btc_df.iloc[-1]["close"]) if btc_df is not None and len(btc_df) else None
    target=get_target_from_market(market) if market else None
    sec=get_seconds_remaining(market) if market else None
    ticker=market.get("ticker","--") if market else "--"
    sig=build_signal(btc_df,target,sec,live) if btc_df is not None else {"price":live or 0,"final_score":0,"up_probability":50,"down_probability":50,"mom3":0,"mom5":0,"distance":None,"distance_pct":None,"ema":"N/A","rsi":50,"vol_ratio":1.0,"momentum":"NEUTRAL"}
    rs=process_round_signal(ticker,sig,market,sec)
    auto_trade_tick(ticker,market,rs)
    return btc_df,market,live,target,sec,ticker,sig,rs,err

def _sparkline_svg(df,live,target):
    if df is None or len(df)<2 or live is None: return '<div class="empty-chart">Esperando datos BTC…</div>'
    vals=[float(v) for v in df.tail(24)["close"].tolist()]; vals[-1]=float(live)
    allv=vals+([float(target)] if target else []); lo,hi=min(allv),max(allv); pad=max((hi-lo)*.15,8); lo-=pad; hi+=pad
    W,H,L,R,T,B=660,220,12,64,12,20; cw,ch=W-L-R,H-T-B; pts=[]
    for i,v in enumerate(vals):
        x=L+cw*i/max(1,len(vals)-1); y=T+(hi-v)/(hi-lo)*ch; pts.append((x,y))
    path=' '.join(("M" if i==0 else "L")+f"{x:.1f},{y:.1f}" for i,(x,y) in enumerate(pts)); ex,ey=pts[-1]
    color="#ff5f6d" if target and live<target else "#31d995"; target_line=""
    if target:
        ty=T+(hi-float(target))/(hi-lo)*ch
        target_line=f'<line x1="{L}" y1="{ty:.1f}" x2="{L+cw}" y2="{ty:.1f}" class="tline"/><text x="{L+cw-8}" y="{ty-6:.1f}" text-anchor="end" class="ttxt">TARGET</text>'
    return f'<div class="chart"><svg viewBox="0 0 {W} {H}" preserveAspectRatio="none">{target_line}<path d="{path}" fill="none" stroke="{color}" stroke-width="4" stroke-linejoin="round"/><circle cx="{ex}" cy="{ey}" r="7" fill="{color}"/></svg><div class="chartlabels"><span>Inicio</span><span>+5 min</span><span>+10 min</span><span>Ahora</span></div></div>'

def _nav():
    current=_page(); st.markdown('<div class="nav-spacer"></div>',unsafe_allow_html=True)
    cols=st.columns(4,gap="small")
    for c,(name,ico) in zip(cols,[("Bot","⌁"),("Operaciones","↗"),("Saldo","▣"),("Ajustes","⚙")]):
        with c:
            if st.button(f"{ico}\n{name}",key=f"nav_{name}",use_container_width=True,type="primary" if current==name else "secondary"): _go(name)

def _money(v): return "--" if v is None else f"${float(v):,.2f}"
def _level_amount(level):
    base=_automatic_base_amount() if st.session_state.amount_mode=="Automático" else max(.01,float(st.session_state.auto_amount))
    return base*(2**(level-1) if st.session_state.auto_martingale else 1)

st.markdown(r'''<style>
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],.stAppDeployButton{display:none!important;visibility:hidden!important}
html,body,[data-testid="stAppViewContainer"],.stApp{background:#020806!important;color:#eef4f1!important}.block-container{max-width:430px!important;padding:10px 12px 112px!important;margin:auto!important}*{box-sizing:border-box}.stApp{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}[data-testid="stVerticalBlock"]{gap:.55rem!important}
.aa-top{display:flex;justify-content:space-between;align-items:center;margin:4px 0 10px}.asset{display:flex;gap:10px;align-items:center}.btc{width:36px;height:36px;border-radius:50%;background:#f7931a;color:#111;display:grid;place-items:center;font-size:23px;font-weight:950}.asset small,.eyebrow{color:#84938c;font-size:9px;font-weight:850;letter-spacing:.8px}.asset b{display:block;font-size:17px;margin-top:1px}.kalshi-live{font-size:9px;color:#31d995;font-weight:900}.round-card{border:1px solid #214438;border-radius:12px;background:#06110d;padding:10px 12px;margin:6px 0}.round-head{display:flex;justify-content:space-between;align-items:center}.round-head b{font-size:12px}.round-head span{font-size:8px;color:#8d9b95}.round-grid{display:grid;grid-template-columns:1fr 86px;gap:8px;align-items:center;margin-top:8px}.prices{display:grid;grid-template-columns:1fr 1fr;gap:8px}.metric small{display:block;color:#82918a;font-size:8px;font-weight:850}.metric b{display:block;font-size:17px;margin-top:3px}.metric em{font-style:normal;font-size:9px}.red{color:#ff6672!important}.green{color:#31d995!important}.clock{width:76px;height:76px;border-radius:50%;border:5px solid #163d31;display:grid;place-items:center;text-align:center;box-shadow:inset 0 0 0 2px #07110e}.clock small{display:block;font-size:7px;color:#809087;font-weight:850}.clock b{font-size:17px}.chart{height:156px;margin:5px 0 8px}.chart svg{width:100%;height:136px}.tline{stroke:#73827c;stroke-width:1.4;stroke-dasharray:5 5}.ttxt{fill:#87968f;font-size:11px;font-weight:900}.chartlabels{display:flex;justify-content:space-between;color:#6f7f77;font-size:7px}.engine{border:1px solid #075c3c;border-radius:13px;background:#03130e;padding:11px;margin:8px 0}.engine-head{display:flex;justify-content:space-between;align-items:center}.engine-title small{display:block;color:#31d995;font-size:8px;font-weight:900;letter-spacing:1px}.engine-title b{font-size:18px}.signal-pill{border:1px solid #22664d;border-radius:999px;padding:4px 9px;font-size:9px;font-weight:900}.prob{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:9px 0}.probbox{background:#061b14;border-radius:9px;padding:8px}.probbox small{font-size:7px;color:#87958f}.probbox b{display:block;font-size:18px}.bar{height:5px;background:#1b2823;border-radius:9px;overflow:hidden;margin-top:4px}.bar i{display:block;height:100%;background:#31d995}.bar.redbar i{background:#ff6672}.engine-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;border-top:1px solid #173128;padding-top:8px}.engine-grid small{display:block;color:#78877f;font-size:6px}.engine-grid b{font-size:9px}.auto-card{border:1px solid #1c4738;border-radius:13px;background:#06110d;padding:11px;margin:8px 0}.auto-row{display:flex;justify-content:space-between;align-items:center}.auto-row h3{font-size:14px;margin:0}.auto-status{font-size:9px;font-weight:900}.auto-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:9px}.auto-grid small{display:block;color:#7d8c85;font-size:6px}.auto-grid b{font-size:10px}.page-title{font-size:21px;font-weight:900;margin:8px 0 16px}.section{color:#31d995;font-size:9px;font-weight:900;letter-spacing:1.1px;margin:18px 0 6px}.card{border:1px solid #253b33;border-radius:12px;background:#06100d;padding:12px;margin:7px 0}.summary{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-bottom:7px}.sum{border:1px solid #243a32;border-radius:10px;padding:9px;background:#06100d}.sum small{font-size:7px;color:#7e8c86}.sum b{display:block;font-size:16px;margin-top:3px}.op{display:grid;grid-template-columns:1.2fr .8fr .7fr .8fr;gap:5px;align-items:center;border-bottom:1px solid #17241f;padding:9px 0;font-size:9px}.op b{font-size:10px}.level-row{display:grid;grid-template-columns:38px 1fr;gap:9px;align-items:center;border:1px solid #214438;border-radius:11px;background:#06110d;padding:8px;margin:7px 0}.levelnum{width:32px;height:32px;border:2px solid #31d995;border-radius:50%;display:grid;place-items:center;font-weight:900}.progress{display:flex;gap:5px;align-items:center;overflow-x:auto;padding:8px 0}.node{min-width:29px;height:29px;border:2px solid #52625b;border-radius:50%;display:grid;place-items:center;font-size:9px;font-weight:900}.node.done{border-color:#31d995;color:#31d995}.node.current{border-color:#f5c84c;color:#f5c84c}.arrow{color:#53635c}.risk{border:1px solid #695818;border-radius:10px;color:#cbb968;padding:10px;font-size:8px}.nav-spacer{height:8px}
.st-key-nav_Bot,.st-key-nav_Operaciones,.st-key-nav_Saldo,.st-key-nav_Ajustes{position:fixed!important;bottom:max(8px,env(safe-area-inset-bottom))!important;z-index:99999!important;width:23.5%!important;background:#020806!important;padding:4px 1px!important;border-top:1px solid #1f302a!important}.st-key-nav_Bot{left:2%!important}.st-key-nav_Operaciones{left:25.5%!important}.st-key-nav_Saldo{left:49%!important}.st-key-nav_Ajustes{left:72.5%!important}.st-key-nav_Bot button,.st-key-nav_Operaciones button,.st-key-nav_Saldo button,.st-key-nav_Ajustes button{min-height:54px!important;height:54px!important;padding:2px!important;font-size:8px!important;line-height:1.2!important;white-space:pre-line!important;overflow:visible!important;border:0!important;border-radius:8px!important}.stButton>button{border-radius:10px!important;font-weight:800!important}.stButton>button[kind="primary"]{background:#0b6b47!important;border-color:#16885e!important}.stSelectbox>div>div,.stNumberInput input,.stTextInput input,.stTextArea textarea{background:#07100d!important;color:#eef4f1!important;border-color:#31423b!important}.stToggle label{color:#eef4f1!important}
@media(max-width:390px){.block-container{padding-left:9px!important;padding-right:9px!important}.metric b{font-size:15px}.engine-grid b{font-size:8px}.auto-grid b{font-size:9px}.st-key-nav_Bot button,.st-key-nav_Operaciones button,.st-key-nav_Saldo button,.st-key-nav_Ajustes button{font-size:7.5px!important}}
</style>''',unsafe_allow_html=True)

@st.fragment(run_every="1s")
def bot_page():
    btc_df,market,live,target,sec,ticker,sig,rs,err=_fetch_state(); start_s,close_s=_round_window(market)
    delta=(live-target) if live is not None and target is not None else 0.0; pct=(delta/target*100) if target else 0.0
    decision=rs.get("decision","NO TRADE"); signal=rs.get("signal",decision); up=int(round(sig.get("up_probability",50))); down=int(round(sig.get("down_probability",50))); quality=rs.get("entry_quality","--"); auto=bool(st.session_state.auto_enabled)
    st.markdown(f'''<div class="aa-top"><div class="asset"><div class="btc">₿</div><div><small>BTC/USD · 15 MIN</small><b>{_money(live)}</b></div></div><div class="kalshi-live">● KALSHI LIVE</div></div><div class="round-card"><div class="round-head"><b>Ronda {start_s} → {close_s}</b><span>{ticker}</span></div><div class="round-grid"><div class="prices"><div class="metric"><small>TARGET</small><b>{_money(target)}</b><em>Precio objetivo</em></div><div class="metric"><small>BTC ACTUAL</small><b class="{'red' if delta<0 else 'green'}">{_money(live)}</b><em class="{'red' if delta<0 else 'green'}">{delta:+,.2f} ({pct:+.3f}%)</em></div></div><div class="clock"><div><small>CIERRA EN</small><b>{format_countdown(sec)}</b></div></div></div></div>{_sparkline_svg(btc_df,live,target)}''',unsafe_allow_html=True)
    st.markdown(f'''<div class="engine"><div class="engine-head"><div class="engine-title"><small>ALPHA ENGINE</small><b>v4.6.1</b></div><div class="signal-pill">{signal}</div></div><div class="prob"><div class="probbox"><small>UP</small><b class="green">{up}%</b><div class="bar"><i style="width:{up}%"></i></div></div><div class="probbox"><small>DOWN</small><b class="red">{down}%</b><div class="bar redbar"><i style="width:{down}%"></i></div></div></div><div class="engine-grid"><div><small>EMA</small><b>{sig.get('ema','--')}</b></div><div><small>RSI</small><b>{sig.get('rsi',0):.1f}</b></div><div><small>MOMENTUM</small><b>{sig.get('momentum','--')}</b></div><div><small>CALIDAD</small><b>{quality}</b></div></div></div>''',unsafe_allow_html=True)
    amount=_amount_for_level(); level=int(st.session_state.auto_level); maxl=int(st.session_state.auto_max_levels); direction=_direction_for_level(decision) if decision in ("UP","DOWN") else "ESPERANDO"
    st.markdown(f'''<div class="auto-card"><div class="auto-row"><h3>Trading Automático</h3><span class="auto-status {'green' if auto else 'red'}">● {'ENCENDIDO' if auto else 'APAGADO'}</span></div><div class="auto-grid"><div><small>NIVEL</small><b>{level}/{maxl}</b></div><div><small>DIRECCIÓN</small><b>{direction}</b></div><div><small>PRÓXIMO MONTO</small><b>${amount:.2f}</b></div><div><small>LÍMITE / TP</small><b>{st.session_state.auto_limit_cents}¢ / +{st.session_state.auto_take_profit}%</b></div></div></div>''',unsafe_allow_html=True)
    if st.button("APAGAR BOT" if auto else "ENCENDER BOT",key="bot_power",use_container_width=True,type="primary"):
        if auto: st.session_state.auto_enabled=False; st.session_state.auto_last_status="AUTO APAGADO"
        elif st.session_state.kalshi_auth_ok: st.session_state.auto_enabled=True; st.session_state.auto_last_status="AUTO ENCENDIDO"
        else: st.toast("Conecta Kalshi primero")
        st.rerun()
    if err: st.caption("Datos BTC: "+err)
    _nav()

def operations_page():
    hist=st.session_state.get("auto_history",[]); wins=sum(1 for x in hist if x.get("_resolved") and x.get("_won")); losses=sum(1 for x in hist if x.get("_resolved") and not x.get("_won")); resolved=wins+losses; wr=(wins/resolved*100) if resolved else 0
    st.markdown('<div class="page-title">Operaciones</div>',unsafe_allow_html=True); st.markdown(f'<div class="summary"><div class="sum"><small>GANADAS</small><b class="green">{wins}</b></div><div class="sum"><small>PERDIDAS</small><b class="red">{losses}</b></div><div class="sum"><small>WIN RATE</small><b>{wr:.0f}%</b></div></div>',unsafe_allow_html=True)
    if not hist: st.markdown('<div class="card">Aún no hay operaciones registradas.</div>',unsafe_allow_html=True)
    else:
        for x in reversed(hist[-20:]):
            d=x.get("direction","--"); lev=x.get("level","--"); t=x.get("ticker","--"); result="WIN" if x.get("_won") else ("LOSS" if x.get("_resolved") else "ABIERTA"); cls="green" if result=="WIN" else ("red" if result=="LOSS" else "")
            st.markdown(f'<div class="op"><b>{d}</b><span>Nivel {lev}</span><span class="{cls}">{result}</span><span>{t[-8:]}</span></div>',unsafe_allow_html=True)
    _nav()

def balance_page():
    bal=None
    if st.session_state.kalshi_auth_ok:
        try: _,b=kalshi_test_connection(); bal=float(b or 0)
        except Exception: pass
    cls="green" if st.session_state.kalshi_auth_ok else "red"; txt="Cuenta conectada" if st.session_state.kalshi_auth_ok else "Kalshi no conectado"
    st.markdown('<div class="page-title">Saldo</div>',unsafe_allow_html=True); st.markdown(f'<div class="card"><div class="eyebrow">SALDO DISPONIBLE EN KALSHI</div><div style="font-size:38px;font-weight:950;margin:8px 0">{_money(bal)}</div><div class="{cls}">● {txt}</div></div><div class="risk"><b>ADVERTENCIA DE RIESGO</b><br>Los mercados de predicción implican riesgo y pueden ocasionar pérdidas. Las ganancias no están aseguradas.</div>',unsafe_allow_html=True); _nav()

def settings_page():
    st.markdown('<div class="page-title">Ajustes</div>',unsafe_allow_html=True)
    if st.button("⚙  Ajustes del bot",use_container_width=True): _go("AjustesBot")
    if st.button("🔗  Conexión Kalshi",use_container_width=True): _go("Conexion")
    if st.button("◉  Progresión y niveles",use_container_width=True): _go("Progresion")
    _nav()

def bot_settings_page():
    st.markdown('<div class="page-title">Ajustes del bot</div>',unsafe_allow_html=True); st.markdown('<div class="section">CEREBRO / GENERACIÓN DE SEÑAL</div>',unsafe_allow_html=True); st.selectbox("Motor",["Alpha Engine v4.6.1 (Tu bot)"],disabled=True,label_visibility="collapsed"); st.caption("EMA, RSI, Momentum, Volumen, Memoria de ronda, Confirmaciones y Probabilidades.")
    st.markdown('<div class="section">ESTRATEGIA DE OPERACIÓN</div>',unsafe_allow_html=True); st.selectbox("Estrategia",["Martingala (Personalizada)"],disabled=True,label_visibility="collapsed")
    st.markdown('<div class="section">MODO DE MONTO</div>',unsafe_allow_html=True); st.session_state.amount_mode=st.radio("Modo",["Manual","Automático"],index=0 if st.session_state.amount_mode=="Manual" else 1,horizontal=True,label_visibility="collapsed")
    if st.session_state.amount_mode=="Manual": st.session_state.auto_amount=st.number_input("Monto inicial ($)",min_value=.01,value=float(st.session_state.auto_amount),step=.25)
    else: st.caption(f"Monto inicial calculado con 90% del saldo: ${_automatic_base_amount():.2f}")
    st.markdown('<div class="section">MÁXIMO DE NIVELES</div>',unsafe_allow_html=True); st.session_state.auto_max_levels=st.selectbox("Niveles",list(range(1,13)),index=max(0,min(11,int(st.session_state.auto_max_levels)-1)),label_visibility="collapsed"); st.caption("Puedes usar de 1 hasta 12 niveles.")
    limits=list(range(5,100,5)); st.markdown('<div class="section">PRECIO LÍMITE DE ENTRADA</div>',unsafe_allow_html=True); st.session_state.auto_limit_cents=st.selectbox("Límite",limits,index=limits.index(int(st.session_state.auto_limit_cents)) if int(st.session_state.auto_limit_cents) in limits else 8,format_func=lambda x:f"{x}¢",label_visibility="collapsed")
    tp=[25,50,70,90,100,125,150,200]; st.markdown('<div class="section">TAKE PROFIT</div>',unsafe_allow_html=True); st.session_state.auto_take_profit=st.selectbox("TP",tp,index=tp.index(int(st.session_state.auto_take_profit)) if int(st.session_state.auto_take_profit) in tp else 3,format_func=lambda x:f"+{x}%",label_visibility="collapsed")
    st.markdown('<div class="section">MARTINGALA</div>',unsafe_allow_html=True); st.session_state.auto_martingale=st.toggle("Activada",value=bool(st.session_state.auto_martingale))
    if st.button("GUARDAR CAMBIOS",use_container_width=True,type="primary"): st.success("Cambios guardados")
    if st.button("← Volver",use_container_width=True): _go("Ajustes")

def connection_page():
    st.markdown('<div class="page-title">Conexión Kalshi</div>',unsafe_allow_html=True); status="CONECTADO" if st.session_state.kalshi_auth_ok else "NO CONECTADO"; cls="green" if st.session_state.kalshi_auth_ok else "red"
    st.markdown(f'<div class="card"><div class="eyebrow">API DE OPERACIONES</div><div style="display:flex;justify-content:space-between;align-items:center"><b style="font-size:18px">Kalshi Live</b><span class="{cls}">● {status}</span></div></div>',unsafe_allow_html=True)
    st.text_input("API Key ID",key="kalshi_key_id_input",placeholder="Solo para conectar o reemplazar credenciales"); st.text_area("Clave privada PEM",key="kalshi_private_key_input",placeholder="Solo para conectar o reemplazar credenciales",height=120)
    if st.button("Verificar y guardar",use_container_width=True,type="primary"):
        try: _,bal=kalshi_test_connection(); st.session_state.kalshi_auth_ok=True; st.session_state.kalshi_auth_message=f"Conectado · ${bal}" if bal else "Conectado"; st.success(st.session_state.kalshi_auth_message)
        except Exception as e: st.session_state.kalshi_auth_ok=False; st.error(str(e))
    if st.button("Eliminar credenciales",use_container_width=True): st.session_state.kalshi_auth_ok=False; st.session_state.auto_enabled=False; st.session_state.kalshi_key_id_input=""; st.session_state.kalshi_private_key_input=""; st.rerun()
    if st.button("← Volver",use_container_width=True): _go("Ajustes")

def progression_page():
    st.markdown('<div class="page-title">Progresión y niveles</div>',unsafe_allow_html=True); c1,c2=st.columns([1.3,1])
    with c1: st.session_state.auto_max_levels=st.selectbox("Niveles activos",list(range(1,13)),index=max(0,min(11,int(st.session_state.auto_max_levels)-1)),key="progress_levels")
    with c2: st.metric("Total disponible","12")
    total=0.0
    for i in range(1,int(st.session_state.auto_max_levels)+1):
        amount=_level_amount(i); total+=amount; k=f"auto_level_direction_{i}"; st.session_state.setdefault(k,"Seguir señal"); st.markdown(f'<div class="level-row"><div class="levelnum">{i}</div><div><span class="eyebrow">Nivel {i}</span><br><b>${amount:.2f}</b></div></div>',unsafe_allow_html=True); st.selectbox(f"Dirección nivel {i}",["Seguir señal","Solo UP","Solo DOWN"],key=k,label_visibility="collapsed")
    current=max(1,min(int(st.session_state.auto_level),int(st.session_state.auto_max_levels))); nodes=[]
    for i in range(1,int(st.session_state.auto_max_levels)+1):
        cls="current" if i==current else ("done" if i<current else ""); nodes.append(f'<span class="node {cls}">{i}</span>');
        if i<int(st.session_state.auto_max_levels): nodes.append('<span class="arrow">→</span>')
    st.markdown(f'<div class="card"><b>Vista de progresión</b><div class="progress">{"".join(nodes)}</div><div style="display:flex;justify-content:space-between"><span class="eyebrow">Monto total<br><b style="color:#eef4f1;font-size:16px">${total:.2f}</b></span><span class="eyebrow">Nivel actual<br><b style="color:#eef4f1;font-size:16px">{current}/{st.session_state.auto_max_levels}</b></span></div></div>',unsafe_allow_html=True)
    if st.button("RESTAURAR PROGRESIÓN",use_container_width=True): st.session_state.auto_level=1; st.rerun()
    if st.button("← Volver",use_container_width=True): _go("Ajustes")

p=_page()
if p=="Bot": bot_page()
elif p=="Operaciones": operations_page()
elif p=="Saldo": balance_page()
elif p=="Ajustes": settings_page()
elif p=="AjustesBot": bot_settings_page()
elif p=="Conexion": connection_page()
elif p=="Progresion": progression_page()
