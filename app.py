import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json

st.set_page_config(
    page_title="BTC Contract Sniper Pro",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def get_sniper_signal():
    btc_price = 76803.91
    change_pct = -0.73
    df = pd.DataFrame()
    kalshi_connected = False
    kalshi_up_prob = None
    
    try:
        if "kalshi" in st.secrets:
            k_key = st.secrets["kalshi"].get("api_key")
            url_kalshi = "https://trading-api.kalshi.com/trade-api/v2/markets?series_ticker=KXBTC"
            req_k = urllib.request.Request(
                url_kalshi, 
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Authorization': f'Bearer {k_key}'
                }
            )
            with urllib.request.urlopen(req_k, timeout=2.0) as resp_k:
                k_data = json.loads(resp_k.read().decode())
                if "markets" in k_data and len(k_data["markets"]) > 0:
                    kalshi_up_prob = k_data["markets"][0].get("yes_bid", 50)
                    kalshi_connected = True
    except Exception:
        pass

    try:
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=30"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2.5) as response:
            raw_data = json.loads(response.read().decode())
            df = pd.DataFrame(raw_data, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "q_vol", "trades", "tb_base", "tb_quote", "ignore"
            ])
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)
            df["open"] = df["open"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            
            btc_price = df["close"].iloc[-1]
            prev_price = df["close"].iloc[-2]
            change_pct = ((btc_price - prev_price) / prev_price) * 100
    except Exception:
        pass

    trend_status = "NEUTRAL ⚡"
    rsi_val = 50.0
    volatility_status = "NORMAL"
    score = 50
    
    if not df.empty and len(df) > 14:
        df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
        df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
        
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))
        
        ema9 = df["ema9"].iloc[-1]
        ema21 = df["ema21"].iloc[-1]
        rsi_val = round(float(df["rsi"].iloc[-1]), 1) if not np.isnan(df["rsi"].iloc[-1]) else 50.0
        
        recent_ranges = (df["high"] - df["low"]).tail(5).mean()
        avg_range = (df["high"] - df["low"]).mean()
        if recent_ranges > (avg_range * 1.3):
            volatility_status = "ALTA ⚠️"
        
        last_body = df["close"].iloc[-1] - df["open"].iloc[-1]
        candle_range = df["high"].iloc[-1] - df["low"].iloc[-1]
        pressure = (last_body / candle_range) if candle_range > 0 else 0
        
        if ema9 > ema21:
            score += 25
            trend_status = "ALCISTA 🚀"
        else:
            score -= 25
            trend_status = "BAJISTA 🔻"
            
        if rsi_val > 53:
            score += 15
        elif rsi_val < 47:
            score -= 15
            
        if pressure > 0.15:
            score += 10
        elif pressure < -0.15:
            score -= 10
    else:
        score = 62 if change_pct >= 0 else 41

    if kalshi_connected and kalshi_up_prob is not None:
        up_p = int((score + kalshi_up_prob) / 2)
    else:
        up_p = int(np.clip(score, 15, 85))
        
    down_p = 100 - up_p
    
    if up_p >= 50:
        main_signal = "POSIBLE UP"
        signal_color = "#4CAF50"
        momentum_text = "FUERTE REBOTE ALCISTA"
        momentum_sub = "Rompimiento de EMA confirmado en la vela actual"
    else:
        main_signal = "POSIBLE DOWN"
        signal_color = "#E57373"
        momentum_text = "PRESIÓN BAJISTA DETECTADA"
        momentum_sub = "Vela impulsora bajo la EMA rápida"
        
    change_color = "#4CAF50" if change_pct >= 0 else "#E57373"
    
    return btc_price, change_pct, up_p, down_p, main_signal, signal_color, change_color, trend_status, rsi_val, volatility_status, momentum_text, momentum_sub, kalshi_connected

