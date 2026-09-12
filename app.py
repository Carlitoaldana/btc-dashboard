
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="BTC Bot 15m - Kalshi", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ BTC Bot Kalshi (15m)")

# Función robusta para traer velas de 1 minuto reales y calcular tendencia exacta
@st.cache_data(ttl=15)
def analizar_mercado_btc():
    try:
        # Consultar las velas de 1 minuto de Binance (Klines)
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=15"
        res = requests.get(url, timeout=3).json()
        
        df = pd.DataFrame(res, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
        ])
        
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        
        precio_actual = df['close'].iloc[-1]
        precio_anterior = df['close'].iloc[-2] # Vela de hace 1 minuto
        
        # Calcular EMA rápida (últimos 5 minutos)
        ema_5 = df['close'].ewm(span=5, adjust=False).mean().iloc[-1]
        
        # Lógica de fuerza basada en estructura de mercado de 1m
        diferencia = ((precio_actual - ema_5) / ema_5) * 100
        
        # Puntaje base
        score = 50.0 + (diferencia * 150) # Amplifica la micro-tendencia
        score = max(min(score, 95.0), 5.0) # Limitar entre 5% y 95%
        
        return precio_actual, round(score, 1), round(100 - score, 1), "OK"
    except Exception as e:
        return 0.0, 50.0, 50.0, str(e)

precio, up_val, down_val, estado = analizar_mercado_btc()

# Definir la señal de compra para Kalshi
if up_val >= 58:
    senal = "🚀 COMPRAR UP"
    color_box = "#0e4429"
elif up_val <= 42:
    senal = "📉 COMPRAR DOWN"
    color_box = "#51151e"
else:
    senal = "⚠️ MERCADO LATERAL / ESPERAR"
    color_box = "#1f242d"

st.markdown(f"""
    <div style="background-color: {color_box}; padding: 22px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px;">
        {senal}
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Fuerza Tendencia UP", value=f"{up_val}%")
with col2:
    st.metric(label="Fuerza Tendencia DOWN", value=f"{down_val}%")

st.progress(up_val / 100)

st.divider()
st.text(f"Precio Actual BTC: ${precio:,.2f}")
st.caption("🤖 Bot conectado a la estructura de velas de 1m de Binance. Actualiza cada 15 segundos.")
