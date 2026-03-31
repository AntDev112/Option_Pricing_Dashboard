from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scipy.stats import norm
import numpy as np

app = FastAPI(title="OptionScope API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class OptionRequest(BaseModel):
    S: float        # Spot price
    K: float        # Strike price
    T: float        # Time to expiry (years)
    v: float        # Implied volatility (decimal, e.g. 0.20)
    r: float        # Risk-free rate (decimal)
    q: float = 0.0  # Dividend yield (decimal)
    option_type: str = "call"   # "call" or "put"
    model: str = "bs"           # "bs" or "binomial"


# ─── Black-Scholes ───────────────────────────────────────────────────────────

def d1d2(S, K, T, v, r, q):
    d1 = (np.log(S / K) + (r - q + 0.5 * v ** 2) * T) / (v * np.sqrt(T))
    d2 = d1 - v * np.sqrt(T)
    return d1, d2


def bs_price(S, K, T, v, r, q, option_type):
    if T <= 0:
        return max(S - K, 0) if option_type == "call" else max(K - S, 0)
    d1, d2 = d1d2(S, K, T, v, r, q)
    if option_type == "call":
        return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)


def bs_greeks(S, K, T, v, r, q, option_type):
    T = max(T, 1e-6)
    d1, d2 = d1d2(S, K, T, v, r, q)
    sqT = np.sqrt(T)
    pdf1 = norm.pdf(d1)
    eqT, erT = np.exp(-q * T), np.exp(-r * T)

    delta = eqT * norm.cdf(d1) if option_type == "call" else -eqT * norm.cdf(-d1)
    gamma = eqT * pdf1 / (S * v * sqT)
    vega = S * eqT * pdf1 * sqT / 100
    theta = (
        (-S * eqT * pdf1 * v / (2 * sqT) - r * K * erT * norm.cdf(d2) + q * S * eqT * norm.cdf(d1)) / 365
        if option_type == "call"
        else (-S * eqT * pdf1 * v / (2 * sqT) + r * K * erT * norm.cdf(-d2) - q * S * eqT * norm.cdf(-d1)) / 365
    )
    rho = (K * T * erT * norm.cdf(d2) / 100 if option_type == "call"
           else -K * T * erT * norm.cdf(-d2) / 100)
    vanna = -eqT * pdf1 * d2 / v
    charm = (
        eqT * (pdf1 * (r - q) / (v * sqT) - (2 * (r - q) * T - d2 * v * sqT) / (2 * T * v * sqT) * pdf1) / 365
    )
    return dict(d1=d1, d2=d2, delta=delta, gamma=gamma, vega=vega,
                theta=theta, rho=rho, vanna=vanna, charm=charm)


# ─── Binomial Tree (CRR, American) ───────────────────────────────────────────

def binomial_price(S, K, T, v, r, q, option_type, N=200):
    dt = T / N
    u = np.exp(v * np.sqrt(dt))
    d = 1 / u
    p = (np.exp((r - q) * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    ST = S * u ** (np.arange(N, -1, -1)) * d ** (np.arange(0, N + 1))
    vals = np.maximum(ST - K, 0) if option_type == "call" else np.maximum(K - ST, 0)

    for j in range(N - 1, -1, -1):
        ST = ST[:-1] * u
        hold = disc * (p * vals[:-1] + (1 - p) * vals[1:])
        ex = np.maximum(ST - K, 0) if option_type == "call" else np.maximum(K - ST, 0)
        vals = np.maximum(hold, ex)

    return float(vals[0])


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.post("/price")
def price_option(req: OptionRequest):
    price = (binomial_price(req.S, req.K, req.T, req.v, req.r, req.q, req.option_type)
             if req.model == "binomial"
             else bs_price(req.S, req.K, req.T, req.v, req.r, req.q, req.option_type))

    greeks = bs_greeks(req.S, req.K, req.T, req.v, req.r, req.q, req.option_type)
    intrinsic = max(req.S - req.K, 0) if req.option_type == "call" else max(req.K - req.S, 0)
    ratio = req.S / req.K
    money = "ITM" if ratio > 1.02 else "OTM" if ratio < 0.98 else "ATM"
    be = req.K + price if req.option_type == "call" else req.K - price
    call_p = bs_price(req.S, req.K, req.T, req.v, req.r, req.q, "call")
    put_p = bs_price(req.S, req.K, req.T, req.v, req.r, req.q, "put")
    pcp = call_p - put_p - (req.S * np.exp(-req.q * req.T) - req.K * np.exp(-req.r * req.T))

    return {
        "price": round(price, 6),
        "intrinsic": round(intrinsic, 6),
        "time_value": round(max(0, price - intrinsic), 6),
        "moneyness": money,
        "moneyness_ratio": round(ratio, 4),
        "breakeven": round(be, 4),
        "put_call_parity_error": round(abs(pcp), 6),
        "greeks": {k: round(v, 6) for k, v in greeks.items()},
    }


@app.post("/pnl_curve")
def pnl_curve(req: OptionRequest):
    price = bs_price(req.S, req.K, req.T, req.v, req.r, req.q, req.option_type)
    spots = np.linspace(req.S * 0.6, req.S * 1.4, 120)
    payoffs = np.maximum(spots - req.K, 0) if req.option_type == "call" else np.maximum(req.K - spots, 0)
    pnl = payoffs - price
    return {"spots": spots.tolist(), "pnl": pnl.tolist(), "premium": round(price, 4)}


@app.post("/delta_curve")
def delta_curve(req: OptionRequest):
    spots = np.linspace(req.S * 0.6, req.S * 1.4, 120)
    deltas = [bs_greeks(s, req.K, req.T, req.v, req.r, req.q, req.option_type)["delta"] for s in spots]
    return {"spots": spots.tolist(), "deltas": deltas}


@app.post("/scenario_matrix")
def scenario_matrix(req: OptionRequest):
    spot_mults = [0.85, 0.925, 1.0, 1.075, 1.15]
    vols = [0.10, 0.15, 0.20, 0.30, 0.40]
    spots = [round(req.S * m, 2) for m in spot_mults]
    matrix = []
    for s in spots:
        row = [round(bs_price(s, req.K, req.T, v, req.r, req.q, req.option_type), 4) for v in vols]
        matrix.append(row)
    return {"spots": spots, "vols": [int(v * 100) for v in vols], "matrix": matrix, "base_spot": req.S}


@app.post("/vol_smile")
def vol_smile(req: OptionRequest):
    strikes = np.linspace(req.S * 0.70, req.S * 1.30, 17)
    ivs = []
    for k in strikes:
        m = np.log(k / req.S)
        smile = 0.20 + 0.05 * m ** 2 - 0.02 * m
        ivs.append(round(max(0.05, smile) * 100, 2))
    return {"strikes": [round(k, 2) for k in strikes], "ivs": ivs}


@app.get("/health")
def health():
    return {"status": "ok", "engine": "Black-Scholes + CRR Binomial"}
