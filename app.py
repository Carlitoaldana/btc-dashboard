import streamlit as st

# Configuración de página responsive para iPhone
st.set_page_config(
    page_title="Predicción BTC",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS exactos para replicar la interfaz al milímetro
st.markdown("""
<style>
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    .stAppViewContainer {padding-top: 0px;}
    .block-container {padding-top: 1rem; padding-bottom: 2rem; max-width: 450px;}
    
    body, .stApp {
        background-color: #0E1117;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #E6E8EF;
    }

    /* Insignia Alerta Superior */
    .badge-alert {
        background-color: #0B3C85;
        color: #64B5F6;
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 13px;
        font-weight: 700;
        text-align: center;
        width: fit-content;
        margin: 0 auto 12px auto;
        border: 1px solid #1565C0;
    }

    /* Tarjeta Estimación Actual */
    .card-estimation {
        background-color: #0F1C15;
        border: 1px solid #1E4620;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        text-align: center;
    }
    .text-subtitle-sm {
        color: #81C784;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .text-main-green {
        color: #4CAF50;
        font-size: 26px;
        font-weight: 900;
        margin: 2px 0;
    }
    .text-sub {
        color: #A5D6A7;
        font-size: 12px;
        margin-bottom: 10px;
    }

    /* Barra Dual (UP / DOWN) */
    .bar-container {
        display: flex;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        background-color: #262931;
        margin-bottom: 6px;
    }
    .bar-up { background-color: #4CAF50; }
    .bar-mid { background-color: #FF9800; }
    .bar-down { background-color: #8D6E63; }

    .bar-labels {
        display: flex;
        justify-content: space-between;
        font-size: 10px;
        font-weight: 700;
    }
    .label-up { color: #4CAF50; }
    .label-down { color: #E57373; }

    /* Tarjeta Momentum */
    .card-momentum {
        background-color: #24190E;
        border: 1px solid #5D3A1A;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        text-align: center;
    }
    .text-momentum-title {
        color: #FFB74D;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    /* Tarjeta Señal Principal */
    .card-main-signal {
        background-color: #141824;
        border: 1px solid #23293A;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        text-align: center;
    }
    .text-gray-title {
        color: #78909C;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .text-gray-sub {
        color: #78909C;
        font-size: 12px;
        margin-top: 4px;
        margin-bottom: 14px;
    }

    /* Cajas UP / DOWN Split */
    .split-container {
        display: flex;
        gap: 10px;
        margin-bottom: 8px;
    }
    .box-up {
        flex: 1;
        background-color: #0F1C15;
        border: 1px solid #1E4620;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
    }
    .box-down {
        flex: 1;
        background-color: #1F1418;
        border: 1px solid #4A1B24;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
    }
    .mini-bar {
        height: 6px;
        border-radius: 3px;
        margin: 8px 0;
    }
    .mini-bar-up { background-color: #4CAF50; width: 41%; }
    .mini-bar-down { background-color: #E57373; width: 59%; }
    .mini-bar-bg { background-color: #262931; width: 100%; border-radius: 3px; }

    /* Bloque Confirmación y Bloque Indicadores */
    .card-section {
        background-color: #141824;
        border: 1px solid #23293A;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .indicator-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #1E2433;
    }
    .indicator-row:last-child { border-bottom: none; }
    .badge-green {
        background-color: #0F2918;
        color: #4CAF50;
        border: 1px solid #1E4620;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
    }
    .badge-orange {
        background-color: #33200A;
        color: #FF9800;
        border: 1px solid #5D3A1A;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
    }
    .footer-credits {
        text-align: center;
        color: #546E7A;
        font-size: 10px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. ALERTA SUPERIOR ---
st.markdown('<div class="badge-alert">🚨 ALERTA: VOLATILIDAD ALTA</div>', unsafe_allow_html=True)

# --- 2. ESTIMACIÓN ACTUAL (15m) ---
st.markdown("""
<div class="card-estimation">
    <div class="text-subtitle-sm">⚡ ESTIMACIÓN ACTUAL (15m)</div>
    <div class="text-main-green">POSIBLE UP · 62%</div>
    <div class="text-sub">Consenso entre Kalshi y Análisis Técnico</div>
    <div class="bar-container">
        <div class="bar-up" style="width: 62%;"></div>
        <div class="bar-mid" style="width: 10%;"></div>
        <div class="bar-down" style="width: 28%;"></div>
    </div>
    <div class="bar-labels">
        <span class="label-up">UP<br>62%</span>
        <span class="label-down">DOWN<br>38%</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 3. MOMENTUM DETECTADO ---
st.markdown("""
<div class="card-momentum">
    <div class="text-momentum-title">🚀 MOMENTUM DETECTADO</div>
    <div class="text-main-green" style="font-size: 22px; margin-top: 4px;">FUERTE REBOTE ALCISTA</div>
    <div style="color: #D7CCC8; font-size: 12px; margin-top: 4px;">Rompimiento de EMA confirmado en la vela actual</div>
</div>
""", unsafe_allow_html=True)

# --- 4. SEÑAL PRINCIPAL & SPLIT KALSHI ---
st.markdown("""
<div class="card-main-signal">
    <div class="text-gray-title">SEÑAL PRINCIPAL</div>
    <div class="text-main-green" style="font-size: 32px; margin: 6px 0;">POSIBLE UP</div>
    <div class="text-gray-sub">Esta llamada se actualiza cada 15 minutos exactos</div>
    
    <div class="split-container">
        <div class="box-up">
            <div style="color: #81C784; font-size: 11px; font-weight: 700;">UP</div>
            <div style="color: #4CAF50; font-size: 28px; font-weight: 900; margin: 2px 0;">41%</div>
            <div class="mini-bar-bg"><div class="mini-bar mini-bar-up"></div></div>
            <div style="color: #81C784; font-size: 10px; font-weight: 700; margin-top: 4px;">COMPRAR UP —</div>
        </div>
        <div class="box-down">
            <div style="color: #E57373; font-size: 11px; font-weight: 700;">DOWN</div>
            <div style="color: #E57373; font-size: 28px; font-weight: 900; margin: 2px 0;">59%</div>
            <div class="mini-bar-bg"><div class="mini-bar mini-bar-down"></div></div>
            <div style="color: #E57373; font-size: 10px; font-weight: 700; margin-top: 4px;">COMPRAR DOWN —</div>
        </div>
    </div>
    
    <div style="color: #78909C; font-size: 11px; margin-top: 6px;">El porcentaje sale directo de la probabilidad de Kalshi</div>
</div>
""", unsafe_allow_html=True)

# --- 5. CONFIRMACIÓN POST-ENTRADA ---
st.markdown("""
<div class="card-section">
    <div class="text-gray-title" style="margin-bottom: 8px;">CONFIRMACIÓN POST-ENTRADA</div>
    <div class="text-main-green" style="font-size: 20px; text-align: center; margin-bottom: 6px;">POSIBLE UP</div>
    <div style="color: #78909C; font-size: 11px; text-align: center;">Estimación basada en probabilidades, no garantía de resultado.</div>
</div>
""", unsafe_allow_html=True)

# --- 6. INDICADORES CLAVE ---
st.markdown("""
<div class="card-section">
    <div class="text-gray-title" style="margin-bottom: 10px;">INDICADORES CLAVE</div>
    
    <div class="indicator-row">
        <span style="font-size: 13px; font-weight: 600; color: #E6E8EF;">EMA 9 / EMA 21</span>
        <span class="badge-green">ALCISTA 🚀</span>
    </div>
    
    <div class="indicator-row">
        <span style="font-size: 13px; font-weight: 600; color: #E6E8EF;">RSI (14)</span>
        <span class="badge-green">NEUTRAL 54.1</span>
    </div>
    
    <div class="indicator-row">
        <span style="font-size: 13px; font-weight: 600; color: #E6E8EF;">Volatilidad (Bandas)</span>
        <span class="badge-orange">ALTA</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown('<div class="footer-credits">Macaly + Alpha Bot v2.1 | Made with AI</div>', unsafe_allow_html=True)
