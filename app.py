import pandas as pd
import requests
import streamlit as st

# Configuración de página limpia para móvil/escritorio
st.set_page_config(
    page_title="TRADING DASHBOARD UI - BTC/USD",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilos CSS generales optimizados
st.markdown(
    """
    <style>
    .stApp {
        background-color: #07090e;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .top-bar {
        background-color: #0d111a;
        border: 1px solid #1a2332;
        border-radius: 8px;
        padding: 10px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        font-size: 11px;
        color: #8b949e;
    }
    .card-box {
        background-color: #0d111a;
        border: 1px solid #1a2332;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .card-title {
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #8b949e;
        margin-bottom: 6px;
        font-weight: 700;
    }
    .val-green {
        color: #00ff88;
        font-weight: 800;
    }
    .center-panel {
        background: linear-gradient(135deg, #0b2216 0%, #0d111a 100%);
        border: 1px solid #163d28;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin-bottom: 10px;
    }
    .gauge-circle {
        background: rgba(0, 255, 136, 0.05);
        border: 2px solid #00ff88;
        border-radius: 50%;
        width: 130px;
        height: 130px;
        margin: 10px auto;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.15);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Obtener precio real de Binance.US para BTC
precio_btc = 68745.38
try:
  res = requests.get(
      "https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT", timeout=3
  )
  if res.status_code == 200:
    precio_btc = float(res.json()["price"])
except Exception:
  pass

# Barra superior estilo terminal
st.markdown(
    f"""
    <div class="top-bar">
        <div><b style="color: #00ff88;">🟢 TRADING DASHBOARD UI</b> &nbsp;|&nbsp; BTC/USD PREDICCIÓN</div>
        <div><b>${precio_btc:,.2f} EN VIVO</b></div>
    </div>
""",
    unsafe_allow_html=True,
)

# Columnas idénticas al monitor de referencia
col_izq, col_centro, col_der = st.columns([1, 1.4, 1])

with col_izq:
  # Estado del Contrato
  st.markdown(
      """
    <div class="card-box">
        <div class="card-title">ESTADO DEL CONTRATO</div>
        <div style="font-size: 8px; color: #8b949e;">TIEMPO PARA EXPIRACIÓN</div>
        <div class="val-green" style="font-size: 16px; margin-bottom: 8px;">13:45 MIN</div>
        <div style="font-size: 8px; color: #8b949e;">VALOR DEL CONTRATO</div>
        <div style="font-size: 18px; font-weight: 800;">$1,000.00</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Volatilidad de Mercado
  st.markdown(
      """
    <div class="card-box">
        <div class="card-title">VOLATILIDAD DE MERCADO (15M)</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  df_vol = pd.DataFrame({"y1": [2, 4, 3, 5, 7, 6, 8, 5, 4, 6], "y2": [1, 3, 2, 4, 6, 5, 7, 4, 3, 5]})
  st.area_chart(df_vol, color=["#00ff88", "#00bcd4"], height=110)

with col_centro:
  # Panel Central de Señal de Evento
  st.markdown(
      f"""
    <div class="center-panel">
        <div style="font-size: 8px; color: #8b949e; letter-spacing: 2px;">SEÑAL DE EVENTO A 15 MINUTOS</div>
        <div style="font-size: 18px; font-weight: 900; margin: 4px 0;">BTC/USD: PREDICCIÓN</div>
        <div style="font-size: 10px; color: #00ff88; margin-bottom: 10px;">${precio_btc:,.2f} EN TIEMPO REAL</div>
        
        <div class="gauge-circle">
            <div style="font-size: 14px; font-weight: 900; color: #00ff88;">SUBE / SÍ</div>
            <div style="font-size: 20px; font-weight: 900; color: #ffffff;">87.2%</div>
            <div style="font-size: 7px; color: #8b949e; letter-spacing: 1px;">CONFIANZA</div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  st.markdown(
      """
    <div class="card-box" style="padding: 6px;">
        <div style="font-size: 8px; color: #8b949e; margin-bottom: 2px;">FLUJO DE TICS (15M)</div>
    </div>
    """,
      unsafe_allow_html=True,
  )
  df_tendencia = pd.DataFrame({"precio": [68700, 68710, 68705, 68725, 68720, 68735, 68745]})
  st.line_chart(df_tendencia, color="#00ff88", height=90)

with col_der:
  # Presión del Libro de Órdenes
  st.markdown(
      """
    <div class="card-box">
        <div class="card-title">PRESIÓN DEL LIBRO DE ÓRDENES</div>
        <div style="display: flex; justify-content: space-between; font-size: 9px; margin-bottom: 4px;">
            <span style="color: #00ff88; font-weight: 700;">65% COMPRA</span>
            <span style="color: #ff4d4d; font-weight: 700;">35% VENTA</span>
        </div>
        <div style="background: #161b22; border-radius: 4px; height: 5px; width: 100%; overflow: hidden;">
            <div style="background: #00ff88; width: 65%; height: 100%;"></div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Sentimiento de Mercado
  st.markdown(
      """
    <div class="card-box">
        <div class="card-title">SENTIMIENTO DE MERCADO</div>
        <div style="display: flex; justify-content: space-around; text-align: center; padding: 4px 0;">
            <div><div style="font-size: 12px;">🎯</div><div style="font-size: 7px; color: #8b949e;">PRECISIÓN</div></div>
            <div><div style="font-size: 12px;">⚡</div><div style="font-size: 7px; color: #8b949e;">MOMENTO</div></div>
            <div><div style="font-size: 12px;">📊</div><div style="font-size: 7px; color: #8b949e;">VOLUMEN</div></div>
            <div><div style="font-size: 12px;">🛡️</div><div style="font-size: 7px; color: #8b949e;">RIESGO</div></div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Rendimiento Reciente
  st.markdown(
      """
    <div class="card-box">
        <div class="card-title">RENDIMIENTO RECIENTE</div>
        <div style="font-size: 8px; display: flex; justify-content: space-between; padding: 2px 0; border-bottom: 1px solid #161b22;">
            <span style="color: #8b949e;">68,745.20</span>
            <span style="color: #00ff88; font-weight: 700;">WIN +$1,000</span>
        </div>
        <div style="font-size: 8px; display: flex; justify-content: space-between; padding: 2px 0; border-bottom: 1px solid #161b22;">
            <span style="color: #8b949e;">68,730.00</span>
            <span style="color: #00ff88; font-weight: 700;">WIN +$1,000</span>
        </div>
        <div style="font-size: 8px; display: flex; justify-content: space-between; padding: 2px 0;">
            <span style="color: #8b949e;">68,715.50</span>
            <span style="color: #ff4d4d; font-weight: 700;">LOSS -$1,000</span>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )
