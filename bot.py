import yfinance as yf
import requests
import time
from datetime import datetime

DISCORD_WEBHOOK = "APNA_WEBHOOK_URL"

def send_discord(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

def get_data():
    df = yf.download("GC=F", period="60d", interval="1d", progress=False)
    df.columns = df.columns.droplevel(1)
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    df['RSI'] = 100-(100/(1+gain.rolling(14).mean()/loss.rolling(14).mean()))
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df

send_discord("🤖 AlgoGoldBot 24/7 Started!")
print("Bot started!")

while True:
    try:
        now = datetime.now().strftime("%H:%M:%S")
        df = get_data()

        price = float(df['Close'].iloc[-1])
        ma20  = float(df['MA20'].iloc[-1])
        ma50  = float(df['MA50'].iloc[-1])
        rsi   = float(df['RSI'].iloc[-1])
        macd  = float(df['MACD'].iloc[-1])
        sig   = float(df['Signal_Line'].iloc[-1])
        prev_macd = float(df['MACD'].iloc[-2])
        prev_sig  = float(df['Signal_Line'].iloc[-2])

        ma_bull = ma20 > ma50
        macd_up = macd > sig and prev_macd <= prev_sig
        macd_dn = macd < sig and prev_macd >= prev_sig

        print(f"⏰ {now} | Gold: ${price:.2f} | RSI: {rsi:.1f}")

        if ma_bull and macd_up and rsi < 70:
            send_discord(f"🟢 BUY!\n💛 Gold: ${price:.2f}\nRSI: {rsi:.1f}")
        elif not ma_bull and macd_dn and rsi > 30:
            send_discord(f"🔴 SELL!\n💛 Gold: ${price:.2f}\nRSI: {rsi:.1f}")

        time.sleep(3600)  # Har 1 ghante mein check

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
