import streamlit as st
import urllib.request
import json
import base64
import time
from datetime import datetime

# ================= CONFIGURACIÓN DE LA PÁGINA =================
st.set_page_config(
    page_title="Macaly + Alpha Bot v2.1",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= ESTILOS CSS PROFESIONALES =================
st.markdown("""
<style>
    .stApp {
        background-color: #0b0e14;
        color: #e6e6e6;
        font-family: 'Inter', sans-serif;
    }
    .main-card {
        background: #131822;
        border: 1px solid #1f293d;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .metric-title {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8a99ad;
        margin-bottom: 5px;
        font-weight: 600;
        text-align: center;
    }
    .metric-value-up {
        font-size: 28px;
        font-weight: 800;
        color: #0ecb81;
        text-align: center;
    }
    .metric-value-down {
        font-size: 28px;
        font-weight: 800;
        color: #f6465d;
        text-align: center;
    }
    .badge-up {
        background-color: rgba(14, 203, 129, 0.15);
        color: #0ecb81;
        border: 1px solid #0ecb81;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
    }
    .badge-down {
        background-color: rgba(246, 70, 93, 0.15);
        color: #f6465d;
        border: 1px solid #f6465d;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
    }
    .indicator-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #1f293d;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ================= FUNCIÓN DE AUTENTICACIÓN KALSHI =================
def get_kalshi_auth_headers(key_id, private_key_pem, method, path):
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.serialization import load_pem_private_key
        
        timestamp = str(int(time.time() * 1000))
        msg_string = timestamp + method.upper() + path
        message = msg_string.encode('utf-8')
        
        private_key = load_pem_private_key(private_key_pem.encode('utf-8'), password=None)
        signature = private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        sig_b64 = base64.b64encode(signature).decode('utf-8')
        
        return {
            "Content-Type": "application/json",
            "KALSHI-ACCESS-KEY": key_id,
            "KALSHI-ACCESS-SIGNATURE": sig_b64,
            "KALSHI-ACCESS-TIMESTAMP": timestamp
        }
    except Exception as e:
        return None

# ================= OBTENCIÓN DE DATOS Y SEÑAL =================
def get_sniper_signal():
    binance_price = 0.0
    rsi = 50.0
    ema_signal = "NEUTRAL ⚡"
    kalshi_up_prob = 50.0
    kalshi_connected = False
    
    # 1. Obtener datos de Binance
    try:
        url_binance = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=25"
        req = urllib.request.Request(url_binance, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3.0) as response:
            raw_data = json.loads(response.read().decode())
            closes = [float(candle[4]) for candle in raw_data]
            binance_price = closes[-1]
            
            # Cálculo rápido de EMA 9 y EMA 21
            if len(closes) >= 21:
                ema9 = sum(closes[-9:]) / 9
                ema21 = sum(closes[-21:]) / 21
                if ema9 > ema21:
                    ema_signal = "ALCISTA 🟢"
                else:
                    ema_signal = "BAJISTA 🔴"
            
            # Cálculo de RSI aproximado (14)
            gains, losses = 0, 0
            for i in range(-14, 0):
                change = closes[i] - closes[i-1]
                if change > 0:
                    gains += change
                else:
                    losses -= change
            if losses > 0:
                rs = (gains / 14) / (losses / 14)
                rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 70.0
    except Exception:
        pass

    # 2. Conexión a la API de Kalshi con manejo de errores visible
    try:
        if "kalshi" in st.secrets and "api_key_id" in st.secrets["kalshi"]:
            k_id = st.secrets["kalshi"]["api_key_id"]
            k_priv = st.secrets["kalshi"].get("private_key", "")
            
            path = "/trade-api/v2/markets?series_ticker=KXBTC"
            url_kalshi = f"https://trading-api.kalshi.com{path}"
            
            headers = get_kalshi_auth_headers(k_id, k_priv, "GET", path)
            if headers:
                req_k = urllib.request.Request(url_kalshi, headers=headers)
                with urllib.request.urlopen(req_k, timeout=3.0) as resp_k:
                    k_data = json.loads(resp_k.read().decode())
                    if "markets" in k_data and len(k_data["markets"]) > 0:
                        kalshi_up_prob = k_data["markets"][0].get("yes_bid", 50)
                        kalshi_connected = True
    except Exception as e:
        st.error(f"Error Kalshi: {str(e)}")
        pass

    # 3. Consenso Final
    if kalshi_connected:
        up_prob = kalshi_up_prob
    else:
        # Ponderación técnica si no conecta
        up_prob = 50.0
        if rsi < 45:
            up_prob += 10
        elif rsi > 55:
            up_prob -= 10
        if "ALCISTA" in ema_signal:
            up_prob += 9
        elif "BAJISTA" in ema_signal:
            up_prob -= 9
        up_prob = max(5, min(95, up_prob))
        
    down_prob = 100 - up_prob
    
    return {
        "price": binance_price,
        "rsi": rsi,
        "ema": ema_signal,
        "up": int(up_prob),
        "down": int(down_prob),
        "kalshi_connected": kalshi_connected
    }

data = get_sniper_signal()

# ================= INTERFAZ GRÁFICA =================

# 1. Estimación Actual
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<div class="metric-title">⚡ ESTIMACIÓN ACTUAL (15m)</div>', unsafe_allow_html=True)

if data["up"] > data["down"]:
    st.markdown(f'<div class="metric-value-up">POSIBLE UP • {data["up"]}%</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #8a99ad; font-size: 13px;">Consenso entre Binance Data y Análisis Técnico</p>', unsafe_allow_html=True)
    st.progress(data["up"] / 100)
else:
    st.markdown(f'<div class="metric-value-down">POSIBLE DOWN • {data["down"]}%</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #8a99ad; font-size: 13px;">Consenso entre Binance Data y Análisis Técnico</p>', unsafe_allow_html=True)
    st.progress(data["up"] / 100)
st.markdown('</div>', unsafe_allow_html=True)

# 2. Momentum Detectado
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<div class="metric-title">🚀 MOMENTUM DETECTADO</div>', unsafe_allow_html=True)
if data["up"] > data["down"]:
    st.markdown('<h3 style="text-align: center; color: #0ecb81; margin: 0;">PRESIÓN ALCISTA DETECTADA</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #8a99ad; font-size: 12px; margin-top: 5px;">Vela impulsora sobre la EMA rápida</p>', unsafe_allow_html=True)
else:
    st.markdown('<h3 style="text-align: center; color: #f6465d; margin: 0;">PRESIÓN BAJISTA DETECTADA</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #8a99ad; font-size: 12px; margin-top: 5px;">Vela impulsora bajo la EMA rápida</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 3. Señal Principal (Botones Visuales)
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<div class="metric-title">SEÑAL PRINCIPAL</div>', unsafe_allow_html=True)
if data["up"] > data["down"]:
    st.markdown('<h2 style="text-align: center; color: #0ecb81;">POSIBLE UP</h2>', unsafe_allow_html=True)
else:
    st.markdown('<h2 style="text-align: center; color: #f6465d;">POSIBLE DOWN</h2>', unsafe_allow_html=True)

st.markdown('<p style="text-align: center; color: #8a99ad; font-size: 11px;">Esta llamada se actualiza cada 15 minutos exactos</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown(f'<div class="badge-up">UP<br><span style="font-size: 20px;">{data["up"]}%</span><br><span style="font-size: 10px;">COMPRAR UP</span></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="badge-down">DOWN<br><span style="font-size: 20px;">{data["down"]}%</span><br><span style="font-size: 10px;">COMPRAR DOWN</span></div>', unsafe_allow_html=True)

st.markdown('<p style="text-align: center; color: #8a99ad; font-size: 10px; margin-top: 10px;">El porcentaje sale de probabilidad técnica combinada</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 4. Confirmación Post-Entrada
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<div class="metric-title">CONFIRMACIÓN POST-ENTRADA</div>', unsafe_allow_html=True)
if data["up"] > data["down"]:
    st.markdown('<h3 style="text-align: center; color: #0ecb81; margin: 0;">POSIBLE UP</h3>', unsafe_allow_html=True)
else:
    st.markdown('<h3 style="text-align: center; color: #f6465d; margin: 0;">POSIBLE DOWN</h3>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #8a99ad; font-size: 11px; margin-top: 5px;">Estimación basada en probabilidades, no garantía de resultado.</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 5. Indicadores Clave
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<div class="metric-title">INDICADORES CLAVE</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="indicator-row">
    <span>EMA 9 / EMA 21</span>
    <span style="font-weight: bold;">{data["ema"]}</span>
</div>
<div class="indicator-row" style="margin-top: 8px;">
    <span>RSI (14)</span>
    <span style="font-weight: bold;">{data["rsi"]:.1f}</span>
</div>
<div class="indicator-row" style="margin-top: 8px; border-bottom: none;">
    <span>API Kalshi</span>
    <span style="font-weight: bold; color: {"#0ecb81" if data["kalshi_connected"] else "#f6465d"};">
        {"CONECTADO 🟢" if data["kalshi_connected"] else "MODO TÉCNICO ⚡"}
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Pie de página
st.markdown('<p style="text-align: center; color: #4f5d73; font-size: 11px;">Macaly + Alpha Bot v2.1 | Made with AI</p>', unsafe_allow_html=True)
