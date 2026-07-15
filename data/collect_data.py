"""
=============================================================
  El Nino Research — Data Collection Script
  Author : Srishti Chauhan
  Date   : May 2026
=============================================================
Run this file to download ALL datasets needed for the project.
Saves everything into data/raw/ as CSV files.
"""

import os
import requests
import pandas as pd
import yfinance as yf
from pycoingecko import CoinGeckoAPI
from io import StringIO
import warnings
warnings.filterwarnings("ignore")

RAW = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(RAW, exist_ok=True)

def banner(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")

def ok(msg):   print(f"  [OK]  {msg}")
def info(msg): print(f"  -->   {msg}")
def warn(msg): print(f"  [!!]  {msg}")

# ─────────────────────────────────────────────────────────────
# 1.  ENSO / Oceanic Nino Index (ONI)  — NOAA
# ─────────────────────────────────────────────────────────────
def download_oni():
    banner("1/6  Oceanic Nino Index (ENSO) — NOAA")
    url = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        lines = [l for l in r.text.strip().splitlines() if l.strip()]
        rows = []
        for line in lines[1:]:          # skip header
            parts = line.split()
            if len(parts) >= 4:
                try:
                    season = parts[0]
                    year   = int(parts[1])
                    oni    = float(parts[3])   # parts[3]=ANOM (anomaly), parts[2]=TOTAL (raw SST)
                    rows.append({"season": season, "year": year, "ONI": oni})
                except ValueError:
                    continue
        df = pd.DataFrame(rows)
        # Label El Nino phases
        def phase(v):
            if   v >= 2.0: return "Super El Nino"
            elif v >= 1.5: return "Strong El Nino"
            elif v >= 1.0: return "Moderate El Nino"
            elif v >= 0.5: return "Weak El Nino"
            elif v <= -0.5: return "La Nina"
            else:           return "Neutral"
        df["phase"] = df["ONI"].apply(phase)
        path = os.path.join(RAW, "oni_enso.csv")
        df.to_csv(path, index=False)
        ok(f"Saved {len(df)} rows  →  {path}")
        info(f"Super El Nino events in data: {(df['phase']=='Super El Nino').sum()} seasons")
        return df
    except Exception as e:
        warn(f"ONI download failed: {e}")
        return None

# ─────────────────────────────────────────────────────────────
# 2.  NCEI Billion-Dollar Disasters — NOAA
# ─────────────────────────────────────────────────────────────
def download_ncei():
    banner("2/6  NCEI Billion-Dollar Disasters — NOAA")
    url = "https://www.ncei.noaa.gov/access/billions/events.csv"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text))
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        path = os.path.join(RAW, "ncei_billion_dollar_disasters.csv")
        df.to_csv(path, index=False)
        ok(f"Saved {len(df)} disaster events  →  {path}")
        info(f"Date range: {df.iloc[:,0].min()} – {df.iloc[:,0].max()}")
        return df
    except Exception as e:
        warn(f"NCEI download failed ({e}) — trying alternative URL...")
        # Alternative: direct CSV from NCEI
        try:
            url2 = "https://www.ncei.noaa.gov/access/billions/summary-stats.csv"
            r2 = requests.get(url2, timeout=30)
            df2 = pd.read_csv(StringIO(r2.text))
            path = os.path.join(RAW, "ncei_summary_stats.csv")
            df2.to_csv(path, index=False)
            ok(f"Saved summary stats  →  {path}")
            return df2
        except Exception as e2:
            warn(f"Both NCEI URLs failed: {e2}")
            return None

# ─────────────────────────────────────────────────────────────
# 3.  Financial Markets — Yahoo Finance (yfinance)
# ─────────────────────────────────────────────────────────────
def download_financial():
    banner("3/6  Financial Markets — Yahoo Finance")

    tickers = {
        # Broad markets
        "^GSPC"  : "SP500",
        "^VIX"   : "VIX",
        "^DJI"   : "DowJones",
        # Insurance & Banking ETFs
        "KIE"    : "Insurance_ETF",
        "KBE"    : "Banking_ETF",
        "XLF"    : "Financials_ETF",
        # Commodity ETFs / Futures
        "DBA"    : "Agriculture_ETF",
        "GLD"    : "Gold_ETF",
        "USO"    : "Oil_ETF",
        # Commodities (via ETF proxies available from 1970s via individual futures)
        "WEAT"   : "Wheat_ETF",
        "CORN"   : "Corn_ETF",
        "JO"     : "Coffee_ETF",
        "NIB"    : "Cocoa_ETF",
    }

    all_frames = []
    for ticker, name in tickers.items():
        try:
            df = yf.download(ticker, start="1990-01-01", end="2025-12-31",
                             progress=False, auto_adjust=True)
            if df.empty:
                warn(f"{ticker} ({name}): no data returned")
                continue
            close = df[["Close"]].copy()
            close.columns = [name]
            close.index.name = "date"
            all_frames.append(close)
            ok(f"{ticker:8s} ({name}): {len(df)} rows  [{df.index[0].date()} → {df.index[-1].date()}]")
        except Exception as e:
            warn(f"{ticker} ({name}): {e}")

    if all_frames:
        merged = pd.concat(all_frames, axis=1)
        path = os.path.join(RAW, "financial_markets.csv")
        merged.to_csv(path)
        ok(f"\nMerged financial data  →  {path}  ({merged.shape[0]} rows x {merged.shape[1]} cols)")
        return merged
    else:
        warn("No financial data downloaded")
        return None

