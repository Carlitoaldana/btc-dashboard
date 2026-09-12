import pandas as pd
import requests
import streamlit as st

# Configuración de página limpia y oscura
st.set_page_config(
    page_title="PREDICTION BOT - MAKING A BAG",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Estilos CSS exactos para replicar la interfaz de la captura
st.markdown(
    """
    <style>
    .stApp {
        background-color: #07050d;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .top-title {
        font-size: 16px;
        font-weight: 900;
        color: #00ff88;
        letter-spacing: 1px;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 9px;
        letter-spacing: 2px;
        color: #7b7299;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .main-vault-card {
        background: linear-gradient(135deg, #0d2618 0%, #120f1c 100%);
        border: 1px solid #1a4a30;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 8px;
    }
    .buy-text {
        font-size: 26px;
        font-weight: 900;
        color: #00ff88;
        letter-spacing: 2px;
        margin: 2px 0;
    }
    .card-box {
        background-color: #120f1c;
        border: 1px solid #231b36;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
    }
    .status-row-card {
        background-color: #120f1c;
        border: 1px solid #231b36;
        border-radius: 10px;
        padding: 8px 12px;
        margin-bottom: 6px;
        text-align: center;
    }
    .win-btn {
        background-color: #00ff88;
        color: #07050d;
        font-weight: 900;
        text-align: center;
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
        letter-spacing: 1px;
        margin-top: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Obtener precio real de Binance.US
precio_btc = 77100.00
try:
  res = requests.get(
      "https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT", timeout=3
  )
  if res.status_code == 200:
    precio_btc = float(res.json()["price"])
except Exception:
  pass

# Generar datos para el gráfico de velas 15M
@st.cache_data(ttl=15)
def cargar_velas_15m():
  try:
    url = "https://api.binance.us/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=25"
    res = requests.get(url, timeout=3)
    if res.status_code == 200:
      df = pd.DataFrame(res.json(), columns=[
          'ts', 'open', 'high', 'low', 'close', 'vol',
          'ct', 'qav', 'trades', 'tb_vol', 'tq_vol', 'ign'
      ])
      df['close'] = df['close'].astype(float)
      df['time'] = pd.to_datetime(df['ts'], unit='ms')
      return df.set_index('time')[['close']]
  except Exception:
    pass
  return None


# Encabezado principal
st.markdown('<div class="top-title">PREDICTION BOT: MAKING A BAG 🚀</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">15MIN MARKET</div>', unsafe_allow_html=True)

# Pestañas de navegación superiores
pestana = st.radio(
    "Navegación",
    ["Dashboard", "Scalping", "1H Desk", "Signals", "Journal"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("<br>", unsafe_allow_html=True)

if pestana in ["Dashboard", "Signals", "Scalping"]:

  # 1. Tarjeta principal "BUY UP"
  st.markdown(
      f"""
    <div class="main-vault-card">
        <div style="font-size: 9px; color: #7b7299; letter-spacing: 1px;">BTC / USD (SPOT) • ${precio_btc:,.2f} • LIVE</div>
        <div class="buy-text">BUY UP 🔺</div>
        <div style="font-size: 20px; font-weight: 800; color: #00ff88;">82.6%</div>
        <div style="margin-top: 4px; background: #161224; border-radius: 4px; height: 4px; width: 100%;">
            <div style="background: #00ff88; width: 82.6%; height: 4px; border-radius: 4px;"></div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # 2. Las 3 barras horizontales con iconos idénticas a tu foto
  st.markdown(
      """
    <div class="status-row-card">
        <span style="font-size: 13px;">🎯</span> <span style="font-size: 10px; font-weight: 700; color: #00ff88; letter-spacing: 1px;">LOCK</span>
    </div>
    <div class="status-row-card">
        <span style="font-size: 13px;">⚡</span> <span style="font-size: 10px; font-weight: 700; color: #7b7299; letter-spacing: 1px;">15M</span>
    </div>
    <div class="status-row-card">
        <span style="font-size: 13px;">📊</span> <span style="font-size: 10px; font-weight: 700; color: #00ff88; letter-spacing: 1px;">PRO</span>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # 3. Gráfico de Tendencia Verde Estilizado
  st.markdown('<div class="card-box">', unsafe_allow_html=True)
  st.markdown('<div style="font-size: 9px; color: #7b7299; letter-spacing: 1px; margin-bottom: 4px;">ESTRUCTURA DE CICLO 15M (TICK FLOW)</div>', unsafe_allow_html=True)
  df_grafico = cargar_velas_15m()
  if df_grafico is not None:
    st.line_chart(df_grafico, color="#00ff88", height=150)
  else:
    st.info(f"Precio actual: ${precio_btc:,.2f}")
  st.markdown('</div>', unsafe_allow_html=True)

  # 4. Bloques inferiores de Análisis y Ganancia en vivo (Lado a lado)
  col_a, col_b = st.columns(2)
  with col_a:
    st.markdown(
        """
        <div class="card-box" style="margin-bottom: 0px;">
            <div style="font-size: 8px; color: #7b7299;">LIVE RESULT</div>
            <div style="font-size: 13px; font-weight: 800; color: #00ff88; margin-top: 2px;">+91,220.00</div>
            <div style="font-size: 9px; color: #00ff88;">+6,100%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
  with col_b:
    st.markdown(
        """
        <div class="card-box" style="margin-bottom: 0px;">
            <div style="font-size: 8px; color: #7b7299;">AI ANALYSIS</div>
            <div style="font-size: 11px; font-weight: 700; color: #fff; margin-top: 2px;">✓ Liquidity Zone Verified</div>
            <div style="font-size: 9px; color: #7b7299;">Immutability Confirmed</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

  # Botón inferior verde "WIN"
  st.markdown('<div class="win-btn">WIN 🚀</div>', unsafe_allow_html=True)

else:
  st.markdown(
      f"""
    <div class="card-box">
        <h3>Módulo: {pestana}</h3>
        <p style="color: #7b7299;">Panel operativo sincronizado con Binance.US.</p>
    </div>
    """,
      unsafe_allow_html=True,
  )
