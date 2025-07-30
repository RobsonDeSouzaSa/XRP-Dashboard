import json
import argparse
from datetime import datetime, timedelta
import random

def gerar_dados(tipo="ciclo", total=100):
    agora = datetime.now()
    dados = []
    preco_base = 20

    for i in range(total):
        timestamp = agora - timedelta(minutes=total - i)

        # Múltiplos ciclos
        if tipo == "ciclo":
            fase = i // (total // 3)
            if fase == 0:   # alta
                preco = preco_base + i * 0.06 + random.uniform(-0.2, 0.2)
            elif fase == 1: # queda
                preco = preco_base + (total//3 * 0.06) - (i - total//3) * 0.08 + random.uniform(-0.2, 0.2)
            else:           # recuperação
                preco = preco_base - (total//3 * 0.08) + (i - 2*(total//3)) * 0.07 + random.uniform(-0.2, 0.2)
        elif tipo == "alta":
            preco = preco_base + i * 0.05 + random.uniform(-0.2, 0.2)
        elif tipo == "queda":
            preco = preco_base - i * 0.05 + random.uniform(-0.2, 0.2)
        elif tipo == "volatilidade":
            preco = preco_base + random.uniform(-3, 3)
        else:
            preco = preco_base + random.uniform(-0.5, 0.5)

        preco = round(preco, 2)
        dados.append({"timestamp": timestamp.isoformat(), "price": preco})

    return dados

# 🎛️ Argumentos da linha de comando
parser = argparse.ArgumentParser(description="Gerador de dados XRP simulados")
parser.add_argument("--tipo", choices=["alta", "queda", "volatilidade", "neutro", "ciclo"], default="ciclo")
parser.add_argument("--total", type=int, default=100)

args = parser.parse_args()
dados = gerar_dados(tipo=args.tipo, total=args.total)

with open("data.json", "w") as f:
    json.dump(dados, f, indent=2)

print(f"✅ Gerado {args.total} dados com cenário: {args.tipo}")
