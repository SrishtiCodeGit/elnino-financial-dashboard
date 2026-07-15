"""
El Nino & Financial Markets — Research Dashboard
Author  : Srishti Chauhan
Advisor : Prof. Haralambos Kostakopoulos
Year    : 2026
Run     : python3 -m streamlit run dashboard/app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="El Nino Financial Risk | Research Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colour tokens ──────────────────────────────────────────────────────────────
BG_PAGE    = "#F0F4F8"
BG_CARD    = "#FFFFFF"
BG_SIDEBAR = "#08111E"      # deep navy
BG_SIDEBAR2= "#040C15"      # darker for brand block
BORDER     = "#E2E8F0"
BORDER_MED = "#CBD5E1"

TX_H    = "#0F172A"
TX_BODY = "#334155"
TX_MUTED= "#64748B"

BLUE    = "#1D4ED8"
BLUE_LT = "#3B82F6"
BLUE_BG = "#EFF6FF"
RED     = "#B91C1C"
RED_LT  = "#EF4444"
GREEN   = "#047857"
AMBER   = "#B45309"
AMBER_BG= "#FFFBEB"
SLATE   = "#475569"

PHASE_CLR = {
    "Super El Nino":    "#EF4444",
    "Strong El Nino":   "#F87171",
    "Moderate El Nino": "#F59E0B",
    "Weak El Nino":     "#D97706",
    "Neutral":          "#94A3B8",
    "La Nina":          "#60A5FA",
}

EL_NINO_EVENTS = [
    ("1972-06-01","1973-03-01","1972-73",       "rgba(185,28,28,0.06)"),
    ("1982-06-01","1983-06-01","1982-83 Super", "rgba(185,28,28,0.10)"),
    ("1997-04-01","1998-05-01","1997-98 Super", "rgba(185,28,28,0.10)"),
    ("2015-04-01","2016-05-01","2015-16 Super", "rgba(185,28,28,0.10)"),
    ("2023-06-01","2024-03-01","2023-24",       "rgba(185,28,28,0.06)"),
]

CHART = dict(
    paper_bgcolor=BG_CARD, plot_bgcolor=BG_CARD,
    font=dict(color=TX_BODY, family="Inter, system-ui, sans-serif", size=11),
    xaxis=dict(gridcolor="#F1F5F9", zerolinecolor=BORDER_MED, linecolor=BORDER,
               tickfont=dict(color=TX_MUTED, size=10), showgrid=True),
    yaxis=dict(gridcolor="#F1F5F9", zerolinecolor=BORDER_MED, linecolor=BORDER,
               tickfont=dict(color=TX_MUTED, size=10), showgrid=True),
    margin=dict(t=48, b=32, l=12, r=16),
    legend=dict(bgcolor=BG_CARD, bordercolor=BORDER, borderwidth=1,
                font=dict(color=TX_BODY, size=10)),
    hoverlabel=dict(bgcolor=BG_CARD, bordercolor=BORDER_MED,
                    font=dict(color=TX_H, size=11)),
    title_font=dict(color=TX_H, size=13, family="Inter, system-ui, sans-serif"),
    title_x=0, title_xanchor="left", title_pad=dict(l=2, t=2),
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*, html, body, [class*="css"] {{
    font-family: 'Inter', system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}}
.stApp {{ background: {BG_PAGE}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stDecoration"], [data-testid="stToolbar"] {{ display: none; }}

/* ── Deep navy sidebar ── */
[data-testid="stSidebar"] {{
    background: {BG_SIDEBAR} !important;
    border-right: 1px solid rgba(59,130,246,0.12);
}}
[data-testid="stSidebar"] * {{ color: #CBD5E1 !important; }}
[data-testid="stSidebar"] section > div {{ padding-top: 0 !important; }}

[data-testid="stSidebar"] .stRadio > label {{ display: none !important; }}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
    gap: 2px; display: flex; flex-direction: column; padding: 6px 0;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
    padding: 10px 20px !important; border-radius: 0 !important;
    color: #64748B !important; font-size: 0.83rem !important;
    font-weight: 400 !important; border: none !important;
    background: transparent !important; cursor: pointer;
    transition: all 0.15s ease;
    border-left: 3px solid transparent !important;
    letter-spacing: 0.01em;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
    background: rgba(59,130,246,0.08) !important;
    color: #E2E8F0 !important;
    border-left-color: rgba(59,130,246,0.5) !important;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[aria-checked="true"] {{
    background: rgba(59,130,246,0.15) !important;
    color: #F1F5F9 !important;
    border-left-color: {BLUE_LT} !important;
    font-weight: 600 !important;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child {{
    display: none !important;
}}

.main .block-container {{ padding: 2rem 2.2rem 2rem !important; max-width: 1400px; }}

/* ── KPI cards ── */
.kpi {{ background:{BG_CARD}; border:1px solid {BORDER}; border-radius:10px;
        padding:18px 20px 16px; height:100%; box-shadow:0 1px 3px rgba(0,0,0,0.04); }}
.kpi-label {{ font-size:0.7rem; font-weight:600; color:{TX_MUTED}; text-transform:uppercase;
              letter-spacing:0.08em; margin-bottom:8px; }}
.kpi-value {{ font-size:1.75rem; font-weight:700; color:{TX_H}; line-height:1; letter-spacing:-0.5px; }}
.kpi-sub   {{ font-size:0.75rem; color:{TX_MUTED}; margin-top:5px; }}
.kpi-positive {{ color:{GREEN}; }}
.kpi-negative {{ color:{RED}; }}
.kpi-neutral  {{ color:{TX_H}; }}

.page-header {{ border-bottom:2px solid {BORDER}; padding-bottom:14px; margin-bottom:22px; }}
.page-title  {{ font-size:1.4rem; font-weight:700; color:{TX_H}; letter-spacing:-0.4px; margin:0; }}
.page-sub    {{ font-size:0.82rem; color:{TX_MUTED}; margin-top:4px; }}

.sec-label {{ font-size:0.68rem; font-weight:700; color:{TX_MUTED}; text-transform:uppercase;
              letter-spacing:0.1em; margin:22px 0 8px; display:flex; align-items:center; gap:8px; }}
.sec-label::after {{ content:''; flex:1; height:1px; background:{BORDER}; }}

.source-badge {{ display:inline-flex; align-items:center; font-size:0.68rem; font-weight:500;
                  color:{TX_MUTED}; background:#F8FAFC; border:1px solid {BORDER};
                  border-radius:4px; padding:2px 7px; margin:2px 3px 2px 0; }}

.callout {{ background:{BLUE_BG}; border:1px solid #BFDBFE; border-left:3px solid {BLUE};
            border-radius:0 8px 8px 0; padding:12px 16px; font-size:0.82rem;
            color:{TX_BODY}; margin:12px 0; line-height:1.6; }}
.callout-amber {{ background:{AMBER_BG}; border:1px solid #FDE68A; border-left:3px solid {AMBER};
                  border-radius:0 8px 8px 0; padding:12px 16px; font-size:0.82rem;
                  color:{TX_BODY}; margin:12px 0; line-height:1.6; }}

/* ── Sidebar brand ── */
.sb-brand  {{ background:{BG_SIDEBAR2}; padding:22px 18px 18px;
              border-bottom:1px solid rgba(59,130,246,0.1); margin-bottom:4px; }}
.sb-dot    {{ width:8px; height:8px; border-radius:50%; background:{BLUE_LT};
              display:inline-block; margin-right:8px; animation:sbPulse 2s ease-in-out infinite; }}
@keyframes sbPulse{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}
.sb-title  {{ font-size:0.92rem; font-weight:700; color:#F1F5F9 !important;
              letter-spacing:-0.2px; display:flex; align-items:center; }}
.sb-sub    {{ font-size:0.7rem; color:#334155 !important; margin-top:5px; line-height:1.4; }}
.sb-divider{{ height:1px; background:rgba(255,255,255,0.05); margin:4px 18px; }}
.sb-nav-lbl{{ font-size:0.58rem; font-weight:700; color:#1E3A5F !important;
              text-transform:uppercase; letter-spacing:0.12em; padding:14px 18px 6px; }}
.sb-info   {{ padding:14px 18px; }}
.sb-info-hd{{ font-size:0.58rem; font-weight:700; color:#1E3A5F !important;
              text-transform:uppercase; letter-spacing:0.12em; margin-bottom:10px; }}
.sb-enso   {{ background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.15);
              border-radius:8px; padding:12px 14px; margin-bottom:14px; }}
.sb-enso-v {{ font-size:1.5rem; font-weight:800; line-height:1; letter-spacing:-1px; }}
.sb-enso-p {{ font-size:0.72rem; color:#475569 !important; margin-top:4px; }}
.sb-src    {{ font-size:0.73rem; color:#334155 !important; line-height:2; }}
.sb-adv    {{ font-size:0.73rem; color:#334155 !important; line-height:1.8; }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def sbadge(*sources):
    html = "".join(f'<span class="source-badge">Source: {s}</span>' for s in sources)
    st.markdown(f'<div style="margin-top:4px;margin-bottom:2px">{html}</div>', unsafe_allow_html=True)

def sec(label):
    st.markdown(f'<div class="sec-label">{label}</div>', unsafe_allow_html=True)

def kpi_card(label, value, sub=None, color="neutral"):
    s = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return (f'<div class="kpi"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value kpi-{color}">{value}</div>{s}</div>')

def ph(title, subtitle=""):
    s = f'<div class="page-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f'<div class="page-header"><div class="page-title">{title}</div>{s}</div>',
                unsafe_allow_html=True)

def safe_1y(series, n=252):
    s = series.dropna()
    if len(s) > n:  return (s.iloc[-1] / s.iloc[-n] - 1) * 100
    if len(s) > 1:  return (s.iloc[-1] / s.iloc[0]  - 1) * 100
    return 0.0

def classify_oni(v):
    if   v >= 2.0:  return "Super El Nino"
    elif v >= 1.5:  return "Strong El Nino"
    elif v >= 1.0:  return "Moderate El Nino"
    elif v >= 0.5:  return "Weak El Nino"
    elif v <= -0.5: return "La Nina"
    return "Neutral"

def add_el_nino_bands(fig, row=None, col=None):
    for s, e, lbl, fc in EL_NINO_EVENTS:
        kw = dict(x0=s, x1=e, fillcolor=fc, line_width=0, layer="below",
                  annotation_text=lbl,
                  annotation=dict(font=dict(size=7.5, color=RED), textangle=-90,
                                  bgcolor="rgba(255,255,255,0.7)",
                                  bordercolor="rgba(185,28,28,0.2)", borderwidth=0.5))
        if row: kw.update(row=row, col=col)
        fig.add_vrect(**kw)

def add_recession_bands(fig, df_nber, row=None, col=None):
    in_rec, start = False, None
    for date, r in df_nber.iterrows():
        if r["recession"] == 1 and not in_rec:
            in_rec, start = True, date
        elif r["recession"] == 0 and in_rec:
            kw = dict(x0=str(start), x1=str(date),
                      fillcolor="rgba(100,116,139,0.10)", line_width=0, layer="below")
            if row: kw.update(row=row, col=col)
            fig.add_vrect(**kw)
            in_rec = False


# ── Data ───────────────────────────────────────────────────────────────────────
@st.cache_data
def load_oni():
    df = pd.read_csv("data/raw/oni_enso.csv")
    m  = {"DJF":1,"JFM":2,"FMA":3,"MAM":4,"AMJ":5,"MJJ":6,
          "JJA":7,"JAS":8,"ASO":9,"SON":10,"OND":11,"NDJ":12}
    df["month"] = df["season"].map(m)
    df["date"]  = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))
    return df.set_index("date").sort_index()

@st.cache_data
def load_fin():
    return pd.read_csv("data/raw/financial_markets.csv",
                       parse_dates=["date"], index_col="date").sort_index()

@st.cache_data
def load_comm():
    return pd.read_csv("data/raw/commodities.csv",
                       parse_dates=["date"], index_col="date").sort_index()

@st.cache_data
def load_crypto():
    return pd.read_csv("data/raw/crypto_prices.csv",
                       parse_dates=["date"], index_col="date").sort_index()

@st.cache_data
def load_nber():
    return pd.read_csv("data/raw/nber_recession.csv",
                       parse_dates=["date"], index_col="date").sort_index()

oni    = load_oni()
fin    = load_fin()
comm   = load_comm()
crypto = load_crypto()
nber   = load_nber()

latest_oni   = float(oni["ONI"].iloc[-1])
latest_phase = str(oni["phase"].iloc[-1])
latest_date  = oni.index[-1].strftime("%b %Y")
phase_col    = PHASE_CLR.get(latest_phase, SLATE)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sb-brand">
        <div class="sb-title"><span class="sb-dot"></span>El Nino Financial Risk</div>
        <div class="sb-sub">Research Dashboard · Srishti Chauhan<br>Supervisor: Prof. Haralambos Kostakopoulos</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sb-nav-lbl">Navigation</div>', unsafe_allow_html=True)

    page = st.radio("nav", [
        "Home",
        "ENSO Monitor",
        "Financial Markets",
        "Commodities",
        "Cryptocurrency",
        "Insurance & Banking",
    ], label_visibility="collapsed")

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sb-info">
        <div class="sb-info-hd">Live ENSO Status</div>
        <div class="sb-enso">
            <div class="sb-enso-v" style="color:{phase_col}">{latest_oni:+.2f} °C</div>
            <div class="sb-enso-p">{latest_phase} · {latest_date}</div>
        </div>
        <div class="sb-info-hd">Data Sources</div>
        <div class="sb-src">
            NOAA Climate Prediction Center<br>
            Yahoo Finance (yfinance)<br>
            NBER Recession Dates<br>
            NCEI Billion-Dollar Disasters
        </div>
        <br>
        <div class="sb-info-hd">Year</div>
        <div class="sb-adv">2026</div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
if page == "Home":
    HOME_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,system-ui,-apple-system,sans-serif}
body{background:#F0F4F8;color:#334155;-webkit-font-smoothing:antialiased;overflow-x:hidden}

/* ── HERO ── */
.hero{
  position:relative;overflow:hidden;
  background:#040C15;
  padding:0;min-height:540px;
  display:flex;flex-direction:column;
}
.hero-canvas{position:absolute;inset:0;width:100%;height:100%}

/* gradient overlays */
.hero-overlay{
  position:absolute;inset:0;pointer-events:none;
  background:
    radial-gradient(ellipse 70% 80% at 10% 50%, rgba(29,78,216,0.18) 0%, transparent 65%),
    radial-gradient(ellipse 50% 60% at 90% 20%, rgba(99,102,241,0.14) 0%, transparent 60%),
    radial-gradient(ellipse 40% 50% at 50% 90%, rgba(16,185,129,0.08) 0%, transparent 50%);
  animation:overlayPulse 10s ease-in-out infinite alternate;
}
@keyframes overlayPulse{0%{opacity:0.7}100%{opacity:1}}

.hero-content{
  position:relative;z-index:2;
  padding:52px 48px 0;flex:1;
}

/* wave at bottom */
.hero-wave{position:relative;z-index:2;margin-top:32px;line-height:0}
.hero-wave svg{display:block;width:100%}

.hero-badge{
  display:inline-flex;align-items:center;gap:8px;
  background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.25);
  border-radius:999px;padding:5px 14px;
  font-size:0.7rem;font-weight:700;color:#60A5FA;
  text-transform:uppercase;letter-spacing:0.1em;
  margin-bottom:22px;
  animation:fadeUp 0.5s ease both;
}
.badge-dot{width:6px;height:6px;border-radius:50%;background:#34D399;
           animation:blinkDot 2s ease-in-out infinite}
@keyframes blinkDot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.4;transform:scale(0.7)}}

.hero-title{
  font-size:2.15rem;font-weight:800;color:#F8FAFC;
  letter-spacing:-0.8px;line-height:1.22;margin-bottom:18px;max-width:680px;
  animation:fadeUp 0.5s 0.08s ease both;
}
.hero-title .hl{
  background:linear-gradient(135deg,#60A5FA 0%,#A78BFA 50%,#34D399 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  background-size:200% 200%;animation:gradMove 5s ease infinite;
}
@keyframes gradMove{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}

.hero-sub{
  font-size:0.93rem;color:rgba(203,213,225,0.8);max-width:580px;
  line-height:1.7;margin-bottom:24px;
  animation:fadeUp 0.5s 0.16s ease both;
}
.hero-author{
  font-size:0.75rem;color:rgba(71,85,105,0.9);letter-spacing:0.01em;
  margin-bottom:26px;animation:fadeUp 0.5s 0.24s ease both;
}
.enso-pill{
  display:inline-flex;align-items:center;gap:10px;
  background:rgba(15,30,60,0.7);
  border:1px solid rgba(59,130,246,0.2);
  border-radius:999px;padding:8px 18px;
  animation:fadeUp 0.5s 0.32s ease both;
  backdrop-filter:blur(4px);
}
.enso-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0;
          animation:ringPulse 2.5s ease-in-out infinite}
@keyframes ringPulse{
  0%{box-shadow:0 0 0 0 currentColor;opacity:1}
  70%{box-shadow:0 0 0 7px transparent;opacity:0.8}
  100%{box-shadow:0 0 0 0 transparent;opacity:1}
}
.enso-text{font-size:0.82rem;color:rgba(226,232,240,0.9)}

/* ── TICKER ── */
.ticker{
  background:#060F1C;border-top:1px solid rgba(59,130,246,0.12);
  border-bottom:1px solid rgba(59,130,246,0.08);
  padding:10px 0;overflow:hidden;
}
.ticker-track{display:flex;width:max-content;animation:tickerMove 40s linear infinite}
.ticker-track:hover{animation-play-state:paused}
.ticker-item{
  white-space:nowrap;padding:0 40px;font-size:0.72rem;
  color:#475569;display:flex;align-items:center;gap:10px;
}
.ticker-item strong{color:#60A5FA}
.ticker-sep{color:#1E3A5F}
@keyframes tickerMove{from{transform:translateX(0)}to{transform:translateX(-50%)}}

/* ── STATS ── */
.stats{display:grid;grid-template-columns:repeat(4,1fr);background:#fff;border-bottom:1px solid #E2E8F0}
.stat{padding:26px 24px;text-align:center;border-right:1px solid #E2E8F0;animation:fadeUp 0.5s ease both}
.stat:last-child{border-right:none}
.stat-num{font-size:2.4rem;font-weight:800;color:#1D4ED8;letter-spacing:-2px;line-height:1}
.stat-lbl{font-size:0.77rem;color:#64748B;margin-top:6px;line-height:1.45}

/* ── CONTENT ── */
.content{padding:34px 48px 40px}

.rq{
  background:linear-gradient(135deg,#EFF6FF 0%,#F0F9FF 100%);
  border:1px solid #BFDBFE;border-left:4px solid #1D4ED8;
  border-radius:0 10px 10px 0;padding:18px 22px;margin-bottom:34px;
  animation:fadeUp 0.5s 0.1s ease both;
}
.rq-tag{font-size:0.65rem;font-weight:700;color:#1D4ED8;text-transform:uppercase;
         letter-spacing:0.12em;margin-bottom:8px}
.rq-text{font-size:0.98rem;font-weight:600;color:#0F172A;line-height:1.5}

.sec-hd{
  font-size:0.67rem;font-weight:700;color:#94A3B8;text-transform:uppercase;
  letter-spacing:0.13em;margin:30px 0 13px;
  display:flex;align-items:center;gap:10px;
}
.sec-hd::after{content:'';flex:1;height:1px;background:#E2E8F0}

/* ── SECTION CARDS ── */
.cards{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:8px}
.card{
  background:#fff;border:1px solid #E2E8F0;border-radius:12px;
  padding:20px 14px 16px;cursor:pointer;
  transition:transform 0.2s ease,box-shadow 0.2s ease,border-color 0.2s ease;
  animation:fadeUp 0.5s ease both;position:relative;overflow:hidden;
}
.card::before{
  content:'';position:absolute;inset:0;opacity:0;
  background:linear-gradient(135deg,rgba(255,255,255,0) 0%,rgba(59,130,246,0.04) 100%);
  transition:opacity 0.2s;
}
.card:hover{
  transform:translateY(-6px);
  box-shadow:0 16px 40px rgba(29,78,216,0.14),0 4px 12px rgba(29,78,216,0.06);
  border-color:#93C5FD;
}
.card:hover::before{opacity:1}
.card-num{
  width:36px;height:36px;border-radius:9px;
  display:flex;align-items:center;justify-content:center;
  font-size:0.72rem;font-weight:800;color:#fff;
  margin-bottom:13px;letter-spacing:0.02em;
  box-shadow:0 4px 12px rgba(0,0,0,0.2);
}
.card-title{font-size:0.85rem;font-weight:700;color:#0F172A;margin-bottom:7px}
.card-desc{font-size:0.72rem;color:#64748B;line-height:1.55}
.card-arrow{
  font-size:0.72rem;color:#93C5FD;margin-top:10px;
  opacity:0;transition:opacity 0.2s,transform 0.2s;transform:translateX(-4px);
}
.card:hover .card-arrow{opacity:1;transform:translateX(0)}

/* ── HYPOTHESES ── */
.hyp-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:8px}
.hyp{
  background:#fff;border:1px solid #E2E8F0;border-radius:10px;
  padding:16px 18px;animation:fadeUp 0.5s ease both;
  transition:box-shadow 0.18s;
}
.hyp:hover{box-shadow:0 4px 16px rgba(0,0,0,0.07)}
.hyp-num{font-size:0.65rem;font-weight:800;color:#1D4ED8;text-transform:uppercase;
          letter-spacing:0.12em;margin-bottom:8px}
.hyp-text{font-size:0.77rem;color:#334155;line-height:1.6}

/* ── SOURCES ── */
.sources{display:flex;flex-wrap:wrap;gap:8px}
.src{
  background:#F8FAFC;border:1px solid #E2E8F0;border-radius:6px;
  padding:6px 12px;font-size:0.72rem;color:#475569;
  transition:all 0.15s;
}
.src:hover{border-color:#60A5FA;background:#EFF6FF;color:#1D4ED8}

.footer{margin-top:32px;padding:14px 0 2px;border-top:1px solid #E2E8F0;
         font-size:0.7rem;color:#94A3B8;line-height:2}

@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
</style>
</head>
<body>
<div id="root"></div>
<script>
(function(){
const { createElement:h, useState, useEffect, useRef } = React;

/* ── Dynamic values injected from Python ── */
const ONI_VAL   = "##ONI_VAL##";
const ONI_PHASE = "##ONI_PHASE##";
const ONI_DATE  = "##ONI_DATE##";
const PHASE_CLR = "##PHASE_CLR##";

/* ── Navigate to a Streamlit page by clicking its sidebar radio ── */
function navigateTo(pageLabel) {
  try {
    const labels = window.parent.document.querySelectorAll(
      '[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label'
    );
    for (const lbl of labels) {
      if (lbl.textContent.trim() === pageLabel) { lbl.click(); return; }
    }
  } catch(e) { /* cross-origin or not found */ }
}

/* ── Canvas: particles + ONI line ── */
function ClimateCanvas() {
  const ref = useRef(null);
  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    function resize() {
      canvas.width  = canvas.offsetWidth  || 800;
      canvas.height = canvas.offsetHeight || 540;
    }
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(canvas);

    /* Particles */
    const types = [
      { color:'rgba(96,165,250,', count:28 },   // blue (La Nina)
      { color:'rgba(248,113,113,', count:18 },   // red  (El Nino)
      { color:'rgba(52,211,153,',  count:10 },   // green (neutral)
      { color:'rgba(255,255,255,', count:14 },   // white
    ];
    const particles = [];
    types.forEach(({ color, count }) => {
      for (let i = 0; i < count; i++) {
        particles.push({
          x: Math.random(), y: Math.random(),
          vx: (Math.random()-0.5)*0.0004,
          vy: (Math.random()-0.5)*0.0002,
          r: Math.random()*2+0.6,
          a: Math.random()*0.5+0.15,
          phase: Math.random()*Math.PI*2,
          color,
        });
      }
    });

    /* Simplified ONI curve (normalised 0-1 x, anomaly y) */
    const oniCurve = [
      [0,0.3],[0.04,-0.8],[0.08,-0.4],[0.12,0.1],[0.17,0.5],
      [0.22,0.3],[0.27,-0.4],[0.31,-0.9],[0.36,2.2],[0.4,1.0],
      [0.44,-0.5],[0.48,-0.8],[0.52,-0.3],[0.56,0.4],[0.61,2.4],
      [0.65,0.8],[0.68,-0.6],[0.72,-1.0],[0.76,-0.5],[0.80,0.3],
      [0.84,2.3],[0.88,0.6],[0.91,-0.6],[0.94,-0.3],[0.97,2.0],
      [1.0,0.4]
    ];

    let lineProgress = 0;
    let raf;
    const startTime = performance.now();

    function draw(ts) {
      const W = canvas.width, H = canvas.height;
      ctx.clearRect(0, 0, W, H);

      /* Background is CSS, so just clear */

      /* ONI line */
      lineProgress = Math.min((ts - startTime) / 5000, 1);
      const midY = H * 0.58, scaleY = H * 0.12;
      const visible = oniCurve.filter(p => p[0] <= lineProgress);
      if (visible.length >= 2) {
        ctx.save();
        ctx.beginPath();
        visible.forEach(([x, y], i) => {
          const px = x * W, py = midY - y * scaleY;
          i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
        });
        ctx.strokeStyle = 'rgba(59,130,246,0.18)';
        ctx.lineWidth = 1.8;
        ctx.lineJoin = 'round';
        ctx.stroke();

        /* Threshold lines */
        ['rgba(248,113,113,0.12)','rgba(96,165,250,0.12)'].forEach((c,i) => {
          const ty = midY - (i===0 ? 1 : -1) * 0.5 * scaleY;
          ctx.beginPath();
          ctx.moveTo(0,ty); ctx.lineTo(W,ty);
          ctx.strokeStyle = c; ctx.lineWidth = 0.8;
          ctx.setLineDash([4,8]);
          ctx.stroke(); ctx.setLineDash([]);
        });
        ctx.restore();
      }

      /* Particles */
      const t = ts * 0.001;
      particles.forEach(p => {
        p.x += p.vx + Math.sin(t * 0.5 + p.phase) * 0.00008;
        p.y += p.vy + Math.cos(t * 0.3 + p.phase) * 0.00004;
        if (p.x < -0.02) p.x = 1.02;
        if (p.x > 1.02)  p.x = -0.02;
        if (p.y < -0.02) p.y = 1.02;
        if (p.y > 1.02)  p.y = -0.02;

        ctx.beginPath();
        ctx.arc(p.x * W, p.y * H, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.color + p.a + ')';
        ctx.fill();
      });

      raf = requestAnimationFrame(draw);
    }
    raf = requestAnimationFrame(draw);
    return () => { cancelAnimationFrame(raf); ro.disconnect(); };
  }, []);

  return h('canvas', {
    ref,
    className: 'hero-canvas',
    style: { position:'absolute', inset:0, width:'100%', height:'100%' }
  });
}

/* ── Animated counter ── */
function Counter({ target, duration }) {
  const [n, setN] = useState(0);
  const done = useRef(false);
  useEffect(() => {
    if (done.current) return;
    done.current = true;
    const t0 = performance.now();
    function tick() {
      const p = Math.min((performance.now()-t0)/duration, 1);
      setN(Math.round((1-Math.pow(1-p,3))*target));
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }, []);
  return h('span', null, n);
}

/* ── Scrolling climate ticker ── */
function Ticker() {
  const items = [
    ['1997-98 Super El Niño', 'Peak ONI: +2.4 °C · Global GDP loss ~USD 5.7 trillion'],
    ['1982-83 Super El Niño', 'GDP losses sustained for 15+ years post-event'],
    ['VIX Volatility', 'Spikes 40–60% above baseline during major El Niño events'],
    ['Wheat Futures', 'Average +3% quarterly during El Niño vs +2.4% neutral periods'],
    ['Insurance Sector', 'Systematically underperforms S&P 500 during El Niño windows'],
    ['Bitcoin', 'Correlation with S&P 500 increases during El Niño stress periods'],
    ['NOAA Threshold', 'ONI ≥ +0.5 °C = El Niño · ONI ≤ −0.5 °C = La Niña'],
    ['2023-24 El Niño', 'Peak ONI +2.0 °C · Global agricultural disruption confirmed'],
    ['Climate Finance', '75 years of ENSO data reveal systematic financial market patterns'],
  ];

  const content = [...items, ...items].map(([key, val], i) =>
    h('span', { className:'ticker-item', key:i },
      h('strong', null, key), ' ', val,
      h('span', { className:'ticker-sep' }, '  ·  ')
    )
  );
  return h('div', { className:'ticker' },
    h('div', { className:'ticker-track' }, ...content)
  );
}

/* ── Section card ── */
const SECTIONS = [
  { num:'01', color:'#1D4ED8', gradient:'linear-gradient(135deg,#1D4ED8,#3B82F6)',
    title:'ENSO Monitor', page:'ENSO Monitor',
    desc:'ONI index 1950–2025, Super El Niño events, phase distribution and historical economic loss estimates.' },
  { num:'02', color:'#B45309', gradient:'linear-gradient(135deg,#B45309,#F59E0B)',
    title:'Financial Markets', page:'Financial Markets',
    desc:'S&P 500, VIX volatility, and equity returns segmented by ENSO phase over 35 years of data.' },
  { num:'03', color:'#047857', gradient:'linear-gradient(135deg,#047857,#10B981)',
    title:'Commodities', page:'Commodities',
    desc:'Wheat, corn, coffee, crude oil and gold futures — supply disruption and price shock analysis.' },
  { num:'04', color:'#7C3AED', gradient:'linear-gradient(135deg,#7C3AED,#A78BFA)',
    title:'Cryptocurrency', page:'Cryptocurrency',
    desc:'Bitcoin and Ethereum behaviour during El Niño cycles — emerging asset class correlation study.' },
  { num:'05', color:'#B91C1C', gradient:'linear-gradient(135deg,#B91C1C,#EF4444)',
    title:'Insurance & Banking', page:'Insurance & Banking',
    desc:'Sector ETF performance vs S&P 500 — testing whether climate tail risk is priced into valuations.' },
];

function SectionCard({ num, gradient, title, page: pg, desc, delay }) {
  return h('div', {
    className:'card', style:{ animationDelay:delay },
    onClick: () => navigateTo(pg),
    title: `Open ${title} dashboard`,
  },
    h('div', { className:'card-num', style:{ background: gradient } }, num),
    h('div', { className:'card-title' }, title),
    h('div', { className:'card-desc' }, desc),
    h('div', { className:'card-arrow' }, 'Open dashboard →')
  );
}

/* ── Root ── */
function App() {
  return h('div', null,
    /* HERO */
    h('div', { className:'hero' },
      h(ClimateCanvas),
      h('div', { className:'hero-overlay' }),
      h('div', { className:'hero-content' },
        h('div', { className:'hero-badge' },
          h('span', { className:'badge-dot' }), 'Live Research Dashboard  ·  2026'
        ),
        h('h1', { className:'hero-title' },
          'Is the Financial Industry Prepared', h('br'),
          'for a ', h('span', { className:'hl' }, 'Super El Niño'), '?'
        ),
        h('p', { className:'hero-sub' },
          'A data-driven analysis of 75 years of ENSO cycles and their cascading effects on global financial markets, commodity supply chains, and emerging asset classes.'
        ),
        h('div', { className:'hero-author' },
          'Srishti Chauhan  ·  Advisor: Prof. Haralambos Kostakopoulos  ·  2026'
        ),
        h('div', { className:'enso-pill' },
          h('div', { className:'enso-dot', style:{ background:PHASE_CLR, color:PHASE_CLR } }),
          h('span', { className:'enso-text' },
            'Current ENSO: ',
            h('strong', { style:{ color:'#F1F5F9' } }, ONI_PHASE),
            '  ·  ONI = ',
            h('strong', { style:{ color:PHASE_CLR } }, ONI_VAL + ' °C'),
            h('span', { style:{ color:'#334155', marginLeft:'8px' } }, '(' + ONI_DATE + ')')
          )
        )
      ),
      /* Wave transition */
      h('div', { className:'hero-wave' },
        h('svg', { viewBox:'0 0 1440 90', xmlns:'http://www.w3.org/2000/svg',
                   preserveAspectRatio:'none', style:{ height:'50px' } },
          h('path', {
            d:'M0,45 C240,90 480,0 720,45 C960,90 1200,10 1440,45 L1440,90 L0,90 Z',
            fill:'#060F1C',
          }),
          h('path', {
            d:'M0,60 C300,20 600,80 900,55 C1100,38 1280,65 1440,60 L1440,90 L0,90 Z',
            fill:'#060F1C', opacity:'0.6'
          })
        )
      )
    ),

    /* TICKER */
    h(Ticker),

    /* STATS */
    h('div', { className:'stats' },
      ...[
        { v:75,  s:'',  l:'Years of ENSO Data\n1950 – 2025',     d:'0.05s' },
        { v:5,   s:'',  l:'Super El Niño Events\nStudied in depth', d:'0.10s' },
        { v:5,   s:'',  l:'Asset Classes\nAnalyzed',                d:'0.15s' },
        { v:13,  s:'+', l:'Financial Instruments\nTracked',          d:'0.20s' },
      ].map(({ v, s, l, d }, i) =>
        h('div', { className:'stat', style:{ animationDelay:d }, key:i },
          h('div', { className:'stat-num' }, h(Counter, { target:v, duration:1800 }), s),
          h('div', { className:'stat-lbl' }, l)
        )
      )
    ),

    /* CONTENT */
    h('div', { className:'content' },
      /* Research question */
      h('div', { className:'rq' },
        h('div', { className:'rq-tag' }, 'Central Research Question'),
        h('div', { className:'rq-text' },
          '"Is the financial industry adequately prepared for the economic disruption of a Super El Niño event? Are current risk models, insurance products, and investment strategies accounting for ENSO-driven climate tail risk?"'
        )
      ),

      /* Navigation cards */
      h('div', { className:'sec-hd' }, 'Click a section to open the dashboard'),
      h('div', { className:'cards' },
        ...SECTIONS.map((s, i) => h(SectionCard, { ...s, delay:(i*0.07)+'s', key:i }))
      ),

      /* Hypotheses */
      h('div', { className:'sec-hd' }, 'Research Hypotheses'),
      h('div', { className:'hyp-grid' },
        ...[
          { n:'H1', t:'El Niño events cause statistically significant negative returns in agriculture and energy commodity markets, driven by supply-side disruptions to global production cycles.' },
          { n:'H2', t:'Financial market volatility (VIX) increases measurably during Super El Niño events, with broad equity indices underperforming their long-run historical trend.' },
          { n:'H3', t:'Insurance and banking sectors fail to adequately price Super El Niño tail risk, resulting in systematic underperformance relative to the S&P 500 during El Niño windows.' },
        ].map(({ n, t }, i) =>
          h('div', { className:'hyp', style:{ animationDelay:(i*0.09)+'s' }, key:i },
            h('div', { className:'hyp-num' }, n),
            h('p', { className:'hyp-text' }, t)
          )
        )
      ),

      /* Data sources */
      h('div', { className:'sec-hd' }, 'Data Sources'),
      h('div', { className:'sources' },
        ...[
          'NOAA Climate Prediction Center — ONI Dataset (1950–2025)',
          'Yahoo Finance via yfinance — Equities, Commodities & Crypto',
          'NBER — Official US Recession Dates',
          'NCEI Billion-Dollar Disasters — Annual Loss Statistics',
          'CoinGecko / Yahoo Finance — BTC, ETH (2013–2025)',
          'S&P 500 (^GSPC)  ·  VIX (^VIX)  ·  Dow Jones (^DJI)',
        ].map((s, i) => h('div', { className:'src', key:i }, s))
      ),

      h('div', { className:'footer' },
        'El Niño & Financial Markets Research  ·  Srishti Chauhan, 2026  ·  All data sourced from publicly available datasets.'
      )
    )
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(h(App, null));
})();
</script>
</body>
</html>"""

    HOME_HTML = (HOME_HTML
        .replace("##ONI_VAL##",   f"{latest_oni:+.2f}")
        .replace("##ONI_PHASE##", latest_phase)
        .replace("##ONI_DATE##",  latest_date)
        .replace("##PHASE_CLR##", phase_col))

    components.html(HOME_HTML, height=1120, scrolling=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ENSO MONITOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "ENSO Monitor":
    ph("ENSO Monitor",
       "Oceanic Nino Index (ONI) — the official NOAA measure of El Nino and La Nina intensity")

    super_cnt = int((oni["phase"] == "Super El Nino").sum())
    col_key   = "negative" if latest_oni > 0.5 else ("positive" if latest_oni < -0.5 else "neutral")

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.markdown(kpi_card("ONI Anomaly", f"{latest_oni:+.2f} °C", sub=latest_date, color=col_key), unsafe_allow_html=True)
    c2.markdown(kpi_card("Current Phase", latest_phase, sub="ENSO Classification"), unsafe_allow_html=True)
    c3.markdown(kpi_card("Super El Nino Seasons", str(super_cnt), sub="Since 1950", color="negative"), unsafe_allow_html=True)
    c4.markdown(kpi_card("Record Peak ONI", f"+{oni['ONI'].max():.2f} °C", sub="Historical max", color="negative"), unsafe_allow_html=True)
    c5.markdown(kpi_card("Record La Nina Low", f"{oni['ONI'].min():.2f} °C", sub="Historical min", color="positive"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sec("ONI INDEX TIMELINE  ·  1950 – 2025")

    pos = oni["ONI"].clip(lower=0)
    neg = oni["ONI"].clip(upper=0)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=oni.index, y=pos, fill="tozeroy",
        fillcolor="rgba(185,28,28,0.12)", line=dict(color=RED, width=1.2), name="El Nino",
        hovertemplate="%{x|%b %Y}  ONI: <b>%{y:.2f} °C</b><extra></extra>"))
    fig.add_trace(go.Scatter(x=oni.index, y=neg, fill="tozeroy",
        fillcolor="rgba(29,78,216,0.12)", line=dict(color=BLUE, width=1.2), name="La Nina",
        hovertemplate="%{x|%b %Y}  ONI: <b>%{y:.2f} °C</b><extra></extra>"))
    fig.add_hline(y=2.0, line=dict(color=RED, dash="dash", width=1),
        annotation_text="Super El Nino (+2.0 °C)", annotation_position="top right",
        annotation=dict(font=dict(color=RED, size=9), bgcolor="rgba(255,255,255,0.9)"))
    fig.add_hline(y=0.5,  line=dict(color="rgba(185,28,28,0.25)", dash="dot", width=1))
    fig.add_hline(y=-0.5, line=dict(color="rgba(29,78,216,0.25)", dash="dot", width=1))
    fig.add_hline(y=0,    line=dict(color=BORDER_MED, width=0.8))
    for d, y2, lbl in [("1982-11-01",2.5,"1982–83"),("1997-10-01",2.7,"1997–98"),("2015-10-01",2.55,"2015–16")]:
        fig.add_annotation(x=d, y=y2, text=f"<b>{lbl}</b>", showarrow=True,
            arrowhead=2, arrowcolor=RED, arrowsize=0.7, arrowwidth=1.2,
            font=dict(color=RED, size=8.5), bgcolor="rgba(255,255,255,0.9)",
            bordercolor=RED, borderwidth=0.5, borderpad=3, ay=-28)
    fig.update_layout(**CHART, height=310,
        title="Oceanic Nino Index 1950–2025  ·  El Nino (red) and La Nina (blue)",
        yaxis_title="ONI Anomaly (°C)")
    st.plotly_chart(fig, use_container_width=True)
    sbadge("NOAA Climate Prediction Center — CPC ONI Dataset (1950–2025)")

    col1, col2 = st.columns([1, 1.8])
    with col1:
        sec("ENSO PHASE DISTRIBUTION")
        counts = oni["phase"].value_counts().reset_index()
        counts.columns = ["Phase","Seasons"]
        order  = ["Super El Nino","Strong El Nino","Moderate El Nino","Weak El Nino","Neutral","La Nina"]
        counts["Phase"] = pd.Categorical(counts["Phase"], categories=order, ordered=True)
        counts = counts.sort_values("Phase")
        fig_pie = go.Figure(go.Pie(
            labels=counts["Phase"], values=counts["Seasons"], hole=0.55,
            marker=dict(colors=[PHASE_CLR.get(p, SLATE) for p in counts["Phase"]],
                        line=dict(color=BG_CARD, width=2.5)),
            textinfo="percent", textfont=dict(size=10, color="white"),
            hovertemplate="<b>%{label}</b><br>%{value} seasons (%{percent})<extra></extra>"))
        fig_pie.add_annotation(text=f"<b>{len(oni)}</b><br><span style='font-size:9px'>seasons</span>",
            x=0.5, y=0.5, showarrow=False, font=dict(size=13, color=TX_H, family="Inter"))
        fig_pie.update_layout(**{**CHART,"margin":dict(t=10,b=10,l=10,r=10),
            "legend":dict(orientation="v",bgcolor=BG_CARD,font=dict(color=TX_BODY,size=9.5),borderwidth=0)},
            height=280, title="")
        st.plotly_chart(fig_pie, use_container_width=True)
        sbadge("NOAA ONI Dataset")

    with col2:
        sec("MAJOR EL NINO EVENTS")
        ev_df = pd.DataFrame({
            "Event":            ["1972–73","1982–83 (Super)","1997–98 (Super)","2015–16 (Super)","2023–24"],
            "Peak ONI (°C)":    ["+2.0","+2.2","+2.4","+2.3","+2.0"],
            "Duration":         ["8 months","14 months","13 months","13 months","9 months"],
            "Est. Global Loss": ["~USD 40 billion","~USD 4.1 trillion","~USD 5.7 trillion","~USD 3.9 trillion","Pending"],
            "US Recession":     ["Yes (1973–75)","Yes (1981–82)","No","No","TBD"],
        })
        st.dataframe(ev_df, use_container_width=True, hide_index=True, height=220)
        sbadge("Callahan & Mankin (Science, 2023)","NOAA NCEI")

    st.markdown("""<div class="callout">
        <strong>Research Context:</strong> The 1982–83 and 1997–98 Super El Nino events caused
        an estimated USD 4.1 trillion and USD 5.7 trillion in cumulative global income losses,
        with GDP suppression persisting up to 15 years post-event (Callahan &amp; Mankin, <em>Science</em>, 2023).
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: FINANCIAL MARKETS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Financial Markets":
    ph("Financial Markets",
       "S&P 500, VIX, and equity index behaviour during El Nino events (1990–2025)")

    sp  = fin["SP500"].dropna();  vix = fin["VIX"].dropna()
    dj  = fin["DowJones"].dropna()
    sp_1y = safe_1y(sp); vix_now = float(vix.iloc[-1])

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi_card("S&P 500", f"{sp.iloc[-1]:,.0f}", sub="Latest close"), unsafe_allow_html=True)
    c2.markdown(kpi_card("VIX", f"{vix_now:.1f}", sub="Volatility index",
                         color="negative" if vix_now>20 else "positive"), unsafe_allow_html=True)
    c3.markdown(kpi_card("S&P 500 1-Year", f"{sp_1y:+.1f}%", sub="Trailing 252 days",
                         color="positive" if sp_1y>0 else "negative"), unsafe_allow_html=True)
    c4.markdown(kpi_card("Dow Jones", f"{dj.iloc[-1]:,.0f}", sub="Latest close"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    fl, fr = st.columns([4,1])
    with fr:
        yr = st.slider("Range", 1990, 2025, (1993,2025), label_visibility="collapsed", key="fin_yr")
    fin_f  = fin [(fin .index.year>=yr[0])&(fin .index.year<=yr[1])]
    nber_f = nber[(nber.index.year>=yr[0])&(nber.index.year<=yr[1])]

    sec("S&P 500 PRICE INDEX")
    sp_f = fin_f["SP500"].dropna()
    fig  = go.Figure()
    fig.add_trace(go.Scatter(x=sp_f.index, y=sp_f, name="S&P 500",
        line=dict(color=BLUE, width=1.8),
        hovertemplate="%{x|%d %b %Y}  <b>%{y:,.0f}</b><extra></extra>"))
    add_recession_bands(fig, nber_f); add_el_nino_bands(fig)
    fig.update_layout(**CHART, height=300,
        title="S&P 500 — Red: El Nino windows  ·  Gray: NBER recessions", yaxis_title="Index")
    st.plotly_chart(fig, use_container_width=True)
    sbadge("Yahoo Finance — ^GSPC","NBER Recession Dates")

    sec("CBOE VIX VOLATILITY INDEX")
    vix_f = fin_f["VIX"].dropna()
    fig2  = go.Figure()
    fig2.add_trace(go.Scatter(x=vix_f.index, y=vix_f, fill="tozeroy",
        fillcolor="rgba(180,83,9,0.07)", line=dict(color=AMBER, width=1.4), name="VIX",
        hovertemplate="%{x|%d %b %Y}  VIX: <b>%{y:.1f}</b><extra></extra>"))
    fig2.add_hline(y=20, line=dict(color=RED_LT, dash="dash", width=1),
        annotation_text="Elevated (20)", annotation_position="top right",
        annotation=dict(font=dict(color=RED, size=9), bgcolor="rgba(255,255,255,0.9)"))
    add_el_nino_bands(fig2)
    fig2.update_layout(**CHART, height=260,
        title="CBOE Volatility Index — higher = more market uncertainty", yaxis_title="VIX")
    st.plotly_chart(fig2, use_container_width=True)
    sbadge("Yahoo Finance — ^VIX")

    sec("AVERAGE QUARTERLY S&P 500 RETURN BY ENSO PHASE")
    sp_q = sp.resample("QS").last().pct_change()*100
    oni_q = oni["ONI"].resample("QS").mean()
    mrg = pd.DataFrame({"ret":sp_q,"ONI":oni_q}).dropna()
    mrg["phase"] = mrg["ONI"].apply(classify_oni)
    avg = mrg.groupby("phase")["ret"].agg(["mean","sem","count"]).reset_index()
    ph_ord = ["Super El Nino","Strong El Nino","Moderate El Nino","Weak El Nino","Neutral","La Nina"]
    avg["phase"] = pd.Categorical(avg["phase"], categories=ph_ord, ordered=True)
    avg = avg.sort_values("phase").dropna(subset=["mean"])
    bclrs = [PHASE_CLR.get(p, SLATE) for p in avg["phase"]]
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=avg["phase"], y=avg["mean"],
        error_y=dict(type="data", array=avg["sem"].fillna(0), color=BORDER_MED, thickness=1.5, width=6),
        marker_color=bclrs, marker_line=dict(color="white", width=1.5),
        text=[f"{v:+.2f}%" for v in avg["mean"]], textfont=dict(color=TX_H, size=10),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>%{y:+.2f}%<extra></extra>"))
    fig3.add_hline(y=0, line=dict(color=BORDER_MED, width=1))
    fig3.update_layout(**CHART, height=300,
        title="Average quarterly S&P 500 returns by ENSO phase (1990–2025)",
        yaxis_title="Avg Quarterly Return (%)")
    st.plotly_chart(fig3, use_container_width=True)
    sbadge("Yahoo Finance (^GSPC)","NOAA ONI Dataset")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: COMMODITIES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Commodities":
    ph("Commodity Markets",
       "El Nino disrupts global agriculture, energy, and raw material supply chains")

    COMM_MAP = {
        "Wheat_Futures":    ("Wheat",       "#B45309"),
        "Corn_Futures":     ("Corn",        "#CA8A04"),
        "Coffee_Futures":   ("Coffee",      "#78350F"),
        "Cocoa_Futures":    ("Cocoa",       "#6D28D9"),
        "CrudeOil_Futures": ("Crude Oil",   "#1D4ED8"),
        "NatGas_Futures":   ("Natural Gas", "#047857"),
        "Gold_Futures":     ("Gold",        "#92400E"),
    }

    c1,c2,c3,c4 = st.columns(4)
    for col_name, (nm, _), card in [
        ("Wheat_Futures",    ("Wheat",     ""), c1),
        ("Corn_Futures",     ("Corn",      ""), c2),
        ("CrudeOil_Futures", ("Crude Oil", ""), c3),
        ("Gold_Futures",     ("Gold",      ""), c4),
    ]:
        if col_name in comm.columns:
            s   = comm[col_name].dropna()
            chg = safe_1y(s)
            card.markdown(kpi_card(f"{nm} Futures", f"${s.iloc[-1]:,.1f}",
                sub=f"{chg:+.1f}% vs 1 year ago",
                color="positive" if chg>=0 else "negative"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    fl, fr = st.columns([4,1])
    with fr:
        yr = st.slider("Range", 2000, 2025, (2000,2025),
                       label_visibility="collapsed", key="comm_yr")
    comm_f = comm[(comm.index.year>=yr[0])&(comm.index.year<=yr[1])]

    valid_cols = [k for k in COMM_MAP if k in comm.columns]
    selected   = st.multiselect("Chart commodities",
        options=valid_cols,
        default=[c for c in ["Wheat_Futures","Corn_Futures","CrudeOil_Futures"] if c in valid_cols],
        format_func=lambda x: COMM_MAP[x][0])

    if selected:
        sec("COMMODITY PRICE HISTORY  ·  RED BANDS = EL NINO WINDOWS")
        n   = len(selected)
        fig = make_subplots(rows=n, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                            subplot_titles=[f"{COMM_MAP[c][0]} Futures (USD)" for c in selected])
        for i, c_name in enumerate(selected, 1):
            nm, color = COMM_MAP[c_name]
            s = comm_f[c_name].dropna()
            if s.empty: continue
            r = int(color[1:3],16); g = int(color[3:5],16); b = int(color[5:7],16)
            fig.add_trace(go.Scatter(x=s.index, y=s, name=nm,
                line=dict(color=color, width=1.6),
                fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.05)",
                hovertemplate=f"<b>{nm}</b>: $%{{y:,.1f}}<br>%{{x|%b %Y}}<extra></extra>"),
                row=i, col=1)
            fig.update_yaxes(title_text="USD", title_font=dict(size=9, color=TX_MUTED),
                             gridcolor="#F1F5F9", tickfont=dict(color=TX_MUTED, size=9), row=i, col=1)
            for s0,e0,_lbl,fc in EL_NINO_EVENTS:
                fig.add_vrect(x0=s0, x1=e0, fillcolor=fc, line_width=0, layer="below", row=i, col=1)
        fig.update_annotations(font=dict(size=10, color=TX_BODY, family="Inter"))
        fig.update_xaxes(gridcolor="#F1F5F9", tickfont=dict(color=TX_MUTED, size=9))
        fig.update_layout(**{**CHART,"margin":dict(t=32,b=24,l=12,r=16)},
            height=max(260,200*n), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        sbadge("Yahoo Finance via yfinance — Commodity Futures (2000–2025)")

    sec("AVERAGE QUARTERLY PRICE CHANGE  ·  EL NINO vs NEUTRAL")
    oni_q   = oni["ONI"].resample("QS").mean()
    results = []
    for c_name,(nm,_) in COMM_MAP.items():
        if c_name not in comm.columns: continue
        s   = comm[c_name].dropna().resample("QS").last().pct_change()*100
        mrg = pd.DataFrame({"ret":s,"ONI":oni_q}).dropna()
        if mrg.empty: continue
        mrg["el"] = mrg["ONI"] >= 0.5
        en  = float(mrg[mrg["el"]]["ret"].mean())  if mrg["el"].any()    else 0.0
        neu = float(mrg[~mrg["el"]]["ret"].mean()) if (~mrg["el"]).any() else 0.0
        results.append({"Commodity":nm,
                        "El Nino Avg (%)": round(en,2),
                        "Neutral Avg (%)": round(neu,2),
                        "Difference (pp)": round(en-neu,2)})
    if results:
        res   = pd.DataFrame(results).sort_values("Difference (pp)", ascending=False)
        fig_b = go.Figure()
        fig_b.add_trace(go.Bar(name="El Nino Periods", x=res["Commodity"], y=res["El Nino Avg (%)"],
            marker_color=RED, marker_line=dict(color="white", width=1.2),
            text=[f"{v:+.2f}%" for v in res["El Nino Avg (%)"]],
            textfont=dict(color=TX_H, size=10), textposition="outside",
            hovertemplate="<b>%{x}</b> El Nino: %{y:+.2f}%<extra></extra>"))
        fig_b.add_trace(go.Bar(name="Neutral Periods", x=res["Commodity"], y=res["Neutral Avg (%)"],
            marker_color=SLATE, marker_line=dict(color="white", width=1.2),
            text=[f"{v:+.2f}%" for v in res["Neutral Avg (%)"]],
            textfont=dict(color=TX_H, size=10), textposition="outside",
            hovertemplate="<b>%{x}</b> Neutral: %{y:+.2f}%<extra></extra>"))
        fig_b.add_hline(y=0, line=dict(color=BORDER_MED, width=1))
        fig_b.update_layout(**CHART, barmode="group", height=320,
            title="Commodity price sensitivity: El Nino (red) vs neutral ENSO periods",
            yaxis_title="Average Quarterly Price Change (%)")
        st.plotly_chart(fig_b, use_container_width=True)
        sbadge("Yahoo Finance — Commodity Futures","NOAA ONI Dataset")
        sec("SUMMARY TABLE")
        st.dataframe(res, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CRYPTOCURRENCY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Cryptocurrency":
    ph("Cryptocurrency Markets",
       "Bitcoin and Ethereum price behaviour during El Nino events — exploratory analysis (2013–2025)")

    st.markdown("""<div class="callout-amber">
        <strong>Methodological Note:</strong> Only the 2015–16 and 2023–24 El Nino events
        overlap with mature cryptocurrency markets. All results are preliminary findings.
    </div>""", unsafe_allow_html=True)

    btc = crypto["BTC_price"].dropna() if "BTC_price" in crypto.columns else pd.Series(dtype=float)
    eth = crypto["ETH_price"].dropna() if "ETH_price" in crypto.columns else pd.Series(dtype=float)
    if len(btc)<10:
        st.error("Bitcoin data missing. Run: python3 data/fix_missing_data.py"); st.stop()

    btc_1y = safe_1y(btc,365);  eth_1y = safe_1y(eth,365) if len(eth)>10 else 0.0
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi_card("Bitcoin (BTC)", f"${btc.iloc[-1]:,.0f}", sub="USD"), unsafe_allow_html=True)
    c2.markdown(kpi_card("Ethereum (ETH)", f"${eth.iloc[-1]:,.0f}" if len(eth)>0 else "N/A", sub="USD"), unsafe_allow_html=True)
    c3.markdown(kpi_card("BTC 1-Year", f"{btc_1y:+.1f}%", sub="Trailing 365 days",
                         color="positive" if btc_1y>0 else "negative"), unsafe_allow_html=True)
    c4.markdown(kpi_card("ETH 1-Year", f"{eth_1y:+.1f}%", sub="Trailing 365 days",
                         color="positive" if eth_1y>0 else "negative"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sec("BITCOIN & ETHEREUM PRICE HISTORY  ·  RED BANDS = EL NINO WINDOWS")
    plot_pairs = [(btc,"Bitcoin",AMBER,"Bitcoin  (BTC-USD)")]
    if len(eth)>10: plot_pairs.append((eth,"Ethereum",BLUE,"Ethereum  (ETH-USD)"))
    n_plots = len(plot_pairs)

    fig = make_subplots(rows=n_plots, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                        subplot_titles=[t for *_,t in plot_pairs])
    for i,(series,nm,color,_) in enumerate(plot_pairs,1):
        fig.add_trace(go.Scatter(x=series.index, y=series, name=nm,
            line=dict(color=color, width=1.8),
            hovertemplate=f"<b>{nm}</b>: $%{{y:,.0f}}<br>%{{x|%d %b %Y}}<extra></extra>"),
            row=i, col=1)
        fig.update_yaxes(title_text="USD", title_font=dict(size=9,color=TX_MUTED),
                         gridcolor="#F1F5F9", tickfont=dict(color=TX_MUTED,size=9), row=i, col=1)
        for s0,e0,_lbl,fc in EL_NINO_EVENTS:
            fig.add_vrect(x0=s0,x1=e0,fillcolor=fc,line_width=0,layer="below",row=i,col=1)
    fig.update_annotations(font=dict(size=10,color=TX_BODY,family="Inter"))
    fig.update_xaxes(gridcolor="#F1F5F9",tickfont=dict(color=TX_MUTED,size=9))
    fig.update_layout(**{**CHART,"margin":dict(t=32,b=24,l=12,r=16)},
        height=max(320,240*n_plots), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    sbadge("Yahoo Finance via yfinance — BTC-USD, ETH-USD (2013–2025)")

    col1, col2 = st.columns(2)
    with col1:
        sec("BTC 30-DAY REALISED VOLATILITY BY ENSO PHASE")
        btc_vol = btc.pct_change().rolling(30).std()*np.sqrt(252)*100
        oni_d   = oni["ONI"].reindex(btc_vol.index, method="ffill")
        vdf     = pd.DataFrame({"vol":btc_vol,"ONI":oni_d}).dropna()
        if not vdf.empty:
            vdf["phase"] = vdf["ONI"].apply(
                lambda v: "El Nino" if v>=0.5 else ("La Nina" if v<=-0.5 else "Neutral"))
            present = [p for p in ["El Nino","Neutral","La Nina"] if p in vdf["phase"].values]
            if present:
                vdf["phase"] = pd.Categorical(vdf["phase"], categories=present, ordered=True)
                fig_box = px.box(vdf.sort_values("phase"), x="phase", y="vol", color="phase",
                    color_discrete_map={"El Nino":RED,"Neutral":SLATE,"La Nina":BLUE},
                    labels={"vol":"Annualised Volatility (%)","phase":"ENSO Phase"})
                fig_box.update_traces(marker_size=3, marker_opacity=0.5)
                fig_box.update_layout(**{**CHART,"margin":dict(t=12,b=24,l=12,r=16)},
                    height=290, showlegend=False,
                    title="BTC volatility by ENSO phase (2013–2025)")
                st.plotly_chart(fig_box, use_container_width=True)
                sbadge("Yahoo Finance (BTC-USD)","NOAA ONI Dataset")

    with col2:
        sec("BTC vs S&P 500  —  CORRELATION BY ENSO PHASE")
        sp_d   = fin["SP500"].dropna().pct_change()
        btc_d  = btc.pct_change()
        oni_d2 = oni["ONI"].reindex(sp_d.index, method="ffill")
        cdf    = pd.DataFrame({"sp":sp_d,"btc":btc_d,"ONI":oni_d2}).dropna()
        if len(cdf)>30:
            cdf["phase"] = cdf["ONI"].apply(lambda v: "El Nino" if v>=0.5 else "Neutral")
            groups = cdf.groupby("phase")[["sp","btc"]].corr().unstack()["btc"]["sp"].dropna()
            if not groups.empty:
                fig_cor = go.Figure(go.Bar(
                    x=groups.index, y=groups.values,
                    marker_color=[RED if p=="El Nino" else SLATE for p in groups.index],
                    marker_line=dict(color="white",width=1.5),
                    text=[f"{v:.3f}" for v in groups.values],
                    textfont=dict(color=TX_H,size=11), textposition="outside",
                    hovertemplate="<b>%{x}</b><br>Pearson r: %{y:.3f}<extra></extra>"))
                fig_cor.add_hline(y=0, line=dict(color=BORDER_MED,width=1))
                fig_cor.update_layout(**{**CHART,"margin":dict(t=12,b=24,l=12,r=16)},
                    height=290,
                    title="BTC–S&P 500 return correlation by ENSO phase",
                    yaxis_title="Pearson Correlation")
                st.plotly_chart(fig_cor, use_container_width=True)
                sbadge("Yahoo Finance (BTC-USD, ^GSPC)","NOAA ONI Dataset")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: INSURANCE & BANKING
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Insurance & Banking":
    ph("Insurance & Banking Sectors",
       "Assessing whether financial institutions are adequately pricing Super El Nino tail risk")

    ins  = fin["Insurance_ETF"].dropna()
    bank = fin["Banking_ETF"].dropna()
    sp   = fin["SP500"].dropna()
    ins_1y=safe_1y(ins); bank_1y=safe_1y(bank); sp_1y=safe_1y(sp)

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi_card("Insurance ETF (KIE)", f"${ins.iloc[-1]:.2f}", sub="SPDR S&P Insurance"), unsafe_allow_html=True)
    c2.markdown(kpi_card("Banking ETF (KBE)",   f"${bank.iloc[-1]:.2f}", sub="SPDR S&P Bank"),     unsafe_allow_html=True)
    c3.markdown(kpi_card("Insurance 1-Year", f"{ins_1y:+.1f}%", sub=f"vs S&P 500 {sp_1y:+.1f}%",
                         color="positive" if ins_1y>0 else "negative"), unsafe_allow_html=True)
    c4.markdown(kpi_card("Banking 1-Year",   f"{bank_1y:+.1f}%", sub=f"vs S&P 500 {sp_1y:+.1f}%",
                         color="positive" if bank_1y>0 else "negative"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sec("RELATIVE PERFORMANCE  ·  INDEXED TO 100 AT COMMON START")

    start_dt  = max(ins.index[0], bank.index[0])
    ins_n     = ins [ins .index>=start_dt] / ins [ins .index>=start_dt].iloc[0] * 100
    bank_n    = bank[bank.index>=start_dt] / bank[bank.index>=start_dt].iloc[0] * 100
    sp_n      = sp  [sp  .index>=start_dt] / sp  [sp  .index>=start_dt].iloc[0] * 100
    nber_trim = nber[nber.index>=start_dt]

    fig = go.Figure()
    for series,nm,color in [(sp_n,"S&P 500",BLUE),(ins_n,"Insurance ETF (KIE)",GREEN),(bank_n,"Banking ETF (KBE)",AMBER)]:
        fig.add_trace(go.Scatter(x=series.index, y=series, name=nm,
            line=dict(color=color, width=1.8),
            hovertemplate=f"<b>{nm}</b>: %{{y:.1f}}<br>%{{x|%d %b %Y}}<extra></extra>"))
    fig.add_hline(y=100, line=dict(color=BORDER_MED, dash="dot", width=1),
        annotation_text="Base (100)", annotation_position="top left",
        annotation=dict(font=dict(color=TX_MUTED,size=8.5)))
    add_el_nino_bands(fig); add_recession_bands(fig, nber_trim)
    fig.update_layout(**CHART, height=360,
        title=f"Relative performance since {start_dt.strftime('%b %Y')} — red: El Nino  ·  gray: recessions",
        yaxis_title="Indexed Value (base = 100)")
    st.plotly_chart(fig, use_container_width=True)
    sbadge("Yahoo Finance — KIE, KBE, ^GSPC","NBER Recession Dates")

    sec("TOTAL RETURN DURING EACH EL NINO WINDOW")
    rows = []
    for s0,e0,lbl,_ in EL_NINO_EVENTS:
        s, e = pd.to_datetime(s0), pd.to_datetime(e0)
        for series,nm in [(ins,"Insurance ETF (KIE)"),(bank,"Banking ETF (KBE)"),(sp,"S&P 500")]:
            w = series[(series.index>=s)&(series.index<=e)].dropna()
            if len(w)<20: continue
            rows.append({"El Nino Event":lbl,"Sector":nm,
                         "Total Return (%)":round((w.iloc[-1]/w.iloc[0]-1)*100,1)})
    if rows:
        rdf  = pd.DataFrame(rows)
        fig2 = px.bar(rdf, x="El Nino Event", y="Total Return (%)", color="Sector",
            barmode="group",
            color_discrete_map={"S&P 500":BLUE,"Insurance ETF (KIE)":GREEN,"Banking ETF (KBE)":AMBER},
            text_auto=".1f")
        fig2.update_traces(marker_line=dict(color="white",width=1.2), textfont=dict(color=TX_H,size=9.5))
        fig2.add_hline(y=0, line=dict(color=BORDER_MED,width=1))
        fig2.update_layout(**CHART, height=330, title="Sector total returns during each El Nino window")
        st.plotly_chart(fig2, use_container_width=True)
        sbadge("Yahoo Finance — KIE, KBE, ^GSPC")

        sec("RETURN SUMMARY TABLE")
        pivot = rdf.pivot(index="El Nino Event", columns="Sector", values="Total Return (%)")
        st.dataframe(pivot.style.format("{:+.1f}%").background_gradient(
            cmap="RdYlGn", axis=None, vmin=-30, vmax=30), use_container_width=True)

    st.markdown("""<div class="callout">
        <strong>Hypothesis H3:</strong> If insurance and banking sectors systematically
        underperform the S&P 500 during El Nino windows, it suggests these sectors are not
        fully pricing in climate tail risk in their equity valuations or insurance premiums.
    </div>""", unsafe_allow_html=True)
