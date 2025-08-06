import requests, json, time
from datetime import datetime

# ⚙️ Configurações de cache
CACHE_EXPIRATION = 5 * 60  # 5 minutos para BRL
USD_EXPIRATION = 10 * 60   # 10 minutos para USD
_cache = {"price": None, "timestamp": 0}
usd_cache = {"price": None, "timestamp": 0}

# 💰 Função principal: busca cotação XRP em BRL com média ponderada
def fetch_xrp_price():
    global _cache
    current_time = time.time()

    if _cache["price"] and (current_time - _cache["timestamp"] < CACHE_EXPIRATION):
        price = _cache["price"]
    else:
        # 🌐 Fontes BRL e seus pesos
        fontes = {
            from_binance: 0.5,
            from_coinpaprika: 0.3,
            from_coingecko: 0.2
        }

        valores_ponderados = []
        pesos_validos = []

        for fonte, peso in fontes.items():
            try:
                valor = fonte()
                if valor:
                    valores_ponderados.append(valor * peso)
                    pesos_validos.append(peso)
            except Exception as e:
                print(f"⚠️ Erro {fonte.__name__}:", e)

        if valores_ponderados:
            price = sum(valores_ponderados) / sum(pesos_validos)
            _cache["price"] = price
            _cache["timestamp"] = current_time
        else:
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

# 💵 Cotação USD com média ponderada
def fetch_xrp_usd():
    global usd_cache
    current_time = time.time()

    if usd_cache["price"] and (current_time - usd_cache["timestamp"] < USD_EXPIRATION):
        return usd_cache["price"]

    fontes_usd = {
        usd_from_coinpaprika: 0.4,
        usd_from_coingecko: 0.4,
        usd_from_messari: 0.2
    }

    valores_usd = []
    pesos_usd = []

    for fonte, peso in fontes_usd.items():
        try:
            valor = fonte()
            if valor:
                valores_usd.append(valor * peso)
                pesos_usd.append(peso)
        except Exception as e:
            print(f"⚠️ Erro {fonte.__name__}:", e)

    if valores_usd:
        price_usd = sum(valores_usd) / sum(pesos_usd)
        usd_cache["price"] = price_usd
        usd_cache["timestamp"] = current_time
        salvar_historico_usd(price_usd)
        return price_usd

    return None

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
