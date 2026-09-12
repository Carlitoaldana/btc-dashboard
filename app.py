
import streamlit as st
import requests

st.set_page_config(page_title="BTC Alpha Bot - 15m Kalshi", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ BTC Alpha Bot (Binance Real-Time)")
st.subheader("SEÑAL TÁCTICA 15M")

# Conexión directa a Binance para precio real al milisegundo
@st.cache_data(ttl=2)
def obtener_precio_binance():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        res = requests.get(url, timeout=2).json()
        return float(res['price'])
    except:
        return 0.0

precio_actual = obtener_precio_binance()

# Guardar memoria en Streamlit para comparar si subió o bajó respecto al segundo anterior
if 'precio_previo' not in st.session_state:
    st.session_state.precio_previo = precio_actual
if 'score' not in st.session_state:
    st.session_state.score = 50.0

if precio_actual > 0:
    if precio_actual > st.session_state.precio_previo:
        st.session_state.score = min(st.session_state.score + 6.0, 90.0)
    elif precio_actual < st.session_state.precio_previo:
        st.session_state.score = max(st.session_state.score - 6.0, 10.0)
    st.session_state.precio_previo = precio_actual

up_val = round(st.session_state.score, 1)
down_val = round(100 - up_val, 1)

# Señal clara
if up_val >= 60:
    senal = "🚀 COMPRAR UP"
    color_box = "#0e4429"
elif up_val <= 40:
    senal = "📉 COMPRAR DOWN"
    color_box = "#51151e"
else:
    senal = "⚠️ ZONA NEUTRAL / ESPERAR"
    color_box = "#1f242d"

st.markdown(f"""
    <div style="background-color: {color_box}; padding: 20px; border-radius: 10px; text-align: center; font-size: 22px; font-weight: bold; margin-bottom: 20px;">
        {senal}
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Fuerza UP", value=f"{up_val}%")
with col2:
    st.metric(label="Fuerza DOWN", value=f"{down_val}%")

st.progress(up_val / 100)

st.divider()
st.text(f"Precio Binance BTCUSDT: ${precio_actual:,.2f}")
st.info("💡 Cada vez que le des a recargar a la página, medirá el cambio exacto contra Binance al instante.")
