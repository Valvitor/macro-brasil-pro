"""
Macro Brasil PRO — Dashboard macroeconômico de segunda geração.
Stack: Plotly Dash · tema escuro profissional · análises exclusivas.
"""

import dash
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime

from src.data import load, last_val, delta_val
from src import charts as ch

# ── Carrega dados na inicialização ────────────────────────────────────────────
print("⏳ Carregando dados do BCB...")
S = load()
print("✅ Dados carregados.")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sparkfig(key: str, col: str, color: str):
    df = S.get(key, pd.DataFrame())
    if df.empty or col not in df.columns:
        return ch.sparkline(pd.Series([], dtype=float), color)
    return ch.sparkline(df[col], color)


def _kpi(label: str, value, delta_str: str, delta_class: str, accent_var: str, spark_fig) -> html.Div:
    return html.Div(className="kpi-card", style={"--kpi-accent": accent_var}, children=[
        html.Div(label, className="kpi-label"),
        html.Div(value if value else "—", className="kpi-value"),
        html.Div(delta_str, className=f"kpi-delta {delta_class}"),
        dcc.Graph(figure=spark_fig, config={"displayModeBar": False},
                  style={"height": "55px", "marginTop": "6px", "marginLeft": "-16px",
                         "marginRight": "-16px"}),
    ])


def _card(figure, style=None) -> html.Div:
    return html.Div(className="chart-card", style=style, children=[
        dcc.Graph(figure=figure, config={"displayModeBar": True, "displaylogo": False,
                                         "modeBarButtonsToRemove": ["select2d", "lasso2d"]},
                  style={"height": "100%"}),
    ])


def _insight(text: str, cls: str = "") -> html.Div:
    return html.Div(className=f"insight-card {cls}",
                    dangerouslyAllowHTML=False,
                    children=dcc.Markdown(text))


def _fmt(v, fmt=".2f", suffix="%"):
    return f"{v:{fmt}}{suffix}" if v is not None else "—"


def _delta_cls(v) -> str:
    if v is None:
        return "neu"
    return "pos" if v >= 0 else "neg"


def _delta_str(v, suffix="pp", fmt="+.2f") -> str:
    if v is None:
        return ""
    return f"{v:{fmt}}{suffix}"


# ── KPIs ──────────────────────────────────────────────────────────────────────

ipca_v  = last_val(S["ipca_12m"],          "ipca_12m")
selic_v = last_val(S["selic"],             "selic")
usd_v   = last_val(S["usdbrl"],            "usdbrl")
prim_v  = last_val(S["resultado_primario"],"resultado_primario")
inad_v  = last_val(S["inadimplencia"],     "inadimplencia")
divb_v  = last_val(S["divida_bruta"],      "divida_bruta")
real_v  = last_val(S["taxa_real"],         "taxa_real")

d_ipca  = delta_val(S["ipca_12m"],          "ipca_12m",   1)
d_usd   = delta_val(S["usdbrl"],            "usdbrl",     5)
d_prim  = delta_val(S["resultado_primario"],"resultado_primario", 1)

kpi_strip = html.Div(className="kpi-strip", children=[
    _kpi("IPCA 12m",       _fmt(ipca_v),      _delta_str(d_ipca,"pp"),     _delta_cls(d_ipca),
         "var(--red)" if ipca_v and ipca_v > 4.5 else "var(--amber)" if ipca_v and ipca_v > 3 else "var(--green)",
         _sparkfig("ipca_12m","ipca_12m","#F43F5E")),
    _kpi("Selic Meta",     _fmt(selic_v),     "",                          "neu",
         "var(--blue)",   _sparkfig("selic","selic","#3B82F6")),
    _kpi("Juro Real",      _fmt(real_v),      "",                          "neu",
         "var(--cyan)" if real_v and real_v >= 4 else "var(--amber)",
         _sparkfig("taxa_real","taxa_real","#06B6D4")),
    _kpi("USD/BRL",        _fmt(usd_v, ".3f",""), _delta_str(d_usd,""," "), _delta_cls(d_usd),
         "var(--amber)",  _sparkfig("usdbrl","usdbrl","#F59E0B")),
    _kpi("Res.Primário",   _fmt(prim_v,"","%PIB"), _delta_str(d_prim,"pp")if d_prim else "",
         _delta_cls(d_prim),"var(--purple)",_sparkfig("resultado_primario","resultado_primario","#8B5CF6")),
    _kpi("Dívida Bruta",   _fmt(divb_v,".1f","%PIB"), "",                 "neu",
         "var(--red)",   _sparkfig("divida_bruta","divida_bruta","#F43F5E")),
])

# ── Layout por seção ──────────────────────────────────────────────────────────