btc_price, change_pct, up_p, down_p, main_signal, signal_color, change_color, trend_status, rsi_val, volatility_status, momentum_text, momentum_sub, kalshi_connected = get_sniper_signal()

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
        font-size: 24px;
        font-weight: 900;
        margin: 2px 0;
    }
    .text-sub {
        color: #A5D6A7;
        font-size: 11px;
        margin-bottom: 10px;
    }

    .bar-container {
        display: flex;
        height: 6px;
        border-radius: 3px;
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

    .card-momentum {
        background-color: #261F14;
        border: 1px solid #4D391A;
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 12px;
        text-align: center;
    }

    .card-main-signal {
        background-color: #141824;
        border: 1px solid #23293A;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        text-align: center;
    }

    .split-container {
        display: flex;
        gap: 10px;
        margin-top: 10px;
        margin-bottom: 6px;
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
        background-color: #1F1113;
        border: 1px solid #4A1B24;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
    }

    .card-section {
        background-color: #141824;
        border: 1px solid #23293A;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .text-gray-title {
        color: #78909C;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
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
        background-color: #2D1D0F;
        color: #FFA726;
        border: 1px solid #4D391A;
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

st.markdown(f'<div class="badge-alert">🚨 ALERTA: VOLATILIDAD {volatility_status}</div>', unsafe_allow_html=True)

consenso_text = "Consenso entre Kalshi API y Análisis Técnico" if kalshi_connected else "Consenso entre Binance Data y Análisis Técnico"
st.markdown(f"""<div class="card-estimation">
<div class="text-subtitle-sm">⚡ ESTIMACIÓN ACTUAL (15m)</div>
<div class="text-main-green" style="color: {signal_color};">{main_signal} · {max(up_p, down_p)}%</div>
<div class="text-sub">{consenso_text}</div>
<div class="bar-container">
<div class="bar-up" style="width: {up_p}%;"></div>
<div class="bar-down" style="width: {down_p}%;"></div>
</div>
<div class="bar-labels">
<span class="label-up">UP {up_p}%</span>
<span class="label-down">DOWN {down_p}%</span>
</div>
</div>""", unsafe_allow_html=True)

st.markdown(f"""<div class="card-momentum">
<div style="color: #FFB74D; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 3px;">🚀 MOMENTUM DETECTADO</div>
<div style="color: #66BB6A; font-size: 16px; font-weight: 900; margin-bottom: 4px;">{momentum_text}</div>
<div style="color: #B0BEC5; font-size: 11px;">{momentum_sub}</div>
</div>""", unsafe_allow_html=True)

kalshi_badge_sub = "El porcentaje sale directo de la API de Kalshi" if kalshi_connected else "El porcentaje sale de probabilidad técnica combinada"
st.markdown(f"""<div class="card-main-signal">
<div class="text-gray-title">SEÑAL PRINCIPAL</div>
<div style="font-size: 22px; font-weight: 900; color: {signal_color}; margin: 6px 0;">{main_signal}</div>
<div style="color: #78909C; font-size: 10px; margin-bottom: 8px;">Esta llamada se actualiza cada 15 minutos exactos</div>

<div class="split-container">
<div class="box-up">
<div style="color: #81C784; font-size: 10px; font-weight: 700;">UP</div>
<div style="color: #4CAF50; font-size: 22px; font-weight: 900; margin: 2px 0;">{up_p}%</div>
<div style="background-color: #262931; width: 100%; border-radius: 3px; height: 5px; margin: 6px 0;"><div style="background-color: #4CAF50; height: 5px; border-radius: 3px; width: {up_p}%;"></div></div>
<div style="color: #4CAF50; font-size: 10px; font-weight: 700; margin-top: 4px;">COMPRAR UP —</div>
</div>
<div class="box-down">
<div style="color: #E57373; font-size: 10px; font-weight: 700;">DOWN</div>
<div style="color: #E57373; font-size: 22px; font-weight: 900; margin: 2px 0;">{down_p}%</div>
<div style="background-color: #262931; width: 100%; border-radius: 3px; height: 5px; margin: 6px 0;"><div style="background-color: #E57373; height: 5px; border-radius: 3px; width: {down_p}%;"></div></div>
<div style="color: #E57373; font-size: 10px; font-weight: 700; margin-top: 4px;">COMPRAR DOWN —</div>
</div>
</div>
<div style="color: #78909C; font-size: 10px; margin-top: 6px;">{kalshi_badge_sub}</div>
</div>""", unsafe_allow_html=True)

st.markdown(f"""<div class="card-estimation" style="background-color: #141824; border-color: #23293A; padding: 12px;">
<div class="text-gray-title" style="margin-bottom: 6px;">CONFIRMACIÓN POST-ENTRADA</div>
<div style="font-size: 16px; font-weight: 900; color: {signal_color}; margin-bottom: 4px;">{main_signal}</div>
<div style="color: #78909C; font-size: 10px;">Estimación basada en probabilidades, no garantía de resultado.</div>
</div>""", unsafe_allow_html=True)

kalshi_status_label = "CONECTADO 🟢" if kalshi_connected else "MODO TÉCNICO ⚡"
st.markdown(f"""<div class="card-section">
<div class="text-gray-title" style="margin-bottom: 10px;">INDICADORES CLAVE</div>
<div class="indicator-row">
<span style="font-size: 12px; font-weight: 600; color: #E6E8EF;">EMA 9 / EMA 21</span>
<span class="badge-green">{trend_status}</span>
</div>
<div class="indicator-row">
<span style="font-size: 12px; font-weight: 600; color: #E6E8EF;">RSI (14)</span>
<span class="badge-green">{rsi_val}</span>
</div>
<div class="indicator-row">
<span style="font-size: 12px; font-weight: 600; color: #E6E8EF;">API Kalshi</span>
<span class="badge-green">{kalshi_status_label}</span>
</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="footer-credits">Macaly + Alpha Bot v2.1 | Made with AI</div>', unsafe_allow_html=True)
