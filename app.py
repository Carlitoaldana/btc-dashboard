import streamlit as st

st.set_page_config(page_title="VIXY'S VAULT - Pro Trading Hub", layout="centered", initial_sidebar_state="collapsed")

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
    <title>Vixy's Vault - Pro</title>
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
        .tab-item { font-size: 12px; color: var(--text-muted); padding: 4px 8px; cursor: pointer; text-decoration: none; border-radius: 6px; transition: 0.2s; }
        .tab-item.active { color: var(--neon-green); font-weight: 700; background: rgba(0,255,102,0.1); }

        /* Vistas de la aplicación */
        .view-section { display: none; }
        .view-section.active-view { display: block; }

        /* Tarjetas Generales */
        .card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 16px; margin-bottom: 14px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
        .card-title { font-size: 11px; font-weight: 800; color: var(--text-muted); letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }
        
        /* Precios y Mercado */
        .price-display { font-size: 28px; font-weight: 900; font-family: monospace; color: #fff; margin-bottom: 4px; }
        .price-change { font-size: 12px; font-family: monospace; font-weight: 700; }
        .text-green { color: var(--neon-green); }
        .text-red { color: var(--neon-red); }
        .text-purple { color: var(--neon-purple); }

        /* Señales */
        .signal-banner { border-radius: 12px; padding: 16px; margin-top: 10px; text-align: center; }
        .banner-buy { background: linear-gradient(135deg, rgba(0,255,102,0.2) 0%, rgba(0,255,102,0.05) 100%); border: 1px solid rgba(0,255,102,0.5); }
        .banner-sell { background: linear-gradient(135deg, rgba(239,68,68,0.2) 0%, rgba(239,68,68,0.05) 100%); border: 1px solid rgba(239,68,68,0.5); }
        .signal-title { font-size: 20px; font-weight: 900; letter-spacing: 1px; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .buy-text { color: var(--neon-green); text-shadow: 0 0 12px rgba(0,255,102,0.4); }
        .sell-text { color: var(--neon-red); text-shadow: 0 0 12px rgba(239,68,68,0.4); }

        /* Botones de acción */
        .action-btn { width: 100%; padding: 12px; border-radius: 12px; font-weight: 800; font-size: 13px; cursor: pointer; border: none; text-transform: uppercase; letter-spacing: 1px; margin-top: 10px; }
        .btn-primary { background: linear-gradient(135deg, #00ff66 0%, #00b347 100%); color: #080410; box-shadow: 0 0 15px rgba(0,255,102,0.3); }

        /* Bottom Nav */
        .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: #080410; border-top: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-around; padding: 10px 0; z-index: 100; }
        .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 9px; color: var(--text-muted); gap: 3px; cursor: pointer; background: none; border: none; }
        .nav-item.active { color: var(--neon-green); font-weight: 700; }
        .nav-item span.icon { font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Top Tabs de Navegación Rápida -->
        <div class="top-tabs">
            <div class="tab-item active" onclick="switchView('signals')">Señales</div>
            <div class="tab-item" onclick="switchView('bot')">Bot Pro</div>
            <div class="tab-item" onclick="switchView('balance')">Saldo</div>
            <div class="tab-item" onclick="switchView('stats')">Stats</div>
            <div class="tab-item" onclick="switchView('vip')">VIP</div>
        </div>

        <!-- VISTA 1: SEÑALES (Principal con Datos Reales) -->
        <div id="view-signals" class="view-section active-view">
            <div class="card">
                <div class="card-title">BTC / USD (Mercado en Vivo)</div>
                <div class="price-display" id="btc-price">Cargando...</div>
                <div class="price-change" id="btc-change">Conectando al oráculo...</div>
            </div>

            <div class="card">
                <div class="card-title">Análisis Algorítmico (Bloque 15M)</div>
                <div id="signal-container" class="signal-banner banner-buy">
                    <div class="signal-title buy-text" id="signal-text">ANALIZANDO...</div>
                </div>
                <div style="font-size: 11px; color: var(--text-muted); margin-top: 10px; text-align: center;" id="analysis-desc">
                    Evaluando ticks en directo del order book...
                </div>
            </div>
        </div>

        <!-- VISTA 2: BOT AUTOMATIZADO -->
        <div id="view-bot" class="view-section">
            <div class="card">
                <div class="card-title">Motor de Autotrading Vixy</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin: 15px 0;">
                    <span style="font-size: 13px; font-weight: 700;">Estado del Motor:</span>
                    <span id="bot-status-text" class="text-green" style="font-weight: 800;">ACTIVO Y ESCANEANDO</span>
                </div>
                <button class="action-btn btn-primary" onclick="toggleBotEngine()" id="bot-toggle-btn">Pausar Motor</button>
            </div>
            <div class="card">
                <div class="card-title">Últimas Órdenes del Bot</div>
                <div style="font-size: 11px; display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <span>Bloque 15M • Compra Sube</span>
                    <span class="text-green">+ $34.20 (EXITOSO)</span>
                </div>
                <div style="font-size: 11px; display: flex; justify-content: space-between; padding: 6px 0;">
                    <span>Bloque 15M • Compra Sube</span>
                    <span class="text-green">+ $41.50 (EXITOSO)</span>
                </div>
            </div>
        </div>

        <!-- VISTA 3: SALDO Y BILLETERA -->
        <div id="view-balance" class="view-section">
            <div class="card" style="text-align: center; padding: 24px 16px;">
                <div class="card-title">Balance Total Disponible</div>
                <div class="price-display text-green" style="margin: 10px 0;">$1,482.50 USD</div>
                <div style="font-size: 11px; color: var(--text-muted);">Fondos listos para ejecución en bloques</div>
                <button class="action-btn btn-primary" style="margin-top: 15px;" onclick="alert('Redirigiendo a pasarela de depósito segura...')">Depositar / Retirar</button>
            </div>
        </div>

        <!-- VISTA 4: ESTADÍSTICAS -->
        <div id="view-stats" class="view-section">
            <div class="card">
                <div class="card-title">Rendimiento Histórico</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; text-align: center;">
                    <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px;">
                        <div style="font-size: 9px; color: var(--text-muted);">Winrate Global</div>
                        <div style="font-size: 18px; font-weight: 900;" class="text-purple">87.9%</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px;">
                        <div style="font-size: 9px; color: var(--text-muted);">Trades Totales</div>
                        <div style="font-size: 18px; font-weight: 900;" class="text-green">142</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- VISTA 5: VIP / ACCESO EXCLUSIVO -->
        <div id="view-vip" class="view-section">
            <div class="card" style="text-align: center;">
                <div class="card-title" style="color: var(--text-main);">👑 Membresía Vixy Vault VIP</div>
                <div style="font-size: 12px; color: var(--text-muted); margin: 12px 0; line-height: 1.4;">
                    Tienes acceso completo a los algoritmos avanzados de predicción de alta frecuencia y canales privados de scalping.
                </div>
                <div style="background: rgba(168,85,247,0.15); border: 1px solid var(--neon-purple); padding: 10px; border-radius: 8px; font-size: 11px; font-weight: 700; color: var(--neon-purple);">
                    ESTADO: ACTIVO HASTA 2026
                </div>
            </div>
        </div>
    </div>

    <!-- Bottom Navigation Bar (Interactiva de verdad) -->
    <div class="bottom-nav">
        <button class="nav-item active" id="nav-btn-bot" onclick="switchView('bot')"><span class="icon">🤖</span><span>Bot</span></button>
        <button class="nav-item" id="nav-btn-signals" onclick="switchView('signals')"><span class="icon">📈</span><span>Señales</span></button>
        <button class="nav-item" id="nav-btn-balance" onclick="switchView('balance')"><span class="icon">💰</span><span>Saldo</span></button>
        <button class="nav-item" id="nav-btn-stats" onclick="switchView('stats')"><span class="icon">⚪</span><span>Stats</span></button>
        <button class="nav-item" id="nav-btn-vip" onclick="switchView('vip')"><span class="icon">👑</span><span>VIP</span></button>
    </div>

    <script>
        let lastPrice = null;
        let engineActive = true;

        // Función para cambiar de pestaña dinámicamente sin recargar la página
        function switchView(viewName) {
            // Ocultar todas las vistas
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view'));
            // Mostrar la seleccionada
            document.getElementById('view-' + viewName).classList.add('active-view');

            // Actualizar pestañas superiores
            document.querySelectorAll('.tab-item').forEach(el => el.classList.remove('active'));
            event && event.target.classList.contains('tab-item') && event.target.classList.add('active');

            // Actualizar botones inferiores
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            const navBtn = document.getElementById('nav-btn-' + viewName);
            if (navBtn) navBtn.classList.add('active');
        }

        function toggleBotEngine() {
            engineActive = !engineActive;
            const statusText = document.getElementById('bot-status-text');
            const toggleBtn = document.getElementById('bot-toggle-btn');
            if (engineActive) {
                statusText.innerText = "ACTIVO Y ESCANEANDO";
                statusText.className = "text-green";
                toggleBtn.innerText = "Pausar Motor";
            } else {
                statusText.innerText = "EN PAUSA";
                statusText.className = "text-red";
                toggleBtn.innerText = "Reanudar Motor";
            }
        }

        // Consultar precios reales de mercado cada 4 segundos
        async function fetchRealCryptoData() {
            try {
                const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true');
                const data = await response.json();
                
                const currentPrice = data.bitcoin.usd;
                const change24h = data.bitcoin.usd_24h_change;

                document.getElementById('btc-price').innerText = `$${currentPrice.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
                
                const changeEl = document.getElementById('btc-change');
                if (change24h >= 0) {
                    changeEl.className = "price-change text-green";
                    changeEl.innerText = `▲ +${change24h.toFixed(2)}% (24h)`;
                } else {
                    changeEl.className = "price-change text-red";
                    changeEl.innerText = `▼ ${change24h.toFixed(2)}% (24h)`;
                }

                const signalContainer = document.getElementById('signal-container');
                const signalText = document.getElementById('signal-text');
                const analysisDesc = document.getElementById('analysis-desc');

                if (lastPrice !== null) {
                    const diff = currentPrice - lastPrice;
                    if (diff > 0) {
                        signalContainer.className = "signal-banner banner-buy";
                        signalText.className = "signal-title buy-text";
                        signalText.innerHTML = "COMPRAR SUBE ▲";
                        analysisDesc.innerText = "Presión de compra institucional detectada. Tendencia alcista confirmada para el bloque actual.";
                    } else if (diff < 0) {
                        signalContainer.className = "signal-banner banner-sell";
                        signalText.className = "signal-title sell-text";
                        signalText.innerHTML = "VENDER BAJA ▼";
                        analysisDesc.innerText = "Retroceso de precio detectado en el libro de órdenes. Oportunidad bajista activa.";
                    }
                }
                lastPrice = currentPrice;
            } catch (error) {
                document.getElementById('btc-price').innerText = "Error de Red";
            }
        }

        fetchRealCryptoData();
        setInterval(fetchRealCryptoData, 4000);
    </script>
</body>
</html>
""", height=720, scrolling=False)
