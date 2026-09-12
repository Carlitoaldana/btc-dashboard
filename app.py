import streamlit as st

st.set_page_config(page_title="BTC Kalshi Sniper Pro", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { background-color: #0b0e11; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC 15 Min Sniper Pro</title>
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

        .chart-card {
            background: #161a22;
            border: 1px solid #2b313a;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 12px;
        }
        .chart-header {
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            color: #848e9c;
            margin-bottom: 6px;
            text-transform: uppercase;
        }
        .canvas-container {
            position: relative;
            width: 100%;
            height: 150px;
            background: #0b0e11;
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid #2b313a;
        }
        canvas {
            width: 100%;
            height: 100%;
            display: block;
        }
        
        .signal-card {
            background: #161a22;
            border: 1px solid #2b313a;
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 12px;
        }
        .signal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-size: 11px;
            color: #848e9c;
        }
        .signal-box {
            background: #2b313a;
            color: #f0b90b;
            padding: 16px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 22px;
            text-align: center;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .signal-sub {
            font-size: 12px;
            margin-top: 6px;
            font-weight: normal;
            opacity: 0.95;
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
            <div style="font-size: 11px; color: #0ecb81; background: rgba(14,203,129,0.1); padding: 3px 6px; border-radius: 4px;">● Blindaje Activo</div>
        </div>

        <div class="prices-grid">
            <div class="price-box">
                <label>Strike Oficial (Bloque)</label>
                <div id="target-price" class="val target">Cargando...</div>
            </div>
            <div class="price-box">
                <label>Actual (Current)</label>
                <div id="current-price" class="val current">Cargando...</div>
            </div>
        </div>

        <div class="chart-card">
            <div class="chart-header">
                <span>Flujo de Precio en Vivo</span>
                <span id="diff-tag" style="font-weight: bold; color: #0ecb81;">+$0.00</span>
            </div>
            <div class="canvas-container">
                <canvas id="priceCanvas"></canvas>
            </div>
        </div>

        <div class="signal-card">
            <div class="signal-header">
                <span>SEÑAL OFICIAL 15M</span>
                <span id="timer-text" style="background: #2b313a; color: #fff; padding: 2px 6px; border-radius: 4px;">Cierra --:--</span>
            </div>
            <div class="signal-box" id="signal-box">
                <div id="signal-main">ANALIZANDO...</div>
                <div class="signal-sub" id="signal-sub">Filtros anti-amague activados</div>
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
        let priceHistory = [];
        let persistedUpCount = 0;
        let persistedDownCount = 0;
        
        const canvas = document.getElementById('priceCanvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        function drawChart(strikePrice, currentPrice) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (priceHistory.length < 2) return;

            let minP = Math.min(...priceHistory, strikePrice);
            let maxP = Math.max(...priceHistory, strikePrice);
            let padding = (maxP - minP) * 0.15;
            if (padding === 0) padding = 5;
            minP -= padding;
            maxP += padding;

            function scaleY(p) {
                return canvas.height - ((p - minP) / (maxP - minP)) * (canvas.height - 20) - 10;
            }

            let strikeY = scaleY(strikePrice);
            ctx.strokeStyle = '#f0b90b';
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(0, strikeY);
            ctx.lineTo(canvas.width, strikeY);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = '#f0b90b';
            ctx.font = '9px sans-serif';
            ctx.fillText('STRIKE', 6, strikeY - 4);

            let step = canvas.width / (priceHistory.length - 1);
            let gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
            let isUp = currentPrice >= strikePrice;
            gradient.addColorStop(0, isUp ? 'rgba(14, 203, 129, 0.25)' : 'rgba(246, 70, 93, 0.25)');
            gradient.addColorStop(1, 'rgba(11, 14, 17, 0.0)');

            ctx.beginPath();
            ctx.moveTo(0, canvas.height);
            for (let i = 0; i < priceHistory.length; i++) {
                let x = i * step;
                let y = scaleY(priceHistory[i]);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.lineTo((priceHistory.length - 1) * step, canvas.height);
            ctx.closePath();
            ctx.fillStyle = gradient;
            ctx.fill();

            ctx.beginPath();
            for (let i = 0; i < priceHistory.length; i++) {
                let x = i * step;
                let y = scaleY(priceHistory[i]);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.strokeStyle = isUp ? '#0ecb81' : '#f6465d';
            ctx.lineWidth = 2;
            ctx.stroke();
        }

        async function fetchBTCData() {
            try {
                let res = await fetch('https://api.coinbase.com/v2/prices/BTC-USD/spot');
                let data = await res.json();
                let currentPrice = parseFloat(data.data.amount);

                priceHistory.push(currentPrice);
                if (priceHistory.length > 40) priceHistory.shift();

                let now = new Date();
                let utcHour = now.getUTCHours();
                let utcMinute = now.getUTCMinutes();
                let utcSecond = now.getUTCSeconds();
                let blockMinute = Math.floor(utcMinute / 15) * 15;
                
                // Clave única para fijar el Strike exacto al iniciar el bloque de 15 min
                let blockKey = now.getUTCDate() + "-" + now.getUTCMonth() + "-" + utcHour + "-" + blockMinute;

                let savedBlock = localStorage.getItem("kalshi_strike_block");
                let savedStrike = localStorage.getItem("kalshi_strike_price");

                let strikePrice = 0;
                if (savedBlock === blockKey && savedStrike) {
                    strikePrice = parseFloat(savedStrike);
                } else {
                    strikePrice = currentPrice;
                    localStorage.setItem("kalshi_strike_block", blockKey);
                    localStorage.setItem("kalshi_strike_price", strikePrice);
                    priceHistory = [currentPrice];
                    persistedUpCount = 0;
                    persistedDownCount = 0;
                }

                let diff = currentPrice - strikePrice;
                let secondsIntoBlock = (utcMinute % 15) * 60 + utcSecond;
                let remainingSeconds = 900 - secondsIntoBlock;
                if (remainingSeconds < 1) remainingSeconds = 1;

                // Filtro de persistencia fuerte: exige distancia real de más de $15 dólares y constancia de 6 segundos
                if (diff > 15.0) {
                    persistedUpCount++;
                    persistedDownCount = 0;
                } else if (diff < -15.0) {
                    persistedDownCount++;
                    persistedUpCount = 0;
                } else {
                    persistedUpCount = Math.max(0, persistedUpCount - 1);
                    persistedDownCount = Math.max(0, persistedDownCount - 1);
                }

                let probability = 50;
                if (persistedUpCount >= 6) {
                    probability = Math.min(96, 60 + Math.floor(diff * 0.8));
                } else if (persistedDownCount >= 6) {
                    probability = Math.min(96, 60 + Math.floor(Math.abs(diff) * 0.8));
                }

                document.getElementById('target-price').innerText = "$" + strikePrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                document.getElementById('current-price').innerText = "$" + currentPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

                let diffTag = document.getElementById('diff-tag');
                diffTag.innerText = (diff >= 0 ? "+$" : "-$") + Math.abs(diff).toFixed(2);
                diffTag.style.color = diff >= 0 ? "#0ecb81" : "#f6465d";

                drawChart(strikePrice, currentPrice);

                let sBox = document.getElementById('signal-box');
                let sMain = document.getElementById('signal-main');
                let sSub = document.getElementById('signal-sub');

                // Si no hay ruptura sólida, se queda esperando en lugar de adivinar a lo idiota
                if (persistedUpCount >= 6) {
                    sBox.style.backgroundColor = "#0ecb81";
                    sBox.style.color = "#000";
                    sMain.innerText = "🟢 UP";
                    sSub.innerText = "Ruptura firme confirmada (" + probability + "%)";
                } else if (persistedDownCount >= 6) {
                    sBox.style.backgroundColor = "#f6465d";
                    sBox.style.color = "#fff";
                    sMain.innerText = "🔴 DOWN";
                    sSub.innerText = "Ruptura firme confirmada (" + probability + "%)";
                } else {
                    sBox.style.backgroundColor = "#2b313a";
                    sBox.style.color = "#f0b90b";
                    sMain.innerText = "⏳ ESPERANDO DIRECCIÓN";
                    sSub.innerText = "Zona de indecisión / Faltan $15 de distancia";
                }

                let remainingMinutes = Math.floor(remainingSeconds / 60);
                let remainingSecs = remainingSeconds % 60;
                let secFormatted = remainingSecs < 10 ? "0" + remainingSecs : remainingSecs;
                document.getElementById('timer-text').innerText = "Cierra " + remainingMinutes + ":" + secFormatted;

            } catch (e) {
                console.error("Error en bot blindado", e);
            }
        }

        setInterval(fetchBTCData, 1000);
        fetchBTCData();
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=780, scrolling=False)
