import streamlit as st

st.set_page_config(page_title="BTC Kalshi Bot Pro", layout="centered", initial_sidebar_state="collapsed")

# Ocultar completamente los elementos de Streamlit para que quede limpio como app nativa
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { background-color: #0b0e11; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

# HTML y JS puro incrustado que maneja el reloj, el target de 15m y la interfaz idéntica
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC 15 Min Pro</title>
    <style>
        body {
            background-color: #0b0e11;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 12px;
            display: flex;
            justify-content: center;
        }
        .app-container {
            width: 100%;
            max-width: 420px;
            padding-bottom: 75px;
        }
        .header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .coin-title {
            font-size: 16px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .prices-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            background: #161a22;
            padding: 10px;
            border-radius: 10px;
            border: 1px solid #2b313a;
            margin-bottom: 12px;
        }
        .price-box label {
            font-size: 10px;
            color: #848e9c;
            text-transform: uppercase;
        }
        .price-box .val {
            font-size: 16px;
            font-weight: bold;
            margin-top: 3px;
        }
        .val.target { color: #f0b90b; }
        .val.current { color: #0ecb81; }
        
        .chart-mock {
            background: #12161c;
            border: 1px solid #2b313a;
            border-radius: 10px;
            height: 160px;
            position: relative;
            margin-bottom: 12px;
            display: flex;
            align-items: flex-end;
            padding: 10px;
            overflow: hidden;
        }
        .target-line {
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            border-top: 1px dashed #f0b90b;
        }
        .target-label {
            position: absolute;
            top: calc(50% - 12px);
            right: 10px;
            background: #f0b90b;
            color: #000;
            font-size: 9px;
            font-weight: bold;
            padding: 2px 5px;
            border-radius: 3px;
        }
        
        .signal-card {
            background: #161a22;
            border: 1px solid #2b313a;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 12px;
        }
        .signal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            font-size: 11px;
            color: #848e9c;
        }
        .signal-box {
            background: #0ecb81;
            color: #000;
            padding: 10px 14px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #12161c;
            border-top: 1px solid #2b313a;
            display: flex;
            justify-content: space-around;
            padding: 8px 0;
            z-index: 1000;
        }
        .nav-item {
            text-align: center;
            color: #848e9c;
            font-size: 10px;
            text-decoration: none;
        }
        .nav-item.active {
            color: #0ecb81;
        }
    </style>
</head>
<body>

    <div class="app-container">
        <div class="header-row">
            <div class="coin-title">
                <span style="color: #f0b90b;">🟠</span> BTC 15 min <span style="font-size: 10px; color: #848e9c;">▼</span>
            </div>
            <div id="live-indicator" style="font-size: 11px; color: #0ecb81; background: rgba(14,203,129,0.1); padding: 3px 6px; border-radius: 4px;">● En vivo</div>
        </div>

        <div class="prices-grid">
            <div class="price-box">
                <label>Objetivo (Strike)</label>
                <div id="target-price" class="val target">Cargando...</div>
            </div>
            <div class="price-box">
                <label>Actual (Current)</label>
                <div id="current-price" class="val current">Cargando...</div>
            </div>
        </div>

        <div class="chart-mock">
            <div class="target-line"></div>
            <div class="target-label">OBJETIVO</div>
            <div id="diff-tag" style="position: absolute; bottom: 10px; left: 10px; font-size: 12px; font-weight: bold; color: #0ecb81;">+$0.00</div>
        </div>

        <div class="signal-card">
            <div class="signal-header">
                <span id="market-status">MERCADO ACTUAL • SEÑAL 15M</span>
                <span id="timer-text" style="background: #2b313a; color: #fff; padding: 2px 5px; border-radius: 3px;">Cierra --:--</span>
            </div>
            <div class="signal-box" id="signal-box">
                <span id="signal-text">↑ UP</span>
                <span id="signal-sub" style="font-size: 11px; font-weight: normal; background: rgba(0,0,0,0.2); padding: 3px 6px; border-radius: 3px;">Sube activo</span>
            </div>
        </div>
    </div>

    <div class="bottom-nav">
        <div class="nav-item active"><div>🤖</div><div>Bot</div></div>
        <div class="nav-item"><div>📈</div><div>Operaciones</div></div>
        <div class="nav-item"><div>💰</div><div>Saldo</div></div>
        <div class="nav-item"><div>⚙️</div><div>Ajustes</div></div>
    </div>

    <script>
        let lastBlockKey = "";

        async function fetchBTCData() {
            try {
                let res = await fetch('https://api.coinbase.com/v2/prices/BTC-USD/spot');
                let data = await res.json();
                let currentPrice = parseFloat(data.data.amount);

                // Calcular bloque UTC de 15 minutos exactos idéntico a Kalshi
                let now = new Date();
                let utcHour = now.getUTCHours();
                let utcMinute = now.getUTCMinutes();
                let blockMinute = Math.floor(utcMinute / 15) * 15;
                let blockKey = now.getUTCDate() + "-" + now.getUTCMonth() + "-" + utcHour + "-" + blockMinute;

                // Manejo de persistencia local en navegador para congelar el Strike del bloque
                let savedBlock = localStorage.getItem("kalshi_block_key");
                let savedStrike = localStorage.getItem("kalshi_strike_price");

                let strikePrice = 0;
                if (savedBlock === blockKey && savedStrike) {
                    strikePrice = parseFloat(savedStrike);
                } else {
                    strikePrice = currentPrice;
                    localStorage.setItem("kalshi_block_key", blockKey);
                    localStorage.setItem("kalshi_strike_price", strikePrice);
                }

                let diff = currentPrice - strikePrice;

                // Actualizar interfaz visual
                document.getElementById('target-price').innerText = "$" + strikePrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                document.getElementById('current-price').innerText = "$" + currentPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                
                let diffTag = document.getElementById('diff-tag');
                diffTag.innerText = (diff >= 0 ? "+$" : "-$") + Math.abs(diff).toFixed(2);
                diffTag.style.color = diff >= 0 ? "#0ecb81" : "#f6465d";

                // Cálculo de señal dinámico basado en la distancia al strike
                let sBox = document.getElementById('signal-box');
                let sText = document.getElementById('signal-text');
                let sSub = document.getElementById('signal-sub');

                if (diff > 1.5) {
                    sBox.style.backgroundColor = "#0ecb81";
                    sBox.style.color = "#000";
                    sText.innerText = "↑ UP";
                    sSub.innerText = "Precio arriba del target";
                } else if (diff < -1.5) {
                    sBox.style.backgroundColor = "#f6465d";
                    sBox.style.color = "#fff";
                    sText.innerText = "↓ DOWN";
                    sSub.innerText = "Precio abajo del target";
                } else {
                    sBox.style.backgroundColor = "#2b313a";
                    sBox.style.color = "#f0b90b";
                    sText.innerText = "⚠️ ZONA DE INDECISIÓN";
                    sSub.innerText = "Cerca del strike";
                }

                // Reloj regresivo para el cierre del bloque de 15m
                let remainingMinutes = 14 - (utcMinute % 15);
                let remainingSeconds = 59 - now.getUTCSeconds();
                let secFormatted = remainingSeconds < 10 ? "0" + remainingSeconds : remainingSeconds;
                document.getElementById('timer-text').innerText = "Cierra " + remainingMinutes + ":" + secFormatted;

            } catch (e) {
                console.error("Error actualizando precio", e);
            }
        }

        setInterval(fetchBTCData, 1000);
        fetchBTCData();
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=750, scrolling=False)