def tab_visao_geral():
    return html.Div(className="db-content", children=[
        html.P("Principais indicadores em um único painel.", className="section-title"),
        html.Div(className="grid-13", children=[
            _card(ch.chart_ipca_gauge(ipca_v or 0), style={"height": "260px"}),
            _card(ch.chart_ipca_12m(S["ipca_12m"]), style={"height": "260px"}),
        ]),
        html.Div(className="grid-2 mt-14", children=[
            _card(ch.chart_selic(S["selic"]),            style={"height": "280px"}),
            _card(ch.chart_focus_selic(S["focus_selic"]),style={"height": "280px"}),
        ]),
        html.Div(className="grid-2 mt-14", children=[
            _card(ch.chart_taxa_real(S["taxa_real"]),         style={"height": "280px"}),
            _card(ch.chart_resultado_primario(S["resultado_primario"]), style={"height": "280px"}),
        ]),
        html.Div(className="mt-14", children=[
            _card(ch.chart_correlacao(S["correlacao"]), style={"height": "460px"}),
        ]),
    ])


def tab_inflacao():
    return html.Div(className="db-content", children=[
        html.Div(className="grid-13", children=[
            _card(ch.chart_ipca_gauge(ipca_v or 0), style={"height": "250px"}),
            _card(ch.chart_inflacao_comparada(S["ipca"], S["inpc"], S["igpm"]),
                  style={"height": "250px"}),
        ]),
        html.Div(className="grid-2 mt-14", children=[
            _card(ch.chart_ipca_mensal(S["ipca"]),             style={"height": "290px"}),
            _card(ch.chart_focus_ipca(S["focus_ipca"]),        style={"height": "290px"}),
        ]),
        html.Div(className="mt-14", children=[
            _card(ch.chart_focus_ipca_evolucao(S["focus_ipca"]), style={"height": "330px"}),
        ]),
        html.Div(className="mt-14 insight-card", children=[
            dcc.Markdown(
                "**Leitura analítica:** A desancoragem das expectativas ocorre quando as projeções "
                "do Focus para anos futuros se afastam da meta de 3%. O gráfico acima ("
                "Ancoragem das Expectativas) mostra essa trajetória de revisão — quando as linhas "
                "convergem para cima ao longo do tempo, o mercado está precificando política monetária "
                "insuficiente para trazer a inflação à meta."
            ),
        ]),
    ])


def tab_juros():
    return html.Div(className="db-content", children=[
        html.Div(className="grid-2", children=[
            _card(ch.chart_selic(S["selic"]),             style={"height": "300px"}),
            _card(ch.chart_focus_selic(S["focus_selic"]), style={"height": "300px"}),
        ]),
        html.Div(className="mt-14", children=[
            _card(ch.chart_taxa_real(S["taxa_real"]), style={"height": "340px"}),
        ]),
        html.Div(className="mt-14 insight-card green", children=[
            dcc.Markdown(
                "**Taxa de Juro Real (ex-post):** Calculada como Selic Meta − IPCA acumulado 12 meses. "
                "A **zona neutra estimada** (4–5% a.a.) representa o r\\* do Brasil — nível compatível com "
                "inflação na meta sem estimular nem contrair a economia. "
                "Quando a taxa real está **acima** da zona neutra, a política monetária é contracionista; "
                "**abaixo**, é expansionista ou acomodatícia."
            ),
        ]),
        if_focus_table(),
    ])


def if_focus_table() -> html.Div:
    if S["focus_ipca"].empty:
        return html.Div()
    ultimo = S["focus_ipca"]["Data"].max()
    df = (
        S["focus_ipca"][S["focus_ipca"]["Data"] == ultimo]
        .groupby("DataReferencia")["Mediana"].median()
        .reset_index()
        .rename(columns={"DataReferencia": "Ano", "Mediana": "Expectativa IPCA (%)"})
        .sort_values("Ano")
    )
    df["Expectativa IPCA (%)"] = df["Expectativa IPCA (%)"].round(2)
    return html.Div(className="mt-14", children=[
        html.P(f"Expectativas Focus IPCA — boletim de {ultimo.strftime('%d/%m/%Y')}",
               className="section-title"),
        dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in df.columns],
            style_header={"backgroundColor": "#111D35", "color": "#475569",
                          "fontWeight": "600", "fontSize": "10px",
                          "textTransform": "uppercase", "letterSpacing": "0.06em",
                          "border": "1px solid #1A2540"},
            style_data={"backgroundColor": "#0F1929", "color": "#E2E8F0",
                        "border": "1px solid #1A2540", "fontSize": "13px"},
            style_data_conditional=[
                {"if": {"filter_query": "{Expectativa IPCA (%)} > 4.5"},
                 "color": "#F43F5E", "fontWeight": "600"},
                {"if": {"filter_query": "{Expectativa IPCA (%)} <= 3"},
                 "color": "#10B981"},
            ],
            style_table={"borderRadius": "10px", "overflow": "hidden"},
        ),
    ])


