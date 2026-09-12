import streamlit as st

st.set_page_config(page_title="VIXY'S VAULT - Bot Pro", layout="centered", initial_sidebar_state="collapsed")

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
    <title>Vixy's Vault - Bot Pro</title>
    <style>
        :root {
            --bg-color: #080410;
            --card-bg: rgba(18, 11, 30, 0.95);
            --border-color: rgba(147, 51, 234, 0.25);
            --neon-green: #00ff66;
            --neon-purple: #a855f7;
            --neon-red: #ef4444;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-main); min-height: 100vh; padding: 10px 10px 90px 10px; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 440px; }
        
        /* Top Navigation Tabs */
        .top-tabs { display: flex; justify-content: space-between; overflow-x: auto; padding-bottom: 8px; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); white-space: nowrap; }
        .tab-item { font-size: 13px; color: var(--text-muted); padding: 4px 8px; cursor: pointer; text-decoration: none; }
        .tab-item.active { color: var(--neon-green); font-weight: 700; border-bottom: 2px solid var(--neon-green); }

        /* Bot Status & Control Bar */
        .bot-control-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 16px; margin-bottom: 14px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
        .bot-status-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .bot-title { font-size: 14px; font-weight: 800; display: flex; align-items: center; gap: 6px; }
        .status-badge { font-size: 10px; padding: 4px 10px; border-radius: 20px; font-weight: 700; display: flex; align-items: center; gap: 5px; }
        .status-badge.active { background: rgba(0,255,102,0.15); border: 1px solid rgba(0,255,102,0.4); color: var(--neon-green); }
        .status-badge.inactive { background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.4); color: var(--neon-red); }
        .dot { width: 6px; height: 6px; border-radius: 50%; }
        .active .dot { background: var(--neon-green); box-shadow: 0 0 6px var(--neon-green); }
        .inactive .dot { background: var(--neon-red); box-shadow: 0 0 6px var(--neon-red); }

        /* Metrics Grid */
        .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; }
        .metric-box { background: rgba(10,5,20,0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 10px; text-align: center; }
        .metric-label { font-size: 9px; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px; }
        .metric-val { font-size: 16px; font-weight: 900; font-family: monospace; }
        .text-green { color: var(--neon-green); }
        .text-purple { color: var(--neon-purple); }

        /* Toggle Button */
        .btn-toggle { width: 100%; padding: 12px; border-radius: 12px; font-weight: 800; font-size: 13px; cursor: pointer; border: none; text-transform: uppercase; letter-spacing: 1px; transition: 0.2s; }
        .btn-start { background: linear-gradient(135deg, #00ff66 0%, #00b347 100%); color: #080410; box-shadow: 0 0 15px rgba(0,255,102,0.4); }
        .btn-stop { background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); color: #fff; box-shadow: 0 0 15px rgba(239,68,68,0.4); }

        /* Live Scalping Action Card */
        .main-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 16px; text-align: center; margin-bottom: 14px; }
        .sub-header { font-size: 10px; color: var(--text-muted); letter-spacing: 1px; margin-bottom: 8px; text-transform: uppercase; }
        .strike-row { display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); margin-bottom: 12px; padding: 0 4px; }
        .strike-row span { color: #fff; font-family: monospace; font-weight: 600; }
        
        .action-banner { background: linear-gradient(135deg, rgba(0,255,102,0.15) 0%, rgba(0,255,102,0.05) 100%); border: 1px solid rgba(0,255,102,0.4); border-radius: 12px; padding: 14px; margin-bottom: 6px; }
        .action-title { font-size: 18px; font-weight: 900; color: var(--neon-green); letter-spacing: 1px; display: flex; align-items: center; justify-content: center; gap: 8px; text-shadow: 0 0 12px rgba(0,255,102,0.4); }

        /* Live Trades Log */
        .log-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 14px; }
        .log-title { font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 10px; display: flex; justify-content: space-between; }
        .log-item { display: flex; justify-content: space-between; align-items: center; font-size: 11px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .log-item:last-child { border-bottom: none; }
        .log-profit { font-family: monospace; font-weight: 700; }

        /* Bottom Nav */
        .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: #080410; border-top: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-around; padding: 10px 0; z-index: 100; }
        .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 9px; color: var(--text-muted); gap: 3px; cursor: pointer; }
        .nav-item.active { color: var(--neon-green); font-weight: 700; }
        .nav-item span.icon { font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Top Tabs -->
        <div class="top-tabs">
            <div class="tab-item">Dashboard</div>
            <div class="tab-item active">Scalping Bot</div>
            <div class="tab-item">1H Desk</div>
            <div class="tab-item">Signals</div>
            <div class="tab-item">Journal</div>
        </div>

        <!-- Bot Engine Panel -->
        <div class="bot-control-card">
            <div class="bot-status-header">
                <div class="bot-title">🤖 VIXY AUTO-TRADER</div>
                <div class="status-badge active" id="bot-badge">
                    <div class="dot"></div> <span id="badge-text">ACTIVO (GANANDO)</span>
                </div>
            </div>

            <div class="metrics-grid">
                <div class="metric-box">
                    <div class="metric-label">Ganancia Neta (PnL)</div>
                    <div class="metric-val text-green" id="pnl-val">+$342.50</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Winrate (Efectividad)</div>
                    <div class="metric-val text-purple" id="winrate-val">88.4%</div>
                </div>
            </div>

            <button class="btn-toggle btn-stop" id="toggle-btn" onclick="toggleBot()">Detener Automatización</button>
        </div>

        <!-- Main Scalping Execution Card -->
        <div class="main-card">
            <div class="sub-header" id="status-time">ESTADO: OPERANDO BLOQUE 15M</div>
            <div class="strike-row">
                <span>BTC SPOT / STRIKE</span>
                <span><b id="strike-price">$62,736.43</b></span>
            </div>
            <div class="action-banner">
                <div class="action-title" id="signal-text">COMPRAR SUBE ▲</div>
            </div>
        </div>

        <!-- Live Operations Log -->
        <div class="log-card">
            <div class="log-title">
                <span>Últimas Órdenes Ejecutadas</span>
                <span style="color: var(--neon-green);">● En Vivo</span>
            </div>
            <div id="logs-container">
                <div class="log-item">
                    <span>15M UTC • Comprar Sube</span>
                    <span class="log-profit text-green">+$45.00 (Win)</span>
                </div>
                <div class="log-item">
                    <span>15M UTC • Comprar Sube</span>
                    <span class="log-profit text-green">+$38.20 (Win)</span>
                </div>
                <div class="log-item">
                    <span>15M UTC • Vender Baja</span>
                    <span class="log-profit text-green">+$52.10 (Win)</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Bottom Nav -->
    <div class="bottom-nav">
        <div class="nav-item active"><span class="icon">🤖</span><span>Bot</span></div>
        <div class="nav-item"><span class="icon">📈</span><span>Operaciones</span></div>
        <div class="nav-item"><span class="icon">💰</span><span>Saldo</span></div>
        <div class="nav-item"><span class="icon">⚪</span><span>Stats</span></div>
        <div class="nav-item"><span class="icon">👑</span><span>VIP</span></div>
    </div>

    <script>
        let botRunning = true;
        let totalPnL = 342.50;

        function toggleBot() {
            botRunning = !botRunning;
            const btn = document.getElementById('toggle-btn');
            const badge = document.getElementById('bot-badge');
            const badgeText = document.getElementById('badge-text');

            if (botRunning) {
                btn.className = "btn-toggle btn-stop";
                btn.innerText = "Detener Automatización";
                badge.className = "status-badge active";
                badgeText.innerText = "ACTIVO (GANANDO)";
            } else {
                btn.className = "btn-toggle btn-start";
                btn.innerText = "Iniciar Automatización";
                badge.className = "status-badge inactive";
                badgeText.innerText = "PAUSADO";
            }
        }

        function liveUpdate() {
            if (!botRunning) return;

            // Actualizar precio dinámico
            const randomBase = 62730.00 + (Math.random() * 25 - 12);
            document.getElementById('strike-price').innerText = `$${randomBase.toFixed(2)}`;

            // Incrementar ganancias gradualmente simulando trades exitosos del bot
            const increment = (Math.random() * 4).toFixed(2);
            totalPnL += parseFloat(increment);
            document.getElementById('pnl-val').innerText = `+$${totalPnL.toFixed(2)}`;
        }

        setInterval(liveUpdate, 2000);
    </script>
</body>
</html>
""", height=720, scrolling=False)
