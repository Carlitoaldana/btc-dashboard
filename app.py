import time
import pandas as pd
import requests
import streamlit as st

# Configuración de página para escritorio
st.set_page_config(
    page_title="TRADING DASHBOARD UI - BTC/USD",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilos CSS avanzados para replicar el monitor de la pantalla
st.markdown(
    """
    <style>
    .stApp {
        background-color: #07090e;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .top-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #0d111a;
        padding: 8px 16px;
        border-bottom: 1px solid #1a2332;
        border-radius: 6px;
        margin-bottom: 16px;
        font-size: 12px;
        color: #8b949e;
    }
    .nav-title {
        color: #00ff88;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .card {
        background: #0d111a;
        border: 1px solid #1a2332;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .card-title {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #8b949e;
        margin-bottom: 8px;
        font-weight: 600;
    }
    .metric-big {
        font-size: 22px;
        font-weight: 800;
        color: #ffffff;
    }
    .metric-green {
        color: #00ff88;
        font-weight: 800;
    }
    .badge-signal {
        background: linear-gradient(135deg, #0b2216 0%, #0d111a 100%);
        border: 1px solid #163d28;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        position: relative;
    }
    .progress-bar-container {
        background: #161b22;
        border-radius: 6px;
        height: 6px;
        width: 100%;
        overflow: hidden;
        margin-top: 8px;
    }
    .progress-bar-fill {
        background: #00ff88;
        height: 100%;
        border-radius: 6px;
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

# Barra superior de navegación estilo terminal
st.markdown(
    f"""
    <div class="top-navbar">
        <div><span class="nav-title">🟢 TRADING DASHBOARD UI</span> &nbsp;|&nbsp; BTC/USD PREDICCIÓN • ${precio_btc:,.2f}</div>
        <div><b>Índice Evento</b> &nbsp;&nbsp;|&nbsp;&nbsp; <b>Spot/Spot</b> &nbsp;&nbsp;|&nbsp;&nbsp; <b>Flujo de Órdenes</b> &nbsp;&nbsp;|&nbsp;&nbsp; <b>Libro de Órdenes</b></div>
    </div>
""",
    unsafe_allow_html=True,
)

# Estructura principal de 3 columnas (Izquierda, Centro, Derecha)
col_izq, col_centro, col_der = st.columns([1.1, 1.8, 1.1])

with col_izq:
  # Estado del contrato
  st.markdown(
      """
    <div class="card">
        <div class="card-title">ESTADO DEL CONTRATO</div>
        <div style="font-size: 9px; color: #8b949e;">TIEMPO PARA EXPIRACIÓN</div>
        <div class="metric-green" style="font-size: 18px; margin-bottom: 10px;">13:45 MIN</div>
        <div style="font-size: 9px; color: #8b949e;">VALOR DEL CONTRATO</div>
        <div class="metric-big">$1,000.00</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Volatilidad del mercado
  st.markdown(
      """
    <div class="card">
        <div class="card-title">VOLATILIDAD DE MERCADO (15M)</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Generar gráfico de calor / volatilidad simulado
  df_vol = pd.DataFrame(
      {
          "x": range(10),
          "y1": [2, 4, 3, 5, 7, 6, 8, 5, 4, 6],
          "y2": [1, 3, 2, 4, 6, 5, 7, 4, 3, 5],
      }
  )
  st.area_chart(df_vol[["y1", "y2"]], color=["#00ff88", "#00bcd4"], height=140)

with col_centro:
  # Panel central de señal de evento a 15 minutos
  st.markdown(
      f"""
    <div class="badge-signal">
        <div style="font-size: 10px; color: #8b949e; letter-spacing: 2px;">SEÑAL DE EVENTO A 15 MINUTOS</div>
        <div style="font-size: 20px; font-weight: 900; color: #ffffff; margin: 6px 0;">BTC/USD: PREDICCIÓN</div>
        <div style="font-size: 11px; color: #00ff88; margin-bottom: 14px;">${precio_btc:,.2f} EN TIEMPO REAL</div>
        
        <div style="background: rgba(0, 255, 136, 0.05); border: 2px solid #00ff88; border-radius: 50%; width: 140px; height: 140px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 0 20px rgba(0,255,136,0.15);">
            <div style="font-size: 16px; font-weight: 900; color: #00ff88;">SUBE / SÍ</div>
            <div style="font-size: 22px; font-weight: 900; color: #ffffff;">87.2%</div>
            <div style="font-size: 8px; color: #8b949e; letter-spacing: 1px;">CONFIANZA</div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Mini gráfico inferior del panel central
  st.markdown(
      """
    <div class="card" style="margin-top: 12px; padding: 8px;">
        <div style="font-size: 9px; color: #8b949e; margin-bottom: 4px;">TENDENCIA DE PRECISIÓN DE TICK</div>
    </div>
    """,
      unsafe_allow_html=True,
  )
  df_tendencia = pd.DataFrame({"precio": [68700, 68710, 68705, 68725, 68720, 68735, 68745]})
  st.line_chart(df_tendencia, color="#00ff88", height=100)

with col_der:
  # Presión de libro de órdenes
  st.markdown(
      """
    <div class="card">
        <div class="card-title">PRESIÓN DEL LIBRO DE ÓRDENES</div>
        <div style="display: flex; justify-content: space-between; font-size: 10px; margin-bottom: 4px;">
            <span style="color: #00ff88;">65% COMPRA</span>
            <span style="color: #ff4d4d;">35% VENTA</span>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: 65%;"></div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Sentimiento de mercado
  st.markdown(
      """
    <div class="card">
        <div class="card-title">SENTIMIENTO DE MERCADO</div>
        <div style="display: flex; justify-content: space-around; text-align: center; margin-top: 8px;">
            <div>
                <div style="font-size: 14px;">🎯</div>
                <div style="font-size: 8px; color: #8b949e; margin-top: 2px;">PRECISIÓN</div>
            </div>
            <div>
                <div style="font-size: 14px;">⚡</div>
                <div style="font-size: 8px; color: #8b949e; margin-top: 2px;">MOMENTO</div>
            </div>
            <div>
                <div style="font-size: 14px;">📊</div>
                <div style="font-size: 8px; color: #8b949e; margin-top: 2px;">VOLUMEN</div>
            </div>
            <div>
                <div style="font-size: 14px;">🛡️</div>
                <div style="font-size: 8px; color: #8b949e; margin-top: 2px;">RIESGO</div>
            </div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Rendimiento reciente
  st.markdown(
      """
    <div class="card">
        <div class="card-title">RENDIMIENTO RECIENTE</div>
        <div style="font-size: 9px; display: flex; justify-content: space-between; padding: 3px 0; border-bottom: 1px solid #161b22;">
            <span style="color: #8b949e;">68,745.20</span>
            <span style="color: #00ff88; font-weight: 700;">WIN +$1,000</span>
        </div>
        <div style="font-size: 9px; display: flex; justify-content: space-between; padding: 3px 0; border-bottom: 1px solid #161b22;">
            <span style="color: #8b949e;">68,730.00</span>
            <span style="color: #00ff88; font-weight: 700;">WIN +$1,000</span>
        </div>
        <div style="font-size: 9px; display: flex; justify-content: space-between; padding: 3px 0;">
            <span style="color: #8b949e;">68,715.50</span>
            <span style="color: #ff4d4d; font-weight: 700;">LOSS -$1,000</span>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )
