import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from indicators import load_price_data, compute_indicators
from services import fetch_xrp_price, fetch_xrp_usd
from utils import compactar_data_json
from datetime import datetime
import json

# 🔒 Esconde elementos do Streamlit (menu, rodapé, cabeçalho)
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ✅ Cabeçalho personalizado do dashboard
st.markdown("""
    <h1 style='text-align: center; color: #00CED1; font-family: Arial; margin-bottom: 10px;'>
        XRP Dashboard 💸📈
    </h1>
""", unsafe_allow_html=True)

# 🖼️ Logo
# Configurações da página
st.set_page_config(page_title="XRP Dashboard", layout="wide")

# Centraliza e ajusta a logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/Logo.png", width=80)  # Tamanho ideal entre 60 e 100

# Estilo adicional com CSS (opcional)
st.markdown(
    """
    <style>
    .logo {
        display: block;
        margin: 0 auto;
        width: 80px;
    }
    </style>
    <img src="assets/logo.png" class="logo">
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="XRP Painel", layout="wide")
st.title("💰 XRP Painel")

quantidade_xrp = st.number_input("Digite a quantidade de XRP", min_value=0.0, step=0.01)

price, percent = fetch_xrp_price()
price_usd = fetch_xrp_usd()
df = load_price_data()

if price is None or df.empty or "price" not in df.columns:
    st.error("Dados indisponíveis.")
    st.stop()

df = compute_indicators(df)

if any(ind not in df.columns for ind in ["rsi", "ema", "macd"]):
    st.warning("Indicadores incompletos.")
    st.stop()

# Salvar novo dado
novo_dado = {
    "timestamp": datetime.now().isoformat(),
    "price": price,
    "rsi": df["rsi"].iloc[-1],
    "ema": df["ema"].iloc[-1],
    "macd": df["macd"].iloc[-1]
}

try:
    with open("data.json", "r", encoding="utf-8") as f:
        historico = json.load(f)
except:
    historico = []

historico.append(novo_dado)

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(historico, f, indent=2, ensure_ascii=False)

compactar_data_json("data.json", max_registros=500)

cor_valor = "lime" if percent >= 0 else "#FF4500"
st.metric(label="Preço atual do XRP", value=f"R$ {price:.2f}", delta=f"{percent:.2f}%")

if percent >= 5:
    st.success(f"🚀 XRP subiu {percent:.2f}%")
    st.audio("assets/alert.mp3")
elif percent <= -5:
    st.error(f"⚠️ XRP caiu {percent:.2f}%")
    st.audio("assets/alert.mp3")

if quantidade_xrp:
    total_brl = quantidade_xrp * price
    st.markdown(f"🟢 **{quantidade_xrp:.2f} XRP ≈ R$ {total_brl:,.2f}**")

    total_usd = quantidade_xrp * price_usd
    st.markdown(f"💵 **{quantidade_xrp:.2f} XRP ≈ US$ {total_usd:,.2f}**")

# Gráfico de Preços
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(x=df["timestamp"], y=df["price"], mode="lines", name="Preço"))
fig_price.update_layout(title="📈 Preço do XRP", template="plotly_dark")
st.plotly_chart(fig_price, use_container_width=True)

# Gráficos de indicadores
col1, col2, col3 = st.columns(3)

with col1:
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df["timestamp"], y=df["rsi"], mode="lines", name="RSI"))
    fig_rsi.update_layout(title="🧭 RSI", template="plotly_dark", yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig_rsi, use_container_width=True)

with col2:
    fig_ema = go.Figure()
    fig_ema.add_trace(go.Scatter(x=df["timestamp"], y=df["ema"], mode="lines", name="EMA"))
    fig_ema.update_layout(title="📊 EMA", template="plotly_dark")
    st.plotly_chart(fig_ema, use_container_width=True)

with col3:
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=df["timestamp"], y=df["macd"], mode="lines", name="MACD"))
    fig_macd.update_layout(title="📈 MACD", template="plotly_dark")
    st.plotly_chart(fig_macd, use_container_width=True)
