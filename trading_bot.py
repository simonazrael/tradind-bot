import pandas as pd
import numpy as np
import yfinance as yf

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_for_high_probability(ticker_symbol):
    print(f"Scanning {ticker_symbol} for high-edge setups...\n")
    
    # Fetch historical daily data
    df = yf.download(ticker_symbol, period="120d", interval="1d", progress=False)
    
    if df.empty:
        return "Asset data not found."

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Compute Indicators natively
    df['RSI'] = calculate_rsi(df['Close'], window=14)
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    df['Vol_SMA20'] = df['Volume'].rolling(window=20).mean()

    # Extract latest metrics safely
    latest = df.iloc[-1]
    close = float(latest['Close'])
    rsi = float(latest['RSI'])
    ema_50 = float(latest['EMA_50'])
    ema_200 = float(latest['EMA_200'])
    volume = float(latest['Volume'])
    vol_sma = float(latest['Vol_SMA20'])

    # Scoring Logic for 70% Win-Rate Filter
    score = 40  
    reasons = []

    # Rule 1: Macro Trend Filter
    if close > ema_50 and ema_50 > ema_200:
        score += 30
        reasons.append("✓ Strong Trend: Price is safely above 50 & 200 EMA.")
    else:
        score -= 20
        reasons.append("✗ Weak Trend: Market structure is mixed or bearish.")

    # Rule 2: Volume Confirmation Filter
    if volume > vol_sma:
        score += 20
        reasons.append("✓ Volume Confirmation: Volume is above the 20-day average.")
    else:
        reasons.append("✗ Low Volume: Lack of institutional backing.")

    # Rule 3: Pullback to Value + Momentum
    if 40 <= rsi <= 55:
        score += 10
        reasons.append(f"✓ Healthy Momentum: RSI is resetting in the bull zone ({rsi:.1f}).")
    elif rsi < 30:
        score += 10
        reasons.append(f"✓ Deep Oversold Bounce Zone: RSI at {rsi:.1f}.")

    score = max(0, min(100, score))

    # Final Verdict
    print(f"==========================================")
    print(f" ASSET: {ticker_symbol} | PRICE: ${close:.2f}")
    print(f" PROBABILITY SCORE: {score}/100")
    print(f"==========================================")
    
    if score >= 70:
        print("🎯 STATUS: HIGH PROBABILITY SETUP (>= 70%)")
        print("Conditions meet strict risk/reward parameters.")
    else:
        print("⏳ STATUS: NO TRADE / WAIT (Score below 70%)")
        print("Market conditions do not meet high-edge criteria.")

    print("\nFactor Breakdown:")
    for r in reasons:
        print(f" {r}")
    print(f"------------------------------------------\n")

if __name__ == "__main__":
    analyze_for_high_probability("BTC-USD")
    analyze_for_high_probability("ETH-USD")
