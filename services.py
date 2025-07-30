import requests, json, time
from datetime import datetime

# ⚙️ Configurações de cache
CACHE_EXPIRATION = 5 * 60  # 5 minutos para BRL
USD_EXPIRATION = 10 * 60   # 10 minutos para USD
_cache = {"price": None, "timestamp": 0}
usd_cache = {"price": None, "timestamp": 0}

# 💰 Função principal: busca cotação XRP em BRL
def fetch_xrp_price():
    global _cache
    current_time = time.time()

    if _cache["price"] and (current_time - _cache["timestamp"] < CACHE_EXPIRATION):
        price = _cache["price"]
    else:
        price = None
        fontes = [from_binance, from_coinpaprika, from_coingecko]
        for fonte in fontes:
            try:
                price = fonte()
                if price:
                    _cache["price"] = price
                    _cache["timestamp"] = current_time
                    break
            except Exception as e:
                print(f"⚠️ Erro {fonte.__name__}:", e)

        if not price:
            return None, None

    timestamp = datetime.now().isoformat()

    # 📝 Histórico BRL
    try:
        with open("data.json", "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    if not history or price != history[-1]["price"]:
        history.append({"timestamp": timestamp, "price": price})

    history = history[-500:]

    try:
        with open("data.json", "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print("⚠️ Erro ao salvar data.json:", e)

    delta, percent = 0, 0
    if len(history) >= 2:
        delta = price - history[-2]["price"]
        if history[-2]["price"]:
            percent = (delta / history[-2]["price"]) * 100

    return price, percent

# 💵 Cotação USD com múltiplas fontes + cache + histórico
def fetch_xrp_usd():
    global usd_cache
    current_time = time.time()

    if usd_cache["price"] and (current_time - usd_cache["timestamp"] < USD_EXPIRATION):
        return usd_cache["price"]

    price_usd = None
    fontes_usd = [usd_from_coinpaprika, usd_from_coingecko, usd_from_messari]

    for fonte in fontes_usd:
        try:
            price_usd = fonte()
            if price_usd:
                usd_cache["price"] = price_usd
                usd_cache["timestamp"] = current_time
                salvar_historico_usd(price_usd)
                break
        except Exception as e:
            print(f"⚠️ Erro {fonte.__name__}:", e)

    return price_usd

# 🌐 Fontes BRL
def from_binance():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=XRPBRL"
    r = requests.get(url, timeout=8)
    r.raise_for_status()
    return float(r.json()["price"])

def from_coinpaprika():
    url = "https://api.coinpaprika.com/v1/tickers/xrp-xrp"
    r = requests.get(url, timeout=8)
    r.raise_for_status()
    return float(r.json()["quotes"]["BRL"]["price"])

def from_coingecko():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "ripple", "vs_currencies": "brl"}
    r = requests.get(url, params=params, timeout=8)
    r.raise_for_status()
    return float(r.json()["ripple"]["brl"])

# 🌎 Fontes USD
def usd_from_coinpaprika():
    url = "https://api.coinpaprika.com/v1/tickers/xrp-xrp"
    r = requests.get(url, timeout=8)
    r.raise_for_status()
    return float(r.json()["quotes"]["USD"]["price"])

def usd_from_coingecko():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "ripple", "vs_currencies": "usd"}
    r = requests.get(url, params=params, timeout=8)
    r.raise_for_status()
    return float(r.json()["ripple"]["usd"])

def usd_from_messari():
    url = "https://data.messari.io/api/v1/assets/xrp/metrics"
    r = requests.get(url, timeout=8)
    r.raise_for_status()
    return float(r.json()["data"]["market_data"]["price_usd"])

# 📦 Salvamento histórico USD
def salvar_historico_usd(price_usd):
    timestamp = datetime.now().isoformat()
    dado = {"timestamp": timestamp, "price": price_usd}

    try:
        with open("xrp_usd_data.json", "r") as f:
            historico_usd = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        historico_usd = []

    historico_usd.append(dado)
    historico_usd = historico_usd[-500:]

    try:
        with open("xrp_usd_data.json", "w") as f:
            json.dump(historico_usd, f, indent=2)
    except Exception as e:
        print("⚠️ Erro ao salvar histórico USD:", e)
