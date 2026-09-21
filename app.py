import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone

# =========================================================
# MACALY + ALPHA BOT v4.6.2 PRO
# BTC 15 MIN • PAPER ONLY • NO REAL ORDERS
# =========================================================

st.set_page_config(page_title="Macaly + Alpha Bot v4.6.2", page_icon="⚡",
                   layout="centered", initial_sidebar_state="collapsed")

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
#MainMenu,footer,header{visibility:hidden}
.stApp{background:radial-gradient(circle at 50% 0,#0b2940 0,#07111d 28%,#050a11 70%);color:#eef7ff}
.block-container{padding:12px 10px 40px!important;max-width:480px}
[data-testid="stToggle"]{background:#081522;border:1px solid #193c57;border-radius:16px;padding:8px 14px;margin-bottom:10px}
.brand,.card,.hero{background:linear-gradient(145deg,#0a1b2b,#07111d);border:1px solid #1b4563;border-radius:20px;margin-bottom:12px;box-shadow:0 12px 28px #0005}
.brand{display:flex;justify-content:space-between;align-items:center;padding:15px}
.brand-name{font-size:16px;font-weight:900;color:#f4fbff;letter-spacing:.6px}.sub{font-size:10px;color:#65a8cf;margin-top:4px;letter-spacing:1px}
.online{font-size:10px;font-weight:900;color:#4adea3;border:1px solid #237b60;background:#0b2b25;padding:7px 9px;border-radius:99px}
.hero{padding:18px;border-color:var(--c)}.eyebrow,.title{font-size:10px;font-weight:900;letter-spacing:1.7px;color:#55c7ff}
.hero-main{font-size:30px;font-weight:950;color:var(--c);margin-top:6px}.btc{font-size:20px;font-weight:900;margin-top:5px}.muted{font-size:10px;color:#6d8da3;margin-top:6px}
.card{padding:16px}.title{margin-bottom:11px}
.row{display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-bottom:1px solid #173247}.row:last-child{border-bottom:0}
.l{font-size:12px;color:#7693a7}.r{font-size:13px;font-weight:850;color:#f0f8ff;text-align:right;overflow-wrap:anywhere}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}.tile{background:#071a29;border:1px solid #183d58;border-radius:14px;padding:11px}
.tl{font-size:9px;color:#6f91a7;font-weight:900;letter-spacing:1px}.tv{font-size:18px;font-weight:950;margin-top:5px}
.up{color:#3ee6a4!important}.down{color:#ff6474!important}.cyan{color:#45c9ff!important}.amber{color:#ffc857!important}
.trade{border:1px solid var(--tc);background:#071b29;border-radius:17px;padding:14px;margin-top:8px}
.trade-top{display:flex;justify-content:space-between;align-items:center}.trade-dir{font-size:20px;font-weight:950;color:var(--tc)}
.pill{font-size:9px;font-weight:900;color:var(--tc);border:1px solid var(--tc);border-radius:99px;padding:5px 8px}
.lock-label{font-size:9px;color:#7293a8;font-weight:900;letter-spacing:1.1px;margin-top:10px}.lock-price{font-size:31px;font-weight:950}
.note{font-size:10px;color:#5f7f94;text-align:center;line-height:1.55;margin-top:10px}
.warn{background:#342509;border:1px solid #a56c14;border-radius:17px;padding:13px;color:#ffd166;text-align:center;font-size:12px;font-weight:900;margin-bottom:12px}
.hist{background:#071a29;border:1px solid #173b56;border-radius:14px;padding:11px;margin-top:8px}.histtop{display:flex;justify-content:space-between;font-weight:900}.histmeta{font-size:10px;color:#66879c;line-height:1.55;margin-top:6px}
.barbg{height:7px;background:#0b2030;border-radius:99px;overflow:hidden;margin-top:11px}.bar{height:100%;background:linear-gradient(90deg,#0ea5e9,#34d399)}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_auto_memory():
    return {"enabled":True,"amount":1,"entries":{},"history":[],"previous_ticker":None,"rounds":{},"active_ticker":None}

memory=get_auto_memory()
if "auto_loaded" not in st.session_state:
    st.session_state.auto_paper_enabled=memory["enabled"]
    st.session_state.auto_paper_amount=memory["amount"]
    st.session_state.auto_paper_entries=memory["entries"]
    st.session_state.auto_paper_history=memory["history"]
    st.session_state.auto_previous_ticker=memory["previous_ticker"]
    st.session_state.rounds=memory["rounds"]
    st.session_state.active_ticker=memory["active_ticker"]
    st.session_state.auto_loaded=True

def save_memory():
    memory["enabled"]=bool(st.session_state.auto_paper_enabled)
    memory["amount"]=int(st.session_state.auto_paper_amount)
    memory["entries"]=st.session_state.auto_paper_entries
    memory["history"]=st.session_state.auto_paper_history
    memory["previous_ticker"]=st.session_state.auto_previous_ticker
    memory["rounds"]=st.session_state.rounds
    memory["active_ticker"]=st.session_state.active_ticker

def new_round_state(ticker,seconds_left):
    return {"ticker":ticker,"detected_at":datetime.now(timezone.utc),"detected_seconds_left":seconds_left,
    "first_direction":None,"first_signal_time":None,"first_signal_seconds":None,"first_signal_price":None,
    "active_direction":None,"active_since":None,"last_score":0.0,"previous_score":0.0,"opposite_count":0,
    "last_live_price":None,"previous_live_price":None,"reversal_warning":False,"reversal_text":""}

@st.cache_data(ttl=5)
def get_btc_data():
    r=requests.get("https://api.exchange.coinbase.com/products/BTC-USD/candles",params={"granularity":60},
                   headers={"User-Agent":"MacalyAlphaBot/4.6.2"},timeout=10);r.raise_for_status();data=r.json()
    if not isinstance(data,list) or len(data)<30:raise ValueError("Coinbase no devolvió suficientes datos.")
    df=pd.DataFrame(data,columns=["time","low","high","open","close","volume"])
    for c in ["low","high","open","close","volume"]:df[c]=pd.to_numeric(df[c],errors="coerce")
    df["time"]=pd.to_datetime(df["time"],unit="s",utc=True)
    return df.dropna().sort_values("time").reset_index(drop=True)

def get_btc_live_price():
    r=requests.get("https://api.exchange.coinbase.com/products/BTC-USD/ticker",
      headers={"User-Agent":"MacalyAlphaBot/4.6.2","Cache-Control":"no-cache"},
      params={"_":int(datetime.now(timezone.utc).timestamp())},timeout=6);r.raise_for_status()
    p=r.json().get("price")
    if p in [None,""]:raise ValueError("Coinbase ticker no devolvió precio.")
    return float(p)

@st.cache_data(ttl=2)
def get_kalshi_btc_market():
    r=requests.get("https://external-api.kalshi.com/trade-api/v2/markets",
      params={"limit":100,"status":"open","series_ticker":"KXBTC15M"},
      headers={"User-Agent":"MacalyAlphaBot/4.6.2"},timeout=10);r.raise_for_status()
    markets=r.json().get("markets",[])
    if not markets:return None
    markets.sort(key=lambda m:str(m.get("close_time") or "9999"));return markets[0]

def get_event_ticker_from_market(m):
    if not m:return None
    if m.get("event_ticker"):return str(m["event_ticker"])
    t=m.get("ticker")
    if not t:return None
    p=str(t).split("-");return "-".join(p[:-1]) if len(p)>=2 else None

def extract_kalshi_btc_price(data):
    if not isinstance(data,dict):return None
    live=data.get("live_data",data);details=live.get("details",{}) if isinstance(live,dict) else {}
    preferred={"price","value","index_value","indexvalue","current_price","currentprice","current_value","currentvalue","last_price","lastprice","close"};found=[]
    def walk(o):
        if isinstance(o,dict):
            for k,v in o.items():
                if str(k).lower().replace("-","_") in preferred:
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
    wp(details);return float(pairs[-1]) if pairs else None

def get_kalshi_live_btc(market):
    event=get_event_ticker_from_market(market)
    if not event:raise ValueError("La ronda no entregó event_ticker.")
    r=requests.get(f"https://external-api.kalshi.com/trade-api/v2/live_data/events/{event}",
      params={"range":"15min","_":int(datetime.now(timezone.utc).timestamp())},
      headers={"User-Agent":"MacalyAlphaBot/4.6.2","Cache-Control":"no-cache"},timeout=6);r.raise_for_status()
    p=extract_kalshi_btc_price(r.json())
    if p is None:raise ValueError("Kalshi live respondió sin precio BTC válido.")
    return float(p)

def add_indicators(df):
    df=df.copy();close=df["close"];df["ema9"]=close.ewm(span=9,adjust=False).mean();df["ema21"]=close.ewm(span=21,adjust=False).mean()
    d=close.diff();g=d.clip(lower=0);loss=-d.clip(upper=0)
    ag=g.ewm(alpha=1/14,adjust=False,min_periods=14).mean();al=loss.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    rs=ag/al.replace(0,np.nan);df["rsi"]=(100-(100/(1+rs))).fillna(50)
    df["mom3"]=close.pct_change(3)*100;df["mom5"]=close.pct_change(5)*100;df["mom15"]=close.pct_change(15)*100
    df["vol_ratio"]=df["volume"]/df["volume"].rolling(20).mean().replace(0,np.nan);return df

def get_target_from_market(m):
    if not m:return None
    for k in ("floor_strike","cap_strike"):
        try:
            x=float(m.get(k))
            if x>1000:return x
        except (TypeError,ValueError):pass
    return None

def get_seconds_remaining(m):
    if not m or not m.get("close_time"):return None
    try:
        dt=datetime.fromisoformat(str(m["close_time"]).replace("Z","+00:00"));return max(0,int((dt-datetime.now(timezone.utc)).total_seconds()))
    except (TypeError,ValueError):return None

def format_countdown(s):
    return "--:--" if s is None else f"{s//60:02d}:{s%60:02d}"

def numeric_kalshi_price(d,c):
    try:
        if d not in [None,""]:return float(d)
    except (TypeError,ValueError):pass
    try:
        if c not in [None,""]:return float(c)/100
    except (TypeError,ValueError):pass
    return None

def kalshi_price(d,c):
    v=numeric_kalshi_price(d,c);return "--" if v is None else f"${v:.2f}"

def get_yes_ask(m):
    return None if not m else numeric_kalshi_price(m.get("yes_ask_dollars"),m.get("yes_ask"))

def get_no_ask(m):
    if not m:return None
    v=numeric_kalshi_price(m.get("no_ask_dollars"),m.get("no_ask"))
    if v is not None:return v
    y=numeric_kalshi_price(m.get("yes_bid_dollars"),m.get("yes_bid"))
    return max(0,min(1,1-y)) if y is not None else None

def estimated_probabilities(score,distance,seconds,mom3,mom5):
    score=float(np.clip(score,-10,10));up=50+score*4.2
    up+=3 if mom3>.04 else -3 if mom3<-.04 else 0;up+=2 if mom5>.06 else -2 if mom5<-.06 else 0
    if distance is not None and seconds is not None and seconds<=180:up+=3 if distance>0 else -3 if distance<0 else 0
    up=float(np.clip(up,5,95));return round(up),round(100-up)

def build_signal(df,target,seconds_left,live_price=None):
    last=df.iloc[-1];candle=float(last["close"]);price=float(live_price) if live_price is not None else candle
    rsi=float(last["rsi"]);m3=float(last["mom3"]) if pd.notna(last["mom3"]) else 0;m5=float(last["mom5"]) if pd.notna(last["mom5"]) else 0
    m15=float(last["mom15"]) if pd.notna(last["mom15"]) else 0;vr=float(last["vol_ratio"]) if pd.notna(last["vol_ratio"]) else 0;ts=0.0
    if last["ema9"]>last["ema21"]:ts+=2;ema="ALCISTA 🚀"
    else:ts-=2;ema="BAJISTA 🔻"
    if rsi>=55:ts+=1
    elif rsi<=45:ts-=1
    if m3>.02:ts+=1.25
    elif m3<-.02:ts-=1.25
    if m5>.03:ts+=1
    elif m5<-.03:ts-=1
    if m15>.05:ts+=.75
    elif m15<-.05:ts-=.75
    if vr>1.2:ts+=.5 if m3>0 else -.5 if m3<0 else 0
    dist=None;dp=None;tgs=0.0
    if target is not None:
        dist=price-target;dp=dist/target*100;tgs+=2 if dist>0 else -2 if dist<0 else 0
        if seconds_left is not None:
            ad=abs(dist);bonus=4 if seconds_left<=30 else 3 if seconds_left<=60 else 2 if seconds_left<=180 else 1 if seconds_left<=300 else 0
            tgs+=bonus if dist>0 else -bonus if dist<0 else 0
            if ad<10:tgs*=.60
            elif ad<20:tgs*=.80
    fs=ts+tgs;up,down=estimated_probabilities(fs,dist,seconds_left,m3,m5)
    return {"price":price,"candle_price":candle,"rsi":rsi,"mom3":m3,"mom5":m5,"mom15":m15,"vol_ratio":vr,"ema":ema,
    "technical_score":ts,"target_score":tgs,"final_score":fs,"distance":dist,"distance_pct":dp,
    "momentum":"ALCISTA" if m3>.02 else "BAJISTA" if m3<-.02 else "NEUTRAL","up_probability":up,"down_probability":down}

def entry_quality(p,s):
    if p is None:return "PRECIO NO DISPONIBLE","#94a3b8"
    if s is not None and s<=NEW_ENTRY_LOCK:return "TARDE ⏰","#fb7185"
    if p<=.60:return "BUENA 🟢","#34d399"
    if p<=.70:return "PRECAUCIÓN 🟡","#fbbf24"
    return "CARA / TARDE 🔴","#fb7185"

def process_round_signal(ticker,sig,market,seconds_left):
    now=datetime.now(timezone.utc)
    if ticker and ticker!="--" and st.session_state.active_ticker!=ticker:
        st.session_state.active_ticker=ticker;st.session_state.rounds[ticker]=new_round_state(ticker,seconds_left);save_memory()
    if not ticker or ticker=="--":return {"decision":"NO TRADE","signal":"SIN RONDA","icon":"⚠️","color":"#fbbf24","round_state":None,"reversal":False,"reversal_text":"","entry_price":None,"entry_quality":"SIN DATOS","entry_quality_color":"#94a3b8"}
    if ticker not in st.session_state.rounds:st.session_state.rounds[ticker]=new_round_state(ticker,seconds_left)
    state=st.session_state.rounds[ticker];age=(now-state["detected_at"]).total_seconds();score=sig["final_score"]
    pp=state["last_live_price"];state["previous_live_price"]=pp;state["last_live_price"]=sig["price"];pc=sig["price"]-pp if pp is not None else 0
    ps=state["last_score"];state["previous_score"]=ps;sc=score-ps;state["last_score"]=score
    if age<NEW_ROUND_WAIT:
        state["reversal_warning"]=False;state["reversal_text"]="";save_memory()
        return {"decision":"ANALIZANDO NUEVA RONDA","signal":"ESPERANDO CONFIRMACIÓN","icon":"⏳","color":"#38bdf8","round_state":state,"reversal":False,"reversal_text":"","entry_price":None,"entry_quality":"ESPERANDO","entry_quality_color":"#38bdf8"}
    locked=seconds_left is not None and seconds_left<=NEW_ENTRY_LOCK;candidate="UP" if score>=UP_THRESHOLD else "DOWN" if score<=DOWN_THRESHOLD else None
    if state["active_direction"] is None and candidate and not locked:
        px=get_yes_ask(market) if candidate=="UP" else get_no_ask(market)
        state.update(active_direction=candidate,active_since=now,first_direction=candidate,first_signal_time=now,first_signal_seconds=seconds_left,first_signal_price=px,opposite_count=0)
    active=state["active_direction"];rev=False;rt=""
    if active=="UP":
        weak=sum([score<3,sc<=-1.25,sig["mom3"]<-.02,sig["mom5"]<0,pc<-8,(sig["distance"] is not None and seconds_left is not None and seconds_left<=180 and sig["distance"]<25 and pc<0)])
        if weak>=2:rev=True;rt="UP PERDIENDO FUERZA • POSIBLE REVERSIÓN A DOWN"
        state["opposite_count"]=state["opposite_count"]+1 if score<=FLIP_DOWN_THRESHOLD and sig["mom3"]<0 else 0
        if state["opposite_count"]>=FLIP_CONFIRMATIONS:
            if not locked:state["active_direction"]="DOWN";state["active_since"]=now
            state["opposite_count"]=0
    elif active=="DOWN":
        weak=sum([score>-3,sc>=1.25,sig["mom3"]>.02,sig["mom5"]>0,pc>8,(sig["distance"] is not None and seconds_left is not None and seconds_left<=180 and sig["distance"]>-25 and pc>0)])
        if weak>=2:rev=True;rt="DOWN PERDIENDO FUERZA • POSIBLE REBOTE A UP"
        state["opposite_count"]=state["opposite_count"]+1 if score>=FLIP_UP_THRESHOLD and sig["mom3"]>0 else 0
        if state["opposite_count"]>=FLIP_CONFIRMATIONS:
            if not locked:state["active_direction"]="UP";state["active_since"]=now
            state["opposite_count"]=0
    state["reversal_warning"]=rev;state["reversal_text"]=rt;active=state["active_direction"]
    if active=="UP":decision,signal,icon,color,ep="POSIBLE UP","SEÑAL UP","🚀","#34d399",get_yes_ask(market)
    elif active=="DOWN":decision,signal,icon,color,ep="POSIBLE DOWN","SEÑAL DOWN","🔻","#fb7185",get_no_ask(market)
    elif locked:decision,signal,icon,color,ep="NO NUEVA ENTRADA","FINAL DE RONDA","⏰","#fbbf24",None
    else:decision,signal,icon,color,ep="NO TRADE","ESPERAR","⚪","#fbbf24",None
    q,qc=entry_quality(ep,seconds_left);save_memory()
    return {"decision":decision,"signal":signal,"icon":icon,"color":color,"round_state":state,"reversal":rev,"reversal_text":rt,"entry_price":ep,"entry_quality":q,"entry_quality_color":qc}

def auto_next_amount(current,won):
    current=int(current);current=current if current in AUTO_LEVELS else 1
    return current if won else AUTO_LEVELS[(AUTO_LEVELS.index(current)+1)%len(AUTO_LEVELS)]

def auto_settle_previous(new_ticker):
    old=st.session_state.auto_previous_ticker
    if not old or old==new_ticker:return
    trade=st.session_state.auto_paper_entries.get(old)
    if not trade or trade.get("status")!="OPEN":return
    price=trade.get("last_seen_btc");target=trade.get("target")
    if price is None or target is None:return
    actual="UP" if float(price)>=float(target) else "DOWN";won=trade["direction"]==actual
    trade["actual"]=actual;trade["result"]="WIN" if won else "LOSS";trade["status"]="SETTLED";trade["next_amount"]=auto_next_amount(trade["amount"],won)
    trade["paper_pnl"]=round((trade.get("contracts",0)*(1 if won else 0))-trade.get("paper_cost",0),2)
    trade["settled_at"]=datetime.now(timezone.utc).isoformat()
    st.session_state.auto_paper_amount=trade["next_amount"];st.session_state.auto_paper_history.append(dict(trade));save_memory()

def auto_process(ticker,round_signal,target,seconds_left,live_price):
    if not ticker or ticker=="--":return
    auto_settle_previous(ticker);st.session_state.auto_previous_ticker=ticker;state=round_signal.get("round_state")
    if st.session_state.auto_paper_enabled and state and state.get("first_direction") and ticker not in st.session_state.auto_paper_entries:
        ep=state.get("first_signal_price")
        if ep is not None and target is not None and not(seconds_left is not None and seconds_left<=NEW_ENTRY_LOCK):
            amount=int(st.session_state.auto_paper_amount);ep=float(ep)
            if 0<ep<=1:
                contracts=max(1,int(amount//ep))
                st.session_state.auto_paper_entries[ticker]={"ticker":ticker,"direction":state["first_direction"],"amount":amount,
                "entry_price":ep,"contracts":contracts,"paper_cost":round(contracts*ep,2),"target":float(target),"status":"OPEN",
                "entry_time":state["first_signal_time"].isoformat() if state.get("first_signal_time") else datetime.now(timezone.utc).isoformat(),
                "entry_seconds_left":state.get("first_signal_seconds"),"last_seen_btc":float(live_price) if live_price is not None else None,
                "last_seen_seconds":seconds_left,"result":None}
    trade=st.session_state.auto_paper_entries.get(ticker)
    if trade and trade.get("status")=="OPEN" and live_price is not None:
        trade["last_seen_btc"]=float(live_price);trade["last_seen_seconds"]=seconds_left
    save_memory()

def card(title,rows,note=""):
    body="".join(f'<div class="row"><span class="l">{a}</span><span class="r">{b}</span></div>' for a,b in rows)
    return f'<div class="card"><div class="title">{title}</div>{body}{f"""<div class="note">{note}</div>""" if note else ""}</div>'

def local_time(v):
    try:return datetime.fromisoformat(str(v).replace("Z","+00:00")).astimezone().strftime("%I:%M:%S %p")
    except:return "--"

st.markdown('<div class="brand"><div><div class="brand-name">⚡ MACALY + ALPHA BOT</div><div class="sub">v4.6.2 • BTC 15 MIN • PRO PAPER</div></div><div class="online">● EN LÍNEA</div></div>',unsafe_allow_html=True)
def auto_toggle_changed():save_memory()
st.toggle("🤖 AUTO PAPER",key="auto_paper_enabled",on_change=auto_toggle_changed)

@st.fragment(run_every="2s")
def live_dashboard():
    btc_error=kalshi_error=kalshi_live_error=""
    try:df=add_indicators(get_btc_data());btc_ok=True
    except Exception as e:btc_ok=False;btc_error=str(e);df=None
    try:market=get_kalshi_btc_market();kalshi_ok=market is not None
    except Exception as e:market=None;kalshi_ok=False;kalshi_error=str(e)
    try:coinbase_live=get_btc_live_price()
    except Exception:coinbase_live=float(df.iloc[-1]["close"]) if btc_ok else None
    kalshi_live=None
    if market:
        try:kalshi_live=get_kalshi_live_btc(market)
        except Exception as e:kalshi_live_error=str(e)
    live_price=kalshi_live if kalshi_live is not None else coinbase_live
    source="KALSHI LIVE 🟢" if kalshi_live is not None else "COINBASE FALLBACK 🟡" if coinbase_live is not None else "SIN DATOS 🔴"
    ticker=market.get("ticker","--") if market else "--";target=get_target_from_market(market) if market else None;seconds_left=get_seconds_remaining(market) if market else None
    sig=build_signal(df,target,seconds_left,live_price) if btc_ok else {"price":live_price or 0,"rsi":50,"mom3":0,"mom5":0,"mom15":0,"vol_ratio":0,"ema":"SIN DATOS","technical_score":0,"target_score":0,"final_score":0,"distance":None,"up_probability":50,"down_probability":50}
    rs=process_round_signal(ticker,sig,market,seconds_left);auto_process(ticker,rs,target,seconds_left,live_price)

    st.markdown(f'<div class="hero" style="--c:{rs["color"]}"><div class="eyebrow">SEÑAL ACTUAL • BITCOIN / KALSHI</div><div class="hero-main">{rs["icon"]} {rs["decision"]}</div><div class="btc">BTC ${sig["price"]:,.2f}</div><div class="muted">{source} • SCORE {sig["final_score"]:.2f}</div></div>',unsafe_allow_html=True)
    pct=max(0,min(100,(seconds_left or 0)/900*100))
    st.markdown(f'<div class="card"><div class="title">⏱️ RONDA EN VIVO</div><div class="grid"><div class="tile"><div class="tl">TIEMPO</div><div class="tv cyan">{format_countdown(seconds_left)}</div></div><div class="tile"><div class="tl">TARGET</div><div class="tv">{f"${target:,.2f}" if target is not None else "--"}</div></div></div><div class="barbg"><div class="bar" style="width:{pct}%"></div></div><div class="note">{ticker}</div></div>',unsafe_allow_html=True)

    trade=st.session_state.auto_paper_entries.get(ticker)
    if trade and trade.get("status")=="OPEN":
        d=trade["direction"];tc="#3ee6a4" if d=="UP" else "#ff6474";live_contract=get_yes_ask(market) if d=="UP" else get_no_ask(market)
        st.markdown(f'<div class="card"><div class="title">🤖 AUTO PAPER • OPERACIÓN ACTUAL</div><div class="trade" style="--tc:{tc}"><div class="trade-top"><div class="trade-dir">{d}</div><div class="pill">OPEN • ENTRADA FIJA</div></div><div class="lock-label">PRECIO DE COMPRA PAPER</div><div class="lock-price">${trade["entry_price"]:.2f}</div><div class="grid"><div class="tile"><div class="tl">NIVEL</div><div class="tv">${trade["amount"]}</div></div><div class="tile"><div class="tl">CONTRATOS</div><div class="tv">{trade["contracts"]}</div></div><div class="tile"><div class="tl">COSTO PAPER</div><div class="tv">${trade["paper_cost"]:.2f}</div></div><div class="tile"><div class="tl">CONTRATO AHORA</div><div class="tv">{f"${live_contract:.2f}" if live_contract is not None else "--"}</div></div></div><div class="note">Entrada {local_time(trade.get("entry_time"))} • Quedaban {format_countdown(trade.get("entry_seconds_left"))}</div></div></div>',unsafe_allow_html=True)
    else:
        st.markdown(card("🤖 AUTO PAPER",[("Estado","ENCENDIDO 🟢" if st.session_state.auto_paper_enabled else "APAGADO ⚪"),("Nivel actual",f'${st.session_state.auto_paper_amount}'),("Operación","ESPERANDO PRIMERA SEÑAL")],"WIN = mismo nivel • LOSS = siguiente nivel<br>$1 → $2 → $3 → $4 → $5 → $1<br>PAPER ONLY"),unsafe_allow_html=True)

    st.markdown(f'<div class="card"><div class="title">📊 PROBABILIDAD ESTIMADA</div><div class="grid"><div class="tile"><div class="tl">🚀 UP</div><div class="tv up">{sig["up_probability"]}%</div></div><div class="tile"><div class="tl">🔻 DOWN</div><div class="tv down">{sig["down_probability"]}%</div></div></div><div class="note">Estimación interna del motor • no representa certeza</div></div>',unsafe_allow_html=True)
    if rs["reversal"]:st.markdown(f'<div class="warn">⚠️ POSIBLE REVERSIÓN / REBOTE<br>{rs["reversal_text"]}</div>',unsafe_allow_html=True)
    dist=sig["distance"];dtxt="--" if dist is None else f'+${abs(dist):,.2f} ARRIBA' if dist>0 else f'-${abs(dist):,.2f} ABAJO' if dist<0 else "$0.00"
    st.markdown(card("🎯 RONDA ACTUAL",[("Ticker",ticker),("Target",f'${target:,.2f}' if target is not None else "NO DISPONIBLE"),("BTC actual",f'${sig["price"]:,.2f}'),("Fuente BTC",source),("Distancia",dtxt),("Tiempo restante",format_countdown(seconds_left))]),unsafe_allow_html=True)
    state=rs["round_state"]
    if state:
        ft=state["first_signal_time"].astimezone().strftime("%I:%M:%S %p") if state["first_signal_time"] else "--";fp=f'${state["first_signal_price"]:.2f}' if state["first_signal_price"] is not None else "--"
        st.markdown(card("⚡ SEÑAL DE ESTA RONDA",[("Primera señal",state["first_direction"] or "NINGUNA"),("Generada",ft),("Tiempo al aparecer",format_countdown(state["first_signal_seconds"])),("Kalshi al aparecer",fp),("Estado actual",state["active_direction"] or "ESPERANDO")]),unsafe_allow_html=True)
    cp=f'${rs["entry_price"]:.2f}' if rs["entry_price"] is not None else "--"
    st.markdown(card("💹 MERCADO AHORA",[("Precio contrato ahora",cp),("Calidad ahora",rs["entry_quality"])],"Este precio es LIVE y puede cambiar. La entrada PAPER queda fija arriba."),unsafe_allow_html=True)
    if market:st.markdown(card("🏛️ KALSHI • BTC 15 MIN",[("YES bid",kalshi_price(market.get("yes_bid_dollars"),market.get("yes_bid"))),("YES ask",kalshi_price(market.get("yes_ask_dollars"),market.get("yes_ask"))),("NO ask",kalshi_price(market.get("no_ask_dollars"),market.get("no_ask"))),("Último",kalshi_price(market.get("last_price_dollars"),market.get("last_price"))),("API Kalshi","CONECTADO 🟢" if kalshi_ok else "SIN MERCADO ⚠️")]),unsafe_allow_html=True)
    st.markdown(card("📈 ANÁLISIS TÉCNICO",[("EMA 9 / 21",sig["ema"]),("RSI 14",f'{sig["rsi"]:.1f}'),("Momentum 3m",f'{sig["mom3"]:+.3f}%'),("Momentum 5m",f'{sig["mom5"]:+.3f}%'),("Momentum 15m",f'{sig["mom15"]:+.3f}%'),("Volumen",f'{sig["vol_ratio"]:.2f}x')]),unsafe_allow_html=True)
    st.markdown(card("🧠 DECISIÓN DEL MOTOR",[("Señal",rs["signal"]),("Score técnico",f'{sig["technical_score"]:.2f}'),("Score target/tiempo",f'{sig["target_score"]:.2f}'),("Score combinado",f'{sig["final_score"]:.2f}')],"Cada ticker = una ronda independiente<br>No crea nuevas entradas en últimos 75 segundos<br>PAPER • NO órdenes reales"),unsafe_allow_html=True)

    hist=st.session_state.auto_paper_history;wins=sum(h.get("result")=="WIN" for h in hist);losses=sum(h.get("result")=="LOSS" for h in hist);pnl=sum(float(h.get("paper_pnl",0) or 0) for h in hist)
    hc="up" if pnl>0 else "down" if pnl<0 else "cyan"
    html=f'<div class="card"><div class="title">📋 HISTORIAL DE OPERACIONES</div><div class="grid"><div class="tile"><div class="tl">GANADAS</div><div class="tv up">{wins}</div></div><div class="tile"><div class="tl">PERDIDAS</div><div class="tv down">{losses}</div></div></div><div class="row"><span class="l">BALANCE PAPER</span><span class="r {hc}">${pnl:+.2f}</span></div>'
    if hist:
        for h in reversed(hist[-10:]):
            rc="up" if h.get("result")=="WIN" else "down";hp=float(h.get("paper_pnl",0) or 0);ep=float(h.get("entry_price",0) or 0);cost=float(h.get("paper_cost",0) or 0)
            html+=f'<div class="hist"><div class="histtop"><span class="{rc}">{h.get("result","--")} • {h.get("direction","--")}</span><span>${hp:+.2f}</span></div><div class="histmeta">{h.get("ticker","--")}<br>Nivel ${h.get("amount","--")} • Entrada ${ep:.2f} • {h.get("contracts","--")} contratos • Costo ${cost:.2f}<br>Resultado: {h.get("actual","--")} • Próximo nivel ${h.get("next_amount","--")}</div></div>'
    else:html+='<div class="note">Todavía no hay operaciones terminadas.</div>'
    st.markdown(html+"</div>",unsafe_allow_html=True)
    if target is None and kalshi_ok:st.warning("Kalshi conectado, pero sin target numérico. El bot no inventará uno.")
    if btc_error:st.error("Error Coinbase velas: "+btc_error)
    if kalshi_live_error and coinbase_live is not None:st.warning("Kalshi BTC live falló; usando Coinbase. "+kalshi_live_error)
    if kalshi_error:st.error("Error Kalshi: "+kalshi_error)

live_dashboard()
