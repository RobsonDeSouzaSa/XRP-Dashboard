import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Simulação de dados (substitua com seus loaders reais!)
np.random.seed(42)
dates = pd.date_range(start="2023-01-01", end="2023-12-31")
prices = np.cumsum(np.random.randn(len(dates))) + 100
volume = np.random.randint(1000, 5000, size=len(dates))

df = pd.DataFrame({
    "timestamp": dates,
    "price": prices,
    "volume": volume
})
df.set_index("timestamp", inplace=True)

# Indicadores técnicos
df["ema"] = df["price"].ewm(span=20, adjust=False).mean()
delta = df["price"].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = -delta.where(delta < 0, 0).rolling(14).mean()
rs = gain / loss
df["rsi"] = 100 - (100 / (1 + rs))
ema12 = df["price"].ewm(span=12, adjust=False).mean()
ema26 = df["price"].ewm(span=26, adjust=False).mean()
df["macd"] = ema12 - ema26
df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
df["bb_upper"] = df["price"].rolling(20).mean() + 2 * df["price"].rolling(20).std()
df["bb_lower"] = df["price"].rolling(20).mean() - 2 * df["price"].rolling(20).std()

# 🧮 Simulação de valores atuais (substitua com fetch_xrp_price e fetch_xrp_usd reais!)
price = df["price"].iloc[-1]
price_usd = round(price / 4.9, 2)  # simulação
percent = round((price - df["price"].iloc[-2]) / df["price"].iloc[-2] * 100, 2)

# Verificação dos dados
if price is None or df.empty or "price" not in df.columns:
    st.error("Dados indisponíveis.")
    st.stop()

# Layout e título
st.set_page_config(page_title="Painel XRP", layout="wide")
st.title("💰 Painel XRP com Indicadores Técnicos 📊")

# 🎛️ Quantidade de XRP
quantidade_xrp = st.number_input("Digite a quantidade de XRP", min_value=0.0, step=0.01)

# 🎯 Métricas de preço
cor_valor = "lime" if percent >= 0 else "#FF4500"
st.metric(label="Preço atual do XRP", value=f"R$ {price:.2f}", delta=f"{percent:.2f}%")

if percent >= 5:
    st.success(f"🚀 XRP subiu {percent:.2f}%")
elif percent <= -5:
    st.error(f"⚠️ XRP caiu {percent:.2f}%")

if quantidade_xrp:
    total_brl = quantidade_xrp * price
    st.markdown(f"🟢 **{quantidade_xrp:.2f} XRP ≈ R$ {total_brl:,.2f}**")

    total_usd = quantidade_xrp * price_usd
    st.markdown(f"💵 **{quantidade_xrp:.2f} XRP ≈ US$ {total_usd:,.2f}**")

# 📅 Filtro de datas
min_date = df.index.min()
max_date = df.index.max()
start_date = st.sidebar.date_input("Data inicial", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.sidebar.date_input("Data final", min_value=min_date, max_value=max_date, value=max_date)
df_filtered = df.loc[start_date:end_date]

# 📈 Gráfico de Preço + EMA + Bollinger Bands
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["price"], mode="lines", name="Preço", line=dict(color="blue"), hovertemplate="Data: %{x}<br>Preço: R$ %{y:.2f}"))
fig_price.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["ema"], mode="lines", name="EMA", line=dict(color="orange", dash="dot"), hovertemplate="Data: %{x}<br>EMA: R$ %{y:.2f}"))
fig_price.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["bb_upper"], mode="lines", name="BB Superior", line=dict(color="green", dash="dot")))
fig_price.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["bb_lower"], mode="lines", name="BB Inferior", line=dict(color="red", dash="dot")))
fig_price.update_layout(title="📈 Preço do XRP com EMA e Bollinger Bands", template="plotly_dark")
st.plotly_chart(fig_price, use_container_width=True)

# 🧭 Gráfico RSI
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["rsi"], mode="lines", name="RSI", line=dict(color="cyan"), hovertemplate="Data: %{x}<br>RSI: %{y:.2f}"))
fig_rsi.add_shape(type="line", x0=df_filtered.index[0], x1=df_filtered.index[-1], y0=70, y1=70, line=dict(color="red", dash="dot"))
fig_rsi.add_shape(type="line", x0=df_filtered.index[0], x1=df_filtered.index[-1], y0=30, y1=30, line=dict(color="green", dash="dot"))
fig_rsi.update_layout(title="🧭 RSI (Índice de Força Relativa)", template="plotly_dark", yaxis=dict(range=[0, 100]))
st.plotly_chart(fig_rsi, use_container_width=True)

# 📉 Gráfico MACD
fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["macd"], mode="lines", name="MACD", line=dict(color="magenta"), hovertemplate="Data: %{x}<br>MACD: %{y:.2f}"))
fig_macd.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["macd_signal"], mode="lines", name="Sinal", line=dict(color="yellow")))
fig_macd.add_shape(type="line", x0=df_filtered.index[0], x1=df_filtered.index[-1], y0=0, y1=0, line=dict(color="white", dash="dot"))
fig_macd.update_layout(title="📉 MACD", template="plotly_dark")
st.plotly_chart(fig_macd, use_container_width=True)

# 📦 Volume
fig_vol = go.Figure()
fig_vol.add_trace(go.Bar(x=df_filtered.index, y=df_filtered["volume"], name="Volume", marker_color="gray", hovertemplate="Data: %{x}<br>Volume: %{y}"))
fig_vol.update_layout(title="📦 Volume negociado", template="plotly_dark")
st.plotly_chart(fig_vol, use_container_width=True)

# 🔻 Rodapé
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
        Painel desenvolvido por <strong>Robson</strong> | Versão 2.1 🚀
    </div>
""", unsafe_allow_html=True)