# ─────────────────────────────────────────────────────────────
# 4.  Commodity Spot Prices — Yahoo Finance (longer history)
# ─────────────────────────────────────────────────────────────
def download_commodities():
    banner("4/6  Commodity Futures — Yahoo Finance")

    futures = {
        "ZW=F"  : "Wheat_Futures",
        "ZC=F"  : "Corn_Futures",
        "KC=F"  : "Coffee_Futures",
        "CC=F"  : "Cocoa_Futures",
        "CL=F"  : "CrudeOil_Futures",
        "GC=F"  : "Gold_Futures",
        "NG=F"  : "NatGas_Futures",
    }

    frames = []
    for ticker, name in futures.items():
        try:
            df = yf.download(ticker, start="1975-01-01", end="2025-12-31",
                             progress=False, auto_adjust=True)
            if df.empty:
                warn(f"{ticker}: no data")
                continue
            close = df[["Close"]].copy()
            close.columns = [name]
            close.index.name = "date"
            frames.append(close)
            ok(f"{ticker:8s} ({name}): {len(df)} rows  [{df.index[0].date()} → {df.index[-1].date()}]")
        except Exception as e:
            warn(f"{ticker}: {e}")

    if frames:
        merged = pd.concat(frames, axis=1)
        path = os.path.join(RAW, "commodities.csv")
        merged.to_csv(path)
        ok(f"\nMerged commodity data  →  {path}  ({merged.shape[0]} rows x {merged.shape[1]} cols)")
        return merged
    return None

# ─────────────────────────────────────────────────────────────
# 5.  Cryptocurrency Data — CoinGecko (free, no API key)
# ─────────────────────────────────────────────────────────────
def download_crypto():
    banner("5/6  Cryptocurrency Data — CoinGecko")
    cg = CoinGeckoAPI()

    coins = {
        "bitcoin"  : "BTC",
        "ethereum" : "ETH",
        "binancecoin": "BNB",
    }

    frames = []
    for coin_id, symbol in coins.items():
        try:
            info(f"Fetching {symbol} ({coin_id}) — this may take 10-15 seconds...")
            data = cg.get_coin_market_chart_by_id(
                id=coin_id, vs_currency="usd", days="max")
            prices = data["prices"]               # [[timestamp_ms, price], ...]
            df = pd.DataFrame(prices, columns=["timestamp", f"{symbol}_price"])
            df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date
            df = df.drop(columns=["timestamp"]).set_index("date")
            frames.append(df)
            ok(f"{symbol}: {len(df)} days  [{df.index[0]} → {df.index[-1]}]")
        except Exception as e:
            warn(f"{coin_id}: {e}")

    if frames:
        merged = pd.concat(frames, axis=1)
        path = os.path.join(RAW, "crypto_prices.csv")
        merged.to_csv(path)
        ok(f"\nMerged crypto data  →  {path}  ({merged.shape[0]} rows x {merged.shape[1]} cols)")
        return merged
    return None

# ─────────────────────────────────────────────────────────────
# 6.  NBER Recession Indicator — FRED (no API key needed)
# ─────────────────────────────────────────────────────────────
def download_nber():
    banner("6/6  NBER Recession Indicator — FRED")
    url = ("https://fred.stlouisfed.org/graph/fredgraph.csv"
           "?vintage_date=2025-01-01&id=USREC")
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text), parse_dates=["DATE"])
        df.columns = ["date", "recession"]
        df = df.set_index("date")
        path = os.path.join(RAW, "nber_recession.csv")
        df.to_csv(path)
        recession_months = df["recession"].sum()
        ok(f"Saved {len(df)} monthly rows  →  {path}")
        info(f"Total recession months: {recession_months}  ({recession_months/len(df)*100:.1f}% of history)")
        return df
    except Exception as e:
        warn(f"NBER download failed: {e}")
        return None

# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────
def print_summary():
    banner("DOWNLOAD COMPLETE — File Summary")
    files = os.listdir(RAW)
    if not files:
        warn("No files found in data/raw/")
        return
    for f in sorted(files):
        fpath = os.path.join(RAW, f)
        size  = os.path.getsize(fpath)
        df    = pd.read_csv(fpath, nrows=2)
        print(f"  {f:<45s}  {size/1024:>6.1f} KB  |  {len(df.columns)} columns")
    print(f"\n  All raw data saved in: {RAW}")
    print(f"\n  NEXT STEP: Open notebooks/01_data_exploration.ipynb")

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n  El Nino Research — Data Collection Pipeline")
    print("  Srishti Chauhan | May 2026")

    oni         = download_oni()
    ncei        = download_ncei()
    financial   = download_financial()
    commodities = download_commodities()
    crypto      = download_crypto()
    nber        = download_nber()

    print_summary()
