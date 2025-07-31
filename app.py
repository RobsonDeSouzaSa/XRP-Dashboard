import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from services import fetch_xrp_price, fetch_xrp_usd
from streamlit_autorefresh import st_autorefresh
import json

# 🔄 Atualiza a cada 60 segundos
st_autorefresh(interval=60 * 1000, key="painel_xrp")

# 📋 Configuração do painel
st.set_page_config(page_title="Painel XRP em Tempo Real", layout="wide")
st.title("💰 Painel XRP com Dados em Tempo Real 📈")

# 🧮 Entrada formatada
def formatar_quantidade(valor_str):
    valor_str = valor_str.replace(".", "").replace(",", ".")
    try:
        valor_float = float(valor_str)
        return f"{valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor_str

quantidade_str = st.text_input("Digite a quantidade de XRP", value="0,00")
quantidade_formatada = formatar_quantidade(quantidade_str)
st.write(f"🧮 Quantidade formatada: **{quantidade_formatada} XRP**")

try:
    quantidade_xrp = float(quantidade_str.replace(".", "").replace(",", "."))
except:
    quantidade_xrp = 0.0

# 💵 Buscar preços reais
price_brl, percent = fetch_xrp_price()
price_usd = fetch_xrp_usd()

if price_brl is None or price_usd is None:
    st.error("⚠️ Não foi possível obter o preço atual do XRP.")
    st.stop()

# 📈 Métricas
cor_valor = "lime" if percent >= 0 else "#FF4500"
st.metric(label="Preço atual do XRP (BRL)", value=f"R$ {price_brl:.2f}", delta=f"{percent:.2f}%")
st.metric(label="Preço atual do XRP (USD)", value=f"US$ {price_usd:.2f}")

# 💸 Valores calculados
if quantidade_xrp:
    total_brl = quantidade_xrp * price_brl
    total_usd = quantidade_xrp * price_usd
    st.markdown(f"🟢 **{quantidade_xrp:.2f} XRP ≈ R$ {total_brl:,.2f}**")
    st.markdown(f"💵 **{quantidade_xrp:.2f} XRP ≈ US$ {total_usd:,.2f}**")

# 📊 Indicador BRL
fig_brl = go.Figure(go.Indicator(
    mode="number+delta",
    value=price_brl,
    delta={"reference": price_brl * (1 - percent / 100), "relative": True, "valueformat": ".2f"},
    title={"text": "📊 Cotação XRP em BRL"},
    number={"prefix": "R$ "}
))
fig_brl.update_layout(template="plotly_dark")
st.plotly_chart(fig_brl, use_container_width=True)

# 🎨 Gráfico histórico BRL
try:
    with open("data.json", "r") as f:
        historico_brl = pd.DataFrame(json.load(f))
        historico_brl["timestamp"] = pd.to_datetime(historico_brl["timestamp"])

    fig_hist_brl = px.line(
        historico_brl, x="timestamp", y="price",
        title="📈 Histórico de XRP em BRL",
        markers=True, template="plotly_dark"
    )
    fig_hist_brl.update_layout(
        yaxis_title="Preço (BRL)",
        xaxis_title="Data",
        xaxis_rangeslider_visible=True
    )
    st.plotly_chart(fig_hist_brl, use_container_width=True)
except Exception as e:
    st.warning(f"⚠️ Erro ao carregar histórico BRL: {e}")

# 🌎 Gráfico histórico USD
try:
    with open("xrp_usd_data.json", "r") as f:
        historico_usd = pd.DataFrame(json.load(f))
        historico_usd["timestamp"] = pd.to_datetime(historico_usd["timestamp"])

    fig_hist_usd = px.line(
        historico_usd, x="timestamp", y="price",
        title="🌍 Histórico de XRP em USD",
        markers=True, template="plotly_dark"
    )
    fig_hist_usd.update_layout(
        yaxis_title="Preço (USD)",
        xaxis_title="Data",
        xaxis_rangeslider_visible=True
    )
    st.plotly_chart(fig_hist_usd, use_container_width=True)
except Exception as e:
    st.warning(f"⚠️ Erro ao carregar histórico USD: {e}")

# 🧠 Rodapé personalizado
st.markdown("""
    <style>
        .custom-footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #0f1117;
            color: #00ffcc;
            text-align: center;
            padding: 10px;
            font-size: 14px;
            font-family: 'Source Sans Pro', sans-serif;
            border-top: 1px solid #00ffcc;
        }
    </style>
    <div class="custom-footer">
        Painel desenvolvido por <strong>Robson</strong> | Versão 3.3 🚀 com gráficos interativos + atualização automática ⏱️
    </div>
""", unsafe_allow_html=True)
