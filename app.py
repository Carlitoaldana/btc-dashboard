# main.py
from datetime import datetime, timezone
import sqlite3
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

DB_FILE = "bot_state.db"


def init_db():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_key TEXT UNIQUE,
            target_price REAL,
            created_at TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()


def obtener_precio_btc():
  try:
    url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
    res = requests.get(url, timeout=3).json()
    return float(res["data"]["amount"])
  except:
    try:
      url2 = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
      res2 = requests.get(url2, timeout=3).json()
      return float(res2["price"])
    except:
      return 0.0


def obtener_o_crear_target(precio_actual):
  ahora_utc = datetime.now(timezone.utc)
  minuto_bloque = (ahora_utc.minute // 15) * 15
  block_key = f"{ahora_utc.date()}-{ahora_utc.hour}-{minuto_bloque}"

  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()

  cursor.execute(
      "SELECT target_price FROM state WHERE block_key = ?", (block_key,)
  )
  row = cursor.fetchone()

  if row:
    target = row[0]
  else:
    target = precio_actual if precio_actual > 0 else 77250.0
    cursor.execute(
        "INSERT OR REPLACE INTO state (block_key, target_price, created_at)"
        " VALUES (?, ?, ?)",
        (block_key, target, str(ahora_utc)),
    )
    conn.commit()

  conn.close()
  return target, block_key


@app.get("/api/data")
def get_bot_data():
  precio_actual = obtener_precio_btc()
  if precio_actual == 0:
    raise HTTPException(
        status_code=500, detail="No se pudo obtener precio de las APIs"
    )

  target, block_key = obtener_o_crear_target(precio_actual)
  diferencia = precio_actual - target

  base = 50.0 + (diferencia * 2.0)
  up_val = round(max(min(base, 98.0), 2.0), 1)
  down_val = round(100 - up_val, 1)

  if up_val >= 58:
    signal = "UP"
    signal_text = "🚀 COMPRAR UP"
    bg_color = "#0e4429"
  elif up_val <= 42:
    signal = "DOWN"
    signal_text = "📉 COMPRAR DOWN"
    bg_color = "#51151e"
  else:
    signal = "NEUTRAL"
    signal_text = "⚠️ ZONA DE INDECISIÓN"
    bg_color = "#1f242d"

  return {
      "target": target,
      "current": precio_actual,
      "diff": diferencia,
      "up_val": up_val,
      "down_val": down_val,
      "signal_text": signal_text,
      "bg_color": bg_color,
      "block_key": block_key,
  }


@app.get("/", response_class=HTMLResponse)
def index():
  return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BTC Bot Pro - Kalshi</title>
        <style>
            body { background-color: #0d1117; color: white; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; display: flex; justify-content: center; }
            .container { width: 100%; max-width: 400px; }
            .card-signal { padding: 20px; border-radius: 12px; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px; transition: background 0.3s ease; }
            .metrics { display: flex; gap: 10px; margin-bottom: 20px; }
            .metric-box { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; flex: 1; text-align: center; }
            .metric-value { font-size: 22px; font-weight: bold; margin-top: 5px; }
            .info-box { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; margin-bottom: 10px; font-size: 14px; display: flex; justify-content: space-between; }
            .progress-bar { background: #30363d; border-radius: 6px; height: 10px; overflow: hidden; margin-bottom: 20px; }
            .progress-fill { background: #2ea043; height: 100%; width: 50%; transition: width 0.3s ease; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>BTC / USD (15m Pro)</h2>
            <div id="signal-card" class="card-signal" style="background-color: #1f242d;">CARGANDO...</div>
            
            <div class="metrics">
                <div class="metric-box">
                    <div style="font-size: 12px; color: #8b949e;">UP</div>
                    <div id="up-val" class="metric-value">50.0%</div>
                </div>
                <div class="metric-box">
                    <div style="font-size: 12px; color: #8b949e;">DOWN</div>
                    <div id="down-val" class="metric-value">50.0%</div>
                </div>
            </div>

            <div class="progress-bar">
                <div id="progress-fill" class="progress-fill"></div>
            </div>

            <div class="info-box">
                <span style="color: #8b949e;">TARGET (Strike):</span>
                <span id="target-val" style="font-weight: bold;">$0.00</span>
            </div>
            <div class="info-box">
                <span style="color: #8b949e;">CURRENT:</span>
                <span id="current-val" style="font-weight: bold;">$0.00</span>
            </div>
            <div class="info-box">
                <span style="color: #8b949e;">DIFERENCIA:</span>
                <span id="diff-val" style="font-weight: bold;">$0.00</span>
            </div>
        </div>

        <script>
            async function actualizarDatos() {
                try {
                    let res = await fetch('/api/data');
                    let data = await res.json();
                    
                    document.getElementById('signal-card').innerText = data.signal_text;
                    document.getElementById('signal-card').style.backgroundColor = data.bg_color;
                    document.getElementById('up-val').innerText = data.up_val + "%";
                    document.getElementById('down-val').innerText = data.down_val + "%";
                    document.getElementById('progress-fill').style.width = data.up_val + "%";
                    document.getElementById('target-val').innerText = "$" + data.target.toLocaleString('en-US', {minimumFractionDigits: 2});
                    document.getElementById('current-val').innerText = "$" + data.current.toLocaleString('en-US', {minimumFractionDigits: 2});
                    document.getElementById('diff-val').innerText = (data.diff >= 0 ? "+$" : "-$") + Math.abs(data.diff).toFixed(2);
                } catch (e) {
                    console.error("Error sincronizando", e);
                }
            }
            setInterval(actualizarDatos, 2000);
            actualizarDatos();
        </script>
    </body>
    </html>
    """
