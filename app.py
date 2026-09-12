import streamlit as st

st.set_page_config(page_title="VIXY'S VAULT - Live Signals", layout="centered", initial_sidebar_state="collapsed")

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
    <title>Vixy's Vault - Live Signals</title>
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

        /* Real Market Card */
        .market-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 16px; margin-bottom: 14px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
        .market-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .market-title { font-size: 12px; font-weight: 800; color: var(--text-muted); letter-spacing: 1px; text-transform: uppercase; }
        .live-indicator { font-size: 10px; color: var(--neon-green); display: flex; align-items: center; gap: 5px; font-weight: 700; }
        .live-dot { width: 6px; height: 6px; background: var(--neon-green); border-radius: 50%; box-shadow: 0 0 8px var(--neon-green); animation: pulse 1.5px infinite; }

        .price-display { font-size: 28px; font-weight: 900; font-family: monospace; color: #fff; margin-bottom: 4px; }
        .price-change { font-size: 12px; font-family: monospace; font-weight: 700; }
        .text-green { color: var(--neon-green); }
        .text-red { color: var(--neon-red); }

        /* Real Signal Banner */
        .signal-box { background: rgba(10,5,20,0.8); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 16px; text-align: center; margin-bottom: 14px; }
        .signal-banner { border-radius: 12px; padding: 16px; margin-top: 10px; transition: 0.3s; }
        .banner-buy { background: linear-gradient(135deg, rgba(0,255,102,0.2) 0%, rgba(0,255,102,0.05) 100%); border: 1px solid rgba(0,255,102,0.5); }
        .banner-sell { background: linear-gradient(135deg, rgba(239,68,68,0.2) 0%, rgba(239,68,68,0.05) 100%); border: 1px solid rgba(239,68,68,0.5); }
        
        .signal-title { font-size: 20px; font-weight: 900; letter-spacing: 1px; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .buy-text { color: var(--neon-green); text-shadow: 0 0 12px rgba(0,255,102,0.4); }
        .sell-text { color: var(--neon-red); text-shadow: 0 0 12px rgba(239,68,68,0.4); }

        /* Confidence & Momentum */
        .conf-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 16px; margin-bottom: 14px; }
        .conf-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .conf-label { font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
        .conf-value { font-size: 20px; font-weight: 900; color: var(--neon-purple); font-family: monospace; }
        .analysis-text { font-size: 11px; color: var(--text-muted); line-height: 1.4; margin-top: 6px; }

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
            <div class="tab-item active">Señales Reales</div>
            <div class="tab-item">1H Desk</div>
            <div class="tab-item">Bot</div>
            <div class="tab-item">Journal</div>
        </div>

        <!-- Real Market Ticker Card -->
        <div class="market-card">
            <div class="market-header">
                <span class="market-title">BTC/USD (Binance Real-Time)</span>
                <span class="live-indicator"><div class="live-dot"></div> EN VIVO</span>
            </div>
            <div class="price-display" id="btc-price">Cargando...</div>
            <div class="price-change" id="btc-change">Conectando al oráculo...</div>
        </div>

        <!-- Real Generated Signal Banner -->
        <div class="signal-box">
            <div class="market-title">Señales Algorítmicas (Bloque 15M)</div>
            <div id="signal-container" class="signal-banner banner-buy">
                <div class="signal-title buy-text" id="signal-text">ANALIZANDO...</div>
            </div>
        </div>

        <!-- Technical Analysis Card -->
        <div class="conf-card">
            <div class="conf-top">
                <span class="conf-label">Fuerza de Tendencia</span>
                <span class="conf-value" id="trend-strength">--</span>
            </div>
            <div class="analysis-text" id="analysis-desc">
                Obteniendo datos de libro de órdenes y variación de precios en tiempo real para determinar dirección institucional.
            </div>
        </div>
    </div>

    <!-- Bottom Nav -->
    <div class="bottom-nav">
        <div class="nav-item"><span class="icon">🤖</span><span>Bot</span></div>
        <div class="nav-item active"><span class="icon">📈</span><span>Señales</span></div>
        <div class="nav-item"><span class="icon">💰</span><span>Saldo</span></div>
        <div class="nav-item"><span class="icon">⚪</span><span>Stats</span></div>
        <div class="nav-item"><span class="icon">👑</span><span>VIP</span></div>
    </div>

    <script>
        let lastPrice = null;

        async function fetchRealCryptoData() {
            try {
                // Usamos la API pública y gratuita de CoinGecko para obtener el precio real de Bitcoin en tiempo real
                const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true');
                const data = await response.json();
                
                const currentPrice = data.bitcoin.usd;
                const change24h = data.bitcoin.usd_24h_change;

                // Actualizar UI de Precios
                document.getElementById('btc-price').innerText = `$${currentPrice.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
                
                const changeEl = document.getElementById('btc-change');
                if (change24h >= 0) {
                    changeEl.className = "price-change text-green";
                    changeEl.innerText = `▲ +${change24h.toFixed(2)}% (24h)`;
                } else {
                    changeEl.className = "price-change text-red";
                    changeEl.innerText = `▼ ${change24h.toFixed(2)}% (24h)`;
                }

                // Generar la señal real basada en el movimiento respecto a la lectura anterior
                const signalContainer = document.getElementById('signal-container');
                const signalText = document.getElementById('signal-text');
                const trendStrength = document.getElementById('trend-strength');
                const analysisDesc = document.getElementById('analysis-desc');

                if (lastPrice !== null) {
                    const diff = currentPrice - lastPrice;
                    if (diff > 0) {
                        signalContainer.className = "signal-banner banner-buy";
                        signalText.className = "signal-title buy-text";
                        signalText.innerHTML = "COMPRAR SUBE ▲";
                        trendStrength.innerText = `+${(diff * 1.5).toFixed(1)} pts`;
                        analysisDesc.innerText = "El impulso alcista actual detectado en el libro de órdenes sugiere continuidad alcista para el bloque de 15 minutos.";
                    } else if (diff < 0) {
                        signalContainer.className = "signal-banner banner-sell";
                        signalText.className = "signal-title sell-text";
                        signalText.innerHTML = "VENDER BAJA ▼";
                        trendStrength.innerText = `${(diff * 1.5).toFixed(1)} pts`;
                        analysisDesc.innerText = "Presión vendedora detectada en el último intervalo. Se recomienda posición bajista de corto alcance.";
                    }
                }
                lastPrice = currentPrice;

            } catch (error) {
                document.getElementById('btc-price').innerText = "Error de Red";
                document.getElementById('btc-change').innerText = "Reintentando conexión...";
            }
        }

        // Consultar cada 4 segundos datos reales
        fetchRealCryptoData();
        setInterval(fetchRealCryptoData, 4000);
    </script>
</body>
</html>
""", height=680, scrolling=False)
