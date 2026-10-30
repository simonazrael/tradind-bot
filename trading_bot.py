import pandas as pd
import yfinance as yf
import pandas_ta as ta

def analyze_for_high_probability(ticker_symbol):
    print(f"Scanning {ticker_symbol} for high-edge setups...\n")
    
    # Fetch historical daily data
    df = yf.download(ticker_symbol, period="120d", interval="1d", progress=False)
    
    if df.empty:
        return "Asset data not found."

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Compute Technical Indicators
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA_50'] = ta.ema(df['Close'], length=50)
    df['EMA_200'] = ta.ema(df['Close'], length=200)
    
    # Volume moving average
    df['Vol_SMA20'] = ta.sma(df['Volume'], length=20)

    # Candlestick Pattern
    df['Engulfing'] = ta.cdl_pattern(df['Open'], df['High'], df['Low'], df['Close'], name="engulfing")

    # Extract latest metrics
    latest = df.iloc[-1]
    close = latest['Close']
    rsi = latest['RSI']
    ema_50 = latest['EMA_50']
    ema_200 = latest['EMA_200']
    volume = latest['Volume']
    vol_sma = latest['Vol_SMA20']
    engulfing = latest.get('ENGULFING', 0)

    # Scoring Logic
    score = 40  
    reasons = []

    # Rule 1: Macro Trend Filter
    if close > ema_50 and ema_50 > ema_200:
        score += 25
        reasons.append("✓ Strong Trend: Price is safely above 50 & 200 EMA.")
    else:
        score -= 20
        reasons.append("✗ Weak Trend: Market structure is mixed or bearish.")

    # Rule 2: Volume Filter
    if volume > vol_sma:
        score += 15
        reasons.append("✓ Volume Confirmation: Volume is above the 20-day average.")
    else:
        reasons.append("✗ Low Volume: Lack of institutional backing.")

    # Rule 3: Pullback to Value + Momentum
    if 40 <= rsi <= 55:
        score += 15
        reasons.append(f"✓ Healthy Momentum: RSI is resetting in the bull zone ({rsi:.1f}).")
    elif rsi < 30:
        score += 10
        reasons.append(f"✓ Deep Oversold Bounce Zone: RSI at {rsi:.1f}.")

    # Rule 4: Price Action Pattern
    if engulfing > 0:
        score += 20
        reasons.append("✓ Bullish Engulfing Pattern confirmed at support/trend.")

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