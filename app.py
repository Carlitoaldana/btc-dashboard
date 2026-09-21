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

def esc(v):
    import html
    return html.escape(str(v))

def rows_html(rows):
    return "".join(
        '<div class="kv"><span>'+esc(a)+'</span><b>'+str(b)+'</b></div>'
        for a,b in rows
    )

def box(title, rows):
    return '<section class="panel"><h3>'+title+'</h3>'+rows_html(rows)+'</section>'

def local_time(v):
    try:
        return datetime.fromisoformat(str(v).replace("Z","+00:00")).astimezone().strftime("%H:%M:%S")
    except Exception:
        return "--"

st.markdown("""
<style>
:root{--bg:#020b13;--card:#061827;--line:#16496b;--cyan:#26b9ff;--green:#21e5a1;--red:#ff5369;--amber:#ffc43d;--text:#f1f7ff;--muted:#7899ae}
#MainMenu,footer,header{visibility:hidden}
.stApp{background:radial-gradient(circle at 50% 0,#08263d 0,#03101c 36%,#020911 100%);color:var(--text)}
.block-container{max-width:1100px!important;padding:10px 10px 25px!important}
[data-testid="stToggle"]{margin:0 0 7px 0}
[data-testid="stToggle"] label p{font-weight:900!important;color:#e7f2fb!important}
.dash{font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.top{display:grid;grid-template-columns:1fr auto auto;gap:12px;align-items:center;background:linear-gradient(135deg,#071a2b,#061321);border:1px solid var(--line);border-radius:12px;padding:11px 14px;margin-bottom:8px}
.brand{display:flex;align-items:center;gap:10px}.logo{width:42px;height:42px;border-radius:8px;background:linear-gradient(145deg,#0875bd,#0a2742);display:grid;place-items:center;font-size:25px}
.brand h1{font-size:20px;margin:0;font-weight:950}.brand h1 i{font-style:normal;color:var(--cyan)}.sub{font-size:9px;color:#87a8bd;margin-top:2px}
.badge{border:1px solid #17845f;background:#062c25;color:#3de7a6;padding:7px 11px;border-radius:99px;font-size:9px;font-weight:950}.clock{font-size:9px;color:#9cb5c6;text-align:right}
.gtop{display:grid;grid-template-columns:1.55fr .65fr;gap:8px;margin-bottom:8px}
.g3{display:grid;grid-template-columns:1.2fr .82fr 1fr;gap:7px;margin-bottom:7px;align-items:start}
.g3b{display:grid;grid-template-columns:1fr .9fr 1fr;gap:7px;margin-bottom:7px;align-items:start}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-bottom:7px;align-items:start}
.panel{background:linear-gradient(145deg,#071a2a,#061421);border:1px solid var(--line);border-radius:10px;padding:9px 10px;min-width:0}
.panel h3{font-size:10px;color:var(--cyan);margin:0 0 5px;font-weight:950;letter-spacing:.7px}
.kv{display:flex;justify-content:space-between;gap:8px;padding:4px 0;border-bottom:1px solid #153b56;font-size:9px}.kv:last-child{border-bottom:0}.kv span{color:#8aa7bb}.kv b{color:#f2f7ff;text-align:right;overflow-wrap:anywhere}
.hero{border-color:var(--hero);box-shadow:inset 0 0 26px var(--glow);padding:14px}.heroflex{display:grid;grid-template-columns:1fr .55fr;gap:12px;align-items:center}.hero small{font-size:8px;color:#67e5b7;font-weight:900}.heroSignal{font-size:24px;font-weight:950;color:var(--hero);margin:6px 0 1px}.heroSub{font-size:10px;font-weight:900;color:var(--hero)}.heroPrice{border-left:1px solid #1b566b;padding-left:12px}.heroPrice label{font-size:8px;color:#58e3b2}.heroPrice strong{font-size:16px;display:block;margin-top:2px}.roundline{text-align:center;border-top:1px solid #16475f;margin-top:8px;padding-top:7px;font-size:8px;color:#8eb0c5}
.timer strong{font-size:26px}.progress{height:7px;border-radius:99px;background:#102c43;overflow:hidden;margin:7px 0}.progress i{display:block;height:100%;background:linear-gradient(90deg,#10aee9,#39d7a0)}
.pill{display:inline-block;font-size:8px;border-radius:99px;padding:4px 7px;background:#073729;color:#42e9aa;border:1px solid #1a8a66;font-weight:900}
.probs{display:grid;gap:6px}.prob{border-radius:7px;padding:9px;border:1px solid #155642;background:#08291f}.prob.red{border-color:#642234;background:#2b1019}.prob label{font-size:9px;font-weight:900}.prob strong{display:block;font-size:23px;margin-top:2px}
.up{color:var(--green)!important}.down{color:var(--red)!important}.cyan{color:var(--cyan)!important}.amber{color:var(--amber)!important}
.warn{margin-top:7px;background:#3a2b06;border:1px solid #b47a09;color:#ffd45b;border-radius:8px;padding:8px;font-size:8px;font-weight:900;line-height:1.4}
.fixed{border:1px solid var(--trade);border-radius:8px;padding:8px}.fixedPrice{font-size:23px;font-weight:950;color:var(--trade);margin:3px 0 7px}.miniGrid{display:grid;grid-template-columns:1fr 1fr;gap:6px}.mini{background:#081d2d;border:1px solid #164b6d;border-radius:7px;padding:7px}.mini label{display:block;color:#7798ae;font-size:7px;font-weight:900}.mini strong{display:block;font-size:14px;margin-top:3px}.tiny{font-size:7px;color:#7192a8;text-align:center;line-height:1.35;margin-top:4px}
.histSummary{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:7px}.histrow{display:grid;grid-template-columns:1.2fr .55fr .65fr .55fr .65fr;gap:6px;padding:6px;border-top:1px solid #153c57;font-size:8px}
.foot{display:flex;justify-content:space-between;gap:10px;align-items:center;background:#071929;border:1px solid #154665;border-radius:9px;padding:8px 11px;font-size:7px;color:#7899ae}
@media(max-width:760px){
 .block-container{padding:5px 4px 15px!important}
 .top{grid-template-columns:1fr auto;padding:7px;gap:5px;margin-bottom:5px}.clock{display:none}.logo{width:31px;height:31px;font-size:19px}.brand{gap:6px}.brand h1{font-size:13px}.sub{font-size:6px}.badge{font-size:6px;padding:5px 7px}
 .gtop{grid-template-columns:1.55fr .75fr;gap:4px;margin-bottom:4px}.g3{grid-template-columns:1.2fr .82fr 1fr;gap:4px;margin-bottom:4px}.g3b{grid-template-columns:1fr .9fr 1fr;gap:4px;margin-bottom:4px}.g2{grid-template-columns:1fr 1fr;gap:4px;margin-bottom:4px}
 .panel{padding:5px 6px;border-radius:7px}.panel h3{font-size:6.4px;margin-bottom:2px;letter-spacing:.25px}.kv{font-size:5.8px;padding:2.7px 0;gap:3px}
 .hero{padding:7px}.heroflex{gap:5px}.hero small{font-size:5.5px}.heroSignal{font-size:14px;margin:3px 0}.heroSub{font-size:6px}.heroPrice{padding-left:5px}.heroPrice label{font-size:5px}.heroPrice strong{font-size:9px}.roundline{font-size:5px;margin-top:4px;padding-top:3px}
 .timer strong{font-size:15px}.progress{height:4px;margin:4px 0}.pill{font-size:5px;padding:2px 4px}.prob{padding:5px}.prob label{font-size:5.5px}.prob strong{font-size:14px}.warn{font-size:5px;padding:5px;margin-top:4px}
 .fixed{padding:4px}.fixedPrice{font-size:14px;margin:2px 0 4px}.miniGrid{gap:3px}.mini{padding:3px 4px}.mini label{font-size:4.8px}.mini strong{font-size:8px}.tiny{font-size:4.8px;margin-top:2px;line-height:1.25}
 .histSummary{gap:3px}.histrow{font-size:5px;padding:3px;gap:2px}.foot{font-size:4.8px;padding:5px}
}
</style>
""", unsafe_allow_html=True)

