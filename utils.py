import json
import os
from datetime import datetime

def compactar_data_json(caminho="data.json", max_registros=500):
    if not os.path.exists(caminho):
        return

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)

        if not isinstance(dados, list):
            return

        for item in dados:
            if "timestamp" in item:
                try:
                    item["timestamp"] = datetime.fromisoformat(item["timestamp"])
                except:
                    pass

        dados.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)
        dados = dados[:max_registros]

        for item in dados:
            if isinstance(item.get("timestamp"), datetime):
                item["timestamp"] = item["timestamp"].isoformat()

        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print("⚠️ Erro ao compactar o arquivo JSON:", e)
