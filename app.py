import streamlit as st
import requests
from datetime import datetime, timezone
import os

st.set_page_config(page_title="BTC Kalshi Bot (15m Real)", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ BTC Kalshi Bot (15m Real)")

@st.cache_data(ttl=2)
def obtener_precio():
    try:
        url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
        res = requests.get(url, timeout=2).json()
        return float(res['data']['amount'])
    except:
        try:
            url2 = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            res2 = requests.get(url2, timeout=2).json()
            return float(res2['price'])
        except:
            return 0.0

precio_actual = obtener_precio()

# Bloque UTC de 15 minutos exactos idéntico a Kalshi
ahora_utc = datetime.now(timezone.utc)
minuto_bloque = (ahora_utc.minute // 15) * 15
clave_bloque = f"{ahora_utc.date()}-{ahora_utc.hour}-{minuto_bloque}"

# Archivo local en disco para mantener el strike guardado y evitar que se borre al refrescar
archivo_strike = "strike_btc.txt"
strike = 0.0

if os.path.exists(archivo_strike):
    try:
        with open(archivo_strike, "r") as f:
            contenido = f.read().strip().split(",")
            if len(contenido) == 2 and contenido[0] == clave_bloque:
                strike = float(contenido[1])
    except:
        pass

if strike == 0.0 and precio_actual > 0:
    strike = precio_actual
    try:
        with open(archivo_strike, "w") as f:
            f.write(f"{clave_bloque},{strike}")
    except:
        pass

if strike == 0.0:
    strike = 77250.0

diferencia = precio_actual - strike if precio_actual > 0 else 0.0

# Cálculo de probabilidad ultra sensible al movimiento en dólares
base = 50.0 + (diferencia * 2.5)
up_val = round(max(min(base, 98.0), 2.0), 1)
down_val = round(100 - up_val, 1)

if up_val >= 58:
    senal = "🚀 COMPRAR UP (SUBE)"
    color_box = "#0e4429"
elif up_val <= 42:
    senal = "📉 COMPRAR DOWN (BAJA)"
    color_box = "#51151e"
else:
    senal = "⚠️ ZONA DE INDECISIÓN"
    color_box = "#1f242d"

st.markdown(f"""
    <div style="background-color: {color_box}; padding: 22px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px;">
        {senal}
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Probabilidad Sube (UP)", value=f"{up_val}%")
with col2:
    st.metric(label="Probabilidad Baja (DOWN)", value=f"{down_val}%")

st.progress(up_val / 100)

st.divider()
st.text(f"Strike Bloque 15m (UTC): ${strike:,.2f}")
st.text(f"Precio en Vivo: ${precio_actual:,.2f}")
st.text(f"Diferencia: ${diferencia:+.2f}")
st.caption("🟢 Sincronizado con persistencia local en disco.")
