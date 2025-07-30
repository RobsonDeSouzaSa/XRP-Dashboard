import streamlit as st
from services import fetch_xrp_price, fetch_xrp_usd

st.title("Monitor de Cotação XRP 🪙")

brl_price, percent_change = fetch_xrp_price()
usd_price = fetch_xrp_usd()

st.metric("Preço em BRL", f"R$ {brl_price:.2f}", f"{percent_change:.2f}%")
st.metric("Preço em USD", f"$ {usd_price:.2f}")
