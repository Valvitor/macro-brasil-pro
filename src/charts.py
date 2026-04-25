"""
Figuras Plotly com tema escuro profissional para o Dash.
Paleta inspirada em terminais financeiros modernos.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

# ── Paleta ───────────────────────────────────────────────────────────────────
BG_PLOT   = "#0D1525"
BG_PAPER  = "#0D1525"
GRID      = "#1A2540"
TEXT      = "#E2E8F0"
MUTED     = "#64748B"
BLUE      = "#3B82F6"
BLUE_DIM  = "rgba(59,130,246,0.12)"
GREEN     = "#10B981"
GREEN_DIM = "rgba(16,185,129,0.12)"
RED       = "#F43F5E"
RED_DIM   = "rgba(244,63,94,0.12)"
AMBER     = "#F59E0B"
PURPLE    = "#8B5CF6"
CYAN      = "#06B6D4"

# Template Plotly base
_tpl = go.layout.Template()
_tpl.layout = go.Layout(
    plot_bgcolor=BG_PLOT,
    paper_bgcolor=BG_PAPER,
    font=dict(family="Inter, -apple-system, sans-serif", color=TEXT, size=12),
    xaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID, showgrid=True),
    yaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID, showgrid=True),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#1E293B", font_color=TEXT, bordercolor=GRID),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
        bgcolor="rgba(0,0,0,0)", font_color=MUTED,
    ),
    margin=dict(t=55, b=45, l=55, r=20),
)
pio.templates["macro_dark"] = _tpl
pio.templates.default = "macro_dark"


def _title(text: str) -> dict:
    return dict(text=text, font=dict(size=14, color=TEXT), x=0.02)


def _source(text: str) -> list[dict]:
    return [dict(
        text=f"Fonte: {text}", xref="paper", yref="paper",
        x=0, y=-0.12, showarrow=False,
        font=dict(size=10, color=MUTED), align="left",
    )]


# ── Sparkline (inline nos cards KPI) ─────────────────────────────────────────

def sparkline(series: pd.Series, color: str = BLUE, n: int = 40) -> go.Figure:
    s = series.dropna().iloc[-n:]
    fig = go.Figure(go.Scatter(
        y=s.values,
        line=dict(color=color, width=1.5),
        fill="tozeroy",
        fillcolor=color.replace(")", ",0.15)").replace("rgb", "rgba") if "rgb" in color
                  else f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15)",
        mode="lines",
    ))
    fig.update_layout(
        height=55,
        margin=dict(t=0, b=0, l=0, r=0, pad=0),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        dragmode=False,
    )
    return fig


# ── Inflação ─────────────────────────────────────────────────────────────────

def chart_ipca_gauge(valor: float) -> go.Figure:
    meta, teto = 3.0, 4.5
    cor = GREEN if valor <= meta else AMBER if valor <= teto else RED
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        number=dict(suffix="%", font=dict(size=32, color=cor)),
        gauge=dict(
            axis=dict(range=[0, 12], ticksuffix="%", tickcolor=MUTED, tickfont=dict(color=MUTED)),
            bar=dict(color=cor, thickness=0.28),
            bgcolor=GRID,
            bordercolor=GRID,
            steps=[
                dict(range=[0, meta], color="rgba(16,185,129,0.18)"),
                dict(range=[meta, teto], color="rgba(245,158,11,0.18)"),
                dict(range=[teto, 12],  color="rgba(244,63,94,0.18)"),
            ],
            threshold=dict(
                line=dict(color=RED, width=3),
                thickness=0.85,
                value=teto,
            ),
        ),
    ))
    fig.add_annotation(
        text="IPCA 12m",
        xref="paper", yref="paper", x=0.5, y=-0.08,
        showarrow=False, font=dict(color=MUTED, size=13),
    )
    fig.update_layout(
        paper_bgcolor=BG_PAPER,
        margin=dict(t=20, b=40, l=30, r=30),
        height=220,
    )
    return fig


def chart_ipca_12m(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df["ipca_12m"],
        name="IPCA 12m",
        line=dict(color=BLUE, width=2.5),
        fill="tozeroy", fillcolor=BLUE_DIM,
        hovertemplate="%{x|%b %Y}: <b>%{y:.2f}%</b><extra></extra>",
    ))
    fig.add_hline(y=3.0, line_dash="dot",  line_color=GREEN, annotation_text="Meta 3%",  annotation_font_color=GREEN)
    fig.add_hline(y=4.5, line_dash="dash", line_color=RED,   annotation_text="Teto 4,5%", annotation_font_color=RED)
    fig.update_layout(title=_title("IPCA — Acumulado 12 Meses"), yaxis_title="% a.a.",
                      annotations=_source("BCB SGS 433"))
    return fig


def chart_inflacao_comparada(df_ipca, df_inpc, df_igpm) -> go.Figure:
    def acum12(df, col):
        return ((1 + df[col] / 100).rolling(12).apply(lambda x: x.prod(), raw=True) - 1) * 100

    fig = go.Figure()
    for df, col, nome, cor in [
        (df_ipca, "ipca_mensal", "IPCA", BLUE),
        (df_inpc, "inpc_mensal", "INPC", CYAN),
        (df_igpm, "igpm_mensal", "IGP-M", AMBER),
    ]:
        if not df.empty:
            s = acum12(df, col).dropna()
            fig.add_trace(go.Scatter(x=s.index, y=s, name=nome, line=dict(color=cor, width=2.2),
                                     hovertemplate=f"{nome} %{{x|%b %Y}}: <b>%{{y:.2f}}%</b><extra></extra>"))
    fig.add_hline(y=3.0, line_dash="dot", line_color=GREEN)
    fig.add_hline(y=4.5, line_dash="dash", line_color=RED)
    fig.update_layout(title=_title("IPCA × INPC × IGP-M — Acumulado 12 Meses"), yaxis_title="% a.a.",
                      annotations=_source("BCB SGS"))
    return fig


def chart_ipca_mensal(df: pd.DataFrame) -> go.Figure:
    colors = [RED if v > 0 else GREEN for v in df["ipca_mensal"]]
    fig = go.Figure(go.Bar(
        x=df.index, y=df["ipca_mensal"],
        marker_color=colors,
        hovertemplate="%{x|%b %Y}: <b>%{y:.2f}%</b><extra></extra>",
    ))
    fig.update_layout(title=_title("IPCA — Variação Mensal"), yaxis_title="% a.m.",
                      annotations=_source("BCB SGS 433"), showlegend=False)
    return fig


# ── Juros ────────────────────────────────────────────────────────────────────

def chart_selic(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=df.index, y=df["selic"],
        line=dict(color=BLUE, width=2.5),
        fill="tozeroy", fillcolor=BLUE_DIM,
        hovertemplate="%{x|%d %b %Y}: <b>%{y:.2f}%</b><extra></extra>",
    ))
    fig.update_layout(title=_title("Taxa Selic — Meta"), yaxis_title="% a.a.",
                      annotations=_source("BCB SGS 432"), showlegend=False)
    return fig


def chart_taxa_real(df: pd.DataFrame) -> go.Figure:
    """Taxa de juro real ex-post = Selic − IPCA 12m. Análise exclusiva v2."""
    if df.empty:
        return go.Figure()
    cor = GREEN if df["taxa_real"].iloc[-1] >= 4 else AMBER
    fig = go.Figure()
    # Zona neutra estimada (r* Brasil ~4–5%)
    fig.add_hrect(y0=4, y1=5, fillcolor="rgba(59,130,246,0.08)", line_width=0,
                  annotation_text="Taxa Neutra Estimada (4–5%)",
                  annotation_font_color=BLUE, annotation_position="top left")
    fig.add_hline(y=0, line_color=MUTED, line_width=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=df["taxa_real"],
        name="Taxa Real (Selic − IPCA 12m)",
        line=dict(color=cor, width=2.5),
        fill="tozeroy",
        fillcolor=GREEN_DIM if df["taxa_real"].iloc[-1] >= 0 else RED_DIM,
        hovertemplate="%{x|%b %Y}: <b>%{y:.2f}% a.a.</b><extra></extra>",
    ))
    fig.update_layout(
        title=_title("Taxa de Juro Real Ex-Post (Selic − IPCA 12m)"),
        yaxis_title="% a.a.",
        annotations=_source("BCB SGS 432 / 433 — cálculo próprio"),
        showlegend=False,
    )
    return fig


def _reuniao_key(r: str):
    try:
        num, ano = r.lstrip("R").split("/")
        return (int(ano), int(num))
    except Exception:
        return (9999, 99)


def chart_focus_selic(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    ultimo = df["Data"].max()
    agg = (
        df[df["Data"] == ultimo]
        .groupby("Reuniao", as_index=False)["Mediana"].median()
    )
    agg["_k"] = agg["Reuniao"].apply(_reuniao_key)
    agg = agg.sort_values("_k").reset_index(drop=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=agg["Reuniao"], y=agg["Mediana"],
        mode="lines+markers",
        line=dict(color=BLUE, width=2.5),
        marker=dict(color=BG_PAPER, size=8, line=dict(color=BLUE, width=2)),
        fill="tozeroy", fillcolor=BLUE_DIM,
        hovertemplate="Copom %{x}: <b>%{y:.2f}% a.a.</b><extra></extra>",
    ))
    fig.update_layout(
        title=_title(f"Trajetória da Selic Esperada — Focus ({ultimo.strftime('%d/%m/%Y')})"),
        yaxis_title="% a.a.", xaxis_title="Reunião Copom",
        annotations=_source("BCB Relatório Focus — mediana das instituições"),
        showlegend=False,
    )
    return fig


def chart_focus_ipca(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    df = df[df["Data"] >= df["Data"].max() - pd.Timedelta(days=365)]
    anos = sorted(df["DataReferencia"].unique())
    cores = [BLUE, CYAN, AMBER, GREEN, PURPLE]
    fig = go.Figure()
    for i, ano in enumerate(anos[:5]):
        sub = df[df["DataReferencia"] == ano].groupby("Data")["Mediana"].median().reset_index()
        fig.add_trace(go.Scatter(
            x=sub["Data"], y=sub["Mediana"], name=str(ano),
            line=dict(color=cores[i % len(cores)], width=2),
            hovertemplate=f"{ano}: <b>%{{y:.2f}}%</b><extra></extra>",
        ))
    fig.add_hline(y=3.0, line_dash="dot", line_color=GREEN, annotation_text="Meta")
    fig.add_hline(y=4.5, line_dash="dash", line_color=RED,  annotation_text="Teto")
    fig.update_layout(title=_title("Expectativas Focus — IPCA por Ano-Calendário"), yaxis_title="% a.a.",
                      annotations=_source("BCB Relatório Focus"))
    return fig


def chart_focus_ipca_evolucao(df: pd.DataFrame) -> go.Figure:
    """Ancoragem das expectativas: como o mercado revisou o IPCA de cada ano ao longo do tempo."""
    if df.empty:
        return go.Figure()
    anos = sorted(df["DataReferencia"].unique(), reverse=True)[:4]
    cores = [BLUE, CYAN, AMBER, GREEN]
    fig = go.Figure()
    fig.add_hline(y=3.0, line_dash="dot", line_color=GREEN,
                  annotation_text="Meta 3%", annotation_font_color=GREEN)
    fig.add_hline(y=4.5, line_dash="dash", line_color=RED,
                  annotation_text="Teto 4,5%", annotation_font_color=RED)
    for i, ano in enumerate(anos):
        sub = (
            df[df["DataReferencia"] == ano]
            .groupby("Data")["Mediana"].median()
            .reset_index()
            .sort_values("Data")
        )
        fig.add_trace(go.Scatter(
            x=sub["Data"], y=sub["Mediana"], name=str(ano),
            line=dict(color=cores[i], width=2),
            hovertemplate=f"IPCA {ano} em %{{x|%d/%m/%Y}}: <b>%{{y:.2f}}%</b><extra></extra>",
        ))
    fig.update_layout(
        title=_title("Ancoragem das Expectativas — Revisão do IPCA ao Longo do Tempo"),
        yaxis_title="% a.a.",
        annotations=_source("BCB Relatório Focus"),
    )
    return fig


# ── Câmbio ───────────────────────────────────────────────────────────────────

def chart_usdbrl_candle(df_ohlc: pd.DataFrame, df_vol: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.70, 0.30], vertical_spacing=0.04,
        subplot_titles=("USD/BRL — Candlestick Semanal", "Volatilidade Realizada (21d, anualizada)"),
    )
    if not df_ohlc.empty:
        fig.add_trace(go.Candlestick(
            x=df_ohlc.index,
            open=df_ohlc["open"], high=df_ohlc["high"],
            low=df_ohlc["low"],   close=df_ohlc["close"],
            name="USD/BRL",
            increasing_line_color=GREEN, decreasing_line_color=RED,
            increasing_fillcolor=GREEN, decreasing_fillcolor=RED,
        ), row=1, col=1)
    if not df_vol.empty:
        fig.add_trace(go.Bar(
            x=df_vol.index, y=df_vol["vol"],
            name="Volatilidade",
            marker_color=[RED if v > 20 else AMBER if v > 12 else MUTED for v in df_vol["vol"]],
            hovertemplate="%{x|%d %b %Y}: <b>%{y:.1f}%</b><extra></extra>",
        ), row=2, col=1)
    fig.update_layout(
        title=_title("Câmbio USD/BRL"),
        height=520, showlegend=False,
        annotations=[*_source("BCB SGS 10813")],
        xaxis_rangeslider_visible=False,
    )
    for row in [1, 2]:
        fig.update_xaxes(gridcolor=GRID, row=row, col=1)
        fig.update_yaxes(gridcolor=GRID, row=row, col=1)
    return fig


# ── Correlação ───────────────────────────────────────────────────────────────

def chart_correlacao(df: pd.DataFrame) -> go.Figure:
    """Heatmap de correlação entre indicadores — análise exclusiva v2."""
    if df.empty:
        return go.Figure()
    corr = df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    z = corr.values.copy()
    z[mask] = None

    text = [[f"{v:.2f}" if v is not None and not np.isnan(v) else "" for v in row] for row in z]

    fig = go.Figure(go.Heatmap(
        z=z, x=list(corr.columns), y=list(corr.index),
        colorscale=[
            [0.0, "#7F1D1D"], [0.25, RED],
            [0.5, "#1E293B"],
            [0.75, GREEN], [1.0, "#064E3B"],
        ],
        zmin=-1, zmax=1,
        text=text, texttemplate="%{text}",
        hovertemplate="%{y} × %{x}: <b>%{z:.2f}</b><extra></extra>",
        showscale=True,
        colorbar=dict(tickcolor=MUTED, tickfont=dict(color=MUTED), outlinewidth=0,
                      bgcolor=BG_PAPER, title=dict(text="Correlação", font=dict(color=MUTED))),
    ))
    fig.update_layout(
        title=_title("Correlação entre Indicadores Macro (últimos 3 anos, mensal)"),
        height=430,
        annotations=_source("BCB SGS — cálculo próprio"),
        xaxis=dict(side="bottom"),
    )
    return fig


# ── Fiscal ───────────────────────────────────────────────────────────────────

def chart_resultado_primario(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    fig = go.Figure(go.Bar(
        x=df.index, y=df["resultado_primario"],
        marker_color=[GREEN if v >= 0 else RED for v in df["resultado_primario"]],
        hovertemplate="%{x|%b %Y}: <b>%{y:.2f}% PIB</b><extra></extra>",
    ))
    fig.add_hline(y=0, line_color=MUTED, line_width=1)
    fig.update_layout(title=_title("Resultado Primário do Setor Público (% do PIB, acum. 12m)"),
                      yaxis_title="% do PIB", annotations=_source("BCB SGS 5793"), showlegend=False)
    return fig


def chart_divida(df_bruta: pd.DataFrame, df_liquida: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if not df_bruta.empty:
        fig.add_trace(go.Scatter(x=df_bruta.index, y=df_bruta["divida_bruta"],
                                  name="Dívida Bruta", line=dict(color=RED, width=2.5),
                                  fill="tozeroy", fillcolor=RED_DIM,
                                  hovertemplate="%{x|%b %Y}: <b>%{y:.1f}% PIB</b><extra></extra>"))
    if not df_liquida.empty:
        fig.add_trace(go.Scatter(x=df_liquida.index, y=df_liquida["divida_liquida"],
                                  name="Dívida Líquida", line=dict(color=AMBER, width=2, dash="dash"),
                                  hovertemplate="%{x|%b %Y}: <b>%{y:.1f}% PIB</b><extra></extra>"))
    fig.update_layout(title=_title("Dívida Bruta e Líquida do Setor Público (% do PIB)"),
                      yaxis_title="% do PIB", annotations=_source("BCB SGS 4537 / 4513"))
    return fig


# ── Crédito ──────────────────────────────────────────────────────────────────

def chart_credito(df_inad: pd.DataFrame, df_conc: pd.DataFrame) -> go.Figure:
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Inadimplência — Pessoa Física", "Concessões (R$ Bi)"))
    if not df_inad.empty:
        fig.add_trace(go.Scatter(x=df_inad.index, y=df_inad["inadimplencia"], name="Inadimpl. PF",
                                  line=dict(color=RED, width=2.5), fill="tozeroy", fillcolor=RED_DIM,
                                  hovertemplate="%{x|%b %Y}: <b>%{y:.2f}%</b><extra></extra>"),
                      row=1, col=1)
    if not df_conc.empty:
        fig.add_trace(go.Bar(x=df_conc.index, y=df_conc["concessoes"] / 1000,
                              marker_color=BLUE,
                              hovertemplate="%{x|%b %Y}: <b>R$ %{y:,.1f} Bi</b><extra></extra>"),
                      row=1, col=2)
    fig.update_layout(title=_title("Crédito — Inadimplência e Concessões"),
                      annotations=[*_source("BCB Nota de Crédito")],
                      height=380, showlegend=False)
    for r in [1, 2]:
        fig.update_xaxes(gridcolor=GRID, row=r, col=1)
        fig.update_yaxes(gridcolor=GRID, row=r, col=1)
    return fig


def chart_credito_pib(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    fig = go.Figure(go.Scatter(
        x=df.index, y=df["credito_pib"],
        line=dict(color=PURPLE, width=2.5),
        fill="tozeroy", fillcolor="rgba(139,92,246,0.12)",
        hovertemplate="%{x|%b %Y}: <b>%{y:.1f}%</b><extra></extra>",
    ))
    fig.update_layout(title=_title("Crédito Total / PIB (%)"), yaxis_title="% do PIB",
                      annotations=_source("BCB SGS 20626"), showlegend=False)
    return fig


# ── Atividade ────────────────────────────────────────────────────────────────

def chart_producao_industrial(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    df = df.copy()
    df["mm3"] = df["producao_industrial"].rolling(3).mean()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df["producao_industrial"], name="Mensal",
                          marker_color=BLUE, opacity=0.45,
                          hovertemplate="%{x|%b %Y}: <b>%{y:.1f}</b><extra></extra>"))
    fig.add_trace(go.Scatter(x=df.index, y=df["mm3"], name="Média móvel 3m",
                              line=dict(color=CYAN, width=2.5),
                              hovertemplate="%{x|%b %Y}: <b>%{y:.1f}</b><extra></extra>"))
    fig.update_layout(title=_title("Produção Industrial (índice, base 2012=100)"),
                      yaxis_title="Índice", annotations=_source("BCB SGS 21859 / IBGE"), barmode="overlay")
    return fig
