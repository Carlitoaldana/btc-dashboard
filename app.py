import streamlit as st

st.set_page_config(page_title="VIXY'S VAULT V2", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px !important; max-width: 100% !important;}
    </style>
""", unsafe_allow_html=True)

st.components.v1.html("""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIXY'S VAULT</title>
    <style>
        :root {
            --bg-color: #0b0614;
            --card-bg: rgba(20, 13, 33, 0.9);
            --border-color: rgba(147, 51, 234, 0.25);
            --neon-green: #00ff66;
            --neon-purple: #a855f7;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-main); min-height: 100vh; padding: 12px 12px 80px 12px; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 440px; }
        .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding: 0 4px; }
        .title-badge { font-size: 15px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 6px; }
        .sync-pill { background: rgba(0, 255, 102, 0.1); border: 1px solid rgba(0, 255, 102, 0.3); color: var(--neon-green); font-size: 10px; padding: 4px 10px; border-radius: 20px; font-weight: 600; display: flex; align-items: center; gap: 5px; }
        .sync-dot { width: 6px; height: 6px; background-color: var(--neon-green); border-radius: 50%; box-shadow: 0 0 6px var(--neon-green); }
        .prices-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; }
        .price-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 14px; padding: 12px; }
        .price-card .label { font-size: 9px; color: var(--text-muted); letter-spacing: 1px; margin-bottom: 6px; text-transform: uppercase; }
        .price-card .val { font-size: 16px; font-weight: 800; font-family: monospace; }
        .val-target { color: #f59e0b; }
        .val-current { color: var(--neon-green); }
        .chart-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 14px; padding: 12px; margin-bottom: 12px; }
        .chart-header { display: flex; justify-content: space-between; font-size: 10px; color: var(--text-muted); margin-bottom: 8px; }
        .chart-profit { color: var(--neon-green); font-weight: 700; }
        .canvas-container { width: 100%; height: 110px; background: rgba(10, 5, 20, 0.6); border-radius: 8px; position: relative; overflow: hidden; display: flex; align-items: flex-end; }
        .chart-svg { width: 100%; height: 100%; }
        .status-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 14px; padding: 14px; text-align: center; margin-bottom: 12px; }
        .status-header { display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: var(--text-muted); margin-bottom: 10px; }
        .time-badge { background: rgba(255, 255, 255, 0.08); padding: 3px 8px; border-radius: 6px; color: #fff; font-weight: 600; }
        .time-box { background: rgba(10, 5, 20, 0.7); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 12px; }
        .time-title { font-size: 15px; font-weight: 900; color: #ef4444; letter-spacing: 1.5px; margin-bottom: 4px; }
        .time-desc { font-size: 9px; color: var(--text-muted); }
        .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: #0b0614; border-top: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-around; padding: 10px 0; z-index: 100; }
        .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 9px; color: var(--text-muted); gap: 3px; }
        .nav-item.active { color: var(--neon-green); font-weight: 700; }
        .nav-item span.icon { font-size: 16px; }
        .action-btn { background: #ef4444; color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-size: 14px; box-shadow: 0 0 10px rgba(239, 68, 68, 0.5); }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <div class="title-badge"><span>⚪</span> BTC 15 min ▾</div>
            <div class="sync-pill"><div class="sync-dot"></div> Kalshi Sync</div>
        </div>
        <div class="prices-grid">
            <div class="price-card">
                <div class="label">STRIKE OBJETIVO</div>
                <div class="val val-target" id="strike-price">$77,249.17</div>
            </div>
            <div class="price-card">
                <div class="label">ACTUAL (CURRENT)</div>
                <div class="val val-current" id="current-price">$77,249.17</div>
            </div>
        </div>
        <div class="chart-card">
            <div class="chart-header">
                <span>FLUJO DE PRECIO EN VIVO</span>
                <span class="chart-profit" id="profit-val">+$0.00</span>
            </div>
            <div class="canvas-container">
                <svg class="chart-svg" viewBox="0 0 300 100" preserveAspectRatio="none">
                    <defs>
                        <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stop-color="#00ff66" stop-opacity="0.25"/>
                            <stop offset="100%" stop-color="#00ff66" stop-opacity="0.0"/>
                        </linearGradient>
                    </defs>
                    <line x1="0" y1="30" x2="300" y2="30" stroke="#f59e0b" stroke-dasharray="4" stroke-width="1.5"/>
                    <path d="M0,35 Q75,35 120,75 T240,60 T300,32" fill="url(#grad)" stroke="#00ff66" stroke-width="2"/>
                </svg>
            </div>
        </div>
        <div class="status-card">
            <div class="status-header">
                <span>🔒 BLOQUE AVANZADO (ZONA CERRADA)</span>
                <span class="time-badge">CIERRA 8:04</span>
            </div>
            <div class="time-box">
                <div class="time-title">🛡️ FUERA DE TIEMPO</div>
                <div class="time-desc">Ventana de 3 min finalizada - Evitar riesgo</div>
            </div>
        </div>
    </div>
    <div class="bottom-nav">
        <div class="nav-item"><span class="icon">🤖</span><span>Bot</span></div>
        <div class="nav-item active"><span class="icon">📈</span><span>Operaciones</span></div>
        <div class="nav-item"><span class="icon">💰</span><span>Saldo</span></div>
        <div class="nav-item"><span class="icon">⚪</span><span>Stats</span></div>
        <div class="nav-item"><div class="action-btn">👑</div></div>
    </div>
    <script>
        function liveUpdate() {
            const base = 77240.00 + (Math.random() * 20);
            const current = base + (Math.random() * 6 - 3);
            document.getElementById('strike-price').innerText = `$${base.toFixed(2)}`;
            document.getElementById('current-price').innerText = `$${current.toFixed(2)}`;
            const profit = (Math.random() * 5 - 2).toFixed(2);
            const profitEl = document.getElementById('profit-val');
            profitEl.innerText = (profit >= 0 ? `+$${profit}` : `-$${Math.abs(profit)}`);
            profitEl.style.color = profit >= 0 ? '#00ff66' : '#ef4444';
        }
        setInterval(liveUpdate, 1500);
    </script>
</body>
</html>
""", height=620, scrolling=False)
""", height=620, scrolling=False)
