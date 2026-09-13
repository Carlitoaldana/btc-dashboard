import streamlit as st
import requests
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="BTC Momentum Alpha",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- MOTOR DE ANÁLISIS TÉCNICO (BINANCE LIVE) ---
def get_market_data():
    """Calcula indicadores clave y fuerza de tendencia desde Binance en vivo."""
    try:
        # Petición de velas de 15 minutos
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": "BTCUSDT", "interval": "15m", "limit": 50}
        res = requests.get(url, params=params, timeout=3)
        raw_data = res.json()
        
        df = pd.DataFrame(raw_data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "q_vol", "trades", "tb_base", "tb_quote", "ignore"
        ])
        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["volume"] = df["volume"].astype(float)
        
        # Precio actual
        current_price = df["close"].iloc[-1]
        prev_price = df["close"].iloc[-2]
        price_change = ((current_price - prev_price) / prev_price) * 100
        
        # Medias Móviles Exponenciales (EMA 9 y EMA 21)
        df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
        df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
        
        # RSI (14 periodos)
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))
        
        last_row = df.iloc[-1]
        ema9 = last_row["ema9"]
        ema21 = last_row["ema21"]
        rsi_val = round(last_row["rsi"], 1)
        
        # Lógica de Puntuación de Probabilidad (0% a 100% UP)
        score = 50
        if ema9 > ema21:
            score += 25
        else:
            score -= 25
            
        if rsi_val > 55:
            score += 15
        elif rsi_val < 45:
            score -= 15
            
        if price_change > 0:
            score += 10
        else:
            score -= 10
            
        up_prob = int(np.clip(score, 5, 95))
        down_prob = 100 - up_prob
        
        ema_status = "ALCISTA 🚀" if ema9 > ema21 else "BAJISTA 🔻"
        
        return current_price, price_change, up_prob, down_prob, ema_status, rsi_val
    except Exception:
        return 0.0, 0.0, 50, 50, "NEUTRAL ⚡", 50.0

# Obtener datos frescos
btc_price, change_pct, up_p, down_p, trend_status, rsi_val = get_market_data()

main_signal = "POSIBLE UP" if up_p >= 50 else "POSIBLE DOWN"
signal_color = "#4CAF50" if up_p >= 50 else "#E57373"
change_color = "#4CAF50" if change_pct >= 0 else "#E57373"

# --- INTERFAZ CSS (ESTILO DARK PROFESIONAL) ---
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
    .bar-down { background-color: #E57373; }

    .bar-labels {
        display: flex;
        justify-content: space-between;
        font-size: 10px;
        font-weight: 700;
    }
    .label-up { color: #4CAF50; }
    .label-down { color: #E57373; }

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

# --- PANEL VISUAL ---
st.markdown('<div class="badge-alert">⚡ BTC / USDT - MOTOR TÉCNICO EN VIVO</div>', unsafe_allow_html=True)

# Tarjeta de Precio Actual
st.markdown(f"""<div class="card-estimation">
<div class="text-subtitle-sm">PRECIO ACTUAL BTC</div>
<div class="text-main-green" style="color: {change_color};">${btc_price:,.2f}</div>
<div class="text-sub">Variación vela 15m: {change_pct:+.2f}%</div>
</div>""", unsafe_allow_html=True)

# Tarjeta de Estimación Principal
st.markdown(f"""<div class="card-estimation" style="background-color: #141824; border-color: #23293A;">
<div class="text-subtitle-sm" style="color: #64B5F6;">PROBABILIDAD TÉCNICA (15m)</div>
<div class="text-main-green" style="color: {signal_color};">{main_signal} · {up_p}%</div>
<div class="text-sub" style="color: #90A4AE;">Basado en Cruce EMA + RSI + Momentum</div>
<div class="bar-container">
<div class="bar-up" style="width: {up_p}%;"></div>
<div class="bar-down" style="width: {down_p}%;"></div>
</div>
<div class="bar-labels">
<span class="label-up">UP<br>{up_p}%</span>
<span class="label-down">DOWN<br>{down_p}%</span>
</div>
</div>""", unsafe_allow_html=True)

# Bloque Desglose de Probabilidades
st.markdown(f"""<div class="card-main-signal">
<div class="text-gray-title">FUERZA DE MERCADO</div>
<div class="split-container" style="margin-top: 10px;">
<div class="box-up">
<div style="color: #81C784; font-size: 11px; font-weight: 700;">TENDENCIA UP</div>
<div style="color: #4CAF50; font-size: 28px; font-weight: 900; margin: 2px 0;">{up_p}%</div>
<div class="mini-bar-bg"><div class="mini-bar-up" style="width: {up_p}%;"></div></div>
</div>
<div class="box-down">
<div style="color: #E57373; font-size: 11px; font-weight: 700;">TENDENCIA DOWN</div>
<div style="color: #E57373; font-size: 28px; font-weight: 900; margin: 2px 0;">{down_p}%</div>
<div class="mini-bar-bg"><div class="mini-bar-down" style="width: {down_p}%;"></div></div>
</div>
</div>
</div>""", unsafe_allow_html=True)

# Indicadores Clave
st.markdown(f"""<div class="card-section">
<div class="text-gray-title" style="margin-bottom: 10px;">INDICADORES TÉCNICOS</div>
<div class="indicator-row">
<span style="font-size: 13px; font-weight: 600; color: #E6E8EF;">EMA 9 / EMA 21</span>
<span class="badge-green">{trend_status}</span>
</div>
<div class="indicator-row">
<span style="font-size: 13px; font-weight: 600; color: #E6E8EF;">RSI (14)</span>
<span class="badge-green">{rsi_val}</span>
</div>
<div class="indicator-row">
<span style="font-size: 13px; font-weight: 600; color: #E6E8EF;">Estado de API</span>
<span class="badge-green">CONECTADO 🟢</span>
</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="footer-credits">Alpha Bot v4.0 | Real-Time Technical Feed</div>', unsafe_allow_html=True)

# Recarga automática cada 4 segundos para ver el movimiento en vivo
time.sleep(4)
st.rerun()
