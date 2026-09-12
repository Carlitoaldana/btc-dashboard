import streamlit as st

st.set_page_config(page_title="VIXY'S VAULT - Scalping", layout="centered", initial_sidebar_state="collapsed")

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
    <title>Vixy's Vault - Scalping</title>
    <style>
        :root {
            --bg-color: #080410;
            --card-bg: rgba(18, 11, 30, 0.95);
            --border-color: rgba(147, 51, 234, 0.25);
            --neon-green: #00ff66;
            --neon-purple: #a855f7;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-main); min-height: 100vh; padding: 10px 10px 80px 10px; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 440px; }
        
        .top-tabs { display: flex; justify-content: space-between; overflow-x: auto; padding-bottom: 8px; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); white-space: nowrap; }
        .tab-item { font-size: 13px; color: var(--text-muted); padding: 4px 8px; cursor: pointer; text-decoration: none; }
        .tab-item.active { color: var(--neon-green); font-weight: 700; border-bottom: 2px solid var(--neon-green); }

        .main-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 18px 14px; text-align: center; margin-bottom: 14px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
        .sub-header { font-size: 10px; color: var(--text-muted); letter-spacing: 1px; margin-bottom: 8px; text-transform: uppercase; }
        .strike-row { display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); margin-bottom: 12px; padding: 0 4px; }
        .strike-row span { color: #fff; font-family: monospace; font-weight: 600; }
        
        .action-banner { background: linear-gradient(135deg, rgba(0,255,102,0.15) 0%, rgba(0,255,102,0.05) 100%); border: 1px solid rgba(0,255,102,0.4); border-radius: 12px; padding: 16px; margin-bottom: 6px; }
        .action-title { font-size: 20px; font-weight: 900; color: var(--neon-green); letter-spacing: 1px; display: flex; align-items: center; justify-content: center; gap: 8px; text-shadow: 0 0 12px rgba(0,255,102,0.4); }

        .conf-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 16px; margin-bottom: 14px; }
        .conf-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .conf-label { font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
        .conf-value { font-size: 22px; font-weight: 900; color: var(--neon-green); font-family: monospace; }
        
        .momentum-badge { display: inline-block; background: rgba(0,255,102,0.1); border: 1px solid rgba(0,255,102,0.3); color: var(--neon-green); font-size: 10px; font-weight: 700; padding: 6px 12px; border-radius: 8px; margin-bottom: 16px; width: 100%; text-align: center; }

        .slider-container { position: relative; margin-top: 10px; }
        .slider-track { width: 100%; height: 6px; background: rgba(255,255,255,0.08); border-radius: 3px; position: relative; }
        .slider-fill { width: 73%; height: 100%; background: var(--neon-green); border-radius: 3px; box-shadow: 0 0 8px var(--neon-green); }
        .slider-thumb { position: absolute; top: 50%; left: 73%; transform: translate(-50%, -50%); width: 14px; height: 14px; background: #fff; border: 3px solid var(--neon-green); border-radius: 50%; box-shadow: 0 0 10px var(--neon-green); }
        
        .slider-labels { display: flex; justify-content: space-between; font-size: 8px; color: var(--text-muted); margin-top: 8px; text-transform: uppercase; }

        .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: #080410; border-top: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-around; padding: 10px 0; z-index: 100; }
        .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 9px; color: var(--text-muted); gap: 3px; cursor: pointer; }
        .nav-item.active { color: var(--neon-green); font-weight: 700; }
        .nav-item span.icon { font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-tabs">
            <div class="tab-item">Dashboard</div>
            <div class="tab-item active">Scalping</div>
            <div class="tab-item">1H Desk</div>
            <div class="tab-item">Signals</div>
            <div class="tab-item">Journal</div>
        </div>

        <div class="main-card">
            <div class="sub-header" id="status-time">FINALIZADO @ 07:08:05 UTC</div>
            <div class="strike-row">
                <span>BLOQUE 15M UTC</span>
                <span>STRIKE: <b id="strike-price">$62,736.43</b></span>
            </div>
            <div class="action-banner">
                <div class="action-title">COMPRAR SUBE ▲</div>
            </div>
        </div>

        <div class="conf-card">
            <div class="conf-top">
                <span class="conf-label">Confianza del Modelo Bloqueada</span>
                <span class="conf-value" id="conf-val">73%</span>
            </div>
            <div class="momentum-badge">MOMENTUM ALCISTA FUERTE</div>
            <div class="slider-container">
                <div class="slider-track">
                    <div class="slider-fill" id="slider-fill"></div>
                    <div class="slider-thumb" id="slider-thumb"></div>
                </div>
                <div class="slider-labels">
                    <span>50% (Desarrollo)</span>
                    <span>60% (Moderado)</span>
                    <span>70% (Fuerte)</span>
                    <span>80%+ (Alto)</span>
                </div>
            </div>
        </div>
    </div>

    <div class="bottom-nav">
        <div class="nav-item"><span class="icon">🤖</span><span>Bot</span></div>
        <div class="nav-item active"><span class="icon">📈</span><span>Operaciones</span></div>
        <div class="nav-item"><span class="icon">💰</span><span>Saldo</span></div>
        <div class="nav-item"><span class="icon">⚪</span><span>Stats</span></div>
        <div class="nav-item"><span class="icon">👑</span><span>VIP</span></div>
    </div>

    <script>
        function liveUpdate() {
            const randomBase = 62730.00 + (Math.random() * 20 - 10);
            document.getElementById('strike-price').innerText = `$${randomBase.toFixed(2)}`;
            const conf = (70 + (Math.random() * 6)).toFixed(1);
            document.getElementById('conf-val').innerText = `${conf}%`;
        }
        setInterval(liveUpdate, 2000);
    </script>
</body>
</html>
""", height=650, scrolling=False)
