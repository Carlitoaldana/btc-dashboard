import streamlit as st
import pandas as pd
import requests

# Configuración de pantalla estilo App móvil
st.set_page_config(page_title="BTC Alpha Bot", layout="centered")

# CSS personalizado para estilo oscuro
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .card-green { background-color: #0e2a1f; border: 1px solid #1f6feb; border-radius: 10px; padding: 15px; color: #2ea043; text-align: center; }
    .card-red { background-color: #2a0e0e; border: 1px solid #da3633; border-radius: 10px; padding: 15px; color: #f85149; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Datos del indicador
precio = 64200.50
ema9 = 64100.00
ema21 = 63800.00
rsi = 64.1
prob_yes = 62
prob_no = 38

st.title("🤖 BTC Alpha Bot")

# 1. INTERFAZ GRÁFICA
st.subheader("⚡ ESTIMACIÓN ACTUAL (15m)")
if ema9 > ema21:
    st.markdown(f'<div class="card-green"><h2>POSIBLE UP · {prob_yes}%</h2><p>Consenso entre Kalshi y Análisis Técnico</p></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="card-red"><h2>POSIBLE DOWN · {prob_no}%</h2><p>Presión bajista detectada</p></div>', unsafe_allow_html=True)

st.write("---")

# Barras de Probabilidad UP vs DOWN
col1, col2 = st.columns(2)
with col1:
    st.metric("UP 🚀", f"{prob_yes}%")
    st.progress(prob_yes / 100)
with col2:
    st.metric("DOWN 📉", f"{prob_no}%")
    st.progress(prob_no / 100)

st.write("---")

# Tabla de Indicadores
st.subheader("INDICADORES CLAVE")
st.write(f"**Precio BTC:** ${precio:,.2f}")
st.write(f"**EMA 9 / EMA 21:** {'ALCISTA 🟢' if ema9 > ema21 else 'BAJISTA 🔴'}")
st.write(f"**RSI 14:** {rsi}")
