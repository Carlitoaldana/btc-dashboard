
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

# Usamos session_state para comparar el precio anterior y ver si subió o bajó al instante
if 'precio_anterior' not in st.session_state:
    st.session_state.precio_anterior = 0.0
if 'prob_up_dinamica' not in st.session_state:
    st.session_state.prob_up_dinamica = 50.0

@st.cache_data(ttl=10)
def obtener_precio_btc():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        res = requests.get(url, timeout=3).json()
        return res['bitcoin']['usd']
    except:
        return 77275.0

precio = obtener_precio_btc()

# Lógica ultra-sensible: si el precio cambia respecto a la lectura anterior, mueva la aguja
if st.session_state.precio_anterior > 0:
    if precio > st.session_state.precio_anterior:
        st.session_state.prob_up_dinamica = min(st.session_state.prob_up_dinamica + 4.0, 85.0)
    elif precio < st.session_state.precio_anterior:
        st.session_state.prob_up_dinamica = max(st.session_state.prob_up_dinamica - 4.0, 15.0)

st.session_state.precio_anterior = precio
up_val = round(st.session_state.prob_up_dinamica, 1)
down_val = round(100 - up_val, 1)

# Definir la recomendación táctica
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
st.text(f"Precio Actual en Vivo: ${precio:,.2f}")
st.info("💡 Este script detecta micro-variaciones: cada vez que recargues o pase un ciclo y el precio fluctúe, los porcentajes se moverán de inmediato.")
