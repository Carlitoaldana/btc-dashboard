import time
import requests
import streamlit as st

# Configuración de la página con diseño oscuro y móvil
st.set_page_config(
    page_title="VIXY'S VAULT - Decision Intelligence",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Estilos CSS personalizados para replicar la interfaz de Vixy's Vault (estilo oscuro, tipografía y tarjetas)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0914;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .header-title {
        font-size: 14px;
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
        padding: 18px;
        margin-bottom: 15px;
    }
    .signal-box {
        background: linear-gradient(135deg, #10261c 0%, #151221 100%);
        border: 1px solid #1f4a34;
        border-radius: 14px;
        padding: 22px;
        text-align: center;
        margin-bottom: 15px;
    }
    .signal-text {
        font-size: 36px;
        font-weight: 900;
        color: #00ff88;
        letter-spacing: 2px;
        margin: 10px 0;
    }
    .confidence-text {
        font-size: 32px;
        font-weight: 800;
        color: #00ff88;
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

# Obtener precio en vivo de Binance.US para BTC
btc_price = 62730.99  # Valor por defecto de respaldo
try:
  response = requests.get(
      "https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT", timeout=3
  )
  if response.status_code == 200:
    btc_price = float(response.json()["price"])
except Exception:
  pass

# Encabezado superior
st.markdown(
    '<div class="header-title">Decision Intelligence</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="main-brand">VIXY\'S VAULT</div>', unsafe_allow_html=True
)

# Pestañas de navegación superiores simuladas
nav_tab = st.radio(
    "Navegación",
    ["Dashboard", "Scalping", "1H Desk", "Signals", "Journal"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("<br>", unsafe_allow_html=True)

if nav_tab == "Dashboard" or nav_tab == "Signals":
  # Bloque de Ciclo y Estado
  st.markdown(
      f"""
    <div class="card-box">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="sub-label">MERCADO EN VIVO (BINANCE.US)</span>
            <span style="font-size: 12px; color: #00ff88;">● ACTIVO</span>
        </div>
        <div style="font-size: 26px; font-weight: 700; margin-top: 6px;">${btc_price:,.2f}</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Tarjeta de Señal Principal (BUY UP)
  st.markdown(
      """
    <div class="signal-box">
        <div class="sub-label">AUTHORITATIVE 15M CYCLE LOCK</div>
        <div class="signal-text">BUY UP 🔺</div>
        <div style="font-size: 12px; color: #a19bb8;">STRIKE: $62,730.99</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Tarjeta de Confianza del Modelo
  st.markdown(
      """
    <div class="card-box">
        <div class="sub-label">LOCKED MODEL CONFIDENCE</div>
        <div class="confidence-text">73%</div>
        <div style="margin-top: 8px; font-size: 13px; color: #00ff88; font-weight: 600;">STRONG BULLISH CONFIDENCE</div>
        <div style="margin-top: 12px; background: #221d36; border-radius: 8px; height: 6px; width: 100%;">
            <div style="background: #00ff88; width: 73%; height: 6px; border-radius: 8px;"></div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Bloque de validación inmutable
  st.markdown(
      """
    <div class="card-box" style="font-size: 12px; color: #9a95b5; line-height: 1.6;">
        ✓ ONE-CYCLE IMMUTABLE LOCK: SPOT AT LOCK: $62,723.645<br>
        CYCLE: 15M-2026-08-14T1 | LOCKED AT: 6:00:16 AM
    </div>
    """,
      unsafe_allow_html=True,
  )

else:
  st.markdown(
      f"""
    <div class="card-box">
        <h3>Sección: {nav_tab}</h3>
        <p style="color: #9a95b5;">Módulo de análisis algorítmico y ejecución en tiempo real conectado al nodo de Binance.US.</p>
        <p><b>Precio actual BTC:</b> ${btc_price:,.2f}</p>
    </div>
    """,
      unsafe_allow_html=True,
  )
