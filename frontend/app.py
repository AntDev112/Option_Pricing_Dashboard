import streamlit as st
import requests
import plotly.graph_objects as go
import numpy as np

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="OptionScope",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000"

# ─── Custom CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0a0e14;
    color: #c8d0dc;
  }

  /* Main background */
  .stApp { background-color: #0a0e14; }
  section[data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #1e2530; }

  /* Header */
  .app-header {
    display: flex; align-items: center; gap: 16px;
    padding: 0 0 20px 0;
    border-bottom: 1px solid #1e2530;
    margin-bottom: 24px;
  }
  .app-logo {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px; font-weight: 500; color: #58a6ff;
    letter-spacing: 0.08em; text-transform: uppercase;
  }
  .app-subtitle {
    font-size: 13px; color: #6b7785;
    letter-spacing: 0.05em; text-transform: uppercase;
  }
  .live-badge {
    margin-left: auto;
    display: flex; align-items: center; gap: 8px;
    font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #3fb950;
  }

  /* Metric cards */
  .metric-card {
    background: #0d1117;
    border: 1px solid #1e2530;
    border-radius: 3px;
    padding: 14px 16px;
  }
  .metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; color: #4a5568;
    letter-spacing: 0.12em; text-transform: uppercase;
    margin-bottom: 6px;
  }
  .metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px; font-weight: 500;
  }
  .metric-sub { font-size: 11px; color: #6b7785; margin-top: 4px; }

  .val-call { color: #3fb950; }
  .val-put  { color: #f85149; }
  .val-blue { color: #58a6ff; }
  .val-amber { color: #e3b341; }

  /* Greek cards */
  .greek-card {
    background: #0d1117;
    border: 1px solid #1e2530;
    border-radius: 3px;
    padding: 14px;
    margin-bottom: 8px;
  }
  .greek-symbol {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; color: #4a5568;
    letter-spacing: 0.1em; text-transform: uppercase;
  }
  .greek-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 20px; font-weight: 500; color: #e6edf3;
    margin: 4px 0;
  }
  .greek-desc { font-size: 11px; color: #4a5568; line-height: 1.4; }

  /* Chart panels */
  .chart-panel {
    background: #0d1117;
    border: 1px solid #1e2530;
    border-radius: 3px;
    padding: 16px;
  }
  .panel-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; color: #8b949e;
    letter-spacing: 0.08em; text-transform: uppercase;
    margin-bottom: 12px;
  }

  /* Section label */
  .section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; color: #4a5568;
    letter-spacing: 0.14em; text-transform: uppercase;
    margin-bottom: 10px; margin-top: 4px;
  }

  /* Footer */
  .footer-bar {
    display: flex; gap: 24px; flex-wrap: wrap;
    padding: 12px 0 0 0;
    border-top: 1px solid #1e2530;
    margin-top: 24px;
  }
  .footer-item {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; color: #4a5568;
  }
  .footer-item span { color: #8b949e; margin-left: 4px; }

  /* Streamlit overrides */
  div[data-testid="stSlider"] > div > div > div { background: #1e2530 !important; }
  .stSlider [data-baseweb="slider"] { padding: 0 !important; }
  label[data-testid="stWidgetLabel"] { color: #8b949e !important; font-size: 12px !important; }
  div[data-testid="stSelectbox"] select { background: #0a0e14 !important; color: #c8d0dc !important; border: 1px solid #1e2530 !important; }
  div[data-testid="stRadio"] label { color: #8b949e !important; }
  .stButton > button {
    background: #1a2d4a !important; border: 1px solid #2d4a6e !important;
    color: #58a6ff !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important; letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    width: 100% !important;
  }
  .stButton > button:hover { background: #213661 !important; }

  div[data-testid="stDataFrame"] { background: #0d1117 !important; }
  .stDataFrame { border: 1px solid #1e2530 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────

st.markdown("""
<div class="app-header">
  <div>
    <div class="app-logo">OptionScope</div>
    <div class="app-subtitle">Options Pricing &amp; Greeks Dashboard</div>
  </div>
  <div class="live-badge">⬤ &nbsp;Black-Scholes + Binomial Engine</div>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="section-label">Option Parameters</div>', unsafe_allow_html=True)

    option_type = st.radio("Type", ["Call", "Put"], horizontal=True).lower()

    S = st.slider("Underlying Price (S)", 50.0, 200.0, 100.0, 0.5, format="$%.2f")
    K = st.slider("Strike Price (K)", 50.0, 200.0, 100.0, 0.5, format="$%.2f")
    T = st.slider("Time to Expiry (T, years)", 0.01, 2.0, 0.25, 0.01, format="%.2f yr")
    v = st.slider("Implied Volatility (σ)", 1.0, 100.0, 20.0, 0.5, format="%.1f%%") / 100
    r = st.slider("Risk-Free Rate (r)", 0.0, 15.0, 5.0, 0.1, format="%.1f%%") / 100
    q = st.slider("Dividend Yield (q)", 0.0, 10.0, 0.0, 0.1, format="%.1f%%") / 100

    st.markdown('<div class="section-label" style="margin-top:20px">Model</div>', unsafe_allow_html=True)
    model = st.selectbox("", ["Black-Scholes (European)", "Binomial Tree (American)"])
    model_key = "bs" if "Black" in model else "binomial"

# ─── API Calls ───────────────────────────────────────────────────────────────

payload = dict(S=S, K=K, T=T, v=v, r=r, q=q, option_type=option_type, model=model_key)


@st.cache_data(ttl=1)
def fetch(endpoint, _payload):
    try:
        r = requests.post(f"{API_URL}/{endpoint}", json=_payload, timeout=5)
        return r.json()
    except Exception as e:
        st.error(f"Backend unavailable — start it with `uvicorn main:app --reload` (error: {e})")
        return None


key = str(payload)
price_data   = fetch("price",           key)
pnl_data     = fetch("pnl_curve",       key)
delta_data   = fetch("delta_curve",     key)
scenario     = fetch("scenario_matrix", key)
smile_data   = fetch("vol_smile",       key)

if not price_data:
    st.stop()

g = price_data["greeks"]

# ─── Plotly Theme ────────────────────────────────────────────────────────────

PLOT_BG   = "#0d1117"
PAPER_BG  = "#0d1117"
GRID_COL  = "#1e2530"
TEXT_COL  = "#6b7785"
FONT_MONO = "IBM Plex Mono"

plot_layout = dict(
    paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
    font=dict(family=FONT_MONO, color=TEXT_COL, size=11),
    margin=dict(l=40, r=16, t=16, b=40),
    xaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, zerolinecolor=GRID_COL),
    yaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, zerolinecolor=GRID_COL),
    showlegend=False,
)

# ─── Price Banner ────────────────────────────────────────────────────────────

color_cls = "val-call" if option_type == "call" else "val-put"
money_map  = {"ITM": "val-call", "ATM": "val-blue", "OTM": "val-put"}

c1, c2, c3, c4, c5 = st.columns(5)

def metric(col, label, value, sub, color="val-blue"):
    col.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value {color}">{value}</div>
      <div class="metric-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

metric(c1, "Option Price",    f"${price_data['price']:.4f}",    option_type.upper(), color_cls)
metric(c2, "Intrinsic Value", f"${price_data['intrinsic']:.4f}", "max(S-K, 0)", "val-blue")
metric(c3, "Time Value",      f"${price_data['time_value']:.4f}", "Price − Intrinsic", "val-blue")
metric(c4, "Moneyness",       price_data["moneyness"], f"S/K = {price_data['moneyness_ratio']:.3f}", money_map[price_data["moneyness"]])
metric(c5, "Break-even",      f"${price_data['breakeven']:.2f}", "at expiry", "val-amber")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Greeks ──────────────────────────────────────────────────────────────────

st.markdown('<div class="section-label">Greeks</div>', unsafe_allow_html=True)

greeks_def = [
    ("Delta (Δ)",  "delta",  "#58a6ff", "Change in price per $1 move in underlying",    1.0),
    ("Gamma (Γ)",  "gamma",  "#e3b341", "Rate of change of delta per $1 move",          0.15),
    ("Vega (ν)",   "vega",   "#3fb950", "Change per 1% move in implied vol",            0.5),
    ("Theta (Θ)",  "theta",  "#f85149", "Daily time decay (per calendar day)",          0.1),
    ("Rho (ρ)",    "rho",    "#bc8cff", "Change per 1% move in risk-free rate",         1.0),
    ("Vanna",      "vanna",  "#79c0ff", "Sensitivity of delta to implied volatility",   0.05),
]

gcols = st.columns(6)
for col, (symbol, key_g, color, desc, scale) in zip(gcols, greeks_def):
    val = g[key_g]
    pct = min(100, abs(val) / scale * 100)
    col.markdown(f"""
    <div class="greek-card">
      <div class="greek-symbol">{symbol}</div>
      <div class="greek-value">{val:.4f}</div>
      <div style="height:2px;background:#1e2530;margin:6px 0 8px;">
        <div style="width:{pct:.1f}%;height:100%;background:{color};"></div>
      </div>
      <div class="greek-desc">{desc}</div>
    </div>""", unsafe_allow_html=True)

# ─── Charts Row 1 ────────────────────────────────────────────────────────────

st.markdown('<div class="section-label">Payoff & Delta Profile</div>', unsafe_allow_html=True)

ch1, ch2 = st.columns(2)

with ch1:
    spots = pnl_data["spots"]
    pnl   = pnl_data["pnl"]
    colors_pnl = ["#3fb950" if p >= 0 else "#f85149" for p in pnl]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=spots, y=pnl,
        mode="lines", line=dict(color="#58a6ff", width=2),
        fill="tozeroy",
        fillcolor="rgba(88,166,255,0.06)",
        hovertemplate="Spot: $%{x:.2f}<br>P&L: $%{y:.4f}<extra></extra>",
    ))
    fig.add_hline(y=0, line=dict(color="#2d3748", width=1, dash="dot"))
    fig.add_vline(x=K, line=dict(color="#e3b341", width=1, dash="dash"),
                  annotation_text="Strike", annotation_font_color="#e3b341",
                  annotation_font_size=10)
    fig.update_layout(**plot_layout, height=240,
                      title=dict(text="P&L at Expiry", font=dict(size=11, color="#8b949e"), x=0),
                      yaxis_title="P&L ($)", xaxis_title="Spot Price")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with ch2:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=delta_data["spots"], y=delta_data["deltas"],
        mode="lines", line=dict(color="#3fb950", width=2),
        hovertemplate="Spot: $%{x:.2f}<br>Delta: %{y:.4f}<extra></extra>",
    ))
    fig2.add_vline(x=S, line=dict(color="#58a6ff", width=1, dash="dash"),
                   annotation_text="Current", annotation_font_color="#58a6ff",
                   annotation_font_size=10)
    fig2.update_layout(**plot_layout, height=240,
                       title=dict(text="Delta vs Spot", font=dict(size=11, color="#8b949e"), x=0),
                       yaxis_title="Delta", xaxis_title="Spot Price")
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# ─── Charts Row 2 ────────────────────────────────────────────────────────────

st.markdown('<div class="section-label">Scenario Analysis & Vol Smile</div>', unsafe_allow_html=True)

ch3, ch4 = st.columns(2)

with ch3:
    spots_s = scenario["spots"]
    vols_s  = [f"{v}%" for v in scenario["vols"]]
    mat     = np.array(scenario["matrix"])

    fig3 = go.Figure(data=go.Heatmap(
        z=mat, x=vols_s, y=[f"${s:.0f}" for s in spots_s],
        colorscale=[[0, "#0d2d1a"], [0.5, "#1a4a6e"], [1, "#58a6ff"]],
        text=[[f"${v:.2f}" for v in row] for row in mat],
        texttemplate="%{text}",
        hovertemplate="Spot: %{y}<br>Vol: %{x}<br>Price: %{text}<extra></extra>",
        showscale=True,
        colorbar=dict(
            tickfont=dict(color=TEXT_COL, size=10, family=FONT_MONO),
            outlinewidth=0,
            bgcolor=PLOT_BG,
        )
    ))

    base_idx = spots_s.index(min(spots_s, key=lambda s: abs(s - scenario["base_spot"])))
    fig3.add_shape(type="rect",
        x0=-0.5, x1=len(vols_s)-0.5,
        y0=base_idx-0.5, y1=base_idx+0.5,
        line=dict(color="#58a6ff", width=1.5),
    )

    fig3.update_layout(**plot_layout, height=260,
                       title=dict(text="Spot × Vol Price Matrix", font=dict(size=11, color="#8b949e"), x=0),
                       xaxis_title="Implied Volatility", yaxis_title="Spot Price")
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

with ch4:
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=smile_data["strikes"], y=smile_data["ivs"],
        mode="lines+markers",
        line=dict(color="#e3b341", width=2),
        marker=dict(size=5, color="#e3b341"),
        hovertemplate="Strike: $%{x:.2f}<br>IV: %{y:.2f}%<extra></extra>",
    ))
    fig4.add_vline(x=S, line=dict(color="#58a6ff", width=1, dash="dash"),
                   annotation_text="ATM", annotation_font_color="#58a6ff",
                   annotation_font_size=10)
    fig4.update_layout(**plot_layout, height=260,
                       title=dict(text="Implied Volatility Smile", font=dict(size=11, color="#8b949e"), x=0),
                       yaxis_title="Implied Vol (%)", xaxis_title="Strike Price")
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

# ─── Footer ──────────────────────────────────────────────────────────────────

pcp_ok = "✓ holds" if price_data["put_call_parity_error"] < 0.001 else f"⚠ err {price_data['put_call_parity_error']:.6f}"
exercise = "European" if model_key == "bs" else "American"

st.markdown(f"""
<div class="footer-bar">
  <div class="footer-item">Model:<span>{model}</span></div>
  <div class="footer-item">Exercise:<span>{exercise}</span></div>
  <div class="footer-item">Put-Call Parity:<span>{pcp_ok}</span></div>
  <div class="footer-item">d1:<span>{g['d1']:.4f}</span></div>
  <div class="footer-item">d2:<span>{g['d2']:.4f}</span></div>
  <div class="footer-item">Vanna:<span>{g['vanna']:.4f}</span></div>
  <div class="footer-item">Charm:<span>{g['charm']:.4f}</span></div>
</div>
""", unsafe_allow_html=True)
