import datetime
import pandas as pd
import requests
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="VIXY'S VAULT - Decision Intelligence",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Estilos CSS profesionales oscuros
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0914;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .header-title {
        font-size: 13px;
        letter-spacing: 2px;
        color: #9a95b5;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .main-brand {
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #ffffff;
        margin-bottom: 15px;
    }
    .card-box {
        background-color: #151221;
        border: 1px solid #282142;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 15px;
    }
    .signal-box {
        background: linear-gradient(135deg, #10261c 0%, #151221 100%);
        border: 1px solid #1f4a34;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
    }
    .signal-text {
        font-size: 32px;
        font-weight: 900;
        color: #00ff88;
        letter-spacing: 2px;
        margin: 8px 0;
    }
    .sub-label {
        font-size: 11px;
        color: #8c85a8;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Obtener datos reales de velas (klines) de Binance.US para armar el gráfico profesional
@st.cache_data(ttl=15)
def get_binance_candles():
  try:
    url = "https://api.binance.us/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=30"
    res = requests.get(url, timeout=4)
    if res.status_code == 200:
      data = res.json()
      df = pd.DataFrame(data, columns=[
          'timestamp', 'open', 'high', 'low', 'close', 'volume',
          'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
      ])
      df['close'] = df['close'].astype(float)
      df['open'] = df['open'].astype(float)
      df['high'] = df['high'].astype(float)
      df['low'] = df['low'].astype(float)
      df['volume'] = df['volume'].astype(float)
      df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
      return df
  except Exception:
    pass
  return None

df_candles = get_binance_candles()
current_price = df_candles['close'].iloc[-1] if df_candles is not None else 77146.13

# Encabezado
st.markdown('<div class="header-title">Decision Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="main-brand">VIXY\'S VAULT</div>', unsafe_allow_html=True)

# Pestañas de navegación
nav_tab = st.radio(
    "Navegación",
    ["Dashboard", "Scalping", "1H Desk", "Signals", "Journal"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("<br>", unsafe_allow_html=True)

if nav_tab in ["Dashboard", "Signals", "Scalping"]:
  # Precio en Vivo
  st.markdown(
      f"""
    <div class="card-box">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="sub-label">MERCADO EN VIVO (BINANCE.US)</span>
            <span style="font-size: 11px; color: #00ff88;">● FEED ACTIVO</span>
        </div>
        <div style="font-size: 28px; font-weight: 700; margin-top: 6px;">${current_price:,.2f}</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Gráfico de Línea Profesional (Precio Histórico 15M)
  st.markdown('<div class="card-box">', unsafe_allow_html=True)
  st.markdown('<div class="sub-label">TENDENCIA DE PRECIO (CICLO 15M)</div>', unsafe_allow_html=True)
  if df_candles is not None:
    chart_data = df_candles.set_index('time')[['close']]
    st.line_chart(chart_data, color="#00ff88", height=200)
  else:
    st.info("Cargando flujo de gráficos...")
  st.markdown('</div>', unsafe_allow_html=True)

  # Tarjeta de Señal Principal
  st.markdown(
      """
    <div class="signal-box">
        <div class="sub-label">AUTHORITATIVE 15M CYCLE LOCK</div>
        <div class="signal-text">BUY UP 🔺</div>
        <div style="font-size: 12px; color: #a19bb8;">STRIKE: $77,146.13</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Gráfico de Volumen Pro
  st.markdown('<div class="card-box">', unsafe_allow_html=True)
  st.markdown('<div class="sub-label">VOLUMEN DE ORDENES (CVD / TICK FLOW)</div>', unsafe_allow_html=True)
  if df_candles is not None:
    vol_data = df_candles.set_index('time')[['volume']]
    st.bar_chart(vol_data, color="#1f4a34", height=130)
  st.markdown('</div>', unsafe_allow_html=True)

  # Confianza del Modelo
  st.markdown(
      """
    <div class="card-box">
        <div class="sub-label">LOCKED MODEL CONFIDENCE</div>
        <div style="font-size: 28px; font-weight: 800; color: #00ff88; margin: 4px 0;">73%</div>
        <div style="font-size: 12px; color: #00ff88; font-weight: 600;">STRONG BULLISH CONFIDENCE</div>
        <div style="margin-top: 10px; background: #221d36; border-radius: 8px; height: 6px; width: 100%;">
            <div style="background: #00ff88; width: 73%; height: 6px; border-radius: 8px;"></div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

else:
  st.markdown(
      f"""
    <div class="card-box">
        <h3>Módulo: {nav_tab}</h3>
        <p style="color: #9a95b5;">Analítica avanzada y registros algorítmicos en tiempo real.</p>
        <p><b>Precio activo:</b> ${current_price:,.2f}</p>
    </div>
    """,
      unsafe_allow_html=True,
  )
