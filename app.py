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
import plotly.graph_objects as go

# =========================================================
# MACALY + ALPHA BOT v4.6.1 • MOBILE PRO UI
# BTC 15 MIN • SAME v4.6.1 SIGNAL ENGINE + CRITIK2 LOOK
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
# DISEÑO MOBILE estilo CRITIK2
# =========================================================

st.markdown(
    """
<style>
#MainMenu, footer, header {visibility:hidden;}
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {display:none;}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background-color: #000000 !important;
    color: #f6f7f6;
}

.block-container {
    max-width: 430px !important;
    padding: 10px 12px 30px !important;
}

div[data-testid="stVerticalBlock"] {gap:.45rem;}

.cr-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0 10px;
}
.cr-brand {
    font-size: 16px;
    font-weight: 900;
    color: #ffffff;
}
.cr-live {
    font-size: 10px;
    color: #20d77c;
    font-weight: 800;
}

.quote-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    padding: 8px 0;
}
.qlbl {
    font-size: 10px;
    color: #8a928e;
    font-weight: 900;
}
.qval {
    font-size: 26px;
    line-height: 1.1;
    font-weight: 1000;
    margin: 4px 0;
}
.qval-target { color: #ffffff; }
.qval-current { color: #ff5662; }
.green { color: #21d779 !important; }
.red { color: #ff5662 !important; }

.past-box {
    font-size: 10px;
    color: #818985;
    font-weight: 900;
    padding: 6px 0 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.signal-card {
    border: 1px solid #155136;
    border-radius: 12px;
    background: linear-gradient(180deg, #06100b, #030806);
    padding: 12px;
    margin-top: 8px;
}
.signal-card-title {
    font-size: 10px;
    color: #20d77c;
    font-weight: 900;
    letter-spacing: 0.8px;
}
.signal-status {
    font-size: 20px;
    font-weight: 1000;
    color: #f0b72f;
    margin: 6px 0;
}
.signal-desc {
    font-size: 10px;
    color: #89938e;
    line-height: 1.35;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# SESSION STATE
# =========================================================

if "rounds" not in st.session_state:
    st.session_state.rounds = {}

if "active_ticker" not in st.session_state:
    st.session_state.active_ticker = None

if "micro_prices" not in st.session_state:
    st.session_state.micro_prices = []

if "micro_ticker" not in st.session_state:
    st.session_state.micro_ticker = None

_AUTO_DEFAULTS = {
    "kalshi_auth_ok": False,
    "kalshi_auth_message": "No conectado",
    "auto_enabled": False,
    "auto_amount": 0.50,
    "auto_limit_cents": 50,
    "auto_take_profit": 90,
    "auto_martingale": False,
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

KALSHI_API_BASE = "https://external-api.kalshi.com"
KALSHI_API_PREFIX = "/trade-api/v2"

# =========================================================
# FUNCIONES DE API KALSHI
# =========================================================

def _kalshi_sign(message):
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
    key_id = st.session_state.get("kalshi_api_key_input", "").strip()
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
    if yes_ask is None:
        y = f("yes_ask")
        yes_ask = y / 100.0 if y and y > 1 else y
    if no_ask is None:
        n = f("no_ask")
        no_ask = n / 100.0 if n and n > 1 else n
    return yes_ask, no_ask

def _amount_for_level():
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
        side = "ask"
        yes_exit = desired_contract_exit
    else:
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
# COINBASE Y MERCADO
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

    df = pd.DataFrame(data, columns=["time", "low", "high", "open", "close", "volume"])
    for col in ["low", "high", "open", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df.dropna().sort_values("time").reset_index(drop=True)

def get_btc_live_price():
    response = requests.get(
        "https://api.exchange.coinbase.com/products/BTC-USD/ticker",
        headers={"User-Agent": "MacalyAlphaBot/4.6.1", "Cache-Control": "no-cache"},
        params={"_": int(datetime.now(timezone.utc).timestamp())},
        timeout=6,
    )
    response.raise_for_status()
    price = response.json().get("price")
    return float(price)

@st.cache_data(ttl=2)
def get_kalshi_btc_market():
    response = requests.get(
        "https://external-api.kalshi.com/trade-api/v2/markets",
        params={"limit": 100, "status": "open", "series_ticker": "KXBTC15M"},
        headers={"User-Agent": "MacalyAlphaBot/4.6.1"},
        timeout=10,
    )
    response.raise_for_status()
    markets = response.json().get("markets", [])
    if not markets:
        return None
    markets.sort(key=lambda m: str(m.get("close_time") or "9999"))
    return markets[0]

def add_indicators(df):
    df = df.copy()
    close = df["close"]
    df["ema9"] = close.ewm(span=9, adjust=False).mean()
    df["ema21"] = close.ewm(span=21, adjust=False).mean()
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
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
        val = market.get(key)
        if val not in [None, ""]:
            try:
                num = float(val)
                if num > 1000:
                    return num
            except Exception:
                pass
    return None

def get_seconds_remaining(market):
    if not market or not market.get("close_time"):
        return None
    try:
        close_dt = datetime.fromisoformat(str(market["close_time"]).replace("Z", "+00:00"))
        seconds = int((close_dt - datetime.now(timezone.utc)).total_seconds())
        return max(0, seconds)
    except Exception:
        return None

def format_countdown(seconds):
    if seconds is None:
        return "--:--"
    return f"{seconds // 60:02d}:{seconds % 60:02d}"

# =========================================================
# MOTOR DE SEÑAL
# =========================================================

def build_signal(df, target, seconds_left, live_price=None):
    last = df.iloc[-1]
    candle_price = float(last["close"])
    price = float(live_price) if live_price is not None else candle_price
    rsi = float(last["rsi"])
    mom3 = float(last["mom3"]) if pd.notna(last["mom3"]) else 0.0
    mom5 = float(last["mom5"]) if pd.notna(last["mom5"]) else 0.0

    technical_score = 0.0
    if last["ema9"] > last["ema21"]: technical_score += 2.0
    else: technical_score -= 2.0

    if rsi >= 55: technical_score += 1.0
    elif rsi <= 45: technical_score -= 1.0

    distance = (price - target) if target else 0.0
    final_score = technical_score + (2.0 if distance > 0 else -2.0)

    return {
        "price": price,
        "rsi": rsi,
        "mom3": mom3,
        "final_score": final_score,
        "distance": distance,
    }

def process_round_signal(ticker, sig, market, seconds_left):
    if not ticker or ticker == "--":
        return {"decision": "ESPERANDO", "signal": "SIN RONDA"}
    
    if ticker not in st.session_state.rounds:
        st.session_state.rounds[ticker] = new_round_state(ticker, seconds_left)

    state = st.session_state.rounds[ticker]
    score = sig["final_score"]

    if score >= UP_THRESHOLD:
        state["active_direction"] = "UP"
    elif score <= DOWN_THRESHOLD:
        state["active_direction"] = "DOWN"

    active = state.get("active_direction", "ESPERANDO")
    return {"decision": active, "signal": f"SEÑAL {active}", "round_state": state}

# =========================================================
# FRONTEND CRITIK2
# =========================================================

market = None
try: market = get_kalshi_btc_market()
except Exception: pass

df_raw = None
df = None
try:
    df_raw = get_btc_data()
    df = add_indicators(df_raw)
except Exception: pass

live_price = None
try: live_price = get_btc_live_price()
except Exception: pass

target = get_target_from_market(market) or 85065.02
seconds_left = get_seconds_remaining(market)
ticker = market.get("ticker", "--") if market else "--"

sig = build_signal(df, target, seconds_left, live_price) if df is not None else {"price": live_price or 0, "final_score": 0, "distance": 0}
rs = process_round_signal(ticker, sig, market, seconds_left)
auto_trade_tick(ticker, market, rs)

# Render de Interfaz
st.markdown(
    f"""
    <div class="cr-top">
        <div class="cr-brand">BTC/USD 15M</div>
        <div class="cr-live">● EN VIVO</div>
    </div>
    <div class="quote-grid">
        <div>
            <div class="qlbl">TARGET</div>
            <div class="qval qval-target">${target:,.2f}</div>
            <div class="qlbl">⏳ Cierre: {format_countdown(seconds_left)}</div>
        </div>
        <div style="text-align: right;">
            <div class="qlbl">CURRENT {"↑" if (sig['distance'] or 0) >= 0 else "↓"}</div>
            <div class="qval qval-current">${sig['price']:,.2f}</div>
            <div class="qlbl {'green' if (sig['distance'] or 0) >= 0 else 'red'}">{sig['distance']:+,.2f}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Gráfica Roja Suave estilo Critik2
times = ["15:00", "15:05", "15:10", "15:15"]
prices = [target + 10, target - 15, target - 25, sig['price']]
fig = go.Figure()
fig.add_trace(go.Scatter(x=times, y=prices, mode='lines', line=dict(color='#ff5662', width=3, shape='spline'), fill='tozeroy', fillcolor='rgba(255, 86, 98, 0.12)'))
fig.add_shape(type="line", x0=times[0], y0=target, x1=times[-1], y1=target, line=dict(color="#818985", width=1, dash="dash"))
fig.update_layout(margin=dict(l=0, r=0, t=5, b=5), height=220, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, side='right'))
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.markdown("""
<div class="past-box">
    <span>PAST MARKETS</span>
    <span class="green">▲</span> <span class="red">▼</span> <span class="green">▲</span> <span class="red">▼▼▼▼</span> <span class="green">▲▲</span>
</div>
""", unsafe_allow_html=True)

