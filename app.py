import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import base64
import time
import uuid
import math
import subprocess
import tempfile

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


.chartbox{margin-top:10px;background:linear-gradient(180deg,#08121d,#060c14);border:1px solid #203a51;border-radius:12px;padding:10px 8px 8px;box-shadow:inset 0 0 28px rgba(20,80,110,.08)}
.charttop{display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#eef6ff}.charttop b{font-size:13px}.chartlive{font-size:7px;color:#28e69a;margin-left:8px}.charttf{border:1px solid #26384b;border-radius:7px;padding:5px 8px;color:#dce8f5;font-size:9px}.ohlc{font-size:7px;color:#8ea0b5;margin-top:5px;white-space:nowrap}.indicators{font-size:7px;color:#aab8ca;margin:7px 0 1px;white-space:nowrap}.ema9dot{color:#df42e7}.ema21dot{color:#32d7ef}.targetdot{color:#23e7c1}.candlesvg{display:block;width:100%;height:265px}.chartfoot{display:flex;align-items:center;gap:10px;border-top:1px solid #18283a;padding:7px 2px 1px;color:#71839a;font-size:6px}.chartfoot .selected{border:1px solid #2a7189;border-radius:7px;padding:4px 8px;color:#e7f5ff;background:#0d2632}.chartempty{height:160px;display:grid;place-items:center;color:#708197;font-size:10px}
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


# =========================================================
# KALSHI AUTO TRADING — CAPA SEPARADA DEL MOTOR v4.6.1
# =========================================================
_AUTO_DEFAULTS = {
    "kalshi_auth_ok": False,
    "kalshi_auth_message": "No conectado",
    "auto_enabled": False,
    "auto_amount": 0.50,
    "auto_limit_cents": 50,
    "auto_take_profit": 90,
    "auto_martingale": False,
    "auto_max_levels": 4,
    "auto_level": 1,
    "auto_stop_after_win": False,
    "auto_last_ticker": None,
    "auto_last_order": None,
    "auto_last_status": "AUTO APAGADO",
    "auto_history": [],
}
for _k, _v in _AUTO_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v



KALSHI_API_BASE = "https://external-api.kalshi.com"
KALSHI_API_PREFIX = "/trade-api/v2"

def _kalshi_sign(message):
    """RSA-PSS/SHA256 signature using system OpenSSL; no Python crypto package required."""
    pem = st.session_state.get("kalshi_private_key_input", "")
    if not pem:
        raise ValueError("Falta la Private Key.")
    key_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False) as f:
            f.write(pem.strip() + "\n")
            key_path = f.name
        proc = subprocess.run(
            [
                "openssl", "dgst", "-sha256",
                "-sigopt", "rsa_padding_mode:pss",
                "-sigopt", "rsa_pss_saltlen:digest",
                "-sign", key_path,
            ],
            input=message,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        if proc.returncode != 0:
            raise ValueError("Private Key inválida o OpenSSL no pudo firmar.")
        return proc.stdout
    finally:
        if key_path:
            try:
                Path(key_path).unlink(missing_ok=True)
            except Exception:
                pass

def _kalshi_headers(method, path):
    key_id = st.session_state.get("kalshi_api_key_input", "").strip()
    if not key_id:
        raise ValueError("Falta el API Key ID.")
    ts = str(int(time.time() * 1000))
    clean_path = path.split("?", 1)[0]
    msg = f"{ts}{method.upper()}{clean_path}".encode("utf-8")
    signature = _kalshi_sign(msg)
    return {
        "KALSHI-ACCESS-KEY": key_id,
        "KALSHI-ACCESS-TIMESTAMP": ts,
        "KALSHI-ACCESS-SIGNATURE": base64.b64encode(signature).decode("ascii"),
        "Content-Type": "application/json",
    }

def kalshi_private_request(method, endpoint, payload=None, params=None):
    path = KALSHI_API_PREFIX + endpoint
    headers = _kalshi_headers(method, path)
    r = requests.request(
        method.upper(),
        KALSHI_API_BASE + path,
        headers=headers,
        json=payload,
        params=params,
        timeout=8,
    )
    if r.status_code >= 400:
        try:
            detail = r.json()
        except Exception:
            detail = r.text[:300]
        raise RuntimeError(f"Kalshi {r.status_code}: {detail}")
    return r.json() if r.text else {}

def kalshi_test_connection():
    data = kalshi_private_request("GET", "/portfolio/balance")
    dollars = data.get("balance_dollars")
    if dollars is None and data.get("balance") is not None:
        dollars = f"{float(data['balance']) / 100:.2f}"
    return data, dollars

def _market_contract_prices(market):
    """Returns current YES/NO asks as dollars when Kalshi exposes them."""
    if not market:
        return None, None
    def f(name):
        try:
            v = market.get(name)
            return float(v) if v not in (None, "") else None
        except Exception:
            return None
    yes_ask = f("yes_ask_dollars")
    no_ask = f("no_ask_dollars")
    # Compatibility with older payloads still returned by some endpoints.
    if yes_ask is None:
        y = f("yes_ask")
        yes_ask = y / 100.0 if y and y > 1 else y
    if no_ask is None:
        n = f("no_ask")
        no_ask = n / 100.0 if n and n > 1 else n
    return yes_ask, no_ask

def _amount_for_level():
    base = max(0.01, float(st.session_state.auto_amount))
    level = max(1, int(st.session_state.auto_level))
    return base * (2 ** (level - 1)) if st.session_state.auto_martingale else base

def _direction_for_level(signal_direction):
    level = max(1, int(st.session_state.auto_level))
    choice = st.session_state.get(f"auto_level_direction_{level}", "Seguir señal")
    if choice == "Solo UP":
        return "UP"
    if choice == "Solo DOWN":
        return "DOWN"
    return signal_direction

def _contracts_for_amount(amount, contract_price):
    if contract_price is None or contract_price <= 0:
        return 0.0
    # Fixed-point quantity; never intentionally exceeds configured premium.
    return math.floor((amount / contract_price) * 100) / 100.0

def kalshi_place_entry(ticker, direction, market):
    limit = max(1, min(99, int(st.session_state.auto_limit_cents))) / 100.0
    yes_ask, no_ask = _market_contract_prices(market)
    observed = yes_ask if direction == "UP" else no_ask
    if observed is not None and observed > limit:
        return {"skipped": True, "reason": f"{direction} está a {observed*100:.1f}¢ > límite {limit*100:.0f}¢"}

    amount = _amount_for_level()
    contract_price = min(observed, limit) if observed is not None else limit
    count = _contracts_for_amount(amount, contract_price)
    if count < 0.01:
        return {"skipped": True, "reason": "Monto demasiado pequeño para el precio actual."}

    # V2 is a single YES book:
    # UP = buy YES -> bid at max YES price.
    # DOWN = buy NO -> economically equivalent to ask YES at 1 - max NO price.
    if direction == "UP":
        side = "bid"
        yes_price = limit
    else:
        side = "ask"
        yes_price = 1.0 - limit

    client_id = f"btc461-{ticker}-{direction}-L{st.session_state.auto_level}"
    payload = {
        "ticker": ticker,
        "client_order_id": client_id[:64],
        "side": side,
        "count": f"{count:.2f}",
        "price": f"{yes_price:.4f}",
        "time_in_force": "immediate_or_cancel",
        "self_trade_prevention_type": "taker_at_cross",
        "cancel_order_on_pause": True,
    }
    result = kalshi_private_request("POST", "/portfolio/events/orders", payload)
    result["_direction"] = direction
    result["_requested_count"] = count
    result["_amount_level"] = amount
    result["_entry_contract_price"] = contract_price
    result["_ticker"] = ticker
    result["_level"] = int(st.session_state.auto_level)
    return result

def kalshi_place_take_profit(entry):
    try:
        filled = float(entry.get("fill_count") or entry.get("fill_count_fp") or 0)
    except Exception:
        filled = 0.0
    if filled <= 0:
        return None

    direction = entry["_direction"]
    p = float(entry["_entry_contract_price"])
    tp = max(0, float(st.session_state.auto_take_profit)) / 100.0
    desired_contract_exit = min(0.99, p * (1.0 + tp))

    if direction == "UP":
        # Close long YES by selling YES.
        side = "ask"
        yes_exit = desired_contract_exit
    else:
        # Close long NO / short YES by buying YES back at complement.
        side = "bid"
        yes_exit = max(0.01, 1.0 - desired_contract_exit)

    payload = {
        "ticker": entry["_ticker"],
        "client_order_id": (f"tp-{entry['_ticker']}-{entry['_direction']}-L{entry['_level']}")[:64],
        "side": side,
        "count": f"{filled:.2f}",
        "price": f"{yes_exit:.4f}",
        "time_in_force": "good_till_canceled",
        "self_trade_prevention_type": "taker_at_cross",
        "reduce_only": True,
        "cancel_order_on_pause": True,
    }
    return kalshi_private_request("POST", "/portfolio/events/orders", payload)

def _public_market_by_ticker(ticker):
    r = requests.get(
        f"{KALSHI_API_BASE}{KALSHI_API_PREFIX}/markets/{ticker}",
        timeout=6,
        headers={"User-Agent": "BTCSignal/4.6.1"},
    )
    r.raise_for_status()
    j = r.json()
    return j.get("market", j)

def auto_check_previous_result(current_ticker):
    prev = st.session_state.get("auto_last_order")
    if not prev or prev.get("_resolved"):
        return
    old_ticker = prev.get("_ticker")
    if not old_ticker or old_ticker == current_ticker:
        return
    try:
        old_market = _public_market_by_ticker(old_ticker)
        result = str(old_market.get("result", "")).lower()
        if result not in ("yes", "no"):
            return
        won = (prev.get("_direction") == "UP" and result == "yes") or \
              (prev.get("_direction") == "DOWN" and result == "no")
        prev["_resolved"] = True
        prev["_won"] = won
        if won:
            st.session_state.auto_level = 1
            st.session_state.auto_last_status = "WIN · MARTINGALA REINICIADA"
            if st.session_state.auto_stop_after_win:
                st.session_state.auto_enabled = False
                st.session_state.auto_last_status = "WIN · AUTO APAGADO"
        else:
            if st.session_state.auto_martingale:
                st.session_state.auto_level = min(
                    int(st.session_state.auto_level) + 1,
                    int(st.session_state.auto_max_levels),
                )
            st.session_state.auto_last_status = f"LOSS · NIVEL {st.session_state.auto_level}"
    except Exception:
        pass

def auto_trade_tick(ticker, market, round_signal):
    if not st.session_state.get("auto_enabled"):
        return
    if not st.session_state.get("kalshi_auth_ok"):
        st.session_state.auto_enabled = False
        st.session_state.auto_last_status = "AUTO APAGADO · KALSHI NO CONECTADO"
        return
    if not ticker or ticker == "--":
        return

    auto_check_previous_result(ticker)

    direction = round_signal.get("decision")
    if direction not in ("UP", "DOWN"):
        return
    direction = _direction_for_level(direction)

    # One entry maximum per Kalshi round.
    if st.session_state.get("auto_last_ticker") == ticker:
        return

    try:
        result = kalshi_place_entry(ticker, direction, market)
        if result.get("skipped"):
            st.session_state.auto_last_status = "ESPERANDO · " + result["reason"]
            return

        st.session_state.auto_last_ticker = ticker
        st.session_state.auto_last_order = result
        st.session_state.auto_history.append({
            "ticker": ticker,
            "direction": direction,
            "level": int(st.session_state.auto_level),
            "time": datetime.now(timezone.utc).isoformat(),
            "order_id": result.get("order_id"),
        })
        filled = float(result.get("fill_count") or 0)
        if filled > 0:
            st.session_state.auto_last_status = f"FILLED {direction} · {filled:.2f} contratos"
            try:
                tp_order = kalshi_place_take_profit(result)
                if tp_order:
                    result["_tp_order_id"] = tp_order.get("order_id")
            except Exception as e:
                result["_tp_error"] = str(e)
        else:
            st.session_state.auto_last_status = f"ORDEN {direction} ENVIADA · SIN FILL"
    except Exception as e:
        st.session_state.auto_last_status = "ERROR AUTO · " + str(e)[:180]

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


def get_coinbase_whale_flow():
    """FLOW PULSE BTC/USD: varias páginas de trades, aceleración y desequilibrio."""
    now = pd.Timestamp.now(tz="UTC").timestamp()
    tape = st.session_state.setdefault("whale_flow_tape", [])
    seen = st.session_state.setdefault("whale_seen_ids", {})
    headers = {"User-Agent": "MacalyAlphaBot/4.6.1", "Cache-Control": "no-cache"}

    all_rows, before = [], None
    for _ in range(5):
        params = {"limit": 100}
        if before:
            params["before"] = before
        r = requests.get(
            "https://api.exchange.coinbase.com/products/BTC-USD/trades",
            params=params, headers=headers, timeout=5
        )
        r.raise_for_status()
        rows = r.json()
        if not isinstance(rows, list) or not rows:
            break
        all_rows.extend(rows)
        before = r.headers.get("cb-before")
        try:
            oldest = pd.to_datetime(rows[-1].get("time"), utc=True, errors="coerce")
            if not pd.isna(oldest) and now - oldest.timestamp() >= 35:
                break
        except Exception:
            pass
        if not before:
            break

    if not all_rows:
        raise ValueError("Coinbase no devolvió operaciones recientes.")

    for row in reversed(all_rows):
        try:
            trade_id = str(row.get("trade_id", ""))
            if not trade_id or trade_id in seen:
                continue
            price = float(row.get("price", 0))
            size = float(row.get("size", 0))
            notional = price * size
            maker_side = str(row.get("side", "")).lower()
            aggressor = "COMPRA" if maker_side == "sell" else "VENTA" if maker_side == "buy" else ""
            ts = pd.to_datetime(row.get("time"), utc=True, errors="coerce")
            t = ts.timestamp() if not pd.isna(ts) else now
            if notional > 0 and aggressor and now - t <= 40:
                tape.append({"id": trade_id, "t": t, "notional": notional, "side": aggressor})
                seen[trade_id] = t
        except Exception:
            continue

    tape[:] = [x for x in tape if now - x["t"] <= 40]
    for k in [k for k, t in seen.items() if now - t > 55]:
        seen.pop(k, None)

    def stats(lo, hi=0):
        xs = [x for x in tape if hi < now - x["t"] <= lo]
        bx = [x for x in xs if x["side"] == "COMPRA"]
        sx = [x for x in xs if x["side"] == "VENTA"]
        buy = sum(x["notional"] for x in bx)
        sell = sum(x["notional"] for x in sx)
        return buy, sell, buy + sell, buy - sell, len(xs), \
               sum(x["notional"] >= 50000 for x in bx), \
               sum(x["notional"] >= 50000 for x in sx)

    buy, sell, total, net, trade_count, big_buy, big_sell = stats(5)
    _, _, old_total, _, _, _, _ = stats(25, 5)

    rate = total / 5.0
    old_rate = old_total / 20.0 if old_total > 0 else 0.0
    acceleration = rate / old_rate if old_rate > 0 else (9.0 if total > 0 else 0.0)
    gross_dom = max(buy, sell) / total if total > 0 else 0.0
    net_dom = abs(net) / total if total > 0 else 0.0
    direction = "UP" if net > 0 else "DOWN" if net < 0 else None
    big_same = big_buy if direction == "UP" else big_sell if direction == "DOWN" else 0

    score = 0
    if total >= 150000: score += 1
    if total >= 300000: score += 1
    if total >= 600000: score += 1
    if gross_dom >= .62: score += 1
    if gross_dom >= .72: score += 1
    if net_dom >= .35: score += 1
    if acceleration >= 1.8: score += 1
    if acceleration >= 3.0: score += 1
    if trade_count >= 80: score += 1
    if big_same >= 2: score += 1

    detected = bool(direction and total >= 200000 and abs(net) >= 100000
                    and gross_dom >= .62 and score >= 5)
    if direction and total >= 500000 and abs(net) >= 250000 and gross_dom >= .68:
        detected = True

    strength = "EXTREMO" if score >= 8 else "FUERTE" if score >= 6 else "ANORMAL"
    alert = None
    if detected:
        alert = {
            "direction": direction, "time": now, "buy": buy, "sell": sell,
            "total": total, "imbalance": gross_dom, "net": abs(net),
            "acceleration": acceleration, "trades": trade_count,
            "big_trades": big_same, "score": score, "strength": strength,
        }

    return {
        "detected": detected, "alert": alert, "live_buy": buy,
        "live_sell": sell, "live_total": total, "imbalance": gross_dom,
        "acceleration": acceleration, "trades": trade_count, "score": score,
    }

def compact_usd(value):
    value = float(value or 0)
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value/1_000:.0f}K"
    return f"${value:,.0f}"


def render_whale_panel(whale, active):
    base = "margin:8px 0;padding:12px;border:1px solid #26384b;border-radius:13px;background:linear-gradient(180deg,#0c1724,#09111b)"
    if not whale or not whale.get("detected"):
        buy = compact_usd((whale or {}).get("live_buy", 0))
        sell = compact_usd((whale or {}).get("live_sell", 0))
        return f'''<section style="{base}">
          <div style="display:flex;justify-content:space-between;align-items:center"><b style="font-size:10px;color:#e4edf7">🐋 FLUJO BALLENA · EN VIVO</b><span style="font-size:8px;color:#35e986">● COINBASE</span></div>
          <div style="margin-top:8px;font-size:13px;font-weight:900;color:#91a2b5">FLUJO NORMAL / SIN CONFIRMACIÓN</div>
          <div style="margin-top:6px;font-size:9px;color:#8da0b4">5s · COMPRAS {buy} · VENTAS {sell}</div>
          <div style="margin-top:4px;font-size:8px;color:#6f8195">Lee hasta 500 trades recientes y compara presión, aceleración y desequilibrio.</div>
        </section>'''

    a = whale["alert"]
    up = a["direction"] == "UP"
    color = "#35e986" if up else "#ff5367"
    arrow = "↑" if up else "↓"
    label = "COMPRADOR · POSIBLE IMPULSO UP" if up else "VENDEDOR · POSIBLE IMPULSO DOWN"
    dominant = a["buy"] if up else a["sell"]
    relation = ""
    if active in ("UP", "DOWN"):
        relation = " · CONFIRMA SEÑAL" if active == a["direction"] else " · CONTRADICE SEÑAL"
    return f'''<section style="{base};border-color:{color};box-shadow:0 0 20px {color}33">
      <div style="display:flex;justify-content:space-between;align-items:center"><b style="font-size:10px;color:#e4edf7">🐋 FLUJO BALLENA · EN VIVO</b><span style="font-size:8px;color:{color}">● ALERTA</span></div>
      <div style="margin-top:8px;font-size:15px;font-weight:950;color:{color}">⚡ {arrow} FLUJO EXTREMO {label}</div>
      <div style="margin-top:6px;font-size:12px;font-weight:900;color:#f3f7fb">{compact_usd(dominant)} dominantes AHORA</div>
      <div style="margin-top:5px;font-size:9px;color:#aab8c7">COMPRAS {compact_usd(a['buy'])} · VENTAS {compact_usd(a['sell'])} · DOMINIO {a['imbalance']*100:.0f}%{relation}</div>
      <div style="margin-top:4px;font-size:8px;color:#7f91a5">Alerta temprana de presión extraordinaria en el flujo real de BTC/USD.</div>
    </section>'''


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

    # Conserva hasta 15 minutos para la gráfica; la microlectura sigue usando ventanas de 10s/30s.
    cutoff = now_ts - 900
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




def render_live_candles(df, live_price, target, active, timeframe="1m"):
    # Renderiza velas BTC/USD para visualización sin cambiar el motor v4.6.1.
    # 3m y 5m se construyen agrupando las velas reales de Coinbase de 1 minuto.
    if df is None or len(df) < 5:
        return f'<div class="chartbox"><div class="charttitle">BTC/USD · {timeframe}</div><div class="chartempty">Esperando velas…</div></div>'

    tf_minutes = {"1m": 1, "3m": 3, "5m": 5}.get(timeframe, 1)
    source_df = df.copy().sort_values("time")
    if tf_minutes > 1:
        d = (
            source_df.set_index("time")
            .resample(f"{tf_minutes}min", label="left", closed="left")
            .agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            })
            .dropna()
            .reset_index()
        )
    else:
        d = source_df[["time", "open", "high", "low", "close", "volume"]].copy()

    d = d.tail(42).reset_index(drop=True)
    # La última vela se mantiene visualmente al precio live recibido por el dashboard.
    if live_price is not None and len(d):
        i = d.index[-1]
        d.loc[i, "close"] = float(live_price)
        d.loc[i, "high"] = max(float(d.loc[i, "high"]), float(live_price))
        d.loc[i, "low"] = min(float(d.loc[i, "low"]), float(live_price))

    close = d["close"].astype(float)
    ema9 = close.ewm(span=9, adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()

    W, H = 760, 430
    left, right, top, bottom = 18, 142, 54, 82
    pw, ph = W-left-right, H-top-bottom
    vals = list(d["low"].astype(float)) + list(d["high"].astype(float))
    if target is not None: vals.append(float(target))
    if live_price is not None: vals.append(float(live_price))
    lo, hi = min(vals), max(vals)
    pad = max((hi-lo)*0.10, 8)
    lo, hi = lo-pad, hi+pad
    def y(v): return top + (hi-float(v))/(hi-lo)*ph
    n=len(d); step=pw/max(n,1); body=max(3.2, min(8, step*.58))

    svg=[]
    # horizontal grid + prices
    for k in range(5):
        yy=top+ph*k/4; price=hi-(hi-lo)*k/4
        svg.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{W-right}" y2="{yy:.1f}" stroke="#182536" stroke-width="1"/>')
        svg.append(f'<text x="{W-right+8}" y="{yy+4:.1f}" fill="#8392a7" font-size="12">{price:,.0f}</text>')
    # vertical grid
    for k in range(5):
        xx=left+pw*k/4
        svg.append(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{top+ph}" stroke="#121e2d" stroke-width="1"/>')

    # volume scaled into bottom 52 px of plot
    vmax=max(float(d["volume"].max()),1)
    vbase=top+ph
    for i,row in d.iterrows():
        x=left+(i+.5)*step; vh=float(row["volume"])/vmax*48
        col='#16b97a' if float(row['close'])>=float(row['open']) else '#c43d59'
        svg.append(f'<rect x="{x-body/2:.1f}" y="{vbase-vh:.1f}" width="{body:.1f}" height="{vh:.1f}" fill="{col}" opacity=".55"/>')

    # candles
    for i,row in d.iterrows():
        x=left+(i+.5)*step
        o,c,h,l=map(float,[row['open'],row['close'],row['high'],row['low']])
        col='#19e6a2' if c>=o else '#ff4e6a'
        svg.append(f'<line x1="{x:.1f}" y1="{y(h):.1f}" x2="{x:.1f}" y2="{y(l):.1f}" stroke="{col}" stroke-width="1.4"/>')
        yy=min(y(o),y(c)); hh=max(2.0,abs(y(o)-y(c)))
        svg.append(f'<rect x="{x-body/2:.1f}" y="{yy:.1f}" width="{body:.1f}" height="{hh:.1f}" rx=".7" fill="{col}"/>')

    # EMA paths
    def path(series,color):
        pts=' '.join(f'{left+(i+.5)*step:.1f},{y(v):.1f}' for i,v in enumerate(series))
        return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
    svg.append(path(ema9,'#df42e7'))
    svg.append(path(ema21,'#32d7ef'))

    # target line
    if target is not None and lo <= float(target) <= hi:
        ty=y(target)
        svg.append(f'<line x1="{left}" y1="{ty:.1f}" x2="{W-right}" y2="{ty:.1f}" stroke="#23e7c1" stroke-width="1.8" stroke-dasharray="7 6"/>')
        # La etiqueta queda en el margen derecho, fuera del área de velas.
        svg.append(f'<rect x="{W-right+18}" y="{ty-12:.1f}" width="96" height="23" rx="3" fill="#20e7bd"/>')
        svg.append(f'<text x="{W-right+25}" y="{ty+4:.1f}" fill="#061510" font-size="10" font-weight="800">TARGET</text>')
    # live price line + label
    if live_price is not None and lo <= float(live_price) <= hi:
        ly=y(live_price); lc='#31e889' if active=='UP' else '#ff5367' if active=='DOWN' else '#38bdf8'
        svg.append(f'<line x1="{left}" y1="{ly:.1f}" x2="{W-right}" y2="{ly:.1f}" stroke="{lc}" stroke-width="1.3" stroke-dasharray="3 4"/>')
        svg.append(f'<rect x="{W-right+18}" y="{ly-12:.1f}" width="96" height="23" rx="3" fill="{lc}"/>')
        svg.append(f'<text x="{W-right+25}" y="{ly+4:.1f}" fill="#061510" font-size="11" font-weight="900">{float(live_price):,.0f}</text>')

    # time labels
    picks=[0, max(0,n//3), max(0,2*n//3), n-1]
    for idx in picks:
        tm=d.iloc[idx]['time'].to_pydatetime().astimezone().strftime('%H:%M')
        xx=left+(idx+.5)*step
        svg.append(f'<text x="{xx:.1f}" y="{H-52}" text-anchor="middle" fill="#8392a7" font-size="11">{tm}</text>')

    last=d.iloc[-1]
    change=float(last['close'])-float(last['open'])
    pct=(change/float(last['open'])*100) if float(last['open']) else 0
    direction_color='#31e889' if change>=0 else '#ff5367'
    target_label=f'${float(target):,.0f}' if target is not None else '--'
    return f'''<section class="chartbox">
      <div class="charttop"><div><b>BTC/USD · {timeframe}</b><span class="chartlive">● LIVE</span></div><div class="charttf">{timeframe}</div></div>
      <div class="ohlc">O {float(last['open']):,.0f} &nbsp; H {float(last['high']):,.0f} &nbsp; L {float(last['low']):,.0f} &nbsp; C {float(last['close']):,.0f} &nbsp; <strong style="color:{direction_color}">{change:+,.0f} ({pct:+.2f}%)</strong></div>
      <div class="indicators"><span class="ema9dot">●</span> EMA9 {float(ema9.iloc[-1]):,.0f} &nbsp;&nbsp; <span class="ema21dot">●</span> EMA21 {float(ema21.iloc[-1]):,.0f} &nbsp;&nbsp; <span class="targetdot">━</span> TARGET {target_label}</div>
      <svg class="candlesvg" viewBox="0 0 {W} {H}" preserveAspectRatio="none">{''.join(svg)}</svg>
      <div class="chartfoot"><span class="selected">{timeframe}</span><span>VELAS REALES COINBASE</span><span>ACTUALIZACIÓN LIVE</span></div>
    </section>'''


# =========================================================
# CRITIK2-STYLE MOBILE FRONTEND — ESPAÑOL + CONTROLES REALES
# =========================================================

st.markdown("""
<style>
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important}
.stApp{background:#010604!important;color:#eef5f1!important}.block-container{max-width:430px!important;padding:7px 10px 92px!important}div[data-testid="stVerticalBlock"]{gap:.38rem!important}
.crit{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.ctop{display:flex;justify-content:space-between;align-items:flex-start;padding:5px 2px 2px}.asset{display:flex;gap:9px;align-items:center}.coin{width:40px;height:40px;border-radius:50%;background:#f7931a;color:#111;display:grid;place-items:center;font-size:25px;font-weight:1000}.kicker{font-size:9px;color:#84918b;font-weight:900}.name{font-size:20px;font-weight:1000;margin-top:3px}.auto{text-align:right;font-size:7px;color:#8b9791;font-weight:900}.power{width:37px;height:37px;border-radius:50%;border:1px solid #653139;color:#e65b65;display:grid;place-items:center;font-size:21px;margin:4px 0 2px auto}.power.on{border-color:#218c59;color:#31db86;box-shadow:0 0 12px #31db8633}.status{font-size:8px;color:#e65b65}.status.on{color:#31db86}
.market{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:8px 2px 2px}.market>div+div{border-left:1px solid #53605a;padding-left:10px}.lab{font-size:9px;color:#89958f;font-weight:1000}.price{font-size:25px;font-weight:1000;margin-top:5px}.green{color:#31db86!important}.red{color:#ff626b!important}.sub{font-size:10px;font-weight:850;margin-top:3px}.count{font-size:18px;font-weight:1000;margin-top:10px}.live{text-align:right;font-size:9px;font-weight:900;padding:0 3px}.live i{display:inline-block;width:8px;height:8px;border-radius:50%;background:#31db86;margin-right:5px;box-shadow:0 0 10px #31db86}
.chartwrap{display:grid;grid-template-columns:6px 1fr 58px;gap:5px;height:320px;margin-top:2px}.sidebar{border-radius:5px;background:linear-gradient(to bottom,#ff626b 0 70%,#0fd47a 70% 100%)}.plot{overflow:hidden}.plot svg{width:100%;height:100%;display:block}.scale{position:relative;color:#81908a;font-size:8px;font-weight:800}.scale span{position:absolute;right:0}.times{display:flex;justify-content:space-between;color:#7d8b85;font-size:7px;padding:0 58px 4px 12px}.past{font-size:8px;color:#83918b;font-weight:900;padding:2px 0 5px}.past .arr{font-size:15px;letter-spacing:2px}
.mode{border:1px solid #18543a;background:linear-gradient(180deg,#06140e,#04100b);border-radius:14px;padding:11px;margin:4px 0}.mhead{display:flex;justify-content:space-between;align-items:center}.guide{display:flex;gap:9px;align-items:center}.guideicon{width:34px;height:34px;border:1px solid #16945b;border-radius:10px;display:grid;place-items:center;color:#29d77f;font-weight:1000}.mhead small{display:block;color:#2ad67f;font-size:7px;font-weight:1000;letter-spacing:1px}.mtitle{font-size:20px;font-weight:1000;margin-top:2px}.minner{border:1px solid #293b34;border-radius:11px;padding:11px;margin-top:9px;min-height:76px}.minner small{display:block;color:#84918c;font-size:7px;font-weight:900}.msig{font-size:22px;font-weight:1000;margin:6px 0}.mnote{color:#aeb8b4;font-size:8px;font-weight:750;line-height:1.35}
.ptitle{font-size:23px;font-weight:1000;padding:14px 2px 3px}.psub{font-size:9px;color:#84918b;padding:0 2px 10px}.card{border:1px solid #173126;background:#07100c;border-radius:13px;padding:12px;margin-bottom:9px}.card h4{margin:0 0 4px}.card p{margin:0;color:#829089;font-size:9px}.stats{display:grid;grid-template-columns:1fr 1fr;gap:8px}.stat{border:1px solid #173126;background:#07100c;border-radius:12px;padding:12px}.stat small{color:#819089;font-size:8px}.stat b{display:block;font-size:20px;margin-top:5px}.op{border-bottom:1px solid #14261e;padding:10px 2px;display:grid;grid-template-columns:1fr auto}.op small{color:#839088}.balance{text-align:center;padding:25px 0}.balance small{color:#839089}.balance b{display:block;font-size:34px;margin-top:6px}.risk{border:1px solid #69540d;background:#171305;border-radius:12px;padding:12px;color:#dfc35c;font-size:9px;margin-top:10px}.kalogo{text-align:center;font-size:45px;font-weight:1000;padding-top:15px}.kabrand{text-align:center;font-size:25px;font-weight:1000}.kabrand span{color:#ff684f}.kastatus{text-align:center;color:#ff626b;font-size:10px;font-weight:900;margin:7px 0 16px}
/* Controles Streamlit reales, compactos y en español */
[data-testid="stToggle"]{background:#06110c;border:1px solid #173126;border-radius:11px;padding:7px 10px!important;margin:0!important}[data-testid="stToggle"] label{font-size:9px!important;font-weight:900!important;color:#dce7e1!important}
div.stButton>button{border-radius:10px;border:1px solid #214b38;background:#07110c;color:#edf4f0;font-weight:850;font-size:9px;min-height:39px}
/* navegación horizontal real */
[data-testid="stHorizontalBlock"]{display:flex!important;flex-direction:row!important;flex-wrap:nowrap!important;gap:.35rem!important;align-items:center!important}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{min-width:0!important;width:auto!important;flex:1 1 0!important}
.stButton button p{font-size:8px!important;white-space:pre-line!important}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:#18543a!important;border-radius:14px!important;background:linear-gradient(180deg,#06140e,#04100b)!important}
</style>
""",unsafe_allow_html=True)

if "crit_page" not in st.session_state: st.session_state.crit_page="Bot"
if "signal_mode" not in st.session_state: st.session_state.signal_mode=False

@st.cache_data(ttl=20)
def get_recent_past_markets(limit=10):
    """Últimos resultados REALES publicados por Kalshi para KXBTC15M."""
    headers={"User-Agent":"MacalyAlphaBot/4.6.1","Cache-Control":"no-cache"}
    collected=[]
    for status in ("settled","closed"):
        try:
            r=requests.get(
                f"{KALSHI_API_BASE}{KALSHI_API_PREFIX}/markets",
                params={"limit":100,"status":status,"series_ticker":"KXBTC15M"},
                headers=headers,timeout=7,
            )
            if r.status_code >= 400:
                continue
            for m in r.json().get("markets",[]):
                result=str(m.get("result","")).lower()
                if result in ("yes","no"):
                    collected.append(m)
        except Exception:
            continue
    unique={str(m.get("ticker")):m for m in collected if m.get("ticker")}
    rows=list(unique.values())
    rows.sort(key=lambda m:str(m.get("close_time") or m.get("expiration_time") or ""),reverse=True)
    return rows[:limit]

def past_markets_html():
    try: rows=get_recent_past_markets(10)
    except Exception: rows=[]
    if not rows:
        return '<span style="color:#66736d">SIN RESULTADOS DISPONIBLES</span>'
    out=[]
    # mostrar de más antiguo a más reciente, como una cinta temporal
    for m in reversed(rows):
        result=str(m.get("result","")).lower()
        if result=="yes": out.append('<span style="color:#31db86">▲</span>')
        elif result=="no": out.append('<span style="color:#ff626b">▼</span>')
    return " ".join(out) if out else '<span style="color:#66736d">SIN RESULTADOS DISPONIBLES</span>'

def close_clock(market):
    try:
        dt=datetime.fromisoformat(str(market.get("close_time")).replace("Z","+00:00"))
        return dt.astimezone().strftime("%I:%M %p").lstrip("0")
    except Exception:
        return "--"

def page_header(title, sub=""):
    st.markdown(f'<div class="ptitle">{title}</div><div class="psub">{sub}</div>',unsafe_allow_html=True)

def connection_page():
    page_header("Conexión con Kalshi","CONECTA TU CUENTA")
    st.markdown(f'<div class="kalogo">K</div><div class="kabrand"><span>Kalshi</span> Cuenta</div><div class="kastatus">● {"CONECTADO" if st.session_state.kalshi_auth_ok else "NO CONECTADO"}</div>',unsafe_allow_html=True)
    st.caption("Conecta tu cuenta para que el modo automático pueda enviar operaciones.")
    st.text_input("ID de API",key="kalshi_api_key_input",placeholder="Pega tu ID de API")
    st.text_area("Clave privada",key="kalshi_private_key_input",placeholder="-----BEGIN PRIVATE KEY-----",height=135)
    if st.button("Conectar cuenta",use_container_width=True):
        try:
            _,bal=kalshi_test_connection();st.session_state.kalshi_auth_ok=True;st.session_state.kalshi_auth_message=f"Conectado · ${bal}";st.rerun()
        except Exception as e:
            st.session_state.kalshi_auth_ok=False;st.session_state.auto_enabled=False;st.session_state.kalshi_auth_message="Error: "+str(e)[:150]
    if st.session_state.kalshi_auth_ok and st.button("Desconectar",use_container_width=True):
        st.session_state.kalshi_auth_ok=False;st.session_state.auto_enabled=False;st.rerun()
    st.caption(st.session_state.kalshi_auth_message)

def bot_settings():
    page_header("Ajustes del bot","INDICADORES")
    st.markdown('<div class="card"><h4>Generación de señal</h4><p>Motor Macaly + Alpha v4.6.1 · BTC 15 MIN.</p></div>',unsafe_allow_html=True)
    st.selectbox("Cálculo del monto",["Manual","Automático"],index=0)
    st.caption("Automático distribuye el 90% del saldo para cubrir los niveles seleccionados.")
    st.selectbox("Administración de la operación",["Martingala","Monto fijo"],index=0 if st.session_state.auto_martingale else 1)
    st.session_state.auto_amount=st.number_input("Monto inicial manual ($)",min_value=.01,value=float(st.session_state.auto_amount),step=.25)
    st.session_state.auto_martingale=st.toggle("Martingala",value=bool(st.session_state.auto_martingale))
    st.session_state.auto_limit_cents=st.select_slider("Precio límite",options=list(range(1,100)),value=int(st.session_state.auto_limit_cents),format_func=lambda x:f"{x}¢")
    st.session_state.auto_take_profit=st.select_slider("Tomar ganancia",options=list(range(0,201,5)),value=int(st.session_state.auto_take_profit),format_func=lambda x:f"+{x}%")
    st.session_state.auto_max_levels=st.select_slider("Máximo de niveles",options=list(range(1,9)),value=int(st.session_state.auto_max_levels))
    st.markdown(f'<div class="card"><h4>Saldo disponible</h4><p>Nivel actual {st.session_state.auto_level}/{st.session_state.auto_max_levels} · Próximo monto ${_amount_for_level():.2f}</p></div>',unsafe_allow_html=True)
    for level in range(1,int(st.session_state.auto_max_levels)+1):
        key=f"auto_level_direction_{level}"
        if key not in st.session_state: st.session_state[key]="Seguir señal"
        st.selectbox(f"Nivel {level}",["Seguir señal","Solo UP","Solo DOWN"],key=key)
    st.session_state.auto_stop_after_win=st.toggle("Apagar bot después de la próxima operación ganadora",value=bool(st.session_state.auto_stop_after_win))
    if st.button("RESTAURAR PROGRESIÓN",use_container_width=True): st.session_state.auto_level=1;st.session_state.auto_last_status="PROGRESIÓN REINICIADA"
    st.caption(st.session_state.auto_last_status)

def settings_page():
    page_header("Ajustes")
    choice=st.radio("Menú",["Ajustes del bot","Conexión con Kalshi","Alertas","Acerca del bot"],label_visibility="collapsed")
    if choice=="Ajustes del bot": bot_settings()
    elif choice=="Conexión con Kalshi": connection_page()
    else: st.info(f"{choice}: sección preparada.")

def operations_page():
    page_header("Operaciones")
    hist=list(reversed(st.session_state.get("auto_history",[])))
    wins=sum(1 for x in hist if x.get("_won") is True);loss=sum(1 for x in hist if x.get("_won") is False);res=wins+loss;wr=wins/res*100 if res else 0
    st.markdown(f'<div class="stats"><div class="stat"><small>GANANCIA/PÉRDIDA DEL DÍA</small><b>$0.00</b></div><div class="stat"><small>PORCENTAJE DE ACIERTO</small><b>{wr:.0f}%</b></div><div class="stat"><small>GANADAS</small><b class="green">{wins}</b></div><div class="stat"><small>PERDIDAS</small><b class="red">{loss}</b></div></div>',unsafe_allow_html=True)
    if not hist: st.info("Todavía no hay operaciones registradas hoy.")
    for x in hist[:40]: st.markdown(f'<div class="op"><div><b>{x.get("direction","--")}</b><br><small>{x.get("ticker","--")}</small></div><div><b>Nivel {x.get("level","--")}</b><br><small>{str(x.get("time",""))[:19]}</small></div></div>',unsafe_allow_html=True)

def balance_page():
    page_header("Saldo en Kalshi")
    if st.session_state.kalshi_auth_ok:
        try: _,bal=kalshi_test_connection();amount=f"${bal}"
        except Exception: amount="--"
    else: amount="--"
    st.markdown(f'<div class="card"><div class="balance"><small>SALDO DISPONIBLE</small><b>{amount}</b></div></div><div class="risk"><b>⚠ ADVERTENCIA DE RIESGO</b><br><br>Los mercados de predicciones implican riesgo y pueden ocasionar pérdidas. Las ganancias no están aseguradas.</div>',unsafe_allow_html=True)

def build_real_line_chart(btc_df, live, target, seconds):
    """Grafica solo la ronda actual y llena el eje X segun avanza el mercado."""
    W,H=330,300; top,bottom=8,18
    now=datetime.now(timezone.utc).timestamp(); elapsed=max(0.0,min(900.0,900.0-float(seconds or 0))); round_start=now-elapsed
    points=[]
    if btc_df is not None and len(btc_df):
        for _,r in btc_df.iterrows():
            try:
                t=r["time"].timestamp(); pr=float(r["close"])
                if round_start-65 <= t <= now+5: points.append((t,pr))
            except Exception: pass
    for z in st.session_state.get("micro_prices",[]):
        try:
            t=float(z["t"]); pr=float(z["p"])
            if t>=round_start: points.append((t,pr))
        except Exception: pass
    if live is not None: points.append((now,float(live)))
    points=sorted({round(t,1):(t,p) for t,p in points}.values())
    if len(points)<2: return '<div style="height:300px;display:grid;place-items:center;color:#6f7d77">Esperando datos en vivo…</div>', ["--"]*5
    vals=[p for _,p in points]; scalevals=vals+([float(target)] if target else []); lo,hi=min(scalevals),max(scalevals); pad=max((hi-lo)*.10,15); lo-=pad; hi+=pad; span=max(hi-lo,1)
    def y(v): return top+(hi-v)/span*(H-top-bottom)
    def x(t):
        denom=max(now-round_start, 30.0)
        return max(1,min(W-2,1+((t-round_start)/denom)*(W-3)))
    xs=[x(t) for t,_ in points]; ys=[y(pr) for _,pr in points]; poly=" ".join(f"{xx:.1f},{yy:.1f}" for xx,yy in zip(xs,ys)); lastx=xs[-1]; area=f"1,{H-bottom} {poly} {lastx:.1f},{H-bottom}"
    up=(live is not None and target is not None and float(live)>=float(target)); color="#31db86" if up else "#ff626b"
    svg=[f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{color}" stop-opacity=".30"/><stop offset="100%" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>']
    if target is not None:
        ty=y(float(target)); svg.append(f'<line x1="0" y1="{ty:.1f}" x2="{W}" y2="{ty:.1f}" stroke="#8a9691" stroke-width="1.15" stroke-dasharray="3 5"/><rect x="132" y="{ty-12:.1f}" width="65" height="18" rx="2" fill="#010604"/><text x="142" y="{ty+1:.1f}" fill="#9aa6a1" font-size="9" font-weight="900">OBJETIVO⌃</text>')
    svg.append(f'<polygon points="{area}" fill="url(#g)"/>'); svg.append(f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="2.15" stroke-linejoin="round" stroke-linecap="round"/>')
    lx,ly=xs[-1],ys[-1]; svg.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="12" fill="none" stroke="{color}" stroke-opacity=".13" stroke-width="4"/><circle cx="{lx:.1f}" cy="{ly:.1f}" r="6" fill="none" stroke="{color}" stroke-opacity=".35" stroke-width="2"/><circle cx="{lx:.1f}" cy="{ly:.1f}" r="3.6" fill="{color}"/>')
    labels=[f"${hi-(hi-lo)*k/4:,.0f}" for k in range(5)]; return f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="none">{"".join(svg)}</svg>',labels

@st.fragment(run_every="2s")
def bot_page():
    try: btc_df=add_indicators(get_btc_data());btc_ok=True
    except Exception: btc_df=None;btc_ok=False
    try: market=get_kalshi_btc_market()
    except Exception: market=None
    try: cb=get_btc_live_price()
    except Exception: cb=float(btc_df.iloc[-1]["close"]) if btc_ok else None
    try: kp=get_kalshi_live_btc(market) if market else None
    except Exception: kp=None
    live=kp if kp is not None else cb; ticker=market.get("ticker","--") if market else "--"; target=get_target_from_market(market); seconds=get_seconds_remaining(market)
    if btc_ok: sig=build_signal(btc_df,target,seconds,live)
    else: sig={"price":live or 0,"rsi":50,"mom3":0,"mom5":0,"mom15":0,"vol_ratio":0,"ema":"N/A","final_score":0,"distance":None,"distance_pct":None,"up_probability":50,"down_probability":50}
    rs=process_round_signal(ticker,sig,market,seconds); auto_trade_tick(ticker,market,rs); state=rs.get("round_state"); active=state.get("active_direction") if state else None
    update_micro_tape(ticker,live); reader=closing_reader(sig,rs,seconds,micro_reading()); delta=(sig["price"]-target) if target else 0; pct=delta/target*100 if target else 0
    chart,labels=build_real_line_chart(btc_df,live,target,seconds); auto=bool(st.session_state.auto_enabled); mode_on=bool(st.session_state.signal_mode); close_txt=close_clock(market or {}); current_cls="green" if delta>=0 else "red"; current_arrow="↑" if delta>=0 else "↓"
    hc1,hc2=st.columns([3.2,1.05],vertical_alignment="top")
    with hc1: st.markdown('<div class="crit"><div class="asset"><div class="coin">₿</div><div><div class="kicker">BTC · 15 MIN</div><div class="name">BTC/USD ▼</div></div></div></div>',unsafe_allow_html=True)
    with hc2:
        st.markdown('<div class="auto-label">TRADING AUTOMÁTICO</div>',unsafe_allow_html=True)
        if st.button("⏻",key="auto_power_real",use_container_width=True):
            if auto: st.session_state.auto_enabled=False; st.rerun()
            elif not st.session_state.kalshi_auth_ok: st.warning("Conecta Kalshi en Ajustes para activar el trading automático.")
            else: st.session_state.auto_enabled=True; st.rerun()
        st.markdown(f'<div class="auto-state {"on" if auto else ""}">● {"ENCENDIDO" if auto else "APAGADO"}</div>',unsafe_allow_html=True)
    scale_html="".join(f'<span style="top:{i*24}%">{v}</span>' for i,v in enumerate(labels)); past_html=past_markets_html(); target_text=f"${target:,.2f}" if target else "--"; now=datetime.now(timezone.utc).timestamp()
    top_html=f'<div class="crit"><div class="market"><div><div class="lab">OBJETIVO</div><div class="price">{target_text}</div><div class="sub">Cierre {close_txt}</div><div class="count">⌛&nbsp; {format_countdown(seconds)}</div></div><div><div class="lab {current_cls}">PRECIO ACTUAL {current_arrow}</div><div class="price {current_cls}">${sig["price"]:,.2f}</div><div class="sub {current_cls}">{delta:+,.2f} ({pct:+.3f}%)</div></div></div><div class="live"><i></i>En vivo</div><div class="chartwrap"><div class="sidebar"></div><div class="plot">{chart}</div><div class="scale">{scale_html}</div></div><div class="times"><span>{datetime.fromtimestamp(now-900, timezone.utc).astimezone().strftime("%H:%M:%S")}</span><span>{datetime.fromtimestamp(now-600, timezone.utc).astimezone().strftime("%H:%M:%S")}</span><span>{datetime.fromtimestamp(now-300, timezone.utc).astimezone().strftime("%H:%M:%S")}</span><span>{datetime.fromtimestamp(now, timezone.utc).astimezone().strftime("%H:%M:%S")}</span></div><div class="past">MERCADOS ANTERIORES&nbsp;&nbsp;<span class="arr">{past_html}</span></div></div>'
    st.markdown(top_html,unsafe_allow_html=True)
    with st.container(border=True):
        mc1,mc2=st.columns([3.25,1],vertical_alignment="center")
        with mc1: st.markdown('<div class="crit"><div class="guide"><div class="guideicon">⌁</div><div><small class="guide-small">GUÍA MANUAL</small><div class="mtitle">Modo señales</div></div></div></div>',unsafe_allow_html=True)
        with mc2: new_mode=st.toggle("Modo señales",value=mode_on,key="signal_switch_real",label_visibility="collapsed")
        if new_mode != st.session_state.signal_mode: st.session_state.signal_mode=new_mode; st.rerun()
        mode_on=bool(new_mode); sigtext=(active or "ESPERANDO") if mode_on else "DESACTIVADO"; sigcolor="#31db86" if active=="UP" else "#ff626b" if active=="DOWN" else "#ffbd39"
        if not mode_on: sigcolor="#ffbd39"
        note=(reader["headline"]+" · "+str(reader["percent"])+"%") if mode_on else "Actívalo para mostrar la señal de tu motor v4.6.1."
        st.markdown(f'<div class="crit"><div class="minner"><small>MERCADO ACTUAL · MOTOR v4.6.1</small><div class="msig" style="color:{sigcolor}">{sigtext}</div><div class="mnote">{note}</div></div></div>',unsafe_allow_html=True)

page=st.session_state.crit_page
if page=="Bot": bot_page()
elif page=="Operaciones": operations_page()
elif page=="Saldo": balance_page()
elif page=="Ajustes": settings_page()

# Barra inferior fija, una sola fila.
st.markdown('<div class="nav-spacer"></div>',unsafe_allow_html=True)
cols=st.columns(4,gap="small")
for col,label,icon in zip(cols,["Bot","Operaciones","Saldo","Ajustes"],["▣","↗","▤","⚙"]):
    with col:
        if st.button(f"{icon}\n{label}",key=f"nav_{label}",use_container_width=True,type="primary" if st.session_state.crit_page==label else "secondary"):
            st.session_state.crit_page=label; st.rerun()


st.markdown(r"""<style>
.block-container{max-width:430px!important;padding:12px 12px 100px!important}.asset{padding-top:4px}.coin{width:39px!important;height:39px!important}.auto-label{text-align:center;font-size:7px;color:#a0aaa5;font-weight:900;white-space:nowrap;margin-top:3px}.auto-state{text-align:center;color:#ff626b;font-size:8px;font-weight:900}.auto-state.on{color:#31db86}.market{padding-top:13px!important}.live{padding-right:61px!important}.chartwrap{height:300px!important;grid-template-columns:7px 1fr 57px!important;gap:7px!important}.times{padding:2px 58px 6px 13px!important}.past{padding:1px 0 7px 3px!important}.guide-small{color:#2ad67f!important;font-size:7px!important;font-weight:1000!important;letter-spacing:1px}.nav-spacer{height:70px}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stToggle"]{background:transparent!important;border:0!important;padding:0!important;display:flex!important;justify-content:flex-end!important}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stToggle"] label{justify-content:flex-end!important}
/* top-right real power button */
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:last-child div.stButton>button#auto_power_real{border-radius:50%!important}
/* bottom navigation: the final horizontal row stays fixed */
div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):last-of-type{position:fixed!important;left:50%!important;transform:translateX(-50%)!important;bottom:0!important;width:min(430px,100vw)!important;height:72px!important;background:#020705!important;border-top:1px solid #26342e!important;z-index:999!important;padding:5px 8px!important}
</style>""",unsafe_allow_html=True)


st.markdown(r"""<style>
/* FINAL MOBILE MATCH OVERRIDES */
.block-container{padding:12px 12px 86px!important}
/* top-right power: remove the Streamlit rectangle completely */
[data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"]:last-child .stButton{display:flex!important;justify-content:center!important}
[data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"]:last-child .stButton>button{
 width:46px!important;height:46px!important;min-height:46px!important;max-width:46px!important;padding:0!important;
 border-radius:50%!important;border:1.5px solid #7d353c!important;background:#07100c!important;color:#ff626b!important;
 font-size:24px!important;line-height:1!important;box-shadow:none!important;margin:3px auto 1px!important
}
[data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"]:last-child .stButton>button p{font-size:24px!important;line-height:1!important}
.auto-label{font-size:8px!important;margin-bottom:0!important}.auto-state{font-size:9px!important}
/* chart proportions closer to reference */
.chartwrap{height:310px!important}.plot svg polyline{vector-effect:non-scaling-stroke}.live{margin-top:-3px!important}
/* signal card: no second outer Streamlit-looking panel */
[data-testid="stVerticalBlockBorderWrapper"]{padding:10px 11px!important;border:1px solid #18543a!important;background:linear-gradient(180deg,#06140e,#04100b)!important}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"]{align-items:center!important}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stToggle"]{background:transparent!important;border:0!important;padding:0!important}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stToggle"]>label{justify-content:flex-end!important}
/* bottom nav: flat, fixed, one row like reference */
div[data-testid="stHorizontalBlock"]:last-of-type{position:fixed!important;left:50%!important;transform:translateX(-50%)!important;bottom:0!important;width:min(430px,100vw)!important;height:70px!important;background:#020705!important;border-top:1px solid #26342e!important;z-index:9999!important;padding:4px 8px!important;gap:0!important}
div[data-testid="stHorizontalBlock"]:last-of-type .stButton>button{
 border:0!important;background:transparent!important;box-shadow:none!important;border-radius:0!important;min-height:58px!important;padding:3px 0!important;color:#8d9994!important
}
div[data-testid="stHorizontalBlock"]:last-of-type .stButton>button[kind="primary"]{color:#24d77d!important;background:transparent!important}
div[data-testid="stHorizontalBlock"]:last-of-type .stButton>button p{font-size:9px!important;line-height:1.8!important}
.nav-spacer{height:58px!important}
</style>""",unsafe_allow_html=True)

# =========================================================
# COMPACT MOBILE PROPORTIONS — keep logic/data unchanged
# =========================================================
st.markdown(r'''<style>
/* Fit the complete bot view much closer to the reference on iPhone. */
.block-container{max-width:430px!important;padding:7px 10px 76px!important}
div[data-testid="stVerticalBlock"]{gap:.18rem!important}

/* header */
.asset{padding-top:0!important}.coin{width:36px!important;height:36px!important;font-size:23px!important}
.kicker{font-size:8px!important}.name{font-size:18px!important;margin-top:1px!important}
.auto-label{font-size:7px!important;margin-top:0!important}
[data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"]:last-child .stButton>button{
 width:40px!important;height:40px!important;min-height:40px!important;max-width:40px!important;font-size:21px!important;margin:0 auto!important
}
[data-testid="stHorizontalBlock"]:first-of-type [data-testid="stColumn"]:last-child .stButton>button p{font-size:21px!important}
.auto-state{font-size:8px!important;line-height:1!important;margin-top:1px!important}

/* target/current block */
.market{padding:5px 2px 0!important;gap:8px!important}
.market>div+div{padding-left:9px!important}
.lab{font-size:8px!important}.price{font-size:22px!important;margin-top:3px!important}.sub{font-size:9px!important;margin-top:2px!important}
.count{font-size:17px!important;margin-top:7px!important}.live{font-size:8px!important;padding-right:58px!important;margin-top:-6px!important;height:12px!important}

/* chart — this was the part making the page huge */
.chartwrap{height:238px!important;margin-top:0!important;grid-template-columns:6px 1fr 54px!important;gap:5px!important}
.scale{font-size:7px!important}.times{font-size:6.5px!important;padding:1px 54px 2px 11px!important}
.past{font-size:7.5px!important;padding:0 0 3px 2px!important}.past .arr{font-size:13px!important;letter-spacing:1px!important}

/* signal card */
[data-testid="stVerticalBlockBorderWrapper"]{padding:7px 9px!important;border-radius:13px!important}
.guide{gap:7px!important}.guideicon{width:30px!important;height:30px!important;border-radius:9px!important}
.guide-small{font-size:6.5px!important}.mtitle{font-size:18px!important;margin-top:0!important}
.minner{min-height:62px!important;padding:8px 10px!important;margin-top:6px!important;border-radius:10px!important}
.minner small{font-size:6.5px!important}.msig{font-size:20px!important;margin:4px 0!important}.mnote{font-size:7.5px!important;line-height:1.2!important}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stToggle"]{transform:scale(.88);transform-origin:right center!important}

/* bottom navigation */
div[data-testid="stHorizontalBlock"]:last-of-type{height:61px!important;padding:2px 7px!important}
div[data-testid="stHorizontalBlock"]:last-of-type .stButton>button{min-height:51px!important;padding:1px 0!important}
div[data-testid="stHorizontalBlock"]:last-of-type .stButton>button p{font-size:8px!important;line-height:1.55!important}
.nav-spacer{height:50px!important}
</style>''', unsafe_allow_html=True)
