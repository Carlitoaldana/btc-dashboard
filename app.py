import streamlit as st

st.set_page_config(page_title="BTC Ultra Sniper Elite", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { background-color: #030508; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC Elite Terminal</title>
    <style>
        body {
            background-color: #030508;
            color: #f1f5f9;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 12px;
            display: flex;
            justify-content: center;
        }

        .terminal-container {
            width: 100%;
            max-width: 420px;
            padding-bottom: 85px;
        }

        /* Top Bar */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(135deg, #0d131f 0%, #090e17 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 12px 16px;
            border-radius: 14px;
            margin-bottom: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .asset-title {
            font-size: 16px;
            font-weight: 800;
            letter-spacing: 0.3px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status-badge {
            font-size: 10px;
            font-weight: 700;
            color: #34d399;
            background: rgba(52, 211, 153, 0.1);
            border: 1px solid rgba(52, 211, 153, 0.3);
            padding: 4px 8px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Data Pods */
        .pods-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 12px;
        }
        .pod {
            background: linear-gradient(145deg, #0d131f, #090e17);
            border: 1px solid rgba(255, 255, 255, 0.06);
            padding: 12px;
            border-radius: 14px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }
        .pod-label {
            font-size: 10px;
            color: #64748b;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.8px;
            margin-bottom: 4px;
        }
        .pod-value {
            font-size: 18px;
            font-weight: 900;
            letter-spacing: -0.4px;
        }
        .pod-value.target { color: #fbbf24; text-shadow: 0 0 15px rgba(251, 191, 36, 0.2); }
        .pod-value.current { color: #34d399; text-shadow: 0 0 15px rgba(52, 211, 153, 0.2); }

        /* Chart Module */
        .chart-module {
            background: linear-gradient(145deg, #0d131f, #090e17);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 12px;
            margin-bottom: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }
        .chart-top {
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            color: #64748b;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 8px;
            letter-spacing: 0.8px;
        }
        .canvas-box {
            position: relative;
            width: 100%;
            height: 155px;
            background: #020406;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.04);
        }
        canvas {
            width: 100%;
            height: 100%;
            display: block;
        }

        /* Action Core Box */
        .action-core {
            background: linear-gradient(145deg, #0d131f, #090e17);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 14px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }
        .action-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-size: 10px;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }
        .time-pill {
            background: #131b2e;
            color: #f1f5f9;
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: 700;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .signal-screen {
            background: #131b2e;
            color: #fbbf24;
            padding: 16px;
            border-radius: 10px;
            font-weight: 900;
            font-size: 19px;
            text-align: center;
            letter-spacing: 0.5px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            box-shadow: inset 0 2px 6px rgba(0,0,0,0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .signal-desc {
            font-size: 12px;
            margin-top: 5px;
            font-weight: 500;
            opacity: 0.9;
        }

        /* Bottom Navbar */
        .elite-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(7, 11, 18, 0.92);
            backdrop-filter: blur(12px);
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            justify-content: space-around;
            padding: 10px 0 14px 0;
            z-index: 1000;
        }
        .nav-tab {
            text-align: center;
            color: #64748b;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            text-decoration: none;
            letter-spacing: 0.5px;
        }
        .nav-tab.active {
            color: #34d399;
        }
        .nav-ico {
            font-size: 16px;
            margin-bottom: 2px;
        }
    </style>
</head>
<body>

    <div class="terminal-container">
        <div class="top-bar">
            <div class="asset-title">
                <span style="color: #fbbf24;">⚡</span> BTC <span style="color: #64748b; font-weight: 500;">15m Kalshi Elite</span>
            </div>
            <div class="status-badge">● Live Sync</div>
        </div>

        <div class="pods-grid">
            <div class="pod">
                <div class="pod-label">Strike Objetivo</div>
                <div id="target-price" class="pod-value target">--.--</div>
            </div>
            <div class="pod">
                <div class="pod-label">Precio Actual</div>
                <div id="current-price" class="pod-value current">--.--</div>
            </div>
        </div>

        <div class="chart-module">
            <div class="chart-top">
                <span>Flujo de Precisión en Vivo</span>
                <span id="diff-tag" style="font-weight: 800; color: #34d399;">+$0.00</span>
            </div>
            <div class="canvas-box">
                <canvas id="priceCanvas"></canvas>
            </div>
        </div>

        <div class="action-core">
            <div class="action-header">
                <span id="window-status">ESTADO DEL BLOQUE</span>
                <span id="timer-text" class="time-pill">Cierra --:--</span>
            </div>
            <div class="signal-screen" id="signal-box">
                <div id="signal-main">INICIALIZANDO...</div>
                <div class="signal-desc" id="signal-sub">Calibrando motores de alta frecuencia</div>
            </div>
        </div>
    </div>

    <div class="elite-nav">
        <div class="nav-tab active"><div class="nav-ico">🤖</div><div>Terminal</div></div>
        <div class="nav-tab"><div class="nav-ico">📊</div><div>Trades</div></div>
        <div class="nav-tab"><div class="nav-ico">💳</div><div>Balance</div></div>
        <div class="nav-tab"><div class="nav-ico">⚙️</div><div>Config</div></div>
    </div>

    <script>
        let priceHistory = [];
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
                return canvas.height - ((p - minP) / (maxP - minP)) * (canvas.height - 24) - 12;
            }

            let strikeY = scaleY(strikePrice);
            ctx.strokeStyle = '#fbbf24';
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(0, strikeY);
            ctx.lineTo(canvas.width, strikeY);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = '#fbbf24';
            ctx.font = 'bold 9px sans-serif';
            ctx.fillText('STRIKE', 8, strikeY - 6);

            let step = canvas.width / (priceHistory.length - 1);
            let gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
            let isUp = currentPrice >= strikePrice;
            gradient.addColorStop(0, isUp ? 'rgba(52, 211, 153, 0.35)' : 'rgba(248, 113, 113, 0.35)');
            gradient.addColorStop(1, 'rgba(2, 4, 6, 0.0)');

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
            ctx.strokeStyle = isUp ? '#34d399' : '#f87171';
            ctx.lineWidth = 2.5;
            ctx.stroke();
        }

        async function fetchBTCData() {
            try {
                let res = await fetch('https://api.coinbase.com/v2/prices/BTC-USD/spot');
                let data = await res.json();
                let currentPrice = parseFloat(data.data.amount);

                let now = new Date();
                let totalSecondsToday = now.getUTCHours() * 3600 + now.getUTCMinutes() * 60 + now.getUTCSeconds();
                let secondsIntoBlock = totalSecondsToday % 900;
                let remainingSeconds = 900 - secondsIntoBlock;

                let blockId = Math.floor(totalSecondsToday / 900) + "-" + now.getUTCDate();

                let activeBlock = localStorage.getItem("elite_block_id");
                let strikePrice = parseFloat(localStorage.getItem("elite_strike_price") || "0");

                if (activeBlock !== blockId || !strikePrice || strikePrice === 0) {
                    strikePrice = currentPrice;
                    localStorage.setItem("elite_block_id", blockId);
                    localStorage.setItem("elite_strike_price", strikePrice);
                    priceHistory = [currentPrice];
                }

                priceHistory.push(currentPrice);
                if (priceHistory.length > 40) priceHistory.shift();

                let diff = currentPrice - strikePrice;

                document.getElementById('target-price').innerText = "$" + strikePrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                document.getElementById('current-price').innerText = "$" + currentPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

                let diffTag = document.getElementById('diff-tag');
                diffTag.innerText = (diff >= 0 ? "+$" : "-$") + Math.abs(diff).toFixed(2);
                diffTag.style.color = diff >= 0 ? "#34d399" : "#f87171";

                drawChart(strikePrice, currentPrice);

                let sBox = document.getElementById('signal-box');
                let sMain = document.getElementById('signal-main');
                let sSub = document.getElementById('signal-sub');
                let windowStatus = document.getElementById('window-status');

                let momentumScore = 0;
                if (priceHistory.length >= 5) {
                    let recent = priceHistory.slice(-5);
                    for (let i = 1; i < recent.length; i++) {
                        if (recent[i] > recent[i-1]) momentumScore++;
                        else if (recent[i] < recent[i-1]) momentumScore--;
                    }
                }

                if (secondsIntoBlock <= 180) {
                    windowStatus.innerText = "⚡ VENTANA ACTIVA (0-3 MIN)";
                    
                    if (momentumScore >= 2 && diff > 1.0) {
                        sBox.style.backgroundColor = "#064e3b";
                        sBox.style.color = "#34d399";
                        sBox.style.borderColor = "#34d399";
                        sMain.innerText = "🟢 ENTRAR UP";
                        sSub.innerText = "Impulso alcista confirmado desde el strike";
                    } else if (momentumScore <= -2 && diff < -1.0) {
                        sBox.style.backgroundColor = "#7f1d1d";
                        sBox.style.color = "#fca5a5";
                        sBox.style.borderColor = "#f87171";
                        sMain.innerText = "🔴 ENTRAR DOWN";
                        sSub.innerText = "Impulso bajista confirmado desde el strike";
                    } else {
                        sBox.style.backgroundColor = "#131b2e";
                        sBox.style.color = "#fbbf24";
                        sBox.style.borderColor = "rgba(255,255,255,0.06)";
                        sMain.innerText = "⏳ ESPERANDO RUPTURA";
                        sSub.innerText = "Monitoreando divergencia en tiempo real";
                    }
                } else {
                    windowStatus.innerText = "🔒 BLOQUE AVANZADO (ZONA CERRADA)";
                    sBox.style.backgroundColor = "#090e17";
                    sBox.style.color = "#475569";
                    sBox.style.borderColor = "rgba(255,255,255,0.03)";
                    sMain.innerText = "🛡️ FUERA DE TIEMPO";
                    sSub.innerText = "Ventana de entrada de 3 min finalizada";
                }

                let remainingMinutes = Math.floor(remainingSeconds / 60);
                let remainingSecs = remainingSeconds % 60;
                let secFormatted = remainingSecs < 10 ? "0" + remainingSecs : remainingSecs;
                document.getElementById('timer-text').innerText = "Cierra " + remainingMinutes + ":" + secFormatted;

            } catch (e) {
                console.error("Error Elite Terminal", e);
            }
        }

        setInterval(fetchBTCData, 1000);
        fetchBTCData();
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=780, scrolling=False)
