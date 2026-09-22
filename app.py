import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone

# =========================================================
# MACALY + ALPHA BOT v4.6.1 • MOBILE PRO UI
# BTC 15 MIN • SAME v4.6.1 SIGNAL ENGINE
# =========================================================

st.set_page_config(
    page_title="BTC Signal v4.6.1",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =========================================================
# CONFIGURACIÓN ORIGINAL
# =========================================================

NEW_ROUND_WAIT = 30
NEW_ENTRY_LOCK = 75

UP_THRESHOLD = 4.0
DOWN_THRESHOLD = -4.0

FLIP_UP_THRESHOLD = 4.75
FLIP_DOWN_THRESHOLD = -4.75
FLIP_CONFIRMATIONS = 2

# =========================================================
# DISEÑO MOBILE — BASADO EN LA REFERENCIA APROBADA
# =========================================================

st.markdown(
    """
<style>
#MainMenu, footer, header {visibility:hidden;}
[data-testid="stToolbar"] {display:none;}
[data-testid="stDecoration"] {display:none;}
[data-testid="stStatusWidget"] {display:none;}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background:
      radial-gradient(circle at 50% -12%, rgba(31,65,104,.24), transparent 30%),
      #070b11;
    color:#f4f7fb;
}

.block-container {
    max-width:410px !important;
    padding:8px 10px 24px !important;
}

div[data-testid="stVerticalBlock"] {gap:.55rem;}

.topbar {
    position:relative;
    min-height:45px;
    padding:3px 2px 4px;
    text-align:center;
}
.brand {
    color:#f8fafc;
    font-size:13px;
    line-height:1.05;
    font-weight:950;
    letter-spacing:.15px;
}
.version {
    color:#647184;
    font-size:7px;
    font-weight:800;
    margin-top:2px;
}
.live {
    position:absolute;
    right:3px;
    top:27px;
    display:flex;
    align-items:center;
    gap:5px;
    color:#91a0b3;
    font-size:7.5px;
    font-weight:800;
}
.live-dot {
    width:7px;
    height:7px;
    border-radius:50%;
    background:#2ee67b;
    box-shadow:0 0 10px rgba(46,230,123,.8);
}

.hero {
    text-align:center;
    padding:0 4px 8px;
}
.hero-signal {
    font-size:58px;
    line-height:.96;
    font-weight:1000;
    letter-spacing:-3px;
    text-shadow:0 0 28px var(--glow);
}
.hero-wait {
    font-size:31px;
    line-height:1.03;
    font-weight:1000;
    letter-spacing:-1.2px;
    color:#51bff3;
    text-shadow:0 0 22px rgba(56,189,248,.20);
}
.confidence {
    display:inline-block;
    margin-top:10px;
    padding:5px 12px;
    border-radius:7px;
    font-size:10px;
    font-weight:1000;
    letter-spacing:.4px;
    border:1px solid var(--accent);
    color:var(--accent);
    background:var(--soft);
}

.two {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:8px;
    margin-top:7px;
}
.mini {
    min-height:61px;
    background:linear-gradient(180deg,#101722,#0c121b);
    border:1px solid #1b2735;
    border-radius:10px;
    padding:8px 9px;
}
.mini-label {
    color:#69778a;
    font-size:8px;
    font-weight:900;
    letter-spacing:.8px;
    text-transform:uppercase;
    margin-bottom:5px;
}
.mini-value {
    color:#f4f7fb;
    font-size:18px;
    font-weight:950;
    letter-spacing:-.4px;
}
.mini-sub {
    color:#7e8b9e;
    font-size:9px;
    font-weight:800;
    margin-top:3px;
}
.green {color:#36e985;}
.red {color:#ff5363;}
.blue {color:#54c6f5;}
.amber {color:#f7bd4d;}

.section {
    background:linear-gradient(180deg,#0f1620,#0b1119);
    border:1px solid #1b2735;
    border-radius:11px;
    padding:11px;
    margin-top:8px;
}
.section-title {
    color:#8b98aa;
    font-size:9px;
    font-weight:1000;
    letter-spacing:.8px;
    text-transform:uppercase;
    margin-bottom:8px;
}
.prob-row {
    display:flex;
    align-items:center;
    gap:7px;
}
.prob-up, .prob-down {
    height:12px;
    border-radius:4px;
    min-width:2px;
}
.prob-up {
    background:linear-gradient(90deg,#1bcf6a,#53ef8d);
    box-shadow:0 0 10px rgba(46,230,123,.18);
}
.prob-down {
    background:linear-gradient(90deg,#ff3d50,#ff6876);
    box-shadow:0 0 10px rgba(255,76,91,.18);
}
.prob-labels {
    display:flex;
    justify-content:space-between;
    margin-top:7px;
    font-size:10px;
    font-weight:900;
}

.close-reader {
    border-radius:11px;
    padding:12px;
    margin-top:8px;
    border:1px solid var(--reader-border);
    background:var(--reader-bg);
    box-shadow:inset 0 0 25px rgba(0,0,0,.10);
}
.reader-top {
    display:flex;
    justify-content:space-between;
    align-items:center;
    color:#e9eef5;
    font-size:9px;
    font-weight:1000;
    letter-spacing:.7px;
}
.reader-active {
    padding:3px 7px;
    border-radius:8px;
    color:#57ee91;
    border:1px solid rgba(69,231,129,.55);
    background:rgba(28,153,78,.15);
    font-size:8px;
}
.reader-main {
    display:grid;
    grid-template-columns:1fr 70px;
    align-items:center;
    gap:8px;
    margin-top:12px;
}
.reader-text {
    color:#f6f8fb;
    font-size:15px;
    line-height:1.15;
    font-weight:1000;
}
.reader-note {
    color:#8390a2;
    font-size:8px;
    line-height:1.35;
    margin-top:6px;
}
.ring {
    --p:50;
    --ring:#36e985;
    width:66px;
    height:66px;
    border-radius:50%;
    display:grid;
    place-items:center;
    background:conic-gradient(var(--ring) calc(var(--p)*1%), #27313e 0);
    position:relative;
}
.ring:after {
    content:"";
    position:absolute;
    width:51px;
    height:51px;
    border-radius:50%;
    background:#0b1119;
}
.ring span {
    position:relative;
    z-index:1;
    color:#f7fafc;
    font-size:15px;
    font-weight:1000;
}

.tech-grid {
    display:grid;
    grid-template-columns:repeat(5,1fr);
    gap:3px;
    text-align:center;
}
.tech-label {
    color:#637084;
    font-size:6.5px;
    font-weight:900;
    letter-spacing:.25px;
    text-transform:uppercase;
}
.tech-value {
    color:#eef3f9;
    font-size:10px;
    font-weight:1000;
    margin-top:5px;
    overflow:hidden;
    white-space:nowrap;
}

.ticker {
    text-align:center;
    color:#4f5c6f;
    font-size:7.5px;
    font-weight:800;
    margin-top:8px;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}

.footer-nav {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    text-align:center;
    padding:10px 2px 1px;
    margin-top:7px;
    border-top:1px solid #182331;
}
.nav-item {
    color:#5f6c7e;
    font-size:8px;
    font-weight:800;
}
.nav-active {color:var(--accent);}

.alert {
    border-radius:10px;
    padding:10px;
    margin-top:8px;
    text-align:center;
    color:#ffd260;
    background:rgba(116,78,7,.18);
    border:1px solid rgba(247,189,77,.42);
    font-size:10px;
    font-weight:900;
}

/* ===== REFERENCE UI OVERRIDES ===== */
.block-container{
    max-width:390px !important;
    padding:5px 9px 20px !important;
}
.topbar{
    min-height:39px !important;
    padding:2px 1px 3px !important;
}
.brand{font-size:12px !important;}
.version{font-size:6.5px !important;color:#536174 !important;}
.live{top:23px !important;font-size:6.8px !important;}

.hero{padding:0 2px 5px !important;}
.hero-signal{
    font-size:55px !important;
    line-height:.90 !important;
    letter-spacing:-4px !important;
}
.confidence{
    margin-top:8px !important;
    padding:4px 9px !important;
    border-radius:6px !important;
    font-size:8px !important;
}

.two{
    gap:6px !important;
    margin-top:6px !important;
}
.mini{
    min-height:57px !important;
    padding:7px 8px !important;
    border-radius:8px !important;
    background:#0d141d !important;
    border-color:#172230 !important;
}
.mini-label{font-size:6.8px !important;margin-bottom:3px !important;}
.mini-value{font-size:15px !important;line-height:1.05 !important;}
.mini-sub{font-size:6.8px !important;margin-top:2px !important;}

.section{
    padding:8px !important;
    margin-top:6px !important;
    border-radius:8px !important;
    background:#0c131c !important;
    border-color:#172230 !important;
}
.section-title{
    font-size:7px !important;
    margin-bottom:6px !important;
}
.prob-row{gap:5px !important;}
.prob-up,.prob-down{height:15px !important;border-radius:3px !important;}
.prob-labels{margin-top:5px !important;font-size:7.5px !important;}

.close-reader{
    padding:9px !important;
    margin-top:6px !important;
    border-radius:8px !important;
}
.reader-top{font-size:7px !important;}
.reader-active{font-size:6px !important;padding:2px 5px !important;}
.reader-main{
    grid-template-columns:1fr 58px !important;
    margin-top:7px !important;
}
.reader-text{font-size:11px !important;line-height:1.08 !important;}
.reader-note{font-size:6.5px !important;margin-top:4px !important;}
.ring{width:54px !important;height:54px !important;}
.ring:after{width:42px !important;height:42px !important;}
.ring span{font-size:12px !important;}

.tech-grid{gap:0 !important;}
.tech-grid > div{
    padding:0 4px !important;
    border-right:1px solid #1c2734;
}
.tech-grid > div:last-child{border-right:none;}
.tech-label{font-size:5.8px !important;}
.tech-value{font-size:8.5px !important;margin-top:3px !important;}

.ref-features{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:4px;
    padding:8px 2px 6px;
    margin-top:6px;
    border-top:1px solid #182331;
}
.ref-feature{
    display:grid;
    grid-template-columns:22px 1fr;
    gap:5px;
    align-items:center;
    color:#66758a;
    font-size:5.6px;
    line-height:1.22;
}
.ref-feature-icon{
    width:20px;height:20px;border-radius:50%;
    display:grid;place-items:center;
    border:1px solid #28dd79;
    color:#34e982;
    font-size:10px;font-weight:1000;
}
.ref-feature strong{
    display:block;color:#cfd7e1;
    font-size:5.8px;margin-bottom:1px;
}
.ref-footer{
    display:flex;
    justify-content:space-between;
    gap:8px;
    padding:5px 1px 1px;
    border-top:1px solid #131d29;
    color:#435064;
    font-size:5.2px;
    font-weight:800;
}
.footer-nav{
    padding:7px 2px 1px !important;
    margin-top:4px !important;
}
.nav-item{font-size:6.8px !important;}


/* FINAL REFERENCE MATCH */
.block-container{max-width:430px!important;padding:7px 10px 22px!important}
.topbar{min-height:48px!important;padding:4px 2px 5px!important;text-align:center!important}
.brand{font-size:15px!important}.version{font-size:8px!important}
.live{top:29px!important;right:4px!important;font-size:8px!important}
.hero{padding:2px 2px 7px!important}
.hero-signal{font-size:72px!important;line-height:.86!important;letter-spacing:-5px!important;text-shadow:0 0 12px currentColor,0 0 28px currentColor!important}
.confidence{font-size:10px!important;padding:5px 16px!important;border-radius:18px!important;margin-top:9px!important}
.two{gap:7px!important;margin-top:7px!important}
.mini{min-height:72px!important;padding:9px 10px!important;border-radius:9px!important}
.mini-label{font-size:8px!important}.mini-value{font-size:19px!important}.mini-sub{font-size:8px!important}
.section{padding:9px!important;margin-top:7px!important;border-radius:9px!important}
.section-title{font-size:8px!important;margin-bottom:6px!important}
.prob-up,.prob-down{height:20px!important}.prob-labels{font-size:9px!important}
.close-reader{padding:10px 11px!important;margin-top:7px!important;border-radius:10px!important}
.reader-top{font-size:9px!important}.reader-active{font-size:7px!important}
.reader-main{grid-template-columns:1fr 68px!important;margin-top:8px!important}
.reader-text{font-size:15px!important;line-height:1.08!important}.reader-note{font-size:7.5px!important}
.ring{width:64px!important;height:64px!important}.ring:after{width:50px!important;height:50px!important}.ring span{font-size:15px!important}
.tech-label{font-size:6.5px!important}.tech-value{font-size:10px!important}
.footer-nav{padding:9px 2px 7px!important}.nav-item{font-size:8px!important}
.ref-features{padding:9px 3px 7px!important}.ref-feature{font-size:6px!important}
.ref-feature strong{font-size:6.2px!important}.ref-footer{font-size:5.6px!important}
.ref-icon{font-size:23px;line-height:1;margin-right:8px;display:inline-block;vertical-align:middle}
.ref-btc{color:#ff9f0a}.ref-target{color:#a9c9f3}
.ref-bars{display:inline-flex;gap:2px;align-items:flex-end;height:19px;margin-right:8px;vertical-align:middle}
.ref-bars i{display:block;width:5px;background:var(--accent);border-radius:1px}
.ref-bars i:nth-child(1){height:7px}.ref-bars i:nth-child(2){height:12px}.ref-bars i:nth-child(3){height:18px}
.ref-clock{font-size:23px;color:#b9d5f5;margin-right:8px;vertical-align:middle}
.ref-timebar{height:5px;background:#16324a;border-radius:5px;margin-top:5px;overflow:hidden}
.ref-timebar b{display:block;height:100%;width:58%;background:var(--accent);border-radius:5px}
.tech-head{display:flex;justify-content:space-between;align-items:center}
.tech-chevron{font-size:13px;color:#b6c6da}


/* ===== REBUILT REFERENCE FRONTEND ===== */
.block-container{max-width:430px!important;padding:4px 9px 18px!important}
.refapp{font-family:Arial,sans-serif;color:#eaf2fb}
.rhead{height:54px;position:relative;text-align:center;padding-top:7px}
.rtitle{font-size:15px;font-weight:900}.rver{font-size:9px;color:#9badc3;margin-top:2px}
.gear{position:absolute;right:9px;top:7px;font-size:19px;color:#a9c9ec}
.rlive{position:absolute;right:8px;bottom:1px;font-size:9px;color:#b9c9db}
.rlive i{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--accent);margin-right:5px;box-shadow:0 0 12px var(--accent)}
.rhero{text-align:center;padding:4px 0 8px}
.rsignal{display:flex;align-items:center;justify-content:center;color:var(--accent);font-size:72px;font-weight:1000;line-height:.82;letter-spacing:-5px;text-shadow:0 0 12px var(--glow),0 0 25px var(--glow)}
.rarrow{font-size:79px;margin-right:5px;line-height:.7}.rhero.waiting .rsignal{font-size:39px;letter-spacing:-2px}.rhero.waiting .rarrow{display:none}
.rconf{display:inline-block;margin-top:11px;border:1.5px solid var(--accent);border-radius:18px;padding:5px 17px;color:#fff;font-size:10px;font-weight:900;box-shadow:0 0 10px var(--soft)}
.rgrid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:2px}
.rcard{background:linear-gradient(180deg,#0d1823,#09131c);border:1px solid #203348;border-radius:8px}
.keycard{height:68px;padding:8px 9px;display:flex;align-items:center;gap:8px}
.bigicon{font-size:31px;font-weight:900;line-height:1}.btcicon{color:#ff9d00}.targeticon{color:#a9cff5}
.rlabel{font-size:8px;color:#b9c9dc;letter-spacing:.4px}.rvalue{font-size:19px;font-weight:900;line-height:1.05;margin-top:2px}.rdelta{font-size:9px;font-weight:900;margin-top:2px}
.green{color:#32e981!important}.red{color:#ff4c5d!important}
.bars{display:flex;align-items:flex-end;gap:3px;width:31px;height:30px}.bars b{width:7px;background:var(--accent);border-radius:2px}.bars b:nth-child(1){height:11px}.bars b:nth-child(2){height:20px}.bars b:nth-child(3){height:28px}
.clock{font-size:30px;color:#b9d8f7}.timecontent{flex:1}.timebar{height:6px;background:#16324a;border-radius:5px;margin-top:5px;overflow:hidden}.timebar b{display:block;height:100%;background:var(--accent);border-radius:5px}
.probs{margin-top:6px;padding:8px}.pbar{display:flex;gap:4px;margin-top:5px}.pup,.pdown{height:21px;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:900;border-radius:4px}.pup{background:linear-gradient(90deg,#10d76d,#54ed91);color:#06331d}.pdown{background:linear-gradient(90deg,#ff3548,#ff6472);color:#3d0710}.pleg{display:flex;justify-content:space-between;font-size:10px;font-weight:900;margin-top:6px}
.reader{margin-top:6px;border:1.5px solid var(--rb);background:var(--rbg);border-radius:9px;padding:9px 10px}
.readerhead{display:flex;align-items:center;gap:7px;font-size:9px;color:var(--rr)}.readerhead .pulse{font-size:18px}.readerhead em{margin-left:auto;border:1px solid #24d873;border-radius:12px;padding:3px 8px;font-style:normal;font-size:8px;color:#45ec8e}
.readerbody{display:grid;grid-template-columns:1fr 65px;align-items:center;margin-top:7px}.readerbody strong{display:block;font-size:15px;line-height:1.12}.readerbody small{display:block;color:#aab8c9;font-size:7px;margin-top:5px}
.rring{width:62px;height:62px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(var(--rr) calc(var(--p)*1%),#263342 0);position:relative}.rring:after{content:"";position:absolute;width:48px;height:48px;background:#08121b;border-radius:50%}.rring span{z-index:1;font-size:15px;font-weight:900}
.tech{margin-top:6px;padding:7px 8px}.techhead{display:flex;justify-content:space-between;font-size:9px;color:#c2d0df;padding-bottom:6px}.techrow{display:grid;grid-template-columns:repeat(5,1fr);border-top:1px solid #172737}.techrow>div{text-align:center;padding:7px 2px 2px;border-right:1px solid #172737}.techrow>div:last-child{border:0}.techrow small,.techrow i{display:block;font-size:6px;color:#8d9db0;font-style:normal}.techrow b{display:block;font-size:10px;margin:4px 0}
.rnav{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid #203448;border-bottom:1px solid #203448;margin-top:7px;padding:7px 0}.rnav div{text-align:center;color:#9db0c5;font-size:8px}.rnav b{display:block;font-size:17px;margin-bottom:2px}.rnav .active{color:var(--accent)}
.features{display:grid;grid-template-columns:repeat(3,1fr);gap:5px;padding:8px 1px}.features>div{display:flex;gap:5px;align-items:center}.features>div>b{width:25px;height:25px;border:1px solid #28e57f;border-radius:50%;display:grid;place-items:center;color:#35e986;font-size:13px}.features p{margin:0}.features strong{display:block;font-size:5.7px;color:#e1e8f0}.features span{display:block;font-size:5.4px;color:#8c9db0;margin-top:2px}
.refapp footer{border-top:1px solid #182a3a;padding:5px 1px;display:flex;justify-content:space-between;color:#708197;font-size:5.2px}
.ticker{text-align:center;color:#53667d;font-size:6px;margin-top:5px}


/* ===== FINAL PHONE REFERENCE PROPORTIONS ===== */
.block-container{max-width:365px!important;padding:3px 7px 14px!important}
.rhead{height:49px!important;padding-top:4px!important}
.rtitle{font-size:14px!important}.rver{font-size:8px!important}
.gear{right:7px!important;top:4px!important;font-size:18px!important}
.rlive{right:7px!important;bottom:0!important;font-size:8px!important}
.rhero{padding:1px 0 7px!important}
.rsignal{font-size:61px!important;line-height:.80!important;letter-spacing:-4px!important}
.rarrow{font-size:66px!important;margin-right:4px!important}
.rhero.waiting .rsignal{font-size:29px!important;letter-spacing:-1px!important}
.rconf{margin-top:9px!important;padding:4px 14px!important;font-size:9px!important}
.rgrid{gap:5px!important}
.keycard{height:57px!important;padding:6px 8px!important;gap:7px!important}
.bigicon{font-size:27px!important}.bars{width:27px!important;height:26px!important}.clock{font-size:27px!important}
.rlabel{font-size:7px!important}.rvalue{font-size:16px!important}.rdelta{font-size:8px!important}
.timebar{height:5px!important;margin-top:4px!important}
.probs{margin-top:5px!important;padding:7px!important}.pup,.pdown{height:18px!important;font-size:9px!important}
.pleg{font-size:9px!important;margin-top:5px!important}
.reader{margin-top:5px!important;padding:7px 8px!important}
.readerhead{font-size:8px!important}.readerhead .pulse{font-size:15px!important}
.readerbody{grid-template-columns:1fr 58px!important;margin-top:5px!important}
.readerbody strong{font-size:13px!important}.readerbody small{font-size:6.3px!important;margin-top:3px!important}
.rring{width:55px!important;height:55px!important}.rring:after{width:43px!important;height:43px!important}.rring span{font-size:13px!important}
.tech{margin-top:5px!important;padding:6px 7px!important}.techhead{font-size:8px!important;padding-bottom:5px!important}
.techrow>div{padding:5px 1px 1px!important}.techrow small,.techrow i{font-size:5.3px!important}.techrow b{font-size:9px!important;margin:3px 0!important}
.rnav{margin-top:6px!important;padding:6px 0!important}.rnav div{font-size:7px!important}.rnav b{font-size:15px!important}
.features{padding:7px 1px 5px!important;gap:3px!important}.features>div{gap:4px!important}
.features>div>b{width:22px!important;height:22px!important;font-size:11px!important}
.features strong{font-size:5px!important}.features span{font-size:4.8px!important}
.refapp footer{padding:4px 1px!important;font-size:4.7px!important}
.ticker{font-size:5.3px!important;margin-top:4px!important}

/* Make arrows chunky like the reference rather than thin text arrows */
.rarrow{font-family:Arial Black,Arial,sans-serif!important;font-weight:1000!important}


/* ===== TRUE FINAL: CSS ARROW + VISIBLE HEADER ===== */
.rhead{
    display:block!important;
    visibility:visible!important;
    height:58px!important;
    min-height:58px!important;
    padding-top:7px!important;
    overflow:visible!important;
    position:relative!important;
    z-index:20!important;
}
.rtitle,.rver,.gear,.rlive{display:block!important;visibility:visible!important}
.rtitle{font-size:14px!important;line-height:17px!important}
.rver{font-size:8px!important;line-height:11px!important}
.gear{top:7px!important;right:8px!important}
.rlive{bottom:3px!important;right:8px!important}

.rhero{padding-top:4px!important}
.rsignal{gap:9px!important}
.rarrow{display:none!important}

/* Solid arrow matching signal color; no iOS emoji rendering */
.cssarrow{
    position:relative;
    display:inline-block;
    width:42px;
    height:46px;
    background:var(--accent);
    border-radius:3px;
    box-shadow:0 0 12px var(--glow),0 0 24px var(--glow);
    flex:0 0 auto;
}
.cssarrow:before{
    content:"";
    position:absolute;
    left:-17px;
    top:-27px;
    width:0;height:0;
    border-left:38px solid transparent;
    border-right:38px solid transparent;
    border-bottom:34px solid var(--accent);
    filter:drop-shadow(0 0 7px var(--glow));
}
/* DOWN: arrow head below shaft */
.refapp.dir-down .cssarrow{transform:rotate(180deg);}
/* Waiting state: no arrow */
.rhero.waiting .cssarrow{display:none!important}

/* Keep final phone proportions compact */
.block-container{max-width:365px!important;padding-top:3px!important}
.rgrid{margin-top:1px!important}
.reader{min-height:0!important}

</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# SESSION STATE ORIGINAL
# =========================================================

if "rounds" not in st.session_state:
    st.session_state.rounds = {}

if "active_ticker" not in st.session_state:
    st.session_state.active_ticker = None

if "micro_prices" not in st.session_state:
    st.session_state.micro_prices = []

if "micro_ticker" not in st.session_state:
    st.session_state.micro_ticker = None


def new_round_state(ticker, seconds_left):
    now = datetime.now(timezone.utc)
    return {
        "ticker": ticker,
        "detected_at": now,
        "detected_seconds_left": seconds_left,
        "first_direction": None,
        "first_signal_time": None,
        "first_signal_seconds": None,
        "first_signal_price": None,
        "active_direction": None,
        "active_since": None,
        "last_score": 0.0,
        "previous_score": 0.0,
        "opposite_count": 0,
        "last_live_price": None,
        "previous_live_price": None,
        "reversal_warning": False,
        "reversal_text": "",
    }


# =========================================================
# COINBASE — VELAS ORIGINALES DE 1 MINUTO
# =========================================================

@st.cache_data(ttl=5)
def get_btc_data():
    response = requests.get(
        "https://api.exchange.coinbase.com/products/BTC-USD/candles",
        params={"granularity": 60},
        headers={"User-Agent": "MacalyAlphaBot/4.6.1"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list) or len(data) < 30:
        raise ValueError("Coinbase no devolvió suficientes datos.")

    df = pd.DataFrame(
        data, columns=["time", "low", "high", "open", "close", "volume"]
    )

    for column in ["low", "high", "open", "close", "volume"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df.dropna().sort_values("time").reset_index(drop=True)


def get_btc_live_price():
    response = requests.get(
        "https://api.exchange.coinbase.com/products/BTC-USD/ticker",
        headers={
            "User-Agent": "MacalyAlphaBot/4.6.1",
            "Cache-Control": "no-cache",
        },
        params={"_": int(datetime.now(timezone.utc).timestamp())},
        timeout=6,
    )
    response.raise_for_status()
    price = response.json().get("price")
    if price in [None, ""]:
        raise ValueError("Coinbase ticker no devolvió precio.")
    return float(price)


# =========================================================
# KALSHI BTC 15 MIN
# =========================================================

@st.cache_data(ttl=2)
def get_kalshi_btc_market():
    response = requests.get(
        "https://external-api.kalshi.com/trade-api/v2/markets",
        params={
            "limit": 100,
            "status": "open",
            "series_ticker": "KXBTC15M",
        },
        headers={"User-Agent": "MacalyAlphaBot/4.6.1"},
        timeout=10,
    )
    response.raise_for_status()
    markets = response.json().get("markets", [])
    if not markets:
        return None
    markets.sort(key=lambda m: str(m.get("close_time") or "9999"))
    return markets[0]


def get_event_ticker_from_market(market):
    if not market:
        return None
    event_ticker = market.get("event_ticker")
    if event_ticker:
        return str(event_ticker)
    ticker = market.get("ticker")
    if not ticker:
        return None
    parts = str(ticker).split("-")
    return "-".join(parts[:-1]) if len(parts) >= 2 else None


def extract_kalshi_btc_price(data):
    if not isinstance(data, dict):
        return None

    live_data = data.get("live_data", data)
    details = live_data.get("details", {}) if isinstance(live_data, dict) else {}
    candidates = []

    preferred_keys = {
        "price", "value", "index_value", "indexvalue",
        "current_price", "currentprice", "current_value", "currentvalue",
        "last_price", "lastprice", "close",
    }

    def walk_preferred(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                normalized_key = str(key).lower().replace("-", "_")
                if normalized_key in preferred_keys:
                    try:
                        number = float(value)
                        if 10000 < number < 1000000:
                            candidates.append(number)
                    except (TypeError, ValueError):
                        pass
                walk_preferred(value)
        elif isinstance(obj, list):
            for item in obj:
                walk_preferred(item)

    walk_preferred(details)
    if candidates:
        return float(candidates[-1])

    pair_candidates = []

    def walk_pairs(obj):
        if isinstance(obj, list):
            if len(obj) >= 2:
                try:
                    possible_price = float(obj[-1])
                    if 10000 < possible_price < 1000000:
                        pair_candidates.append(possible_price)
                except (TypeError, ValueError):
                    pass
            for item in obj:
                walk_pairs(item)
        elif isinstance(obj, dict):
            for value in obj.values():
                walk_pairs(value)

    walk_pairs(details)
    return float(pair_candidates[-1]) if pair_candidates else None


def get_kalshi_live_btc(market):
    event_ticker = get_event_ticker_from_market(market)
    if not event_ticker:
        raise ValueError("La ronda no entregó event_ticker.")

    response = requests.get(
        "https://external-api.kalshi.com/trade-api/v2/live_data/events/"
        f"{event_ticker}",
        params={
            "range": "15min",
            "_": int(datetime.now(timezone.utc).timestamp()),
        },
        headers={
            "User-Agent": "MacalyAlphaBot/4.6.1",
            "Cache-Control": "no-cache",
        },
        timeout=6,
    )
    response.raise_for_status()
    price = extract_kalshi_btc_price(response.json())
    if price is None:
        raise ValueError("Kalshi live respondió sin precio BTC válido.")
    return float(price)


# =========================================================
# INDICADORES ORIGINALES
# =========================================================

def add_indicators(df):
    df = df.copy()
    close = df["close"]

    df["ema9"] = close.ewm(span=9, adjust=False).mean()
    df["ema21"] = close.ewm(span=21, adjust=False).mean()

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / 14, adjust=False, min_periods=14
    ).mean()
    avg_loss = loss.ewm(
        alpha=1 / 14, adjust=False, min_periods=14
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"] = (100 - (100 / (1 + rs))).fillna(50)

    df["mom3"] = close.pct_change(3) * 100
    df["mom5"] = close.pct_change(5) * 100
    df["mom15"] = close.pct_change(15) * 100

    avg_volume = df["volume"].rolling(20).mean()
    df["vol_ratio"] = df["volume"] / avg_volume.replace(0, np.nan)
    return df


def get_target_from_market(market):
    if not market:
        return None

    for key in ("floor_strike", "cap_strike"):
        value = market.get(key)
        if value not in [None, ""]:
            try:
                number = float(value)
                if number > 1000:
                    return number
            except Exception:
                pass
    return None


def get_seconds_remaining(market):
    if not market or not market.get("close_time"):
        return None
    try:
        close_dt = datetime.fromisoformat(
            str(market["close_time"]).replace("Z", "+00:00")
        )
        seconds = int(
            (close_dt - datetime.now(timezone.utc)).total_seconds()
        )
        return max(0, seconds)
    except Exception:
        return None


def format_countdown(seconds):
    if seconds is None:
        return "--:--"
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def numeric_kalshi_price(dollar_value, cent_value):
    if dollar_value not in [None, ""]:
        try:
            return float(dollar_value)
        except Exception:
            pass
    if cent_value not in [None, ""]:
        try:
            return float(cent_value) / 100
        except Exception:
            pass
    return None


def get_yes_ask(market):
    if not market:
        return None
    return numeric_kalshi_price(
        market.get("yes_ask_dollars"), market.get("yes_ask")
    )


def get_no_ask(market):
    if not market:
        return None

    direct = numeric_kalshi_price(
        market.get("no_ask_dollars"), market.get("no_ask")
    )
    if direct is not None:
        return direct

    yes_bid = numeric_kalshi_price(
        market.get("yes_bid_dollars"), market.get("yes_bid")
    )
    if yes_bid is not None:
        return max(0.0, min(1.0, 1.0 - yes_bid))
    return None


# =========================================================
# PROBABILIDAD ORIGINAL
# =========================================================

def estimated_probabilities(
    final_score, distance, seconds_left, mom3, mom5
):
    score = float(np.clip(final_score, -10, 10))
    up_prob = 50 + score * 4.2

    if mom3 > 0.04:
        up_prob += 3
    elif mom3 < -0.04:
        up_prob -= 3

    if mom5 > 0.06:
        up_prob += 2
    elif mom5 < -0.06:
        up_prob -= 2

    if (
        distance is not None
        and seconds_left is not None
        and seconds_left <= 180
    ):
        if distance > 0:
            up_prob += 3
        elif distance < 0:
            up_prob -= 3

    up_prob = float(np.clip(up_prob, 5, 95))
    return round(up_prob), round(100 - up_prob)


# =========================================================
# MOTOR ORIGINAL v4.6.1
# =========================================================

def build_signal(df, target, seconds_left, live_price=None):
    last = df.iloc[-1]
    candle_price = float(last["close"])
    price = float(live_price) if live_price is not None else candle_price

    rsi = float(last["rsi"])
    mom3 = float(last["mom3"]) if pd.notna(last["mom3"]) else 0.0
    mom5 = float(last["mom5"]) if pd.notna(last["mom5"]) else 0.0
    mom15 = float(last["mom15"]) if pd.notna(last["mom15"]) else 0.0
    vol_ratio = (
        float(last["vol_ratio"]) if pd.notna(last["vol_ratio"]) else 0.0
    )

    technical_score = 0.0

    if last["ema9"] > last["ema21"]:
        technical_score += 2.0
        ema_text = "BULL"
    else:
        technical_score -= 2.0
        ema_text = "BEAR"

    if rsi >= 55:
        technical_score += 1.0
    elif rsi <= 45:
        technical_score -= 1.0

    if mom3 > 0.02:
        technical_score += 1.25
    elif mom3 < -0.02:
        technical_score -= 1.25

    if mom5 > 0.03:
        technical_score += 1.0
    elif mom5 < -0.03:
        technical_score -= 1.0

    if mom15 > 0.05:
        technical_score += 0.75
    elif mom15 < -0.05:
        technical_score -= 0.75

    if vol_ratio > 1.20:
        if mom3 > 0:
            technical_score += 0.50
        elif mom3 < 0:
            technical_score -= 0.50

    distance = None
    distance_pct = None
    target_score = 0.0

    if target is not None:
        distance = price - target
        distance_pct = distance / target * 100

        if distance > 0:
            target_score += 2.0
        elif distance < 0:
            target_score -= 2.0

        if seconds_left is not None:
            abs_distance = abs(distance)

            if seconds_left <= 30:
                target_score += 4.0 if distance > 0 else -4.0 if distance < 0 else 0
            elif seconds_left <= 60:
                target_score += 3.0 if distance > 0 else -3.0 if distance < 0 else 0
            elif seconds_left <= 180:
                target_score += 2.0 if distance > 0 else -2.0 if distance < 0 else 0
            elif seconds_left <= 300:
                target_score += 1.0 if distance > 0 else -1.0 if distance < 0 else 0

            if abs_distance < 10:
                target_score *= 0.60
            elif abs_distance < 20:
                target_score *= 0.80

    final_score = technical_score + target_score

    if mom3 > 0.02:
        momentum = "ALCISTA"
    elif mom3 < -0.02:
        momentum = "BAJISTA"
    else:
        momentum = "NEUTRAL"

    up_probability, down_probability = estimated_probabilities(
        final_score, distance, seconds_left, mom3, mom5
    )

    return {
        "price": price,
        "candle_price": candle_price,
        "rsi": rsi,
        "mom3": mom3,
        "mom5": mom5,
        "mom15": mom15,
        "vol_ratio": vol_ratio,
        "ema": ema_text,
        "technical_score": technical_score,
        "target_score": target_score,
        "final_score": final_score,
        "distance": distance,
        "distance_pct": distance_pct,
        "momentum": momentum,
        "up_probability": up_probability,
        "down_probability": down_probability,
    }


def entry_quality(price, seconds_left):
    if price is None:
        return "PRECIO NO DISPONIBLE", "#94a3b8"
    if seconds_left is not None and seconds_left <= NEW_ENTRY_LOCK:
        return "TARDE", "#fb7185"
    if price <= 0.60:
        return "BUENA", "#34d399"
    if price <= 0.70:
        return "PRECAUCIÓN", "#fbbf24"
    return "CARA / TARDE", "#fb7185"


# =========================================================
# CONTROL DE RONDA ORIGINAL
# =========================================================

def process_round_signal(ticker, sig, market, seconds_left):
    now = datetime.now(timezone.utc)

    if (
        ticker
        and ticker != "--"
        and st.session_state.active_ticker != ticker
    ):
        st.session_state.active_ticker = ticker
        st.session_state.rounds[ticker] = new_round_state(
            ticker, seconds_left
        )

    if not ticker or ticker == "--":
        return {
            "decision": "NO TRADE",
            "signal": "SIN RONDA",
            "icon": "•",
            "color": "#fbbf24",
            "round_state": None,
            "reversal": False,
            "reversal_text": "",
            "entry_price": None,
            "entry_quality": "SIN DATOS",
            "entry_quality_color": "#94a3b8",
        }

    if ticker not in st.session_state.rounds:
        st.session_state.rounds[ticker] = new_round_state(
            ticker, seconds_left
        )

    state = st.session_state.rounds[ticker]
    age = (now - state["detected_at"]).total_seconds()
    score = sig["final_score"]

    previous_live_price = state["last_live_price"]
    state["previous_live_price"] = previous_live_price
    state["last_live_price"] = sig["price"]

    price_change = (
        sig["price"] - previous_live_price
        if previous_live_price is not None
        else 0.0
    )

    previous_score = state["last_score"]
    state["previous_score"] = previous_score
    score_change = score - previous_score
    state["last_score"] = score

    if age < NEW_ROUND_WAIT:
        state["reversal_warning"] = False
        state["reversal_text"] = ""
        return {
            "decision": "ANALIZANDO NUEVA RONDA",
            "signal": "ESPERANDO CONFIRMACIÓN",
            "icon": "⌛",
            "color": "#38bdf8",
            "round_state": state,
            "reversal": False,
            "reversal_text": "",
            "entry_price": None,
            "entry_quality": "ESPERANDO",
            "entry_quality_color": "#38bdf8",
        }

    lock_new_entries = (
        seconds_left is not None and seconds_left <= NEW_ENTRY_LOCK
    )

    candidate = None
    if score >= UP_THRESHOLD:
        candidate = "UP"
    elif score <= DOWN_THRESHOLD:
        candidate = "DOWN"

    if (
        state["active_direction"] is None
        and candidate is not None
        and not lock_new_entries
    ):
        direction_price = (
            get_yes_ask(market)
            if candidate == "UP"
            else get_no_ask(market)
        )

        state["active_direction"] = candidate
        state["active_since"] = now
        state["first_direction"] = candidate
        state["first_signal_time"] = now
        state["first_signal_seconds"] = seconds_left
        state["first_signal_price"] = direction_price
        state["opposite_count"] = 0

    active = state["active_direction"]
    reversal = False
    reversal_text = ""

    if active == "UP":
        weakness_points = 0

        if score < 3:
            weakness_points += 1
        if score_change <= -1.25:
            weakness_points += 1
        if sig["mom3"] < -0.02:
            weakness_points += 1
        if sig["mom5"] < 0:
            weakness_points += 1
        if price_change < -8:
            weakness_points += 1
        if (
            sig["distance"] is not None
            and seconds_left is not None
            and seconds_left <= 180
            and sig["distance"] < 25
            and price_change < 0
        ):
            weakness_points += 1

        if weakness_points >= 2:
            reversal = True
            reversal_text = "UP PERDIENDO FUERZA • POSIBLE REVERSIÓN A DOWN"

    elif active == "DOWN":
        weakness_points = 0

        if score > -3:
            weakness_points += 1
        if score_change >= 1.25:
            weakness_points += 1
        if sig["mom3"] > 0.02:
            weakness_points += 1
        if sig["mom5"] > 0:
            weakness_points += 1
        if price_change > 8:
            weakness_points += 1
        if (
            sig["distance"] is not None
            and seconds_left is not None
            and seconds_left <= 180
            and sig["distance"] > -25
            and price_change > 0
        ):
            weakness_points += 1

        if weakness_points >= 2:
            reversal = True
            reversal_text = "DOWN PERDIENDO FUERZA • POSIBLE REBOTE A UP"

    state["reversal_warning"] = reversal
    state["reversal_text"] = reversal_text

    if active == "UP":
        if score <= FLIP_DOWN_THRESHOLD and sig["mom3"] < 0:
            state["opposite_count"] += 1
        else:
            state["opposite_count"] = 0

        if state["opposite_count"] >= FLIP_CONFIRMATIONS:
            if not lock_new_entries:
                state["active_direction"] = "DOWN"
                state["active_since"] = now
            state["opposite_count"] = 0

    elif active == "DOWN":
        if score >= FLIP_UP_THRESHOLD and sig["mom3"] > 0:
            state["opposite_count"] += 1
        else:
            state["opposite_count"] = 0

        if state["opposite_count"] >= FLIP_CONFIRMATIONS:
            if not lock_new_entries:
                state["active_direction"] = "UP"
                state["active_since"] = now
            state["opposite_count"] = 0

    active = state["active_direction"]

    if active == "UP":
        decision = "UP"
        signal = "SEÑAL UP"
        icon = "⬆"
        color = "#34e982"
        current_entry_price = get_yes_ask(market)
    elif active == "DOWN":
        decision = "DOWN"
        signal = "SEÑAL DOWN"
        icon = "⬇"
        color = "#ff4e5f"
        current_entry_price = get_no_ask(market)
    else:
        current_entry_price = None
        if lock_new_entries:
            decision = "NO NUEVA ENTRADA"
            signal = "FINAL DE RONDA"
            icon = "⏱"
            color = "#fbbf24"
        else:
            decision = "ESPERANDO"
            signal = "ESPERAR"
            icon = "•"
            color = "#38bdf8"

    quality, quality_color = entry_quality(
        current_entry_price, seconds_left
    )

    return {
        "decision": decision,
        "signal": signal,
        "icon": icon,
        "color": color,
        "round_state": state,
        "reversal": reversal,
        "reversal_text": reversal_text,
        "entry_price": current_entry_price,
        "entry_quality": quality,
        "entry_quality_color": quality_color,
    }


# =========================================================
# LECTOR DE CIERRE PRO — MICRO LECTURA ~2 SEGUNDOS
# Mantiene intacto el motor v4.6.1 y sus señales.
# No inventa velas REST de 1 segundo: construye una cinta
# de muestras del BTC live que ya recibe el dashboard.
# =========================================================

def update_micro_tape(ticker, live_price):
    if not ticker or ticker == "--" or live_price is None:
        return

    # Cada ronda empieza con su propia cinta.
    if st.session_state.micro_ticker != ticker:
        st.session_state.micro_ticker = ticker
        st.session_state.micro_prices = []

    now_ts = datetime.now(timezone.utc).timestamp()
    tape = st.session_state.micro_prices

    # Evita duplicar muestras dentro del mismo refresco.
    if not tape or now_ts - tape[-1]["t"] >= 1.0:
        tape.append({"t": now_ts, "p": float(live_price)})

    # Conserva aproximadamente los últimos 90 segundos.
    cutoff = now_ts - 90
    st.session_state.micro_prices = [
        x for x in tape if x["t"] >= cutoff
    ]


def micro_reading():
    tape = st.session_state.micro_prices

    if len(tape) < 4:
        return {
            "ready": False,
            "change_10s": 0.0,
            "change_30s": 0.0,
            "slope": 0.0,
            "up_ratio": 0.5,
            "pressure": "NEUTRAL",
        }

    now_t = tape[-1]["t"]
    current = tape[-1]["p"]

    def price_ago(seconds):
        target_t = now_t - seconds
        candidates = [x for x in tape if x["t"] <= target_t]
        if candidates:
            return candidates[-1]["p"]
        return tape[0]["p"]

    p10 = price_ago(10)
    p30 = price_ago(30)

    changes = [
        tape[i]["p"] - tape[i - 1]["p"]
        for i in range(1, len(tape))
    ]
    nonzero = [x for x in changes if x != 0]
    up_ratio = (
        sum(1 for x in nonzero if x > 0) / len(nonzero)
        if nonzero else 0.5
    )

    # Regresión simple precio/tiempo para medir dirección micro.
    xs = np.array([x["t"] - tape[0]["t"] for x in tape], dtype=float)
    ys = np.array([x["p"] for x in tape], dtype=float)
    slope = float(np.polyfit(xs, ys, 1)[0]) if len(xs) >= 3 and xs[-1] > 0 else 0.0

    c10 = current - p10
    c30 = current - p30

    if slope > 0.35 and up_ratio >= 0.58:
        pressure = "ALCISTA"
    elif slope < -0.35 and up_ratio <= 0.42:
        pressure = "BAJISTA"
    else:
        pressure = "NEUTRAL"

    return {
        "ready": True,
        "change_10s": c10,
        "change_30s": c30,
        "slope": slope,
        "up_ratio": up_ratio,
        "pressure": pressure,
    }


def closing_reader(sig, round_signal, seconds_left, micro):
    """
    Lector independiente de cierre.
    - La señal principal v4.6.1 NO se modifica.
    - En los últimos segundos, tiempo + distancia al target dominan sobre
      una pequeña contradicción de momentum/microlectura.
    - Nunca llama "confirmado" a un resultado antes del cierre.
    """
    state = round_signal.get("round_state")
    active_direction = state.get("active_direction") if state else None

    if active_direction not in ("UP", "DOWN"):
        return {
            "percent": 50,
            "headline": "ESPERANDO SEÑAL",
            "note": "El motor todavía no confirmó una dirección.",
            "micro": "MICROLECTURA PREPARÁNDOSE",
            "color": "#38bdf8",
            "border": "rgba(56,189,248,.45)",
            "bg": "linear-gradient(135deg,rgba(11,64,91,.30),rgba(9,23,34,.72))",
        }

    distance = sig.get("distance")
    close_direction = active_direction
    terminal_override = False
    terminal_too_close = False

    # En cierre extremo, la posición REAL respecto al target manda.
    # Umbrales deliberadamente conservadores para no llamar un flip por $2-$10.
    if seconds_left is not None and distance is not None:
        abs_d = abs(distance)
        market_side = "UP" if distance > 0 else "DOWN"

        if seconds_left <= 15:
            strong_distance = abs_d >= 30
            too_close = abs_d < 15
        elif seconds_left <= 30:
            strong_distance = abs_d >= 45
            too_close = abs_d < 20
        elif seconds_left <= 60:
            strong_distance = abs_d >= 70
            too_close = abs_d < 25
        else:
            strong_distance = False
            too_close = False

        if strong_distance:
            close_direction = market_side
            terminal_override = True
        elif too_close and seconds_left <= 30:
            terminal_too_close = True

    direction = close_direction
    base = sig["up_probability"] if direction == "UP" else sig["down_probability"]
    confidence = float(base)

    if distance is not None:
        aligned = distance > 0 if direction == "UP" else distance < 0
        confidence += 6 if aligned else -9

    aligned_momentum = sig["mom3"] > 0 if direction == "UP" else sig["mom3"] < 0
    confidence += 3 if aligned_momentum else -5

    if round_signal.get("reversal") and not terminal_override:
        confidence -= 12

    micro_text = "MICROLECTURA REUNIENDO DATOS"
    strong_contradiction = False

    if micro.get("ready"):
        wanted = 1 if direction == "UP" else -1
        c10 = micro["change_10s"] * wanted
        c30 = micro["change_30s"] * wanted
        slope = micro["slope"] * wanted
        ratio = micro["up_ratio"] if direction == "UP" else 1 - micro["up_ratio"]

        micro_score = 0
        micro_score += 6 if c10 > 8 else (3 if c10 > 2 else (-7 if c10 < -8 else (-4 if c10 < -2 else 0)))
        micro_score += 7 if c30 > 15 else (4 if c30 > 5 else (-9 if c30 < -15 else (-5 if c30 < -5 else 0)))
        micro_score += 4 if slope > 0.45 else (-5 if slope < -0.45 else 0)
        micro_score += 4 if ratio >= 0.62 else (-5 if ratio <= 0.38 else 0)

        # La microlectura pesa menos cuando quedan segundos y la distancia es amplia.
        weight = 1.0
        if seconds_left is not None:
            if seconds_left <= 30:
                weight = 0.45 if terminal_override else 1.20
            elif seconds_left <= 60:
                weight = 0.70 if terminal_override else 1.35
            elif seconds_left <= 120:
                weight = 1.35
            elif seconds_left <= 180:
                weight = 1.20

        confidence += float(np.clip(micro_score * weight, -28, 20))
        strong_contradiction = (c10 < -5 and c30 < -10)

        # Solo limitar por contradicción si tiempo/distancia NO hacen el cierre dominante.
        if strong_contradiction and not terminal_override:
            confidence = min(confidence, 69)

        micro_text = (
            f"MICRO {micro['pressure']} • "
            f"10s {micro['change_10s']:+.1f} • "
            f"30s {micro['change_30s']:+.1f}"
        )

    if seconds_left is not None and seconds_left <= 180:
        confidence += 2

    # Refuerzo específico de tiempo + distancia.
    if terminal_override and distance is not None:
        abs_d = abs(distance)
        if seconds_left <= 15:
            confidence = max(confidence, 90 if abs_d >= 75 else 82)
        elif seconds_left <= 30:
            confidence = max(confidence, 86 if abs_d >= 100 else 78)
        elif seconds_left <= 60:
            confidence = max(confidence, 80 if abs_d >= 120 else 74)

    confidence = int(round(np.clip(confidence, 5, 95)))

    if terminal_too_close:
        confidence = min(confidence, 58)
        headline = "DEMASIADO CERRADO"
        note = "Queda muy poco tiempo y BTC está demasiado cerca del target."
    elif terminal_override:
        headline = f"CIERRE MUY FAVORECIDO PARA {direction}"
        note = (
            f"Quedan {seconds_left}s y BTC está ${abs(distance):,.0f} "
            f"{'arriba' if distance > 0 else 'abajo'} del target."
        )
    elif round_signal.get("reversal"):
        headline = "SEÑAL PERDIENDO FUERZA"
        note = round_signal.get("reversal_text") or "Posible cambio de dirección."
    elif strong_contradiction:
        headline = f"{direction} PERDIENDO FUERZA"
        note = "La presión live de 10s y 30s va contra la señal activa."
    elif confidence >= 75:
        headline = ("ALTA PROBABILIDAD DE CIERRE EN VERDE" if direction == "UP"
                    else "ALTA PROBABILIDAD DE CIERRE EN ROJO")
        note = "Basado en momentum, volatilidad, presión de precio y distancia al target."
    elif confidence >= 60:
        headline = f"VENTAJA MODERADA PARA {direction}"
        note = "La dirección sigue activa, pero la presión inmediata aún puede cambiar."
    else:
        headline = f"CIERRE {direction} SIN VENTAJA CLARA"
        note = "La microlectura no confirma con fuerza la dirección."

    if direction == "UP":
        color = "#34e982"
        border = "rgba(52,233,130,.48)"
        bg = "linear-gradient(135deg,rgba(4,86,43,.46),rgba(7,36,25,.78))"
    else:
        color = "#ff4e5f"
        border = "rgba(255,78,95,.48)"
        bg = "linear-gradient(135deg,rgba(102,20,31,.48),rgba(43,10,17,.80))"

    return {
        "percent": confidence,
        "headline": headline,
        "note": note,
        "micro": micro_text,
        "color": color,
        "border": border,
        "bg": bg,
    }


@st.fragment(run_every="2s")
def live_dashboard():
    btc_error = ""
    live_price_error = ""
    kalshi_error = ""
    kalshi_live_error = ""

    try:
        btc_df = add_indicators(get_btc_data())
        btc_ok = True
    except Exception as error:
        btc_ok = False
        btc_error = str(error)
        btc_df = None

    try:
        market = get_kalshi_btc_market()
        kalshi_ok = market is not None
    except Exception as error:
        kalshi_ok = False
        kalshi_error = str(error)
        market = None

    try:
        coinbase_live_price = get_btc_live_price()
        coinbase_live_ok = True
    except Exception as error:
        coinbase_live_ok = False
        live_price_error = str(error)
        coinbase_live_price = (
            float(btc_df.iloc[-1]["close"]) if btc_ok else None
        )

    kalshi_live_price = None
    kalshi_live_ok = False

    if market:
        try:
            kalshi_live_price = get_kalshi_live_btc(market)
            kalshi_live_ok = True
        except Exception as error:
            kalshi_live_error = str(error)

    if kalshi_live_price is not None:
        live_btc_price = kalshi_live_price
        source = "KALSHI LIVE"
    else:
        live_btc_price = coinbase_live_price
        source = (
            "COINBASE"
            if coinbase_live_ok or live_btc_price is not None
            else "SIN DATOS"
        )

    if market:
        ticker = market.get("ticker", "--")
        target = get_target_from_market(market)
        seconds_left = get_seconds_remaining(market)
    else:
        ticker = "--"
        target = None
        seconds_left = None

    if btc_ok:
        sig = build_signal(
            btc_df, target, seconds_left, live_btc_price
        )
    else:
        sig = {
            "price": live_btc_price if live_btc_price is not None else 0,
            "candle_price": 0,
            "rsi": 50,
            "mom3": 0,
            "mom5": 0,
            "mom15": 0,
            "vol_ratio": 0,
            "ema": "N/A",
            "technical_score": 0,
            "target_score": 0,
            "final_score": 0,
            "distance": None,
            "distance_pct": None,
            "momentum": "NEUTRAL",
            "up_probability": 50,
            "down_probability": 50,
        }

    round_signal = process_round_signal(
        ticker, sig, market, seconds_left
    )

    # Cinta live de segundos para el Lector de Cierre.
    update_micro_tape(ticker, live_btc_price)
    micro = micro_reading()
    reader = closing_reader(sig, round_signal, seconds_left, micro)

    state = round_signal.get("round_state")
    active = (
        state.get("active_direction")
        if state
        else None
    )

    if active == "UP":
        accent = "#34e982"
        glow = "rgba(52,233,130,.46)"
        soft = "rgba(52,233,130,.10)"
        hero = "↑ UP"
        confidence = sig["up_probability"]
    elif active == "DOWN":
        accent = "#ff4e5f"
        glow = "rgba(255,78,95,.45)"
        soft = "rgba(255,78,95,.10)"
        hero = "↓ DOWN"
        confidence = sig["down_probability"]
    else:
        accent = "#38bdf8"
        glow = "rgba(56,189,248,.30)"
        soft = "rgba(56,189,248,.09)"
        hero = None
        confidence = max(
            sig["up_probability"], sig["down_probability"]
        )

    market_live = kalshi_ok and live_btc_price is not None

    distance = sig["distance"]
    distance_pct = sig.get("distance_pct")
    up = int(sig["up_probability"])
    down = int(sig["down_probability"])
    target_text = f"${target:,.0f}" if target is not None else "--"
    countdown = format_countdown(seconds_left)

    if distance is None:
        distance_text, distance_sub = "--", "SIN TARGET"
    else:
        distance_text = f"${abs(distance):,.0f}"
        distance_sub = f"{abs(distance_pct):.2f}%"
    first_signal = (state.get("first_direction") if state else None) or "--"
    first_time = "--"
    if state and state.get("first_signal_time"):
        first_time = state["first_signal_time"].astimezone().strftime("%H:%M")

    if active == "UP":
        hero_arrow, hero_word = "", "UP"
        btc_delta = f"{sig['mom3']:+.2f}%"
    elif active == "DOWN":
        hero_arrow, hero_word = "", "DOWN"
        btc_delta = f"{sig['mom3']:+.2f}%"
    else:
        hero_arrow, hero_word = "•", "ESPERANDO"
        btc_delta = f"{sig['mom3']:+.2f}%"

    ema_class = "green" if sig["ema"] == "BULL" else "red"
    rsi_class = "green" if sig["rsi"] >= 55 else "red" if sig["rsi"] <= 45 else ""
    mom_class = "green" if sig["mom3"] > 0 else "red" if sig["mom3"] < 0 else ""
    time_pct = max(0, min(100, int((seconds_left or 0) / 900 * 100)))

    st.markdown(
        f"""
<div class="refapp dir-{active.lower() if active in ("UP","DOWN") else "wait"}" style="--accent:{accent};--glow:{glow};--soft:{soft};">
  <header class="rhead">
    <div class="rtitle">BTC Signal</div>
    <div class="rver">v4.6.1</div>
    <div class="gear">⚙</div>
    <div class="rlive"><i></i>{'Mercado en vivo' if market_live else 'Conexión parcial'}</div>
  </header>

  <section class="rhero {'waiting' if active not in ('UP','DOWN') else ''}">
    <div class="rsignal"><span class="cssarrow"></span><span>{hero_word}</span></div>
    <div class="rconf">{'CONFIANZA ' + str(confidence) + '%' if active in ('UP','DOWN') else round_signal["signal"]}</div>
  </section>

  <div class="rgrid">
    <div class="rcard keycard">
      <div class="bigicon btcicon">₿</div>
      <div><div class="rlabel">BTC</div><div class="rvalue">${sig["price"]:,.0f}</div>
      <div class="rdelta {'green' if sig["mom3"] >= 0 else 'red'}">{btc_delta}</div></div>
    </div>
    <div class="rcard keycard">
      <div class="bigicon targeticon">◎</div>
      <div><div class="rlabel">TARGET</div><div class="rvalue">{target_text}</div></div>
    </div>
    <div class="rcard keycard">
      <div class="bars"><b></b><b></b><b></b></div>
      <div><div class="rlabel">DISTANCIA AL TARGET</div><div class="rvalue">{distance_text}</div>
      <div class="rdelta" style="color:var(--accent)">{distance_sub}</div></div>
    </div>
    <div class="rcard keycard">
      <div class="clock">◷</div>
      <div class="timecontent"><div class="rlabel">TIEMPO RESTANTE</div><div class="rvalue">{countdown}</div>
      <div class="timebar"><b style="width:{time_pct}%"></b></div></div>
    </div>
  </div>

  <section class="rcard probs">
    <div class="rlabel">PROBABILIDADES</div>
    <div class="pbar"><div class="pup" style="width:{up}%">{up}%</div><div class="pdown" style="width:{down}%">{down}%</div></div>
    <div class="pleg"><span class="green">● &nbsp;UP&nbsp; {up}%</span><span class="red">● &nbsp;DOWN&nbsp; {down}%</span></div>
  </section>

  <section class="reader" style="--rb:{reader['border']};--rbg:{reader['bg']};--rr:{reader['color']}">
    <div class="readerhead"><span class="pulse">⌁</span><span>LECTOR DE CIERRE</span><em>ACTIVO</em></div>
    <div class="readerbody"><div><strong>{reader['headline']}</strong><small>{reader['note']}</small></div>
    <div class="rring" style="--p:{reader['percent']}"><span>{reader['percent']}%</span></div></div>
  </section>

  <section class="rcard tech">
    <div class="techhead"><span>DETALLES TÉCNICOS</span><span>⌃</span></div>
    <div class="techrow">
      <div><small>1ª SEÑAL</small><b style="color:var(--accent)">{first_signal}</b><i>{first_time}</i></div>
      <div><small>KALSHI</small><b>{confidence}%</b><i>{round_signal["entry_quality"]}</i></div>
      <div><small>EMA</small><b class="{ema_class}">{sig["ema"]}</b><i>9 / 21</i></div>
      <div><small>RSI</small><b class="{rsi_class}">{sig["rsi"]:.0f}</b><i>14</i></div>
      <div><small>MOMENTUM</small><b class="{mom_class}">{sig["mom3"]:+.2f}</b><i>3 MIN</i></div>
    </div>
  </section>

  <nav class="rnav">
    <div class="active"><b>⌂</b><span>Señal</span></div>
    <div><b>⌁</b><span>Gráfico</span></div>
    <div><b>▣</b><span>Kalshi</span></div>
    <div><b>⚙</b><span>Ajustes</span></div>
  </nav>

  <section class="features">
    <div><b>ϟ</b><p><strong>SEÑAL EN TIEMPO REAL</strong><span>UP o DOWN, sin duda</span></p></div>
    <div><b>◎</b><p><strong>DATOS CLAVE</strong><span>BTC, target, distancia y countdown</span></p></div>
    <div><b>▥</b><p><strong>PROBABILIDADES VISUALES</strong><span>Con barra y porcentaje</span></p></div>
  </section>
  <footer><span>BTC SIGNAL v4.6.1 &nbsp; | &nbsp; DISEÑADO PARA TRADERS REALES</span><span>MENOS RUIDO. MÁS RESULTADOS.</span></footer>
</div>
<div class="ticker">{ticker} • SCORE {sig["final_score"]:+.2f}</div>
""", unsafe_allow_html=True)
    if round_signal["reversal"]:
        st.markdown(
            f'<div class="alert">⚠ {round_signal["reversal_text"]}</div>',
            unsafe_allow_html=True,
        )

    if target is None and kalshi_ok:
        st.warning(
            "Kalshi está conectado, pero esta ronda no entregó un target numérico."
        )
    if btc_error:
        st.error("Error Coinbase velas: " + btc_error)
    if live_price_error and live_btc_price is None:
        st.warning("Coinbase live: " + live_price_error)
    if kalshi_live_error and coinbase_live_price is not None:
        st.warning(
            "Kalshi BTC live falló temporalmente; usando Coinbase."
        )
    if kalshi_error:
        st.error("Error Kalshi: " + kalshi_error)


live_dashboard()
