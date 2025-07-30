import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from indicators import load_price_data, compute_indicators
from services import fetch_xrp_price, fetch_xrp_usd
from utils import compactar_data_json
from datetime import datetime
import plotly.graph_objects as go
import json

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "XRP Painel"

app.layout = dbc.Container([
    html.H1("💰 XRP Painel", className="text-center mt-3"),
    html.Hr(),

    html.Div([
        html.H4("💸 Quanto vale meu XRP?", className="text-center mb-2"),
        dbc.Input(id="xrp-quantidade", type="number", placeholder="Digite a quantidade de XRP", min=0, step=0.01),
        html.P(id="valor-em-reais", className="mt-2", style={"fontSize": "20px", "color": "aqua"}),
        html.P(id="valor-em-dolar", className="mt-1", style={"fontSize": "20px", "color": "gold"})
    ], className="text-center mb-4"),

    dbc.Row([
        dbc.Col(html.Div([
            html.H3("Resumo do mercado > XRP", className="mb-0"),
            html.H4(id="resumo-preco", className="display-5"),
            html.P(id="resumo-var", className="mt-0", style={"fontSize": "18px"})
        ], style={
            "padding": "20px",
            "background": "#121212",
            "border": "2px solid",
            "borderImage": "linear-gradient(to right, #00CED1, #007BFF) 1",
            "borderRadius": "10px",
            "color": "white",
            "boxShadow": "0 0 12px #00CED1"
        }), width=4),

        dbc.Col(dcc.Graph(id="grafico-precos", config={"displaylogo": False}), width=8)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico-rsi", config={"displaylogo": False}), width=4),
        dbc.Col(dcc.Graph(id="grafico-ema", config={"displaylogo": False}), width=4),
        dbc.Col(dcc.Graph(id="grafico-macd", config={"displaylogo": False}), width=4),
    ]),

    html.Div(id="alerta-xrp", className="text-center mt-2"),
    dcc.Interval(id="atualizador", interval=60*1000, n_intervals=0)
], fluid=True)

@app.callback(
    Output("resumo-preco", "children"),
    Output("resumo-var", "children"),
    Output("alerta-xrp", "children"),
    Output("grafico-precos", "figure"),
    Output("grafico-rsi", "figure"),
    Output("grafico-ema", "figure"),
    Output("grafico-macd", "figure"),
    Output("valor-em-reais", "children"),
    Output("valor-em-dolar", "children"),
    Input("atualizador", "n_intervals"),
    Input("xrp-quantidade", "value")
)
def atualizar_dashboard(n, quantidade_xrp):
    price, percent = fetch_xrp_price()
    price_usd = fetch_xrp_usd()
    df = load_price_data()

    if price is None or df.empty or "price" not in df:
        msg = "Dados indisponíveis"
        return msg, msg, msg, {}, {}, {}, {}, "", ""

    df = compute_indicators(df)

    if any(ind not in df for ind in ["rsi", "ema", "macd"]):
        msg = f"R$ {price:.2f}"

        return msg, "Indicadores incompletos", "", {}, {}, {}, {}, "", ""

    # ✅ NOVO: salvar e compactar data.json
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

    resumo_valor = html.Span(f"R$ {price:.2f}", style={
        "color": cor_valor,
        "fontWeight": "bold",
        "transition": "0.5s"
    })
    resumo_variacao = f"{'+' if percent >= 0 else ''}{percent:.2f}% hoje"

    alerta = []
    if percent >= 5:
        alerta.append(html.Div(f"🚀 XRP subiu {percent:.2f}%", style={"color": "lime"}))
        alerta.append(html.Audio(src="/assets/alert.mp3", autoPlay=True))
    elif percent <= -5:
        alerta.append(html.Div(f"⚠️ XRP caiu {percent:.2f}%", style={"color": "#FF4500"}))
        alerta.append(html.Audio(src="/assets/alert.mp3", autoPlay=True))

    valor_convertido = ""
    if quantidade_xrp and price:
        total = quantidade_xrp * price
        valor_convertido = f"🟢 {quantidade_xrp:.2f} XRP ≈ R$ {total:,.2f}"

    valor_convertido_dolar = ""
    if quantidade_xrp and price_usd:
        total_usd = quantidade_xrp * price_usd
        valor_convertido_dolar = f"💵 {quantidade_xrp:.2f} XRP ≈ US$ {total_usd:,.2f}"

    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(
        x=df["timestamp"], y=df["price"],
        mode="lines+markers", name="Preço",
        line=dict(color="#00CED1", width=2),
        marker=dict(size=6, color="orange", symbol="circle")
    ))
    fig_price.update_layout(
        title="📈 Preço do XRP",
        template="plotly_dark",
        xaxis_title="Data e Hora",
        yaxis_title="Preço (BRL)",
        hovermode="x unified",
        xaxis=dict(rangeslider=dict(visible=True)),
        dragmode="pan",
        margin=dict(t=40, b=30, l=30, r=30),
        height=400
    )

    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df["timestamp"], y=df["rsi"], mode="lines", name="RSI",
                                 line=dict(color="blue")))
    fig_rsi.update_layout(
        title="🧭 RSI",
        template="plotly_dark",
        yaxis=dict(range=[0, 100]),
        xaxis=dict(rangeslider=dict(visible=True)),
        hovermode="x unified",
        dragmode="pan",
        shapes=[
            {"type": "line", "x0": df["timestamp"].min(), "x1": df["timestamp"].max(), "y0": 70, "y1": 70,
             "line": {"color": "red", "dash": "dash"}},
            {"type": "line", "x0": df["timestamp"].min(), "x1": df["timestamp"].max(), "y0": 30, "y1": 30,
             "line": {"color": "green", "dash": "dash"}}
        ]
    )

    fig_ema = go.Figure()
    fig_ema.add_trace(go.Scatter(x=df["timestamp"], y=df["ema"], mode="lines", name="EMA",
                                 line=dict(color="gold")))
    fig_ema.update_layout(
        title="📊 EMA",
        template="plotly_dark",
        xaxis=dict(rangeslider=dict(visible=True)),
        hovermode="x unified",
        dragmode="pan"
    )

    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=df["timestamp"], y=df["macd"], mode="lines", name="MACD",
                                  line=dict(color="orchid")))
    fig_macd.update_layout(
        title="📈 MACD",
        template="plotly_dark",
        xaxis=dict(rangeslider=dict(visible=True)),
        hovermode="x unified",
        dragmode="pan"
    )

    return resumo_valor, resumo_variacao, alerta, fig_price, fig_rsi, fig_ema, fig_macd, valor_convertido, valor_convertido_dolar

if __name__ == "__main__":
    app.run_server(debug=True)
