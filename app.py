import streamlit as st
import requests

st.set_page_config(page_title="Macaly Test", page_icon="⚡")

st.title("⚡ Macaly + Alpha Bot")
st.write("Probando conexiones...")

# ---------- BTC: Coinbase ----------
try:
    btc_url = "https://api.exchange.coinbase.com/products/BTC-USD/ticker"
    btc_response = requests.get(
        btc_url,
        headers={"User-Agent": "MacalyAlphaBot/1.0"},
        timeout=10
    )
    btc_response.raise_for_status()
    btc_data = btc_response.json()
    btc_price = float(btc_data["price"])

    st.success(f"BTC CONECTADO 🟢 — ${btc_price:,.2f}")

except Exception as e:
    st.error(f"BTC ERROR 🔴 — {e}")


# ---------- KALSHI: API pública ----------
try:
    kalshi_url = "https://api.elections.kalshi.com/trade-api/v2/markets"

    kalshi_response = requests.get(
        kalshi_url,
        params={
            "limit": 5,
            "status": "open"
        },
        headers={"User-Agent": "MacalyAlphaBot/1.0"},
        timeout=10
    )

    kalshi_response.raise_for_status()
    kalshi_data = kalshi_response.json()

    markets = kalshi_data.get("markets", [])

    st.success(
        f"KALSHI CONECTADO 🟢 — {len(markets)} mercados recibidos"
    )

except Exception as e:
    st.error(f"KALSHI ERROR 🔴 — {e}")
