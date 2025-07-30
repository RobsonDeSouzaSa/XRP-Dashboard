import pandas as pd
import pandas_ta as ta
import json

def load_price_data():
    try:
        with open("data.json", "r") as f:
            history = json.load(f)
        df = pd.DataFrame(history)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except Exception as e:
        print("Erro ao carregar dados:", e)
        return pd.DataFrame()

def compute_indicators(df):
    df["rsi"] = ta.rsi(df["price"])
    df["ema"] = ta.ema(df["price"])

    macd_resultado = ta.macd(df["price"])
    if macd_resultado is not None and "MACD_12_26_9" in macd_resultado:
        df["macd"] = macd_resultado["MACD_12_26_9"]
    else:
        df["macd"] = None  # ou df["macd"] = pd.NA

    return df

