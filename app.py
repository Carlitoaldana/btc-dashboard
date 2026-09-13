import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json

st.set_page_config(
    page_title="BTC Signal Sniper",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Motor ultra seguro a prueba de bloqueos de nube
def get_sniper_signal():
    btc_price = 77000.0
    change_pct = 0.0
    df = pd.DataFrame()
    
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=15"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2) as response:
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
            pass

    score = 50
    if not df.empty and len(df) > 5:
        df["ema5"] = df["close"].ewm(span=5, adjust=False).mean()
        df["ema13"] = df["close"].ewm(span=13, adjust=False).mean()
        
        last_body = df["close"].iloc[-1] - df["open"].iloc[-1]
        candle_range = df["high"].iloc[-1] - df["low"].iloc[-1]
        pressure = (last_body / candle_range) if candle_range > 0 else 0
        
        if df["ema5"].iloc[-1] > df["ema13"].iloc[-1]:
            score += 30
        else:
            score -= 30
            
        if pressure > 0.15:
            score += 20
        elif pressure < -0.15:
            score -= 20
            
        if change_pct > 0:
            score += 10
        else:
            score -= 10
    else:
        score = 65 if change_pct >= 0 else 35

    final_up = int(np.clip(score, 10, 90))
    final_down = 100 - final_up
    
    if final_up >= 50:
        signal = "ENTRADA: POSIBLE UP 🚀"
        color = "#4CAF50"
        conf = final_up
        card_class = "card-signal"
    else:
        signal = "ENTRADA: POSIBLE DOWN 🔻"
        color = "#E57373"
        conf = final_down
        card_class = "card-signal-down"
        
    return btc_price, change_pct, signal, color, conf, final_up, final_down, card_class

btc_price, change_pct, signal, color, conf, up_p, down_p, card_class = get_sniper_signal()
change_color = "#4CAF50" if change_pct >= 0 else "#E57373"

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 2rem; max-width: 450px;}
    body, .stApp { background-color: #0E1117; color: #E6E8EF; font-family: sans-serif; }
    .sniper-header { background-color: #161B22; border: 1px solid #30363D; border-radius: 14px; padding: 12px; text-align: center; margin-bottom: 12px; font-size: 13px; font-weight: 700; color: #58A6FF; }
    .card-signal { background-color: #111A16; border: 2px solid #238636; border-radius: 18px; padding: 20px; text-align: center; margin-bottom: 14px; }
    .card-signal-down { background-color: #1F1113; border: 2px solid #DA3633; border-radius: 18px; padding: 20px; text-align: center; margin-bottom: 14px; }
    .price-tag { font-size: 32px; font-weight: 900; margin: 6px 0; }
    .direction-title { font-size: 20px; font-weight: 900; margin: 10px 0; }
    .info-box { background-color: #161B22; border: 1px solid #30363D; border-radius: 14px; padding: 14px; margin-bottom: 12px; }
    .row-detail { display: flex; justify-content: space-between; margin: 6px 0; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="sniper-header">🎯 BTC CONTRACT SNIPER</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="{card_class}">
    <div style="color: #8B949E; font-size: 11px; font-weight: 700;">PRECIO ACTUAL</div>
    <div class="price-tag" style="color: {change_color};">${btc_price:,.2f}</div>
    <div style="color: #8B949E; font-size: 12px;">Variación: {change_pct:+.2f}%</div>
    <hr style="border: 0; border-top: 1px solid #30363D; margin: 15px 0;">
    <div style="color: #8B949E; font-size: 11px; font-weight: 700;">VEREDICTO DE ENTRADA</div>
    <div class="direction-title" style="color: {color};">{signal}</div>
    <div style="font-size: 14px; font-weight: 800; color: #E6E8EF;">Confianza: {conf}%</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="info-box">
    <div style="color: #8B949E; font-size: 11px; font-weight: 700; margin-bottom: 8px;">FUERZA DE MERCADO</div>
    <div class="row-detail"><span>Fuerza UP:</span><span style="color: #4CAF50; font-weight: 700;">{up_p}%</span></div>
    <div class="row-detail"><span>Fuerza DOWN:</span><span style="color: #E57373; font-weight: 700;">{down_p}%</span></div>
</div>
""", unsafe_allow_html=True)