# Panel Guía Manual
tc1, tc2 = st.columns([3, 1])
with tc1:
    st.markdown("**⚡ GUÍA MANUAL**  \n### Modo Señales")
with tc2:
    st.toggle("", value=False, key="main_sig_toggle")

st.markdown(
    f"""
    <div class="signal-card">
        <div class="signal-card-title">MERCADO ACTUAL · SEÑAL v4.6.1</div>
        <div class="signal-status" style="color: {'#20d77c' if rs['decision']=='UP' else '#ff5662' if rs['decision']=='DOWN' else '#f0b72f'}">
            {rs['decision']}
        </div>
        <div class="signal-desc">
            Score actual: {sig['final_score']:+.2f} | Disparador automático activo sobre la cuenta de Kalshi.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar para Configurar Kalshi
with st.sidebar:
    st.header("⚡ Ajustes de Kalshi API")
    st.session_state.kalshi_api_key_input = st.text_input("API Key ID", value=st.session_state.get("kalshi_api_key_input", ""), type="password")
    st.session_state.kalshi_private_key_input = st.text_area("Private Key (PEM)", value=st.session_state.get("kalshi_private_key_input", ""), height=120)
    if st.button("Conectar Kalshi"):
        try:
            _, dollars = kalshi_test_connection()
            st.session_state.kalshi_auth_ok = True
            st.success(f"Conectado. Balance: ${dollars}")
        except Exception as e:
            st.session_state.kalshi_auth_ok = False
            st.error(str(e))

    st.session_state.auto_enabled = st.checkbox("Activar Auto Trading", value=st.session_state.get("auto_enabled", False))
    st.session_state.auto_amount = st.number_input("Monto ($)", value=float(st.session_state.get("auto_amount", 0.50)))

time.sleep(2)
st.rerun()
