import streamlit as st
from datetime import datetime

st.set_page_config(page_title='Alpha Visual', page_icon='₿', layout='centered', initial_sidebar_state='collapsed')

# VISUAL ONLY — NO SIGNAL ENGINE / NO KALSHI API / NO ORDER EXECUTION
if 'page' not in st.session_state: st.session_state.page='Bot'
if 'auto' not in st.session_state: st.session_state.auto=False
if 'cfg' not in st.session_state:
    st.session_state.cfg={
        'signal':'Motor pendiente (se agrega al final)', 'strategy':'Martingala personalizada',
        'amount_mode':'Manual','initial':0.50,'martingale':True,'limit':'Desactivado',
        'tp':'+90%','levels':4,'restart':False,'stopwin':False,'sound_on':True,'sound_trade':True,
        'dirs':['Contraria a la señal','Seguir señal','Seguir señal','Contraria a la señal']+['Seguir señal']*8
    }

st.markdown('''<style>
:root{--bg:#020706;--card:#07110e;--line:#17382e;--green:#22d789;--muted:#85958f;--white:#eef4f1;--red:#ff6670}
html,body,[data-testid="stAppViewContainer"],.stApp{background:var(--bg)!important;color:var(--white)!important}
[data-testid="stHeader"],#MainMenu,footer{display:none!important}.block-container{max-width:820px;padding:20px 22px 120px!important}
h1,h2,h3,p{margin-top:0}.muted{color:var(--muted)}.green{color:var(--green)}
.card{border:1px solid var(--line);border-radius:22px;background:linear-gradient(180deg,#07120f,#030908);padding:22px;margin:14px 0}
.row{display:flex;gap:18px;align-items:center;justify-content:space-between}.grow{flex:1}.big{font-size:42px;font-weight:800;letter-spacing:-1px}.label{font-size:13px;font-weight:800;color:var(--muted);letter-spacing:1px}.title{font-size:28px;font-weight:800}.section{font-size:21px;font-weight:850;letter-spacing:1px;margin:28px 0 12px}.btc{width:58px;height:58px;border-radius:50%;display:grid;place-items:center;background:#ff9418;color:#111;font-size:34px;font-weight:900}
.chart{height:330px;position:relative;margin:15px 0}.chart svg{width:100%;height:100%}.target{border-top:2px dotted #809087;position:absolute;left:2%;right:2%;bottom:27%}.live{position:absolute;right:3%;top:5%;color:#e8efec}.past{font-size:19px;letter-spacing:4px;color:var(--green)}
.trade{display:grid;grid-template-columns:1fr 1fr;gap:18px}.red{color:var(--red)}
.nav{position:fixed;z-index:999;bottom:0;left:0;right:0;background:#030807;border-top:1px solid #22302c;padding:8px max(10px,env(safe-area-inset-right)) calc(8px + env(safe-area-inset-bottom)) max(10px,env(safe-area-inset-left));display:grid;grid-template-columns:repeat(4,1fr);gap:4px}
.nav button{width:100%;min-height:58px;background:transparent;border:0;color:#7f8b87;font-weight:750;font-size:13px}.nav button.active{color:var(--green)}
.stButton>button{border-radius:14px;min-height:48px;font-weight:800}.stSelectbox div[data-baseweb="select"],.stNumberInput input,.stTextInput input,.stTextArea textarea{background:#070c0b!important;border-color:#303a37!important;color:white!important}
[data-testid="stMetricValue"]{color:var(--white)}
hr{border-color:#18221f!important}.warning{border:1px solid #67520c;border-radius:16px;padding:16px;color:#c7b875}.fakegraph{height:210px;border-bottom:4px solid var(--green);background:linear-gradient(180deg,transparent,#07301f);margin-top:20px}
@media(max-width:520px){.block-container{padding:12px 14px 105px!important}.big{font-size:31px}.trade{grid-template-columns:1fr 1fr}.card{padding:17px}.chart{height:290px}.nav button{font-size:11px}}
</style>''', unsafe_allow_html=True)

def nav():
    icons={'Bot':'⚙','Operaciones':'↗','Saldo':'▣','Ajustes':'⚙'}
    st.markdown('<div style="height:20px"></div>',unsafe_allow_html=True)
    cols=st.columns(4)
    for c,p in zip(cols,icons):
        with c:
            if st.button(f"{icons[p]}\n{p}",key='nav_'+p,use_container_width=True):
                st.session_state.page=p; st.rerun()