def auto_toggle_changed():
    save_memory()

@st.fragment(run_every="2s")
def live_dashboard():
    btc_error = ""
    kalshi_error = ""
    kalshi_live_error = ""

    try:
        df = add_indicators(get_btc_data())
        btc_ok = True
    except Exception as e:
        btc_ok = False
        btc_error = str(e)
        df = None

    try:
        market = get_kalshi_btc_market()
        kalshi_ok = market is not None
    except Exception as e:
        market = None
        kalshi_ok = False
        kalshi_error = str(e)

    try:
        coinbase_live = get_btc_live_price()
    except Exception:
        coinbase_live = float(df.iloc[-1]["close"]) if btc_ok else None

    kalshi_live = None
    if market:
        try:
            kalshi_live = get_kalshi_live_btc(market)
        except Exception as e:
            kalshi_live_error = str(e)

    live_price = kalshi_live if kalshi_live is not None else coinbase_live
    source = "KALSHI LIVE 🟢" if kalshi_live is not None else ("COINBASE 🟡" if coinbase_live is not None else "SIN DATOS 🔴")
    ticker = market.get("ticker","--") if market else "--"
    target = get_target_from_market(market) if market else None
    seconds_left = get_seconds_remaining(market) if market else None

    if btc_ok:
        sig = build_signal(df,target,seconds_left,live_price)
    else:
        sig = {"price":live_price or 0,"rsi":50,"mom3":0,"mom5":0,"mom15":0,"vol_ratio":0,"ema":"SIN DATOS","technical_score":0,"target_score":0,"final_score":0,"distance":None,"up_probability":50,"down_probability":50}

    rs = process_round_signal(ticker,sig,market,seconds_left)
    auto_process(ticker,rs,target,seconds_left,live_price)

    state = rs["round_state"]
    trade = st.session_state.auto_paper_entries.get(ticker)
    pct = max(0,min(100,(seconds_left or 0)/900*100))
    hero = rs["color"]
    glow = "#0b5f3b44" if rs["decision"] == "POSIBLE UP" else "#6d1e3144"
    target_txt = f"${target:,.2f}" if target is not None else "--"
    dist = sig["distance"]
    if dist is None:
        dtxt = "--"
    elif dist > 0:
        dtxt = f'<span class="up">+${abs(dist):,.2f} ARRIBA</span>'
    elif dist < 0:
        dtxt = f'<span class="down">-${abs(dist):,.2f} ABAJO</span>'
    else:
        dtxt = "$0.00"

    nowtxt = datetime.now().astimezone().strftime("%d %b %Y<br>%H:%M:%S")

    st.markdown(
        '<div class="dash"><div class="top">'
        '<div class="brand"><div class="logo">⚡</div><div><h1>MACALY <i>+ ALPHA BOT</i> <span style="font-size:9px;color:#8dcfff">v4.6.2</span></h1>'
        '<div class="sub">BTC 15 MIN • PAPER ONLY • NO REAL ORDERS</div></div></div>'
        '<div class="badge">● EN LÍNEA</div><div class="clock">'+nowtxt+'</div></div></div>',
        unsafe_allow_html=True
    )

    st.toggle("🤖 AUTO PAPER", key="auto_paper_enabled", on_change=auto_toggle_changed)

    st.markdown(
        '<div class="dash gtop">'
        '<section class="panel hero" style="--hero:'+hero+';--glow:'+glow+'">'
        '<div class="heroflex"><div><small>SEÑAL ACTUAL</small><div class="heroSignal">'+rs["icon"]+' '+esc(rs["decision"])+'</div>'
        '<div class="heroSub">'+esc(rs["signal"])+'</div></div>'
        '<div class="heroPrice"><label>BTC ACTUAL</label><strong>$'+f'{sig["price"]:,.2f}'+'</strong>'
        '<span style="font-size:7px;color:#5ddca9">SCORE '+f'{sig["final_score"]:.2f}'+'</span></div></div>'
        '<div class="roundline">KALSHI 15 MIN • RONDA EN CURSO</div></section>'
        '<section class="panel timer"><h3>⏱️ TIEMPO RESTANTE</h3><strong>'+format_countdown(seconds_left)+'</strong>'
        '<div class="progress"><i style="width:'+str(pct)+'%"></i></div>'
        '<div class="tiny">RONDA: '+esc(ticker)+'<br>TARGET: '+target_txt+'</div></section></div>',
        unsafe_allow_html=True
    )

    if trade and trade.get("status") == "OPEN":
        d = trade["direction"]
        tc = "#21e6a1" if d == "UP" else "#ff5369"
        next_loss = auto_next_amount(trade["amount"],False)
        auto_rows = [
            ("Monto actual", f'${trade["amount"]}'),
            ("Siguiente monto (si pierde)", f'${next_loss}'),
            ("Ronda actual", f'<span style="color:{tc}">{d} • ${trade["amount"]} • ABIERTA</span>'),
            ("Precio de entrada (paper)", f'${trade["entry_price"]:.2f}'),
            ("Contratos", trade["contracts"])
        ]
        auto_body = '<div style="text-align:right"><span class="pill">● ENCENDIDO</span></div>'+rows_html(auto_rows)
    else:
        auto_body = '<div style="text-align:right"><span class="pill">● '+("ENCENDIDO" if st.session_state.auto_paper_enabled else "APAGADO")+'</span></div>'+rows_html([
            ("Monto actual",f'${st.session_state.auto_paper_amount}'),
            ("Ronda actual","ESPERANDO SEÑAL")
        ])
    auto_body += '<div class="tiny">WIN = mismo monto • LOSS = siguiente nivel<br>$1 → $2 → $3 → $4 → $5 → $1<br>PAPER: NO ENVÍA ÓRDENES REALES</div>'

    warn_html = ""
    if rs["reversal"]:
        warn_html = '<div class="warn">⚠️ POSIBLE REVERSIÓN / REBOTE<br>'+esc(rs["reversal_text"])+'</div>'

    round_rows = [
        ("Ticker",esc(ticker)),("Target",target_txt),("BTC actual",f'${sig["price"]:,.2f}'),
        ("Distancia",dtxt),("Tiempo restante",format_countdown(seconds_left)),("Fuente BTC",source)
    ]

    st.markdown(
        '<div class="dash g3">'
        '<section class="panel"><h3>🤖 AUTO PAPER</h3>'+auto_body+'</section>'
        '<section class="panel"><h3>🧠 PROBABILIDAD ESTIMADA</h3><div class="probs">'
        '<div class="prob"><label class="up">⬆ UP</label><strong class="up">'+str(sig["up_probability"])+'%</strong></div>'
        '<div class="prob red"><label class="down">⬇ DOWN</label><strong class="down">'+str(sig["down_probability"])+'%</strong></div>'
        '</div><div class="tiny">Estimación interna del motor<br>No representa certeza</div></section>'
        '<div><section class="panel"><h3>⏱ RONDA ACTUAL</h3>'+rows_html(round_rows)+'</section>'+warn_html+'</div></div>',
        unsafe_allow_html=True
    )

    if state:
        ft = state["first_signal_time"].astimezone().strftime("%H:%M:%S") if state["first_signal_time"] else "--"
        fp = f'${state["first_signal_price"]:.2f}' if state["first_signal_price"] is not None else "--"
        first_dir = state["first_direction"] or "--"
        dir_class = "up" if first_dir == "UP" else "down" if first_dir == "DOWN" else ""
        signal_rows = [
            ("Primera señal",f'<span class="{dir_class}">{first_dir}</span>'),
            ("Generada",ft),
            ("Tiempo restante al aparecer",format_countdown(state["first_signal_seconds"])),
            ("Precio de entrada (paper)",fp),
            ("Estado actual",state["active_direction"] or "--")
        ]
    else:
        signal_rows = [("Primera señal","--"),("Generada","--"),("Tiempo restante al aparecer","--"),("Precio de entrada (paper)","--"),("Estado actual","--")]

    if trade and trade.get("status") == "OPEN":
        d = trade["direction"]
        tc = "#21e6a1" if d == "UP" else "#ff5369"
        live_contract = get_yes_ask(market) if d == "UP" else get_no_ask(market)
        q,qc = entry_quality(live_contract,seconds_left)
        live_txt = f"${live_contract:.2f}" if live_contract is not None else "--"
        entry_body = (
            '<div class="fixed" style="--trade:'+tc+'"><div style="font-size:7px;color:#7d9eb4">ENTRADA FIJA PAPER • '+d+'</div>'
            '<div class="fixedPrice">$'+f'{trade["entry_price"]:.2f}'+'</div>'
            '<div class="miniGrid"><div class="mini"><label>CONTRATOS</label><strong>'+str(trade["contracts"])+'</strong></div>'
            '<div class="mini"><label>CONTRATO AHORA</label><strong>'+live_txt+'</strong></div></div>'
            '<div class="tiny">Entrada '+local_time(trade.get("entry_time"))+' • Quedaban '+format_countdown(trade.get("entry_seconds_left"))+
            '<br>Calidad ahora: <span style="color:'+qc+'">'+q+'</span></div></div>'
        )
    else:
        entry_body = '<div class="tiny">ESPERANDO ENTRADA PAPER<br>No se crean nuevas entradas en los últimos 75 segundos</div>'

    if market:
        kalshi_rows = [
            ("YES bid",kalshi_price(market.get("yes_bid_dollars"),market.get("yes_bid"))),
            ("YES ask",kalshi_price(market.get("yes_ask_dollars"),market.get("yes_ask"))),
            ("NO ask",kalshi_price(market.get("no_ask_dollars"),market.get("no_ask"))),
            ("Último",kalshi_price(market.get("last_price_dollars"),market.get("last_price"))),
            ("API Kalshi","CONECTADO 🟢" if kalshi_ok else "SIN MERCADO")
        ]
    else:
        kalshi_rows = [("API Kalshi","SIN MERCADO")]

    st.markdown(
        '<div class="dash g3b">'+
        box("🔀 SEÑAL DE ESTA RONDA",signal_rows)+
        '<section class="panel"><h3>🐎 ENTRADA ACTUAL</h3>'+entry_body+'</section>'+
        box("📊 KALSHI • BTC 15 MIN",kalshi_rows)+
        '</div>',
        unsafe_allow_html=True
    )

    tech_rows = [
        ("EMA 9 / 21",sig["ema"]),("RSI 14",f'{sig["rsi"]:.1f}'),
        ("Momentum 3m",f'<span class="{"up" if sig["mom3"]>=0 else "down"}">{sig["mom3"]:+.3f}%</span>'),
        ("Momentum 5m",f'<span class="{"up" if sig["mom5"]>=0 else "down"}">{sig["mom5"]:+.3f}%</span>'),
        ("Momentum 15m",f'<span class="{"up" if sig["mom15"]>=0 else "down"}">{sig["mom15"]:+.3f}%</span>'),
        ("Volumen",f'{sig["vol_ratio"]:.2f}x'),("BTC referencia",source)
    ]
    signal_class = "up" if rs["signal"] == "SEÑAL UP" else "down" if rs["signal"] == "SEÑAL DOWN" else "amber"
    motor_rows = [
        ("Señal",f'<span class="{signal_class}">{rs["signal"]}</span>'),
        ("Score técnico",f'{sig["technical_score"]:.2f}'),
        ("Score target/tiempo",f'{sig["target_score"]:.2f}'),
        ("Score combinado",f'{sig["final_score"]:.2f}')
    ]

    st.markdown(
        '<div class="dash g2">'+
        box("📈 ANÁLISIS TÉCNICO (1 MIN)",tech_rows)+
        '<section class="panel"><h3>⚙️ DECISIÓN DEL MOTOR</h3>'+rows_html(motor_rows)+
        '<div class="tiny">Cada ticker = una ronda independiente<br>Modo análisis / paper<br>No envía órdenes reales</div></section></div>',
        unsafe_allow_html=True
    )

    hist = st.session_state.auto_paper_history
    wins = sum(h.get("result")=="WIN" for h in hist)
    losses = sum(h.get("result")=="LOSS" for h in hist)
    pnl = sum(float(h.get("paper_pnl",0) or 0) for h in hist)
    history_rows = ""
    for h in reversed(hist[-8:]):
        result = h.get("result","--")
        rc = "up" if result == "WIN" else "down"
        history_rows += (
            '<div class="histrow"><span>'+esc(h.get("ticker","--"))+'</span><span>'+esc(h.get("direction","--"))+
            '</span><span>$'+f'{float(h.get("entry_price",0) or 0):.2f}'+'</span><span class="'+rc+'">'+result+
            '</span><span>$'+f'{float(h.get("paper_pnl",0) or 0):+.2f}'+'</span></div>'
        )
    if not history_rows:
        history_rows = '<div class="tiny">Todavía no hay operaciones terminadas.</div>'

    pnl_class = "up" if pnl >= 0 else "down"
    st.markdown(
        '<div class="dash"><section class="panel"><h3>📋 HISTORIAL DE OPERACIONES</h3>'
        '<div class="histSummary"><div class="mini"><label>GANADAS</label><strong class="up">'+str(wins)+'</strong></div>'
        '<div class="mini"><label>PERDIDAS</label><strong class="down">'+str(losses)+'</strong></div>'
        '<div class="mini"><label>BALANCE PAPER</label><strong class="'+pnl_class+'">$'+f'{pnl:+.2f}'+'</strong></div></div>'+
        history_rows+'</section></div>'
        '<div class="dash foot"><span>ⓘ MACALY + ALPHA BOT v4.6.2 • Herramienta de análisis en tiempo real • PAPER ONLY</span>'
        '<span>BTC 15 MIN • KALSHI</span></div>',
        unsafe_allow_html=True
    )

    if target is None and kalshi_ok:
        st.warning("Kalshi conectado, pero sin target numérico. El bot no inventará uno.")
    if btc_error:
        st.error("Error Coinbase velas: "+btc_error)
    if kalshi_live_error and coinbase_live is not None:
        st.warning("Kalshi BTC live falló; usando Coinbase. "+kalshi_live_error)
    if kalshi_error:
        st.error("Error Kalshi: "+kalshi_error)

live_dashboard()
