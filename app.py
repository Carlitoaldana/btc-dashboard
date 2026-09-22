import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone

# =========================================================
# MACALY + ALPHA BOT v4.6.1 + AUTO PAPER
# BTC 15 MIN • PAPER ONLY • NO REAL ORDERS
# =========================================================

st.set_page_config(page_title="Macaly + Alpha Bot v4.6.1", page_icon="⚡", layout="centered", initial_sidebar_state="collapsed")

NEW_ROUND_WAIT = 30
NEW_ENTRY_LOCK = 75
UP_THRESHOLD = 4.0
DOWN_THRESHOLD = -4.0
FLIP_UP_THRESHOLD = 4.75
FLIP_DOWN_THRESHOLD = -4.75
FLIP_CONFIRMATIONS = 2
AUTO_LEVELS = (1, 2, 3, 4, 5)

st.markdown("""
<style>
#MainMenu{visibility:hidden} footer{visibility:hidden} header{visibility:hidden}
.stApp{background-color:#0b0e14}.block-container{padding:10px!important;max-width:460px}
.bot-card{background:#11161f;border:1px solid #334155;border-radius:18px;padding:20px;margin-bottom:12px;color:#e8edf5}
.bot-title{background:#111a2e;border:1px solid #2563eb;border-radius:18px;padding:18px;margin-bottom:12px;text-align:center;color:#38bdf8;font-weight:900;letter-spacing:2px}
.bot-label{text-align:center;color:#94a3b8;font-size:13px;font-weight:800;letter-spacing:2px;margin-bottom:12px}
.bot-row{display:flex;justify-content:space-between;gap:12px;padding:11px 0;border-bottom:1px solid #334155}
.bot-row:last-child{border-bottom:none}.bot-left{color:#94a3b8}.bot-right{color:#e8edf5;font-weight:800;text-align:right}
.small-note{color:#64748b;font-size:12px;line-height:1.5;text-align:center}
.warning-box{background:#2a2110;border:1px solid #f59e0b;border-radius:14px;padding:14px;margin-top:12px;color:#fbbf24;text-align:center;font-weight:800}
.round-box{background:#0f172a;border:1px solid #38bdf8;border-radius:14px;padding:12px;margin-bottom:12px;text-align:center;color:#7dd3fc;font-weight:800}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
defaults = {
    "rounds": {}, "active_ticker": None,
    "auto_paper_enabled": True, "auto_paper_amount": 1,
    "auto_paper_entries": {}, "auto_paper_history": [],
    "auto_previous_ticker": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def new_round_state(ticker, seconds_left):
    return {
        "ticker": ticker, "detected_at": datetime.now(timezone.utc), "detected_seconds_left": seconds_left,
        "first_direction": None, "first_signal_time": None, "first_signal_seconds": None, "first_signal_price": None,
        "active_direction": None, "active_since": None, "last_score": 0.0, "previous_score": 0.0,
        "opposite_count": 0, "last_live_price": None, "previous_live_price": None,
        "reversal_warning": False, "reversal_text": ""
    }

# ---------------- DATA ----------------
@st.cache_data(ttl=5)
def get_btc_data():
    r = requests.get("https://api.exchange.coinbase.com/products/BTC-USD/candles",
                     params={"granularity":60}, headers={"User-Agent":"MacalyAlphaBot/4.6.1"}, timeout=10)
    r.raise_for_status(); data=r.json()
    if not isinstance(data,list) or len(data)<30: raise ValueError("Coinbase no devolvió suficientes datos.")
    df=pd.DataFrame(data,columns=["time","low","high","open","close","volume"])
    for c in ["low","high","open","close","volume"]: df[c]=pd.to_numeric(df[c],errors="coerce")
    df["time"]=pd.to_datetime(df["time"],unit="s",utc=True)
    return df.dropna().sort_values("time").reset_index(drop=True)

def get_btc_live_price():
    r=requests.get("https://api.exchange.coinbase.com/products/BTC-USD/ticker",
        headers={"User-Agent":"MacalyAlphaBot/4.6.1","Cache-Control":"no-cache"},
        params={"_":int(datetime.now(timezone.utc).timestamp())},timeout=6)
    r.raise_for_status(); p=r.json().get("price")
    if p in [None,""]: raise ValueError("Coinbase ticker no devolvió precio.")
    return float(p)

@st.cache_data(ttl=2)
def get_kalshi_btc_market():
    r=requests.get("https://external-api.kalshi.com/trade-api/v2/markets",
        params={"limit":100,"status":"open","series_ticker":"KXBTC15M"},
        headers={"User-Agent":"MacalyAlphaBot/4.6.1"},timeout=10)
    r.raise_for_status(); markets=r.json().get("markets",[])
    if not markets:return None
    markets.sort(key=lambda m:str(m.get("close_time") or "9999"))
    return markets[0]

def get_event_ticker_from_market(market):
    if not market:return None
    if market.get("event_ticker"):return str(market["event_ticker"])
    t=market.get("ticker")
    if not t:return None
    parts=str(t).split("-")
    return "-".join(parts[:-1]) if len(parts)>=2 else None

def extract_kalshi_btc_price(data):
    if not isinstance(data,dict):return None
    live=data.get("live_data",data); details=live.get("details",{}) if isinstance(live,dict) else {}
    preferred={"price","value","index_value","indexvalue","current_price","currentprice","current_value","currentvalue","last_price","lastprice","close"}
    found=[]
    def walk(o):
        if isinstance(o,dict):
            for k,v in o.items():
                nk=str(k).lower().replace("-","_")
                if nk in preferred:
                    try:
                        n=float(v)
                        if 10000<n<1000000:found.append(n)
                    except (TypeError,ValueError):pass
                walk(v)
        elif isinstance(o,list):
            for x in o:walk(x)
    walk(details)
    if found:return float(found[-1])
    pairs=[]
    def wp(o):
        if isinstance(o,list):
            if len(o)>=2:
                try:
                    n=float(o[-1])
                    if 10000<n<1000000:pairs.append(n)
                except (TypeError,ValueError):pass
            for x in o:wp(x)
        elif isinstance(o,dict):
            for v in o.values():wp(v)
    wp(details)
    return float(pairs[-1]) if pairs else None

def get_kalshi_live_btc(market):
    event=get_event_ticker_from_market(market)
    if not event:raise ValueError("La ronda no entregó event_ticker.")
    r=requests.get(f"https://external-api.kalshi.com/trade-api/v2/live_data/events/{event}",
        params={"range":"15min","_":int(datetime.now(timezone.utc).timestamp())},
        headers={"User-Agent":"MacalyAlphaBot/4.6.1","Cache-Control":"no-cache"},timeout=6)
    r.raise_for_status(); p=extract_kalshi_btc_price(r.json())
    if p is None:raise ValueError("Kalshi live respondió sin precio BTC válido.")
    return float(p)

# ---------------- INDICATORS / MARKET ----------------
def add_indicators(df):
    df=df.copy(); c=df["close"]
    df["ema9"]=c.ewm(span=9,adjust=False).mean(); df["ema21"]=c.ewm(span=21,adjust=False).mean()
    d=c.diff(); gain=d.clip(lower=0); loss=-d.clip(upper=0)
    ag=gain.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    al=loss.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    rs=ag/al.replace(0,np.nan); df["rsi"]=(100-(100/(1+rs))).fillna(50)
    df["mom3"]=c.pct_change(3)*100; df["mom5"]=c.pct_change(5)*100; df["mom15"]=c.pct_change(15)*100
    av=df["volume"].rolling(20).mean(); df["vol_ratio"]=df["volume"]/av.replace(0,np.nan)
    return df

def get_target_from_market(m):
    if not m:return None
    for key in ("floor_strike","cap_strike"):
        try:
            x=float(m.get(key))
            if x>1000:return x
        except:pass
    return None

def get_seconds_remaining(m):
    if not m or not m.get("close_time"):return None
    try:
        dt=datetime.fromisoformat(str(m["close_time"]).replace("Z","+00:00"))
        return max(0,int((dt-datetime.now(timezone.utc)).total_seconds()))
    except:return None

def format_countdown(s):
    return "--:--" if s is None else f"{s//60:02d}:{s%60:02d}"

def numeric_kalshi_price(d,c):
    try:
        if d not in [None,""]:return float(d)
    except:pass
    try:
        if c not in [None,""]:return float(c)/100
    except:pass
    return None

def kalshi_price(d,c):
    v=numeric_kalshi_price(d,c); return "--" if v is None else f"${v:.2f}"

def get_yes_ask(m):
    return None if not m else numeric_kalshi_price(m.get("yes_ask_dollars"),m.get("yes_ask"))

def get_no_ask(m):
    if not m:return None
    x=numeric_kalshi_price(m.get("no_ask_dollars"),m.get("no_ask"))
    if x is not None:return x
    y=numeric_kalshi_price(m.get("yes_bid_dollars"),m.get("yes_bid"))
    return max(0,min(1,1-y)) if y is not None else None

# ---------------- ORIGINAL SIGNAL ENGINE ----------------
def estimated_probabilities(score,distance,seconds,m3,m5):
    s=float(np.clip(score,-10,10)); up=50+s*4.2
    up += 3 if m3>0.04 else (-3 if m3<-0.04 else 0)
    up += 2 if m5>0.06 else (-2 if m5<-0.06 else 0)
    if distance is not None and seconds is not None and seconds<=180:
        up += 3 if distance>0 else (-3 if distance<0 else 0)
    up=float(np.clip(up,5,95)); return round(up),round(100-up)

def build_signal(df,target,seconds_left,live_price=None):
    last=df.iloc[-1]; candle=float(last["close"]); price=float(live_price) if live_price is not None else candle
    rsi=float(last["rsi"]); m3=float(last["mom3"]) if pd.notna(last["mom3"]) else 0
    m5=float(last["mom5"]) if pd.notna(last["mom5"]) else 0; m15=float(last["mom15"]) if pd.notna(last["mom15"]) else 0
    vr=float(last["vol_ratio"]) if pd.notna(last["vol_ratio"]) else 0; tech=0.0
    if last["ema9"]>last["ema21"]:tech+=2; ema="ALCISTA 🚀"
    else:tech-=2; ema="BAJISTA 🔻"
    tech += 1 if rsi>=55 else (-1 if rsi<=45 else 0)
    tech += 1.25 if m3>0.02 else (-1.25 if m3<-0.02 else 0)
    tech += 1 if m5>0.03 else (-1 if m5<-0.03 else 0)
    tech += .75 if m15>0.05 else (-.75 if m15<-0.05 else 0)
    if vr>1.20:tech += .5 if m3>0 else (-.5 if m3<0 else 0)
    dist=None; dp=None; ts=0.0
    if target is not None:
        dist=price-target; dp=dist/target*100
        ts += 2 if dist>0 else (-2 if dist<0 else 0)
        if seconds_left is not None:
            ad=abs(dist); bonus=4 if seconds_left<=30 else 3 if seconds_left<=60 else 2 if seconds_left<=180 else 1 if seconds_left<=300 else 0
            ts += bonus if dist>0 else (-bonus if dist<0 else 0)
            if ad<10:ts*=.60
            elif ad<20:ts*=.80
    final=tech+ts; momentum="ALCISTA" if m3>.02 else ("BAJISTA" if m3<-.02 else "NEUTRAL")
    up,down=estimated_probabilities(final,dist,seconds_left,m3,m5)
    return {"price":price,"candle_price":candle,"rsi":rsi,"mom3":m3,"mom5":m5,"mom15":m15,"vol_ratio":vr,
            "ema":ema,"technical_score":tech,"target_score":ts,"final_score":final,"distance":dist,"distance_pct":dp,
            "momentum":momentum,"up_probability":up,"down_probability":down}

def entry_quality(price,seconds):
    if price is None:return "PRECIO NO DISPONIBLE","#94a3b8"
    if seconds is not None and seconds<=NEW_ENTRY_LOCK:return "TARDE ⏰","#fb7185"
    if price<=.60:return "BUENA 🟢","#34d399"
    if price<=.70:return "PRECAUCIÓN 🟡","#fbbf24"
    return "CARA / TARDE 🔴","#fb7185"

def process_round_signal(ticker,sig,market,seconds_left):
    now=datetime.now(timezone.utc)
    if ticker and ticker!="--" and st.session_state.active_ticker!=ticker:
        st.session_state.active_ticker=ticker; st.session_state.rounds[ticker]=new_round_state(ticker,seconds_left)
    if not ticker or ticker=="--":
        return {"decision":"NO TRADE","signal":"SIN RONDA","icon":"⚠️","color":"#fbbf24","round_state":None,
                "reversal":False,"reversal_text":"","entry_price":None,"entry_quality":"SIN DATOS","entry_quality_color":"#94a3b8"}
    if ticker not in st.session_state.rounds:st.session_state.rounds[ticker]=new_round_state(ticker,seconds_left)
    state=st.session_state.rounds[ticker]; age=(now-state["detected_at"]).total_seconds(); score=sig["final_score"]
    prevp=state["last_live_price"]; state["previous_live_price"]=prevp; state["last_live_price"]=sig["price"]
    pchg=sig["price"]-prevp if prevp is not None else 0
    prevs=state["last_score"]; state["previous_score"]=prevs; schg=score-prevs; state["last_score"]=score
    if age<NEW_ROUND_WAIT:
        state["reversal_warning"]=False; state["reversal_text"]=""
        return {"decision":"ANALIZANDO NUEVA RONDA","signal":"ESPERANDO CONFIRMACIÓN","icon":"⏳","color":"#38bdf8",
                "round_state":state,"reversal":False,"reversal_text":"","entry_price":None,"entry_quality":"ESPERANDO","entry_quality_color":"#38bdf8"}
    locked=seconds_left is not None and seconds_left<=NEW_ENTRY_LOCK
    candidate="UP" if score>=UP_THRESHOLD else ("DOWN" if score<=DOWN_THRESHOLD else None)
    if state["active_direction"] is None and candidate and not locked:
        px=get_yes_ask(market) if candidate=="UP" else get_no_ask(market)
        state.update(active_direction=candidate,active_since=now,first_direction=candidate,first_signal_time=now,
                     first_signal_seconds=seconds_left,first_signal_price=px,opposite_count=0)
    active=state["active_direction"]; reversal=False; rt=""
    if active=="UP":
        weak=sum([score<3,schg<=-1.25,sig["mom3"]<-.02,sig["mom5"]<0,pchg<-8,
                  sig["distance"] is not None and seconds_left is not None and seconds_left<=180 and sig["distance"]<25 and pchg<0])
        if weak>=2:reversal=True;rt="UP PERDIENDO FUERZA • POSIBLE REVERSIÓN A DOWN"
        state["opposite_count"]=state["opposite_count"]+1 if score<=FLIP_DOWN_THRESHOLD and sig["mom3"]<0 else 0
        if state["opposite_count"]>=FLIP_CONFIRMATIONS:
            if not locked:state["active_direction"]="DOWN";state["active_since"]=now
            state["opposite_count"]=0
    elif active=="DOWN":
        weak=sum([score>-3,schg>=1.25,sig["mom3"]>.02,sig["mom5"]>0,pchg>8,
                  sig["distance"] is not None and seconds_left is not None and seconds_left<=180 and sig["distance"]>-25 and pchg>0])
        if weak>=2:reversal=True;rt="DOWN PERDIENDO FUERZA • POSIBLE REBOTE A UP"
        state["opposite_count"]=state["opposite_count"]+1 if score>=FLIP_UP_THRESHOLD and sig["mom3"]>0 else 0
        if state["opposite_count"]>=FLIP_CONFIRMATIONS:
            if not locked:state["active_direction"]="UP";state["active_since"]=now
            state["opposite_count"]=0
    state["reversal_warning"]=reversal;state["reversal_text"]=rt;active=state["active_direction"]
    if active=="UP":decision,signal,icon,color,px="POSIBLE UP","SEÑAL UP","🚀","#34d399",get_yes_ask(market)
    elif active=="DOWN":decision,signal,icon,color,px="POSIBLE DOWN","SEÑAL DOWN","🔻","#fb7185",get_no_ask(market)
    elif locked:decision,signal,icon,color,px="NO NUEVA ENTRADA","FINAL DE RONDA","⏰","#fbbf24",None
    else:decision,signal,icon,color,px="NO TRADE","ESPERAR","⚪","#fbbf24",None
    q,qc=entry_quality(px,seconds_left)
    return {"decision":decision,"signal":signal,"icon":icon,"color":color,"round_state":state,
            "reversal":reversal,"reversal_text":rt,"entry_price":px,"entry_quality":q,"entry_quality_color":qc}

# ---------------- AUTO PAPER ----------------
def auto_next_amount(current, won):
    current=int(current)
    if current not in AUTO_LEVELS:current=1
    if won:return current
    return AUTO_LEVELS[(AUTO_LEVELS.index(current)+1)%len(AUTO_LEVELS)]

def auto_settle_previous(new_ticker):
    old=st.session_state.auto_previous_ticker
    if not old or old==new_ticker:return
    trade=st.session_state.auto_paper_entries.get(old)
    if not trade or trade["status"]!="OPEN":return
    p=trade.get("last_seen_btc"); target=trade.get("target")
    if p is None or target is None:return
    actual="UP" if p>=target else "DOWN"; won=trade["direction"]==actual
    trade["actual"]=actual;trade["result"]="WIN" if won else "LOSS";trade["status"]="SETTLED"
    trade["next_amount"]=auto_next_amount(trade["amount"],won)
    st.session_state.auto_paper_amount=trade["next_amount"]
    st.session_state.auto_paper_history.append(dict(trade))

def auto_process(ticker,round_signal,target,seconds_left,live_price):
    if not st.session_state.auto_paper_enabled or not ticker or ticker=="--":return
    auto_settle_previous(ticker)
    state=round_signal.get("round_state")
    if state and state.get("first_direction") and ticker not in st.session_state.auto_paper_entries:
        px=state.get("first_signal_price")
        if px is not None and target is not None and not(seconds_left is not None and seconds_left<=NEW_ENTRY_LOCK):
            amount=int(st.session_state.auto_paper_amount)
            contracts=max(1,int(amount//float(px)))
            st.session_state.auto_paper_entries[ticker]={
                "ticker":ticker,"direction":state["first_direction"],"amount":amount,"entry_price":float(px),
                "contracts":contracts,"paper_cost":contracts*float(px),"target":float(target),
                "status":"OPEN","last_seen_btc":live_price,"result":None
            }
    trade=st.session_state.auto_paper_entries.get(ticker)
    if trade and trade["status"]=="OPEN" and live_price is not None:trade["last_seen_btc"]=float(live_price)
    st.session_state.auto_previous_ticker=ticker

def card(title,rows,note=""):
    body=''.join(f'<div class="bot-row"><span class="bot-left">{a}</span><span class="bot-right">{b}</span></div>' for a,b in rows)
    n=f'<div class="small-note" style="margin-top:12px;">{note}</div>' if note else ""
    return f'<div class="bot-card"><div class="bot-label">{title}</div>{body}{n}</div>'

st.markdown('<div class="bot-title">⚡ MACALY + ALPHA BOT • v4.6.1</div>',unsafe_allow_html=True)
st.toggle("🤖 AUTO PAPER",key="auto_paper_enabled")

@st.fragment(run_every="2s")
def live_dashboard():
    btc_error=kalshi_error=kalshi_live_error=""
    try:df=add_indicators(get_btc_data());btc_ok=True
    except Exception as e:btc_ok=False;btc_error=str(e);df=None
    try:market=get_kalshi_btc_market();kalshi_ok=market is not None
    except Exception as e:market=None;kalshi_ok=False;kalshi_error=str(e)
    try:cb=get_btc_live_price()
    except:cb=float(df.iloc[-1]["close"]) if btc_ok else None
    kl=None
    if market:
        try:kl=get_kalshi_live_btc(market)
        except Exception as e:kalshi_live_error=str(e)
    live=kl if kl is not None else cb
    source="KALSHI LIVE 🟢" if kl is not None else ("COINBASE FALLBACK 🟡" if cb is not None else "SIN DATOS 🔴")
    if market:
        ticker=market.get("ticker","--");target=get_target_from_market(market);seconds=get_seconds_remaining(market)
    else:ticker="--";target=None;seconds=None
    if btc_ok:sig=build_signal(df,target,seconds,live)
    else:sig={"price":live or 0,"rsi":50,"mom3":0,"mom5":0,"mom15":0,"vol_ratio":0,"ema":"SIN DATOS",
              "technical_score":0,"target_score":0,"final_score":0,"distance":None,"up_probability":50,"down_probability":50}
    rs=process_round_signal(ticker,sig,market,seconds)
    auto_process(ticker,rs,target,seconds,live)

    st.markdown(f'<div class="bot-card" style="text-align:center;"><div class="bot-label">BITCOIN • KALSHI 15 MIN</div>'
                f'<div style="font-size:30px;font-weight:900;color:{rs["color"]};">{rs["icon"]} {rs["decision"]}</div>'
                f'<div style="font-size:19px;margin-top:8px;color:#e2e8f0;">BTC ${sig["price"]:,.2f}</div></div>',unsafe_allow_html=True)

    # AUTO PANEL
    trade=st.session_state.auto_paper_entries.get(ticker)
    if trade:
        current=f'{trade["direction"]} • ${trade["amount"]} • {trade["status"]}'
    else:current="ESPERANDO SEÑAL"
    last="--"
    if st.session_state.auto_paper_history:
        h=st.session_state.auto_paper_history[-1];last=f'{h["result"]} • ${h["amount"]} → ${h["next_amount"]}'
    st.markdown(card("🤖 AUTO PAPER",[
        ("Estado","ENCENDIDO 🟢" if st.session_state.auto_paper_enabled else "APAGADO ⚪"),
        ("Monto actual",f'${st.session_state.auto_paper_amount}'),
        ("Ronda",current),("Último resultado",last)],
        "WIN = mismo monto • LOSS = siguiente nivel<br>$1 → $2 → $3 → $4 → $5 → $1<br>PAPER: NO ENVÍA ÓRDENES REALES"),unsafe_allow_html=True)

    st.markdown(card("PROBABILIDAD ESTIMADA",[("🚀 UP",f'{sig["up_probability"]}%'),("🔻 DOWN",f'{sig["down_probability"]}%')],
                     "Estimación interna del motor • no representa certeza"),unsafe_allow_html=True)
    if rs["reversal"]:
        st.markdown(f'<div class="warning-box">⚠️ POSIBLE REVERSIÓN / REBOTE<br><br>{rs["reversal_text"]}</div>',unsafe_allow_html=True)

    dist=sig["distance"]; disttext="--" if dist is None else (f'+${abs(dist):,.2f} ARRIBA' if dist>0 else f'-${abs(dist):,.2f} ABAJO' if dist<0 else "$0.00")
    st.markdown(card("RONDA ACTUAL",[("Ticker",ticker),("Target",f'${target:,.2f}' if target else "NO DISPONIBLE"),
        ("BTC actual",f'${sig["price"]:,.2f}'),("Fuente BTC",source),("Distancia",disttext),("Tiempo restante",format_countdown(seconds))]),unsafe_allow_html=True)

    state=rs["round_state"]
    if state:
        tm=state["first_signal_time"].astimezone().strftime("%H:%M:%S") if state["first_signal_time"] else "--"
        ss=format_countdown(state["first_signal_seconds"]); fp=f'${state["first_signal_price"]:.2f}' if state["first_signal_price"] is not None else "--"
        st.markdown(card("SEÑAL DE ESTA RONDA",[("Primera señal",state["first_direction"] or "NINGUNA"),("Generada",tm),
            ("Tiempo restante al aparecer",ss),("Kalshi al aparecer",fp),("Estado actual",state["active_direction"] or "ESPERANDO")]),unsafe_allow_html=True)

    ep=f'${rs["entry_price"]:.2f}' if rs["entry_price"] is not None else "--"
    st.markdown(card("ENTRADA ACTUAL",[("Precio contrato",ep),("Calidad",rs["entry_quality"])]),unsafe_allow_html=True)
    if market:
        st.markdown(card("KALSHI • BTC 15 MIN",[("YES bid",kalshi_price(market.get("yes_bid_dollars"),market.get("yes_bid"))),
            ("YES ask",kalshi_price(market.get("yes_ask_dollars"),market.get("yes_ask"))),
            ("NO ask",kalshi_price(market.get("no_ask_dollars"),market.get("no_ask"))),
            ("Último",kalshi_price(market.get("last_price_dollars"),market.get("last_price"))),
            ("API Kalshi","CONECTADO 🟢" if kalshi_ok else "SIN MERCADO ⚠️")]),unsafe_allow_html=True)

    st.markdown(card("ANÁLISIS TÉCNICO",[("EMA 9 / 21",sig["ema"]),("RSI 14",f'{sig["rsi"]:.1f}'),
        ("Momentum 3m",f'{sig["mom3"]:+.3f}%'),("Momentum 5m",f'{sig["mom5"]:+.3f}%'),("Momentum 15m",f'{sig["mom15"]:+.3f}%'),
        ("Volumen",f'{sig["vol_ratio"]:.2f}x'),("BTC referencia",source)]),unsafe_allow_html=True)
    st.markdown(card("DECISIÓN DEL MOTOR",[("Señal",rs["signal"]),("Score técnico",f'{sig["technical_score"]:.2f}'),
        ("Score target/tiempo",f'{sig["target_score"]:.2f}'),("Score combinado",f'{sig["final_score"]:.2f}')],
        "Cada ticker = una ronda independiente<br>No crea nuevas entradas en últimos 75 segundos<br>Modo análisis / paper<br>No envía órdenes reales"),unsafe_allow_html=True)

    if target is None and kalshi_ok:st.warning("Kalshi conectado, pero sin target numérico. El bot no inventará uno.")
    if btc_error:st.error("Error Coinbase velas: "+btc_error)
    if kalshi_live_error and cb is not None:st.warning("Kalshi BTC live falló; usando Coinbase. "+kalshi_live_error)
    if kalshi_error:st.error("Error Kalshi: "+kalshi_error)

live_dashboard()
