
import streamlit as st
import requests

st.set_page_config(page_title="BTC Bot Kalshi (15m)", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ BTC Bot Kalshi (15m)")

# Usamos Coinbase para evitar bloqueos y refrescar directo
@st.cache_data(ttl=5)
def obtener_precio():
    try:
        url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
        res = requests.get(url, timeout=3).json()
        return float(res['data']['amount'])
    except:
        return 0.0

precio_actual = obtener_precio()

if 'prev' not in st.session_state:
    st.session_state.prev = precio_actual
if 'score' not in st.session_state:
    st.session_state.score = 50.0

if precio_actual > 0 and st.session_state.prev > 0:
    diff = precio_actual - st.session_state.prev
    if diff > 0:
        st.session_state.score = min(st.session_state.score + 8.0, 92.0)
    elif diff < 0:
        st.session_state.score = max(st.session_state.score - 8.0, 8.0)
    st.session_state.prev = precio_actual
elif precio_actual > 0 and st.session_state.prev == 0:
    st.session_state.prev = precio_actual

up_val = round(st.session_state.score, 1)
down_val = round(100 - up_val, 1)

if up_val >= 60:
    senal = "🚀 COMPRAR UP"
    color_box = "#0e4429"
elif up_val <= 40:
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
st.text(f"Precio Coinbase BTC-USD: ${precio_actual:,.2f}")
st.caption("🟢 Conectado en tiempo real sin bloqueos.")
