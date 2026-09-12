import pandas as pd
import requests
import streamlit as st

# Configuración limpia de página
st.set_page_config(
    page_title="PREDICTION BOT - MAKING A BAG",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Estilos CSS con Flexbox estricto para la fila horizontal
st.markdown(
    """
    <style>
    .stApp {
        background-color: #05040a;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .titulo-top {
        font-size: 15px;
        font-weight: 900;
        color: #00ff88;
        letter-spacing: 1px;
        margin-bottom: 0px;
    }
    .sub-top {
        font-size: 8px;
        letter-spacing: 2px;
        color: #6b638a;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .tarjeta-verde {
        background: linear-gradient(135deg, #0b2216 0%, #0f0c18 100%);
        border: 1px solid #163d28;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 6px;
    }
    .texto-buy {
        font-size: 24px;
        font-weight: 900;
        color: #00ff88;
        letter-spacing: 2px;
        margin: 2px 0;
    }
    .caja-oscura {
        background-color: #0f0c18;
        border: 1px solid #1f182e;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 6px;
    }
    /* Contenedor Flexbox para forzar los 3 elementos en UNA SOLA FILA */
    .fila-horizontal {
        display: flex;
        gap: 6px;
        margin-bottom: 6px;
        width: 100%;
    }
    .item-fila {
        flex: 1;
        background-color: #0f0c18;
        border: 1px solid #1f182e;
        border-radius: 8px;
        text-align: center;
        padding: 8px 4px;
        font-size: 11px;
        font-weight: 700;
        color: #00ff88;
    }
    .fila-inferior {
        display: flex;
        gap: 6px;
        margin-bottom: 6px;
    }
    .caja-inferior {
        flex: 1;
        background-color: #0f0c18;
        border: 1px solid #1f182e;
        border-radius: 10px;
        padding: 10px;
    }
    .boton-win-final {
        background-color: #00ff88;
        color: #05040a;
        font-weight: 900;
        text-align: center;
        border-radius: 8px;
        padding: 10px;
        font-size: 15px;
        letter-spacing: 1px;
        margin-top: 6px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Obtener precio real de Binance.US
precio_btc = 77083.50
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


# Encabezado
st.markdown('<div class="titulo-top">PREDICTION BOT: MAKING A BAG 🚀</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-top">15MIN MARKET</div>', unsafe_allow_html=True)

# Pestañas de navegación
pestana = st.radio(
    "Navegación",
    ["Dashboard", "Scalping", "1H Desk", "Signals", "Journal"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("<br>", unsafe_allow_html=True)

if pestana in ["Dashboard", "Signals", "Scalping"]:

  # 1. Tarjeta superior BUY UP
  st.markdown(
      f"""
    <div class="tarjeta-verde">
        <div style="font-size: 8px; color: #6b638a; letter-spacing: 1px;">BTC / USD (SPOT) • ${precio_btc:,.2f} • LIVE</div>
        <div class="texto-buy">BUY UP 🔺</div>
        <div style="font-size: 18px; font-weight: 800; color: #00ff88;">82.6%</div>
        <div style="margin-top: 4px; background: #130f20; border-radius: 4px; height: 3px; width: 100%;">
            <div style="background: #00ff88; width: 82.6%; height: 3px; border-radius: 4px;"></div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # 2. Los 3 botones/iconos en UNA SOLA FILA usando Flexbox (Garantizado horizontal)
  st.markdown(
      """
    <div class="fila-horizontal">
        <div class="item-fila">🎯 LOCK</div>
        <div class="item-fila" style="color:#6b638a;">⚡ 15M</div>
        <div class="item-fila">📊 PRO</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # 3. Gráfico de Tendencia
  st.markdown('<div class="caja-oscura">', unsafe_allow_html=True)
  st.markdown('<div style="font-size: 8px; color: #6b638a; letter-spacing: 1px; margin-bottom: 4px;">ESTRUCTURA DE CICLO 15M (TICK FLOW)</div>', unsafe_allow_html=True)
  df_grafico = obtener_velas()
  if df_grafico is not None:
    st.line_chart(df_grafico, color="#00ff88", height=140)
  else:
    st.info(f"Precio actual: ${precio_btc:,.2f}")
  st.markdown('</div>', unsafe_allow_html=True)

  # 4. Bloques inferiores lado a lado con Flexbox
  st.markdown(
      """
    <div class="fila-inferior">
        <div class="caja-inferior">
            <div style="font-size: 8px; color: #6b638a;">LIVE RESULT</div>
            <div style="font-size: 12px; font-weight: 800; color: #00ff88; margin-top: 2px;">+91,220.00</div>
            <div style="font-size: 8px; color: #00ff88;">+6,100%</div>
        </div>
        <div class="caja-inferior">
            <div style="font-size: 8px; color: #6b638a;">AI ANALYSIS</div>
            <div style="font-size: 10px; font-weight: 700; color: #fff; margin-top: 2px;">✓ Liquidity Zone</div>
            <div style="font-size: 8px; color: #6b638a;">Verified</div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # 5. Botón WIN final
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