def tab_cambio():
    serie = S["usdbrl"]["usdbrl"].dropna() if not S["usdbrl"].empty else pd.Series(dtype=float)
    cutoff_52w = serie.index[-1] - pd.DateOffset(weeks=52) if len(serie) else None
    cutoff_12m = serie.index[-1] - pd.DateOffset(months=12) if len(serie) else None

    s52 = serie[serie.index >= cutoff_52w] if cutoff_52w is not None else serie
    s12 = serie[serie.index >= cutoff_12m] if cutoff_12m is not None else serie

    return html.Div(className="db-content", children=[
        html.Div(className="grid-3", children=[
            html.Div(className="kpi-card", style={"--kpi-accent": "var(--amber)"}, children=[
                html.Div("Mínimo 52 semanas", className="kpi-label"),
                html.Div(_fmt(float(s52.min()) if len(s52) else None, ".4f", ""),
                         className="kpi-value"),
            ]),
            html.Div(className="kpi-card", style={"--kpi-accent": "var(--red)"}, children=[
                html.Div("Máximo 52 semanas", className="kpi-label"),
                html.Div(_fmt(float(s52.max()) if len(s52) else None, ".4f", ""),
                         className="kpi-value"),
            ]),
            html.Div(className="kpi-card", style={"--kpi-accent": "var(--blue)"}, children=[
                html.Div("Média 12 meses", className="kpi-label"),
                html.Div(_fmt(float(s12.mean()) if len(s12) else None, ".4f", ""),
                         className="kpi-value"),
            ]),
        ]),
        html.Div(className="mt-14", children=[
            _card(ch.chart_usdbrl_candle(S["usdbrl_ohlc"], S["usdbrl_vol"]),
                  style={"height": "560px"}),
        ]),
    ])


def tab_atividade():
    return html.Div(className="db-content", children=[
        _card(ch.chart_producao_industrial(S["producao_industrial"]), style={"height": "380px"}),
    ])


def tab_fiscal():
    return html.Div(className="db-content", children=[
        html.Div(className="grid-3", children=[
            html.Div(className="kpi-card", style={"--kpi-accent": "var(--purple)"}, children=[
                html.Div("Resultado Primário", className="kpi-label"),
                html.Div(_fmt(prim_v, "", "% PIB"), className="kpi-value"),
            ]),
            html.Div(className="kpi-card", style={"--kpi-accent": "var(--red)"}, children=[
                html.Div("Dívida Bruta", className="kpi-label"),
                html.Div(_fmt(divb_v, ".1f", "% PIB"), className="kpi-value"),
            ]),
            html.Div(className="kpi-card", style={"--kpi-accent": "var(--amber)"}, children=[
                html.Div("Dívida Líquida", className="kpi-label"),
                html.Div(_fmt(last_val(S["divida_liquida"], "divida_liquida"), ".1f", "% PIB"),
                         className="kpi-value"),
            ]),
        ]),
        html.Div(className="mt-14", children=[
            _card(ch.chart_resultado_primario(S["resultado_primario"]), style={"height": "320px"}),
        ]),
        html.Div(className="mt-14", children=[
            _card(ch.chart_divida(S["divida_bruta"], S["divida_liquida"]), style={"height": "320px"}),
        ]),
    ])


def tab_credito():
    return html.Div(className="db-content", children=[
        html.Div(className="grid-3", children=[
            html.Div(className="kpi-card", style={"--kpi-accent": "var(--red)"}, children=[
                html.Div("Inadimplência PF", className="kpi-label"),
                html.Div(_fmt(inad_v), className="kpi-value"),
            ]),
            html.Div(className="kpi-card", style={"--kpi-accent": "var(--blue)"}, children=[
                html.Div("Concessões (último mês)", className="kpi-label"),
                html.Div(_fmt(last_val(S["concessoes"],"concessoes"), ".0f", " Bi").replace("Bi","")
                         + " Bi" if last_val(S["concessoes"],"concessoes") else "—",
                         className="kpi-value"),
            ]),
            html.Div(className="kpi-card", style={"--kpi-accent": "var(--purple)"}, children=[
                html.Div("Crédito / PIB", className="kpi-label"),
                html.Div(_fmt(last_val(S["credito_pib"],"credito_pib"), ".1f"), className="kpi-value"),
            ]),
        ]),
        html.Div(className="mt-14", children=[
            _card(ch.chart_credito(S["inadimplencia"], S["concessoes"]), style={"height": "400px"}),
        ]),
        html.Div(className="mt-14", children=[
            _card(ch.chart_credito_pib(S["credito_pib"]), style={"height": "290px"}),
        ]),
    ])


def tab_analises():
    return html.Div(className="db-content", children=[
        html.P("Análises quantitativas exclusivas", className="section-title"),
        html.Div(className="mt-14", children=[
            _card(ch.chart_taxa_real(S["taxa_real"]), style={"height": "360px"}),
        ]),
        html.Div(className="mt-14 insight-card green", children=[
            dcc.Markdown(
                "**Por que a taxa real importa para gestoras?** A taxa de juro real é o principal "
                "balizador da alocação entre renda fixa e outros ativos. Uma taxa real elevada (> 5% a.a.) "
                "torna o carrego de títulos pós-fixados e NTN-B muito atrativo relativamente à bolsa. "
                "Historicamente, reversões do juro real antecedem compressão de spread de crédito e "
                "início de ciclos de alta em ativos de risco."
            ),
        ]),
        html.Div(className="mt-14", children=[
            _card(ch.chart_correlacao(S["correlacao"]), style={"height": "480px"}),
        ]),
        html.Div(className="mt-14 insight-card", children=[
            dcc.Markdown(
                "**Leitura do heatmap:** Correlações próximas de **+1** (verde escuro) indicam que os "
                "indicadores se movem juntos — útil para identificar redundância analítica. "
                "Correlações próximas de **−1** (vermelho escuro) indicam relação inversa — útil para hedge. "
                "A diagonal principal é sempre 1 (autocorrelação). "
                "Período: últimos 3 anos de dados mensais."
            ),
        ]),
        html.Div(className="mt-14", children=[
            _card(ch.chart_focus_ipca_evolucao(S["focus_ipca"]), style={"height": "380px"}),
        ]),
        html.Div(className="mt-14 insight-card amber", children=[
            dcc.Markdown(
                "**Ancoragem das expectativas:** Este gráfico mostra como o mercado foi revisando "
                "suas projeções de IPCA para cada ano-calendário ao longo do tempo. "
                "Uma linha que **sobe consistentemente** sinaliza desancoragem — o mercado acredita "
                "que o Banco Central não entregará a meta. Uma linha que **converge para baixo** "
                "em direção a 3% indica credibilidade crescente da política monetária."
            ),
        ]),
    ])


# ── App ───────────────────────────────────────────────────────────────────────

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="Macro Brasil PRO",
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

TABS = [
    ("visao-geral",  "Visão Geral"),
    ("inflacao",     "Inflação"),
    ("juros",        "Juros & Focus"),
    ("cambio",       "Câmbio"),
    ("atividade",    "Atividade"),
    ("fiscal",       "Fiscal"),
    ("credito",      "Crédito"),
    ("analises",     "📐 Análises"),
]

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),

    # Header
    html.Div(className="db-header", children=[
        html.Div(className="db-header-logo", children=[
            html.Div(className="db-header-logo-dot"),
            html.Span("Macro Brasil", className="db-header-title"),
            html.Span("PRO · Dashboard Macroeconômico", className="db-header-subtitle"),
        ]),
        html.Div(className="db-header-right", children=[
            html.Span(f"{datetime.today().strftime('%d %b %Y')}", className="db-badge"),
            html.Span("BCB · IBGE · Focus", className="db-badge"),
        ]),
    ]),

    # KPI strip
    kpi_strip,

    # Nav
    html.Div(className="db-nav", id="nav-bar", children=[
        html.A(label, href=f"/{tab_id}", id=f"tab-{tab_id}", className="db-nav-tab")
        for tab_id, label in TABS
    ]),

    # Content
    html.Div(id="page-content"),

    # Footer
    html.Div(className="db-footer", children=[
        html.Span("Desenvolvido por Valvitor Santos · Consultoria de Dados para Gestoras · "
                  "valvitorscf@gmail.com"),
        html.Span([
            "Dados: ",
            html.A("BCB/SGS", href="https://www.bcb.gov.br/estatisticas/tabelaespecial"),
            " · ",
            html.A("Relatório Focus", href="https://www.bcb.gov.br/publicacoes/focus"),
        ]),
    ]),
])


@callback(Output("page-content", "children"), Input("url", "pathname"))
def render(pathname):
    page = (pathname or "/").lstrip("/") or "visao-geral"
    if page == "inflacao":   return tab_inflacao()
    if page == "juros":      return tab_juros()
    if page == "cambio":     return tab_cambio()
    if page == "atividade":  return tab_atividade()
    if page == "fiscal":     return tab_fiscal()
    if page == "credito":    return tab_credito()
    if page == "analises":   return tab_analises()
    return tab_visao_geral()


@callback(
    [Output(f"tab-{tab_id}", "className") for tab_id, _ in TABS],
    Input("url", "pathname"),
)
def highlight_tab(pathname):
    page = (pathname or "/").lstrip("/") or "visao-geral"
    return [
        "db-nav-tab active" if tab_id == page else "db-nav-tab"
        for tab_id, _ in TABS
    ]


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8502)
