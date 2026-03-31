# OptionScope 📈

> Real-time options pricing dashboard with Black-Scholes and Binomial Tree models.

Built with FastAPI + Streamlit. Designed for quant students, traders, and finance engineers.

![Python](https://img.shields.io/badge/Python-3.11+-58a6ff?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-3fb950?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39-e3b341?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-f85149?style=flat-square)

---

## Features

- **Two pricing models** — Black-Scholes (European) and CRR Binomial Tree (American, N=200)
- **Six Greeks** — Delta, Gamma, Vega, Theta, Rho, Vanna with live bar indicators
- **Second-order Greeks** — Vanna, Charm computed analytically
- **P&L at expiry** diagram with break-even overlay
- **Delta vs Spot** profile curve
- **Spot × Vol scenario matrix** — heatmap across 5 spot levels × 5 vol levels
- **Implied vol smile** — stylised skew curve
- **Put-call parity** verification in real time
- **Dark terminal aesthetic** — IBM Plex Mono, Bloomberg-inspired layout

---

## Project Structure

```
optionscope/
├── backend/
│   ├── main.py              # FastAPI app — pricing engine & API routes
│   └── requirements.txt
├── frontend/
│   ├── app.py               # Streamlit dashboard
│   └── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/price` | Full price + Greeks for one option |
| POST | `/pnl_curve` | P&L at expiry across spot range |
| POST | `/delta_curve` | Delta across spot range |
| POST | `/scenario_matrix` | 5×5 spot/vol price matrix |
| POST | `/vol_smile` | Implied vol skew curve |
| GET | `/health` | Health check |

### Example Request

```bash
curl -X POST http://localhost:8000/price \
  -H "Content-Type: application/json" \
  -d '{
    "S": 100, "K": 100, "T": 0.25,
    "v": 0.20, "r": 0.05, "q": 0.0,
    "option_type": "call", "model": "bs"
  }'
```

### Example Response

```json
{
  "price": 3.5228,
  "intrinsic": 0.0,
  "time_value": 3.5228,
  "moneyness": "ATM",
  "moneyness_ratio": 1.0,
  "breakeven": 103.5228,
  "put_call_parity_error": 0.0,
  "greeks": {
    "d1": 0.2750, "d2": 0.175,
    "delta": 0.6084, "gamma": 0.0389,
    "vega": 0.1946, "theta": -0.0176,
    "rho": 0.1312, "vanna": -0.0021, "charm": 0.0
  }
}
```

---

## Deployment

### Backend — Railway

```bash
# root of backend/
railway init
railway up
```

Set `PORT` env var → Railway auto-detects FastAPI.

### Frontend — Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Point to `frontend/app.py`
4. Set `API_URL` in Streamlit secrets:
   ```toml
   API_URL = "https://your-backend.railway.app"
   ```

Update `API_URL` in `app.py` to read from `st.secrets`:
```python
API_URL = st.secrets.get("API_URL", "http://localhost:8000")
```

---

## Roadmap

- [ ] Live market data via `yfinance` (real spot + IV)
- [ ] 3D volatility surface (Plotly `surface`)
- [ ] Historical IV percentile rank
- [ ] Multi-leg strategy builder (spreads, straddles, condors)
- [ ] Monte Carlo pricing for exotic payoffs
- [ ] Portfolio Greeks aggregation

---

## Author

Built by [your name] · Imperial College London MSc Fintech  
Background: Murex (capital markets software)

---

## License

MIT
