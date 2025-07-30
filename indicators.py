import pandas as pd
import pandas_ta as ta

def load_price_data():
    try:
        with open("data.json", "r") as f:
            history = pd.read_json(f)
        history["timestamp"] = pd.to_datetime(history["timestamp"])
        return history
    except Exception as e:
        print("Erro ao carregar dados:", e)
        return pd.DataFrame()

def compute_indicators(df):
    df["rsi"] = ta.rsi(df["price"])
    df["ema"] = ta.ema(df["price"])
    macd_result = ta.macd(df["price"])
    df["macd"] = macd_result["MACD_12_26_9"] if "MACD_12_26_9" in macd_result else pd.NA
    return df
