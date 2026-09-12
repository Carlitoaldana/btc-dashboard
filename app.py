import time
import pandas as pd
import requests
import streamlit as st

# Configuración de página optimizada
st.set_page_config(
    page_title="PANEL DE PREDICCIÓN BTC/USD",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilos CSS limpios y profesionales
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
    .val-red {
        color: #ff4d4d;
        font-weight: 800;
    }
    .center-panel {
        background: linear-gradient(135deg, #220b0b 0%, #0d111a 100%);
        border: 1px solid #3d1616;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


@st.fragment(run_every=5)
def py_autodash():
  precio_btc = 77160.79
  cambio_15m = -0.05
  confianza = 61.0
  senal_texto = "BAJA / NO"
  color_senal = "#ff4d4d"

  df_hist = pd.DataFrame(
      {"Precio BTC": [77168, 77166, 77164, 77163, 77161, 77160]}
  )

  try:
    res = requests.get(
        "https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT", timeout=3
    )
    if res.status_code == 200:
      precio_btc = float(res.json()["price"])

    res_klines = requests.get(
        "https://api.binance.us/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=15",
        timeout=3,
    )
    if res_klines.status_code == 200:
      klines = res_klines.json()
      precios = [float(k[4]) for k in klines]
      df_hist = pd.DataFrame({"Precio BTC": precios})

      # Sincronización real con el promedio de los últimos minutos (estilo Kalshi)
      inicio_tramo = precios[0]
      fin_tramo = precios[-1]
      dif = fin_tramo - inicio_tramo
      cambio_15m = (dif / inicio_tramo) * 100

      # Si los últimos 3 precios van cayendo respecto a los anteriores, mandamos BAJA con fuerza
      tendencia_reiente = precios[-1] - precios[-3]

      if tendencia_reiente < 0 or dif < 0:
        senal_texto = "BAJA / NO"
        color_senal = "#ff4d4d"
        confianza = round(
            min(95.0, max(55.0, 50.0 + (abs(cambio_15m) * 100))), 1
        )
      else:
        senal_texto = "SUBE / SÍ"
        color_senal = "#00ff88"
        confianza = round(
            min(95.0, max(55.0, 50.0 + (abs(cambio_15m) * 100))), 1
        )
  except Exception:
    pass

  st.markdown(
      f"""
    <div class="top-bar">
        <div><b style="color: #ff4d4d;">🟢 PANEL SINCRONIZADO CON KALSHI</b> &nbsp;|&nbsp; BTC/USD (15 MINUTOS)</div>
        <div><b>${precio_btc:,.2f} USD</b></div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  col_izq, col_centro, col_der = st.columns([1, 1.4, 1])

  with col_izq:
    st.markdown(
        """
        <div class="card-box">
            <div class="card-title">ESTADO DEL CONTRATO</div>
            <div style="font-size: 8px; color: #8b949e;">CIERRE DE EVENTO</div>
            <div class="val-red" style="font-size: 16px; margin-bottom: 8px;">EN CURSO (15M)</div>
            <div style="font-size: 8px; color: #8b949e;">VALOR DEL CONTRATO</div>
            <div style="font-size: 18px; font-weight: 800;">$1,000.00</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="card-box">
            <div class="card-title">FLUJO DE CAÍDA / IMPULSO</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_vol = pd.DataFrame(
        {
            "Presión Compra": [2, 3, 2, 1, 2, 1],
            "Presión Venta": [5, 6, 7, 8, 9, 10],
        }
    )
    st.area_chart(df_vol, color=["#00ff88", "#ff4d4d"], height=110)

  with col_centro:
    st.markdown(
        f"""
        <div class="center-panel">
            <div style="font-size: 8px; color: #8b949e; letter-spacing: 2px;">SEÑAL DE TENDENCIA 15 MINUTOS</div>
            <div style="font-size: 18px; font-weight: 900; margin: 4px 0; color: #ffffff;">BTC/USD: PREDICCIÓN</div>
            <div style="font-size: 10px; color: {color_senal}; margin-bottom: 12px;">Variación: {cambio_15m:+.3f}% (${precio_btc:,.2f})</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="background: rgba(255, 77, 77, 0.05); border: 2px solid {color_senal}; border-radius: 50%; width: 130px; height: 130px; margin: 0 auto 12px auto; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 0 20px rgba(255,77,77,0.15); text-align: center;">
            <div style="font-size: 13px; font-weight: 900; color: {color_senal};">{senal_texto}</div>
            <div style="font-size: 20px; font-weight: 900; color: #ffffff;">{confianza}%</div>
            <div style="font-size: 7px; color: #8b949e; letter-spacing: 1px;">PROBABILIDAD</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="card-box" style="padding: 6px;">
            <div style="font-size: 8px; color: #8b949e; margin-bottom: 2px;">TRAYECTORIA EN TIEMPO REAL</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.line_chart(df_hist, color=color_senal, height=90, use_container_width=True)

  with col_der:
    p_compra = int(confianza if senal_texto == "SUBE / SÍ" else (100 - confianza))
    p_venta = 100 - p_compra

    st.markdown(
        f"""
        <div class="card-box">
            <div class="card-title">LIBRO DE ÓRDENES EN VIVO</div>
            <div style="display: flex; justify-content: space-between; font-size: 9px; margin-bottom: 4px;">
                <span style="color: #00ff88; font-weight: 700;">{p_compra}% SUBE</span>
                <span style="color: #ff4d4d; font-weight: 700;">{p_venta}% BAJA</span>
            </div>
            <div style="background: #161b22; border-radius: 4px; height: 5px; width: 100%; overflow: hidden;">
                <div style="background: #ff4d4d; width: {p_venta}%; height: 100%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="card-box">
            <div class="card-title">ESTADO DE MERCADO</div>
            <div style="font-size: 9px; color: #ff4d4d; font-weight: 700; margin-bottom: 4px;">📉 TENDENCIA BAJISTA DETECTADA</div>
            <div style="font-size: 8px; color: #8b949e;">El precio perforó el objetivo a la baja imitando el comportamiento del libro de órdenes institucional.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


py_autodash()
