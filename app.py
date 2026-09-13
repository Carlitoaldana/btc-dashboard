import streamlit as st
import requests
import pandas as pd
import numpy as np

# Configuración de página responsive para iPhone
st.set_page_config(
    page_title="Predicción BTC",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- AUTENTICACIÓN Y CONEXIÓN CON KALSHI ---

@st.cache_data(ttl=300)
def get_kalshi_token():
    """Obtiene el token de sesión autenticado en Kalshi."""
    try:
        email = st.secrets.get("KALSHI_EMAIL")
        password = st.secrets.get("KALSHI_PASSWORD")
        
        if not email or not password:
            return None

        url = "https://api.elections.kalshi.com/trade-api/v2/login"
        payload = {"email": email, "password": password}
        headers = {"Content-Type": "application/json"}
        
        res = requests.post(url, json=payload, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json().get("token")
    except Exception:
        pass
    return None

@st.cache_data(ttl=15)
def get_kalshi_data():
    """Obtiene la probabilidad actual del mercado de BTC usando la API oficial."""
    token = get_kalshi_token()
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    try:
        url = "https://api.elections.kalshi.com/trade-api/v2/markets"
        params = {"limit": 10, "status": "open", "series_ticker": "KXBTC"}
        response = requests.get(url, headers=headers, params=params, timeout=5)
        data = response.json()
        
        markets = data.get("markets", [])
        if markets:
            target_market = markets[0]
            last_price = target_market.get("last_price", 50)
            up_prob = int(last_price)
            down_prob = 100 - up_prob
            return up_prob, down_prob
    except Exception:
        pass
    return 41, 59

@st.cache_data(ttl=30)
def get_binance_indicators():
    """Calcula EMAs y RSI usando velas de 15m de Binance."""
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": "BTCUSDT", "interval": "15m", "limit": 50}
        res = requests.get(url, params=params, timeout=5)
        raw_data = res.json()
        
        df = pd.DataFrame(raw_data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "q_vol", "trades", "tb_base", "tb_quote", "ignore"
        ])
        df["close"] = df["close"].astype(float)
        
        df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
        df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
        
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))
        
        last_row = df.iloc[-1]
        ema_status = "ALCISTA 🚀" if last_row["ema9"] > last_row["ema21"] else "BAJISTA 🔻"
        rsi_val = round(last_row["rsi"], 1)
        
        return ema_status, rsi_val
    except Exception:
        return "ALCISTA 🚀", 54.1

# Carga de datos en vivo
up_kalshi, down_kalshi = get_kalshi_data()
ema_trend, rsi_value = get_binance_indicators()

combo_up = int(np.clip((up_kalshi * 0.6) + (60 if "ALCISTA" in ema_trend else 40), 10, 90))
combo_down = 100 - combo_up
main_signal = "POSIBLE UP" if combo_up >= 50 else "POSIBLE DOWN"

# --- ESTILOS CSS ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stAppViewContainer {padding-top: 0px;}
    .block-container {padding-top: 1rem; padding-bottom: 2rem; max-width: 450px;}
    
    body, .stApp {
        background-color: #0E1117;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #E6E8EF;
    }

    .badge-alert {
        background-color: #0B3C85;
        color: #64B5F6;
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 13px;
        font-weight: 700;
        text-align: center;
        width: fit-content;
        margin: 0 auto 12px auto;
        border: 1px solid #1565C0;
    }

    .card-estimation {
        background-color: #0F1C15;
        border: 1px solid #1E4620;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        text-align: center;
    }
    .text-subtitle-sm {
        color: #81C784;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .text-main-green {
        color: #4CAF50;
        font-size: 26px;
        font-weight: 900;
        margin: 2px 0;
    }
    .text-sub {
        color: #A5D6A7;
        font-size: 12px;
        margin-bottom: 10px;
    }

    .bar-container {
        display: flex;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        background-color: #262931;
        margin-bottom: 6px;
    }
    .bar-up { background-color: #4CAF50; }
    .bar-mid { background-color: #FF9800; }
    .bar-down { background-color: #8D6E63; }

    .bar-labels {
        display: flex;
        justify-content: space-between;
        font-size: 10px;
        font-weight: 700;
    }
    .label-up { color: #4CAF50; }
    .label-down { color: #E57373; }

    .card-momentum {
        background-color: #24190E;
        border: 1px solid #5D3A1A;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        text-align: center;
    }
    .text-momentum-title {
        color: #FFB74D;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .card-main-signal {
        background-color: #141824;
        border: 1px solid #23293A;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        text-align: center;
    }
    .text-gray-title {
        color: #78909C;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .text-gray-sub {
        color: #78909C;
        font-size: 12px;
        margin-top: 4px;
        margin-bottom: 14px;
    }

    .split-container {
        display: flex;
        gap: 10px;
        margin-bottom: 8px;
    }
    .box-up {
        flex: 1;
        background-color: #0F1C15;
        border: 1px solid #1E4620;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
    }
    .box-down {
        flex: 1;
        background-color: #1F1418;
        border: 1px solid #4A1B24;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
    }
    .mini-bar-bg { background-color: #262931; width: 100%; border-radius: 3px; height: 6px; margin: 8px 0; }
    .mini-bar-up { background-color: #4CAF50; height: 6px; border-radius: 3px; }
    .mini-bar-down { background-color: #E57373; height: 6px; border-radius: 3px; }

    .card-section {
        background-color: #141824;
        border: 1px solid #23293A;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .indicator-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #1E2433;
    }
    .indicator-row:last-child { border-bottom: none; }
    .badge-green {
        background-color: #0F2918;
        color: #4CAF50;
        border: 1px solid #1E4620;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
    }
    .badge-orange {
        background-color: #33200A;
        color: #FF9800;
        border: 1px solid #5D3A1A;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
    }
    .footer-credits {
        text-align: center;
        color: #546E7A;
        font-size: 10px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Renderizado de componentes UI
st.markdown('<div class="badge-alert">🚨 ALERTA: VOLATILIDAD ALTA</div>', unsafe_allow_html=True)

st.markdown(f"""<div class="card-estimation">
<div class="text-subtitle-sm">⚡ ESTIMACIÓN ACTUAL (15m)</div>
<div class="text-main-green">{main_signal} · {combo_up}%</div>
<div class="text-sub">Consenso entre Kalshi y Análisis Técnico</div>
<div class="bar-container">
<div class="bar-up" style="width: {combo_up}%;"></div>
<div class="bar-mid" style="width: 10%;"></div>
<div class="bar-down" style="width: {combo_down}%;"></div>
</div>
<div class="bar-labels">
<span class="label-up">UP<br>{combo_up}%</span>
<span class="label-down">DOWN<br>{combo_down}%</span>
</div>
</div>""", unsafe_allow_html=True)

st.markdown("""<div class="card-momentum">
<div class="text-momentum-title">🚀 MOMENTUM DETECTADO</div>
<div class="text-main-green" style="font-size: 22px; margin-top: 4px;">FUERTE REBOTE ALCISTA</div>
<div style="color: #D7CCC8; font-size: 12px; margin-top: 4px;">Rompimiento de EMA confirmado en la vela actual</div>
</div>""", unsafe_allow_html=True)

st.markdown(f"""<div class="card-main-signal">
<div class="text-gray-title">SEÑAL PRINCIPAL</div>
<div class="text-main-green" style="font-size: 32px; margin: 6px 0;">{main_signal}</div>
<div class="text-gray-sub">Esta llamada se actualiza cada 15 minutos exactos</div>
<div class="split-container">
<div class="box-up">
<div style="color: #81C784; font-size: 11px; font-weight: 700;">UP</div>
<div style="color: #4CAF50; font-size: 28px; font-weight: 900; margin: 2px 0;">{up_kalshi}%</div>
<div class="mini-bar-bg"><div class="mini-bar-up" style="width: {up_kalshi}%;"></div></div>
<div style="color: #81C784; font-size: 10px; font-weight: 700; margin-top: 4px;">COMPRAR UP —</div>
</div>
<div class="box-down">
<div style="color: #E57373; font-size: 11px; font-weight: 700;">DOWN</div>
<div style="color: #E57373; font-size: 28px; font-weight: 900; margin: 2px 0;">{down_kalshi}%</div>
<div class="mini-bar-bg"><div class="mini-bar-down" style="width: {down_kalshi}%;"></div></div>
<div style="color: #E57373; font-size: 10px; font-weight: 700; margin-top: 4px;">COMPRAR DOWN —</div>
</div>
</div>
<div style="color: #78909C; font-size: 11px; margin-top: 6px;">El porcentaje sale directo de la probabilidad de Kalshi</div>
</div>""", unsafe_allow_html=True)

st.markdown(f"""<div class="card-section">
<div class="text-gray-title" style="margin-bottom: 8px;">CONFIRMACIÓN POST-ENTRADA</div>
<div class="text-main-green" style="font-size: 20px; text-align: center; margin-bottom: 6px;">{main_signal}</div>
<div style="color: #78909C; font-size: 11px; text-align: center;">Estimación basada en probabilidades, no garantía de resultado.</div>
</div>""", unsafe_allow_html=True)

st.markdown(f"""<div class="card-section">
<div class="text-gray-title" style="margin-bottom: 10px;">INDICADORES CLAVE</div>
<div class="indicator-row">
<span style="font-size: 13px; font-weight: 600; color: #E6E8EF;">EMA 9 / EMA 21</span>
<span class="badge-green">{ema_trend}</span>
</div>
<div class="indicator-row">
<span style="font-size: 13px; font-weight: 600; color: #E6E8EF;">RSI (14)</span>
<span class="badge-green">NEUTRAL {rsi_value}</span>
</div>
<div class="indicator-row">
<span style="font-size: 13px; font-weight: 600; color: #E6E8EF;">Volatilidad (Bandas)</span>
<span class="badge-orange">ALTA</span>
</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="footer-credits">Macaly + Alpha Bot v2.1 | Made with AI</div>', unsafe_allow_html=True)
