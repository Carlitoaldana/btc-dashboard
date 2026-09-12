import streamlit as st

st.set_page_config(page_title="BTC Kalshi Pro Sniper", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { background-color: #07090c; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC Pro Sniper</title>
    <style>
        :root {
            --bg-main: #07090c;
            --bg-card: #12161f;
            --bg-card-hover: #181f2c;
            --border-color: #1f2736;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-yellow: #f59e0b;
            --accent-green: #10b981;
            --accent-red: #ef4444;
        }
        
        body {
            background-color: var(--bg-main);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 14px;
            display: flex;
            justify-content: center;
            -webkit-font-smoothing: antialiased;
        }

        .app-container {
            width: 100%;
            max-width: 420px;
            padding-bottom: 80px;
        }

        /* Top Header */
        .header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding: 0 4px;
        }
        .coin-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 17px;
            font-weight: 700;
            letter-spacing: -0.3px;
        }
        .sync-pill {
            font-size: 11px;
            font-weight: 600;
            color: var(--accent-green);
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.25);
            padding: 4px 10px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .sync-dot {
            width: 6px;
            height: 6px;
            background-color: var(--accent-green);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--accent-green);
        }

        /* Prices Grid */
        .prices-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            background: var(--bg-card);
            padding: 14px;
            border-radius: 16px;
            border: 1px solid var(--border-color);
            margin-bottom: 14px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }
        .price-box label {
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .price-box .val {
            font-size: 19px;
            font-weight: 800;
            margin-top: 4px;
            letter-spacing: -0.5px;
        }
        .val.target { color: var(--accent-yellow); }
        .val.current { color: var(--accent-green); }

        /* Chart Card */
        .chart-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 14px;
            margin-bottom: 14px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }
        .chart-header {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: var(--text-secondary);
            margin-bottom: 10px;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .canvas-container {
            position: relative;
            width: 100%;
            height: 160px;
            background: #040608;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }
        canvas {
            width: 100%;
            height: 100%;
            display: block;
        }

        /* Signal Card */
        .signal-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 14px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }
        .signal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            font-size: 11px;
            font-weight: 700;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .timer-badge {
            background: #1a2230;
            color: var(--text-primary);
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 600;
            border: 1px solid var(--border-color);
        }
        .signal-box {
            background: #1a2230;
            color: var(--accent-yellow);
            padding: 18px;
            border-radius: 12px;
            font-weight: 800;
            font-size: 20px;
            text-align: center;
            letter-spacing: 0.5px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(255,255,255,0.05);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .signal-sub {
            font-size: 13px;
            margin-top: 6px;
            font-weight: 500;
            opacity: 0.9;
        }

        /* Bottom Nav */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(11, 15, 22, 0.95);
            backdrop-filter: blur(10px);
            border-top: 1px solid var(--border-color);
            display: flex;
            justify-content: space-around;
            padding: 10px 0 16px 0;
            z-index: 1000;
        }
        .nav-item {
            text-align: center;
            color: var(--text-secondary);
            font-size: 11px;
            font-weight: 500;
            text-decoration: none;
            transition: color 0.2s;
        }
        .nav-item.active {
            color: var(--accent-green);
        }
        .nav-icon {
            font-size: 18px;
            margin-bottom: 2px;
        }
    </style>
</head>
<body>

    <div class="app-container">
        <div class="header-row">
            <div class="coin-title coin-badge">
                <span style="color: var(--accent-yellow); font-size: 20px;">🪙</span> BTC 15 min <span style="font-size: 12px; color: var(--text-secondary);">▾</span>
            </div>
            <div class="sync-pill">
                <div class="sync-dot"></div> Kalshi Sync
            </div>
        </div>

        <div class="prices-grid">
            <div class="price-box">
                <label>Strike Objetivo</label>
                <div id="target-price" class="val target">--.--</div>
            </div>
            <div class="price-box">
                <label>Actual (Current)</label>
                <div id="current-price" class="val current">--.--</div>
            </div>
        </div>

        <div class="chart-card">
            <div class="chart-header">
                <span>Flujo de Precio en Vivo</span>
                <span id="diff-tag" style="font-weight: 700; color: var(--accent-green);">+$0.00</span>
            </div>
            <div class="canvas-container">
                <canvas id="priceCanvas"></canvas>
            </div>
        </div>

        <div class="signal-card">
            <div class="signal-header">
                <span id="window-status">ESTADO DEL BLOQUE</span>
                <span id="timer-text" class="timer-badge">Cierra --:--</span>
            </div>
            <div class="signal-box" id="signal-box">
                <div id="signal-main">CALCULANDO...</div>
                <div class="signal-sub" id="signal-sub">Sincronizando reloj de bloques</div>
            </div>
        </div>
    </div>

    <div class="bottom-nav">
        <div class="nav-item active"><div class="nav-icon">🤖</div><div>Bot</div></div>
        <div class="nav-item"><div class="nav-icon">📈</div><div>Operaciones</div></div>
        <div class="nav-item"><div class="nav-icon">💰</div><div>Saldo</div></div>
        <div class="nav-item"><div class="nav-icon">⚙️</div><div>Ajustes</div></div>
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
            ctx.strokeStyle = '#f59e0b';
            ctx.lineWidth = 1.2;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(0, strikeY);
            ctx.lineTo(canvas.width, strikeY);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = '#f59e0b';
            ctx.font = 'bold 10px sans-serif';
            ctx.fillText('STRIKE', 8, strikeY - 6);

            let step = canvas.width / (priceHistory.length - 1);
            let gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
            let isUp = currentPrice >= strikePrice;
            gradient.addColorStop(0, isUp ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)');
            gradient.addColorStop(1, 'rgba(7, 9, 12, 0.0)');

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
            ctx.strokeStyle = isUp ? '#10b981' : '#ef4444';
            ctx.lineWidth = 2.2;
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

                let activeBlock = localStorage.getItem("kalshi_exact_block");
                let strikePrice = parseFloat(localStorage.getItem("kalshi_exact_strike") || "0");

                if (activeBlock !== blockId || !strikePrice || strikePrice === 0) {
                    strikePrice = currentPrice;
                    localStorage.setItem("kalshi_exact_block", blockId);
                    localStorage.setItem("kalshi_exact_strike", strikePrice);
                    priceHistory = [currentPrice];
                }

                priceHistory.push(currentPrice);
                if (priceHistory.length > 40) priceHistory.shift();

                let diff = currentPrice - strikePrice;

                document.getElementById('target-price').innerText = "$" + strikePrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                document.getElementById('current-price').innerText = "$" + currentPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

                let diffTag = document.getElementById('diff-tag');
                diffTag.innerText = (diff >= 0 ? "+$" : "-$") + Math.abs(diff).toFixed(2);
                diffTag.style.color = diff >= 0 ? "#10b981" : "#ef4444";

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
                    windowStatus.innerText = "⚡ VENTANA DE APERTURA (0-3 MIN)";
                    
                    if (momentumScore >= 2 && diff > 1.0) {
                        sBox.style.backgroundColor = "#10b981";
                        sBox.style.color = "#07090c";
                        sBox.style.borderColor = "#34d399";
                        sMain.innerText = "🟢 ENTRAR UP";
                        sSub.innerText = "Ruptura alcista limpia desde el strike";
                    } else if (momentumScore <= -2 && diff < -1.0) {
                        sBox.style.backgroundColor = "#ef4444";
                        sBox.style.color = "#ffffff";
                        sBox.style.borderColor = "#f87171";
                        sMain.innerText = "🔴 ENTRAR DOWN";
                        sSub.innerText = "Ruptura bajista limpia desde el strike";
                    } else {
                        sBox.style.backgroundColor = "#1a2230";
                        sBox.style.color = "#f59e0b";
                        sBox.style.borderColor = "var(--border-color)";
                        sMain.innerText = "⏳ ESPERANDO RUPTURA";
                        sSub.innerText = "Monitoreando salida del strike base...";
                    }
                } else {
                    windowStatus.innerText = "🔒 BLOQUE AVANZADO (ZONA CERRADA)";
                    sBox.style.backgroundColor = "#141923";
                    sBox.style.color = "#64748b";
                    sBox.style.borderColor = "var(--border-color)";
                    sMain.innerText = "🛡️ FUERA DE TIEMPO";
                    sSub.innerText = "Ventana de 3 min finalizada - Evitar riesgo";
                }

                let remainingMinutes = Math.floor(remainingSeconds / 60);
                let remainingSecs = remainingSeconds % 60;
                let secFormatted = remainingSecs < 10 ? "0" + remainingSecs : remainingSecs;
                document.getElementById('timer-text').innerText = "Cierra " + remainingMinutes + ":" + secFormatted;

            } catch (e) {
                console.error("Error en sincronización exacta", e);
            }
        }

        setInterval(fetchBTCData, 1000);
        fetchBTCData();
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=780, scrolling=False)
