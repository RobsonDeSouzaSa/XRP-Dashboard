import json

def compactar_data_json(path, max_registros=500):
    try:
        with open(path, "r", encoding="utf-8") as f:
            dados = json.load(f)
        dados = dados[-max_registros:]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Erro ao compactar JSON:", e)
