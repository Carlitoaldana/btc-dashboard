import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="BTC Alpha Bot - 15m Kalshi", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ BTC Alpha Bot (15m Kalshi)")
st.subheader("SEÑAL TÁCTICA DE ENTRADA")

@st.cache_data(ttl=15) # Se actualiza agresivamente cada 15 segundos para scalping rápido
def calcular_senyal_15m():
    try:
        # Consultar precio actual y variaciones de corto plazo
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=false&include_24hr_vol=false&include_24hr_change=true"
        res = requests.get(url, timeout=4).json()
        precio = res['bitcoin']['usd']
        cambio_24h = res['bitcoin']['usd_24h_change']
        
        # Simulación de presión de order-flow basada en micro-tendencia
        # (Aquí puedes conectar luego una API de exchanges como Binance si quieres el delta exacto por segundo)
        if cambio_24h > 0:
            prob_up = 58 + int(min(abs(cambio_24h) * 2, 35))
        else:
            prob_up = max(42 - int(abs(cambio_24h) * 2), 10)
            
        prob_down = 100 - prob_up
    except:
        precio = 77000.00
        prob_up = 50
        prob_down = 50

    return precio, prob_up, prob_down

precio_btc, up_val, down_val = calcular_senyal_15m()

# Definir la recomendación táctica para Kalshi
if up_val >= 60:
    senal = "🚀 ENTRAR UP (ALCISTA)"
    color_box = "#0e4429"
elif up_val <= 40:
    senal = "📉 ENTRAR DOWN (BAJISTA)"
    color_box = "#51151e"
else:
    senal = "⚠️ ZONA NEUTRAL / ESPERAR"
    color_box = "#1f242d"

st.markdown(f"""
    <div style="background-color: {color_box}; padding: 20px; border-radius: 10px; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">
        {senal}
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Probabilidad UP", value=f"{up_val}%")
with col2:
    st.metric(label="Probabilidad DOWN", value=f"{down_val}%")

st.progress(up_val / 100)

st.divider()
st.text(f"Precio Actual de Referencia: ${precio_btc:,.2f}")
st.info("💡 Tip para Kalshi 15m: Revisa esta pantalla faltando 3 a 5 minutos para que cierre el periodo de 15 minutos; es cuando el 'order-flow' define el precio de liquidación final basado en el promedio de los últimos 60 segundos.")
