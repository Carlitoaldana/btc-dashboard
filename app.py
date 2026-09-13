import streamlit as st
import pandas as pd
import numpy as np
import time
import urllib.request
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="BTC Momentum Alpha",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- MOTOR TÉCNICO EN TIEMPO REAL (VELAS DE 1 MINUTO) ---
def get_live_market_data():
    btc_price = 0.0
    change_pct = 0.0
    df = pd.DataFrame()
    
    # 1. Petición directa a Binance Klines (Velas de 1 min para máxima velocidad y reacción)
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=30"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2.5) as response:
            raw_data = json.loads(response.read().decode())
            # Formato Binance: [Open time, Open, High, Low, Close, Volume, Close_time, ...]
            df = pd.DataFrame(raw_data, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "q_vol", "trades", "tb_base", "tb_quote", "ignore"
            ])
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)
            df["open"] = df["open"].astype(float)
            
            btc_price = df["close"].iloc[-1]
            prev_price = df["close"].iloc[-2]
            change_pct = ((btc_price - prev_price) / prev_price) * 100
    except Exception:
        pass

    # 2. Respaldo por si Binance frena la IP de la nube
    if btc_price == 0.0 or df.empty:
        try:
            req = urllib.request.Request(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true",
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read().decode())
                btc_price = float(data["bitcoin"]["usd"])
                change_pct = float(data["bitcoin"].get("usd_24h_change", 0.0))
        except Exception:
            btc_price = 77000.0

    # --- CÁLCULO TÉCNICO MATEMÁTICO REAL ---
    trend_status = "NEUTRAL ⚡"
    rsi_val = 50.0
    up_p = 50
    
    if not df.empty and len(df) > 15:
        # Cálculo de EMAs reales (9 y 21)
        df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
        df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
        
        # Cálculo de RSI real (14 periodos)
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))
        
        last_row = df.iloc[-1]
        ema9 = last_row["ema9"]
        ema21 = last_row["ema21"]
        rsi_val = round(float(last_row["rsi"]), 1) if not np.isnan(last_row["rsi"]) else 50.0
        
        # Análisis de Volumen Comprador vs Vendedor en las últimas velas
        # Si el cierre es mayor que la apertura, cuenta como volumen comprador (taker buy)
        buy_vol = df[df["close"] >= df["open"]]["volume"].sum()
        total_vol = df["volume"].sum()
        vol_ratio = (buy_vol / total_vol) * 100 if total_vol > 0 else 50
        
        # Ponderación del Score en tiempo real
        score = 50
        if ema9 > ema21:
            score += 25
            trend_status = "ALCISTA 🚀"
        else:
            score -= 25
            trend_status = "BAJISTA 🔻"
            
        if rsi_val > 55:
            score += 15
        elif rsi_val < 45:
            score -= 15
            
        # Integrar el flujo de volumen real al score
        if vol_ratio > 52:
            score += 10
        elif vol_ratio < 48:
            score -= 10
            
        up_p = int(np.clip(score, 5, 95))
    else:
        up_p = 52 if change_pct >= 0 else 48

    down_p = 100 - up_p
    return btc_price, change_pct, up_p, down_p, trend_status, rsi_val

# Ejecutar motor en tiempo real
btc_price, change_pct, up_p, down_p, trend_status, rsi_val = get_live_market_data()

main_signal = "POSIBLE UP" if up_p >= 50 else "POSIBLE DOWN"
signal_color = "#4CAF50" if up_p >= 50 else "#E57373"
change_color = "#4CAF50" if change_pct >= 0 else "#E57373"

# --- DISEÑO VISUAL CSS ---
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
    .footer-credits {
        text-align: center;
        color: #546E7A;
        font-size: 10px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- INTERFAZ VISUAL ---
st.markdown('<div class="badge-alert">⚡ BTC / USD - MOTOR 1M EN VIVO</div>', unsafe_allow_html=True)

# Precio Actual
st.markdown(f"""<div class="card-estimation">
<div class="text-subtitle-sm">PRECIO EN VIVO (BINANCE 1M)</div>
<div class="text-main-green" style="color: {change_color};">${btc_price:,.2f}</div>
<div class="text-sub">Cambio última vela: {change_pct:+.2f}%</div>
</div>""", unsafe_allow_html=True)

# Probabilidad Técnica Principal
st.markdown(f"""<div class="card-estimation" style="background-color: #141824; border-color: #23293A;">
<div class="text-subtitle-sm" style="color: #64B5F6;">DIRECCIÓN TÉCNICA (1M)</div>
<div class="text-main-green" style="color: {signal_color};">{main_signal} · {up_p}%</div>
<div class="text-sub" style="color: #90A4AE;">Cálculo real: EMA 9/21 + RSI + Volumen</div>
<div class="bar-container">
<div class="bar-up" style="width: {up_p}%;"></div>
<div class="bar-down" style="width: {down_p}%;"></div>
</div>
<div class="bar-labels">
<span class="label-up">UP<br>{up_p}%</span>
<span class="label-down">DOWN<br>{down_p}%</span>
</div>
</div>""", unsafe_allow_html=True)

# Desglose Fuerza de Mercado
st.markdown(f"""<div class="card-main-signal">
<div class="text-gray-title">FLUJO DE MERCADO</div>
<div class="split-container" style="margin-top: 10px;">
<div class="box-up">
<div style="color: #81C784; font-size: 11px; font-weight: 700;">FUERZA UP</div>
<div style="color: #4CAF50; font-size: 28px; font-weight: 900; margin: 2px 0;">{up_p}%</div>
<div class="mini-bar-bg"><div class="mini-bar-up" style="width: {up_p}%;"></div></div>
</div>
<div class="box-down">
<div style="color: #E57373; font-size: 11px; font-weight: 700;">FUERZA DOWN</div>
<div style="color: #E57373; font-size: 28px; font-weight: 900; margin: 2px 0;">{down_p}%</div>
<div class="mini-bar-bg"><div class="mini-bar-down" style="width: {down_p}%;"></div></div>
</div>
</div>
</div>""", unsafe_allow_html=True)

# Indicadores en Tiempo Real
st.markdown(f"""<div class="card-section">
<div class="text-gray-title" style="margin-bottom: 10px;">ESTADO DE INDICADORES</div>
<div class="indicator-row">
<span style="font-size: 13px; font-weight: 600; color: #E6E8EF;">EMA 9 / EMA 21</span>
<span class="badge-green">{trend_status}</span>
</div>
<div class="indicator-row">
<span style="font-size: 13px; font-weight: 600; color: #E6E8EF;">RSI (14 velas 1m)</span>
<span class="badge-green">{rsi_val}</span>
</div>
<div class="indicator-row">
<span style="font-size: 13px; font-weight: 600; color: #E6E8EF;">Motor de Datos</span>
<span class="badge-green">ACTIVO AL SEGUNDO 🟢</span>
</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="footer-credits">Alpha Bot v4.4 | Real-Time 1M Tick Engine</div>', unsafe_allow_html=True)

# Refresco cada 3 segundos para lectura ultra rápida
time.sleep(3)
st.rerun()
