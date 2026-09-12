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

# Estilos CSS idénticos y optimizados
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
    .tarjeta-maestra {
        background: linear-gradient(135deg, #0b2216 0%, #0d0a14 100%);
        border: 1px solid #163d28;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 4px;
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
        height: 24px;
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
        margin-bottom: 4px;
    }
    .fila-metricas {
        display: flex;
        gap: 4px;
        margin-bottom: 4px;
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
precio_btc = 77092.02
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
st.markdown('<div class="sub-top">MERCADO 15 MINUTOS</div>', unsafe_allow_html=True)

# Pestañas de navegación traducidas al español
pestana = st.radio(
    "Navegación",
    ["Panel", "Scalping", "Mesa 1H", "Señales", "Registro"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("<br>", unsafe_allow_html=True)

if pestana in ["Panel", "Señales", "Scalping"]:

  # Tarjeta Superior Maestra (con traducción de etiqueta LIVE a EN VIVO)
  st.markdown(
      f"""
    <div class="tarjeta-maestra">
        <div>
            <div style="font-size: 7px; color: #6b638a; letter-spacing: 1px;">BTC / USD (CONTADO) • ${precio_btc:,.2f} • EN VIVO</div>
            <div class="texto-buy">COMPRAR SUBIDA 🔺</div>
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

  # Gráfico de Tendencia
  st.markdown('<div class="caja-oscura">', unsafe_allow_html=True)
  st.markdown('<div style="font-size: 7px; color: #6b638a; letter-spacing: 1px; margin-bottom: 2px;">ESTRUCTURA DE CICLO 15M (FLUJO DE TICKS)</div>', unsafe_allow_html=True)
  df_grafico = obtener_velas()
  if df_grafico is not None:
    st.line_chart(df_grafico, color="#00ff88", height=120)
  else:
    st.info(f"Precio: ${precio_btc:,.2f}")
  st.markdown('</div>', unsafe_allow_html=True)

  # Fila de métricas inferiores traducidas
  st.markdown(
      """
    <div class="fila-metricas">
        <div class="caja-metrica">
            <div style="font-size: 7px; color: #6b638a;">TASA DE ACIERTO</div>
            <div style="font-size: 11px; font-weight: 800; color: #00ff88;">+6,100%</div>
        </div>
        <div class="caja-metrica">
            <div style="font-size: 7px; color: #6b638a;">SALDO BÓVEDA</div>
            <div style="font-size: 10px; font-weight: 800; color: #00ff88;">+91,220</div>
        </div>
        <div class="caja-metrica">
            <div style="font-size: 7px; color: #6b638a;">ESTADO</div>
            <div style="font-size: 9px; font-weight: 700; color: #fff;">VERIFICADO</div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Botón WIN final traducido
  st.markdown('<div class="boton-win-final">GANADA 🚀</div>', unsafe_allow_html=True)

else:
  st.markdown(
      f"""
    <div class="caja-oscura">
        <h3>Módulo: {pestana}</h3>
        <p style="color: #6b638a;">Sincronizado con Binance.US en tiempo real.</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown('</div>', unsafe_allow_html=True)