def bot():
    st.markdown('<div class="row"><div class="row"><div class="btc">₿</div><div><div class="label">BTC · 15 MIN</div><div class="title">BTC/USD ▾</div></div></div><div class="green"><b>● VISUAL</b></div></div>',unsafe_allow_html=True)
    st.markdown('''<div class="row" style="margin-top:42px"><div class="grow"><div class="label">TARGET</div><div class="big">$87,061.36</div><div class="muted"><b>Cierre 12:45 a. m.</b></div></div><div style="width:1px;height:100px;background:#34433e"></div><div class="grow"><div class="label green">CURRENT ↑</div><div class="big green">$87,262.58</div><div class="green"><b>+$201.22 (+0.231%)</b></div></div></div><div style="font-size:27px;font-weight:800;margin:25px 0">⌛ 08:05</div>''',unsafe_allow_html=True)
    st.markdown('''<div class="chart"><div class="live"><span class="green">●</span> En vivo</div><svg viewBox="0 0 700 330" preserveAspectRatio="none"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1fbf78" stop-opacity=".35"/><stop offset="1" stop-color="#1fbf78" stop-opacity="0"/></linearGradient></defs><path d="M10 270 C40 330,60 300,90 230 S130 230,155 185 S195 190,220 140 S250 150,280 95 S320 120,350 70 S390 115,420 55 S455 190,490 95 S530 130,560 85 S590 170,620 95 S650 80,680 35 L680 330 L10 330Z" fill="url(#g)"/><path d="M10 270 C40 330,60 300,90 230 S130 230,155 185 S195 190,220 140 S250 150,280 95 S320 120,350 70 S390 115,420 55 S455 190,490 95 S530 130,560 85 S590 170,620 95 S650 80,680 35" fill="none" stroke="#35cf8b" stroke-width="4"/></svg><div class="target"></div></div>''',unsafe_allow_html=True)
    st.markdown('<div class="label">PAST MARKETS &nbsp; <span class="past">▲ ▲ ▼ ▲ ▼ ▲ ▲ ▼ ▲ ▲</span></div>',unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="row"><div><div class="label green">AUTOMATIZACIÓN</div><div class="title">Trading Automático</div></div><div class="green"><b>'+('● ON' if st.session_state.auto else '○ OFF')+'</b></div></div><p class="muted" style="margin-top:12px">Visual solamente. Todavía no existe motor ni se envían operaciones.</p></div>',unsafe_allow_html=True)
    if st.button('APAGAR BOT' if st.session_state.auto else 'ENCENDER BOT',use_container_width=True,type='primary'):
        st.session_state.auto=not st.session_state.auto; st.rerun()

def operations():
    st.markdown('<div class="title">Operaciones</div><p class="muted">Vista visual del historial. Sin operaciones reales todavía.</p>',unsafe_allow_html=True)
    for t,d,a,r in [('12:30 → 12:45','UP','$0.50','WIN'),('12:15 → 12:30','DOWN','$1.00','LOSS'),('12:00 → 12:15','UP','$0.50','WIN')]:
        st.markdown(f'<div class="card row"><div><div class="label">{t}</div><b>{d}</b></div><div>{a}</div><b class="{"green" if r=="WIN" else "red"}">{r}</b></div>',unsafe_allow_html=True)

def balance():
    st.markdown('<div class="title">Saldo en Kalshi</div>',unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="label">SALDO DISPONIBLE</div><div class="big">$19.68</div><div class="green" style="font-size:24px;font-weight:800">+$0.00 (+0.00%) <span class="muted">Hoy</span></div><div class="fakegraph"></div></div><div class="warning"><b>⚠ ADVERTENCIA DE RIESGO</b><br>Los mercados de predicciones implican riesgo y pueden ocasionar pérdidas. Las ganancias no están aseguradas.</div>',unsafe_allow_html=True)

def settings():
    c=st.session_state.cfg
    st.markdown('<div class="title">Ajustes del bot</div><p class="muted">Configuración visual. El motor se agregará al final.</p>',unsafe_allow_html=True)
    st.markdown('<div class="section">INDICADORES</div>',unsafe_allow_html=True)
    c['signal']=st.selectbox('Generación de señal',['Motor pendiente (se agrega al final)'],index=0)
    st.markdown('<div class="section">SELECCIONAR ESTRATEGIA</div>',unsafe_allow_html=True)
    c['strategy']=st.selectbox('Administración de la operación',['Martingala personalizada','Monto fijo'])
    st.markdown('<div class="section">MONTO POR OPERACIÓN</div>',unsafe_allow_html=True)
    c['amount_mode']=st.selectbox('Cálculo del monto',['Manual','Automático'],index=['Manual','Automático'].index(c['amount_mode']))
    c['initial']=st.number_input('Monto inicial manual ($)',min_value=0.01,value=float(c['initial']),step=0.25)
    c['martingale']=st.toggle('Martingala',value=c['martingale'])
    c['limit']=st.selectbox('Precio de orden límite',['Desactivado','40¢','45¢','50¢'],index=['Desactivado','40¢','45¢','50¢'].index(c['limit']))
    c['tp']=st.selectbox('Tomar profit',['+50%','+75%','+90%','+100%'],index=['+50%','+75%','+90%','+100%'].index(c['tp']))
    c['levels']=st.selectbox('Máximo de niveles',list(range(1,13)),index=c['levels']-1)
    auto_amt=19.68*.90/sum(2**i for i in range(c['levels'])) if c['levels'] else 0
    st.markdown(f'<div class="card green"><b>Saldo disponible: $19.68</b> · Monto inicial automático (90% / {c["levels"]} niveles): <b>${auto_amt:.2f}</b></div>',unsafe_allow_html=True)
    st.markdown('<div class="section">ELIGE LA DIRECCIÓN</div><p class="muted">Configura cada nivel por separado.</p>',unsafe_allow_html=True)
    opts=['Seguir señal','Contraria a la señal','Solo UP','Solo DOWN']
    for i in range(c['levels']):
        amount=c['initial']*(2**i if c['martingale'] else 1)
        left,right=st.columns([1.25,1])
        with left: st.markdown(f'<div style="padding-top:10px"><b>{"Entrada inicial" if i==0 else f"Martingala {i}"}</b><div class="muted">Nivel {i+1} · ${amount:.2f}</div></div>',unsafe_allow_html=True)
        with right:
            current=c['dirs'][i] if c['dirs'][i] in opts else opts[0]
            c['dirs'][i]=st.selectbox('Dirección',opts,index=opts.index(current),key=f'dir{i}',label_visibility='collapsed')
        st.markdown('<hr>',unsafe_allow_html=True)
    st.markdown('<div class="section">CONTINUIDAD</div>',unsafe_allow_html=True)
    c['restart']=st.toggle('Reiniciar martingala',value=c['restart'])
    st.markdown('<div class="section">FINALIZACIÓN</div>',unsafe_allow_html=True)
    c['stopwin']=st.toggle('Apagar bot en la próxima operación ganadora',value=c['stopwin'])
    st.markdown('<div class="section">SONIDOS Y ALERTAS</div>',unsafe_allow_html=True)
    c['sound_on']=st.toggle('Sonido al encender el bot',value=c['sound_on'])
    c['sound_trade']=st.toggle('Sonido al abrir una operación',value=c['sound_trade'])
    st.markdown('<div class="section">CONEXIÓN KALSHI</div>',unsafe_allow_html=True)
    st.info('Visual solamente: todavía no se realiza ninguna conexión a Kalshi.')
    st.text_input('API Key ID',placeholder='Solo para conectar o reemplazar credenciales')
    st.text_area('Clave privada PEM',placeholder='Solo para conectar o reemplazar credenciales',height=130)
    a,b=st.columns(2)
    with a: st.button('Verificar y guardar',use_container_width=True,disabled=True,help='Se habilitará cuando agreguemos la conexión Kalshi.')
    with b: st.button('Eliminar credenciales',use_container_width=True,disabled=True)
    st.markdown('<div style="height:15px"></div>',unsafe_allow_html=True)
    if st.button('GUARDAR CAMBIOS VISUALES',use_container_width=True,type='primary'): st.success('Configuración guardada durante esta sesión.')

page=st.session_state.page
{'Bot':bot,'Operaciones':operations,'Saldo':balance,'Ajustes':settings}[page]()
nav()
