import pandas as pd
import requests
import streamlit as st

# Configuración idéntica de página compacta
st.set_page_config(
    page_title="PREDICTION BOT - MAKING A BAG",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Estilos CSS exactos para replicar la tarjeta compacta de la captura
st.markdown(
    """
    <style>
    .stApp {
        background-color: #05040a;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .main-container {
        max-width: 420px;
        margin: 0 auto;
        padding: 4px;
    }
    .titulo-top {
        font-size: 13px;
        font-weight: 900;
        color: #00ff88;
        letter-spacing: 1px;
        margin-bottom: -2px;
    }
    .sub-top {
        font-size: 7px;
        letter-spacing: 2px;
        color: #6b638a;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    /* Tarjeta maestra que encierra el BUY UP y los mini círculos a la derecha */
    .tarjeta-maestra {
        background: linear-gradient(135deg, #0b2216 0%, #0d0a14 100%);
        border: 1px solid #163d28;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .texto-buy {
        font-size: 20px;
        font-weight: 900;
        color: #00ff88;
        letter-spacing: 1px;
        margin: 1px 0;
    }
    /* Contenedor de los 4 botoncitos circulares/cuadrados en columna derecha */
    .columna-iconos {
        display: flex;
        flex-direction: column;
        gap: 3px;
    }
    .mini-circulo {
        background-color: #151122;
        border: 1px solid #251d3b;
        border-radius: 6px;
        width: 32px;
        height: 26px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
    }
    .caja-oscura {
        background-color: #0d0a14;
        border: 1px solid #1f182e;
        border-radius: 8px;
        padding: 8px;
        margin-bottom: 6px;
    }
    .fila-metricas {
        display: flex;
        gap: 4px;
        margin-bottom: 6px;
    }
    .caja-metrica {
        flex: 1;
        background-color: #0d0a14;
        border: 1px solid #1f182e;
        border-radius: 8px;
        padding: 6px;
        text-align: center;
    }
    .boton-win-final {
        background-color: #00ff88;
        color: #05040a;
        font-weight: 900;
        text-align: center;
        border-radius: 8px;
        padding: 8px;
        font-size: 13px;
        letter-spacing: 1px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Obtener precio real de Binance.US
precio_btc = 77075.25
try:
  res = requests.get(
      "https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT", timeout=3
  )
  if res.status_code == 200:
    precio_btc = float(res.json()["price"])
except Exception:
  pass


# Datos para el gráfico de velas 15M
@st.cache_data(ttl=10)
def obtener_velas():
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


# Contenedor general centrado
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Encabezado
st.markdown('<div class="titulo-top">PREDICTION BOT: MAKING A BAG 🚀</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-top">15MIN MARKET</div>', unsafe_allow_html=True)

# Pestañas de navegación compactas
pestana = st.radio(
    "Navegación",
    ["Dashboard", "Scalping", "1H Desk", "Signals", "Journal"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("<br>", unsafe_allow_html=True)

if pestana in ["Dashboard", "Signals", "Scalping"]:

  # Tarjeta Superior Maestra (BUY UP a la izquierda + 4 iconos exactos a la derecha como en la foto)
  st.markdown(
      f"""
    <div class="tarjeta-maestra">
        <div>
            <div style="font-size: 7px; color: #6b638a; letter-spacing: 1px;">BTC / USD (SPOT) • ${precio_btc:,.2f} • LIVE</div>
            <div class="texto-buy">BUY UP 🔺</div>
            <div style="font-size: 15px; font-weight: 800; color: #00ff88;">82.6%</div>
            <div style="margin-top: 3px; background: #130f20; border-radius: 4px; height: 3px; width: 140px;">
                <div style="background: #00ff88; width: 82.6%; height: 3px; border-radius: 4px;"></div>
            </div>
        </div>
        <div class="columna-iconos">
            <div class="mini-circulo">🎯</div>
            <div class="mini-circulo">⚡</div>
            <div class="mini-circulo">📊</div>
            <div class="mini-circulo">🛡️</div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Gráfico de Tendencia Verde Integrado
  st.markdown('<div class="caja-oscura">', unsafe_allow_html=True)
  st.markdown('<div style="font-size: 7px; color: #6b638a; letter-spacing: 1px; margin-bottom: 2px;">ESTRUCTURA DE CICLO 15M (TICK FLOW)</div>', unsafe_allow_html=True)
  df_grafico = obtener_velas()
  if df_grafico is not None:
    st.line_chart(df_grafico, color="#00ff88", height=120)
  else:
    st.info(f"Precio: ${precio_btc:,.2f}")
  st.markdown('</div>', unsafe_allow_html=True)

  # Fila de métricas inferiores (3 columnas idénticas a la captura de TikTok)
  st.markdown(
      """
    <div class="fila-metricas">
        <div class="caja-metrica">
            <div style="font-size: 7px; color: #6b638a;">WIN RATE</div>
            <div style="font-size: 11px; font-weight: 800; color: #00ff88;">+6,100%</div>
        </div>
        <div class="caja-metrica">
            <div style="font-size: 7px; color: #6b638a;">VAULT BAL</div>
            <div style="font-size: 10px; font-weight: 800; color: #00ff88;">+91,220</div>
        </div>
        <div class="caja-metrica">
            <div style="font-size: 7px; color: #6b638a;">STATUS</div>
            <div style="font-size: 9px; font-weight: 700; color: #fff;">VERIFIED</div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Botón WIN final idéntico
  st.markdown('<div class="boton-win-final">WIN 🚀</div>', unsafe_allow_html=True)

else:
  st.markdown(
      f"""
    <div class="caja-oscura">
        <h3>Módulo: {pestana}</h3>
        <p style="color: #6b638a;">Sincronizado con Binance.US.</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown('</div>', unsafe_allow_html=True)
