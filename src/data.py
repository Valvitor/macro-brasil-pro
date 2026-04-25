"""
Coleta de dados macroeconômicos via BCB SGS e Relatório Focus.
Sem dependência de Streamlit — compatível com Dash/Flask.
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional

BCB_SGS  = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados"
FOCUS_ANUAIS = (
    "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
    "ExpectativasMercadoAnuais"
    "?$top=2000&$filter=Indicador%20eq%20%27{}%27%20and%20baseCalculo%20eq%200"
    "&$orderby=Data%20desc&$format=json&$select=Indicador,Data,Mediana,DataReferencia"
)
FOCUS_SELIC = (
    "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
    "ExpectativasMercadoSelic"
    "?$top=500&$orderby=Data%20desc&$format=json&$select=Data,Reuniao,Mediana"
)


def _fetch(code: int, start: str, name: str) -> pd.DataFrame:
    end = datetime.today().strftime("%d/%m/%Y")
    try:
        r = requests.get(
            BCB_SGS.format(code),
            params={"formato": "json", "dataInicial": start, "dataFinal": end},
            timeout=15,
        )
        r.raise_for_status()
        df = pd.DataFrame(r.json())
        df["data"]  = pd.to_datetime(df["data"], dayfirst=True)
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
        return df.rename(columns={"valor": name}).dropna(subset=[name]).set_index("data")
    except Exception:
        return pd.DataFrame()


def _focus(indicator: str, url_tpl: str) -> pd.DataFrame:
    try:
        r = requests.get(url_tpl.format(indicator) if "{}" in url_tpl else url_tpl, timeout=15)
        r.raise_for_status()
        df = pd.DataFrame(r.json().get("value", []))
        if df.empty:
            return df
        df["Data"]    = pd.to_datetime(df["Data"])
        df["Mediana"] = pd.to_numeric(df["Mediana"], errors="coerce")
        return df.dropna(subset=["Mediana"])
    except Exception:
        return pd.DataFrame()


def load() -> dict:
    d5 = (datetime.today() - timedelta(days=365 * 5)).strftime("%d/%m/%Y")
    d3 = (datetime.today() - timedelta(days=365 * 3)).strftime("%d/%m/%Y")
    d2 = (datetime.today() - timedelta(days=365 * 2)).strftime("%d/%m/%Y")

    raw = {
        "ipca"               : _fetch(433,   d5, "ipca_mensal"),
        "inpc"               : _fetch(188,   d5, "inpc_mensal"),
        "igpm"               : _fetch(189,   d5, "igpm_mensal"),
        "selic"              : _fetch(432,   d5, "selic"),
        "usdbrl"             : _fetch(10813, d2, "usdbrl"),
        "resultado_primario" : _fetch(5793,  d5, "resultado_primario"),
        "divida_bruta"       : _fetch(4537,  d5, "divida_bruta"),
        "divida_liquida"     : _fetch(4513,  d5, "divida_liquida"),
        "inadimplencia"      : _fetch(21082, d3, "inadimplencia"),
        "concessoes"         : _fetch(20631, d2, "concessoes"),
        "credito_pib"        : _fetch(20626, d3, "credito_pib"),
        "producao_industrial": _fetch(21859, d5, "producao_industrial"),
        "ibcbr"              : _fetch(24363, d5, "ibcbr"),
        "focus_ipca"         : _focus("IPCA", FOCUS_ANUAIS),
        "focus_selic"        : _focus("", FOCUS_SELIC),
    }

    # ── Derivados ────────────────────────────────────────────────────────────

    # IPCA acumulado 12 meses
    if not raw["ipca"].empty:
        df = raw["ipca"].copy()
        df["ipca_12m"] = (
            (1 + df["ipca_mensal"] / 100).rolling(12).apply(lambda x: x.prod(), raw=True) - 1
        ) * 100
        raw["ipca_12m"] = df[["ipca_12m"]].dropna()
    else:
        raw["ipca_12m"] = pd.DataFrame()

    # Taxa de juro real ex-post = Selic mensal − IPCA 12m
    if not raw["selic"].empty and not raw["ipca_12m"].empty:
        selic_m = raw["selic"]["selic"].resample("MS").last().rename("selic_m")
        df_real = pd.concat([selic_m, raw["ipca_12m"]["ipca_12m"]], axis=1).dropna()
        df_real["taxa_real"] = df_real["selic_m"] - df_real["ipca_12m"]
        raw["taxa_real"] = df_real
    else:
        raw["taxa_real"] = pd.DataFrame()

    # USD/BRL: volatilidade realizada 21 dias (anualizada)
    if not raw["usdbrl"].empty:
        vol = raw["usdbrl"].copy()
        vol["ret"] = vol["usdbrl"].pct_change()
        vol["vol"] = vol["ret"].rolling(21).std() * (252 ** 0.5) * 100
        raw["usdbrl_vol"] = vol.dropna(subset=["vol"])
    else:
        raw["usdbrl_vol"] = pd.DataFrame()

    # USD/BRL OHLC semanal para candlestick
    if not raw["usdbrl"].empty:
        ohlc = raw["usdbrl"]["usdbrl"].resample("W").ohlc()
        ohlc.columns = ["open", "high", "low", "close"]
        raw["usdbrl_ohlc"] = ohlc.dropna()
    else:
        raw["usdbrl_ohlc"] = pd.DataFrame()

    # Correlação entre principais indicadores (últimos 3 anos, freq. mensal)
    slices = {
        "IPCA 12m"     : ("ipca_12m",            "ipca_12m"),
        "Selic"        : ("selic",                "selic"),
        "USD/BRL"      : ("usdbrl",               "usdbrl"),
        "Res.Primário" : ("resultado_primario",   "resultado_primario"),
        "Inadimpl. PF" : ("inadimplencia",        "inadimplencia"),
        "Prod.Ind."    : ("producao_industrial",  "producao_industrial"),
        "Ativ. IBC-Br" : ("ibcbr",                "ibcbr"),
    }
    corr_frames = {}
    cutoff = datetime.today() - timedelta(days=365 * 3)
    for label, (key, col) in slices.items():
        df = raw.get(key, pd.DataFrame())
        if not df.empty and col in df.columns:
            s = df[col].resample("MS").last()
            s = s[s.index >= cutoff]
            corr_frames[label] = s
    if len(corr_frames) >= 2:
        raw["correlacao"] = pd.DataFrame(corr_frames)
    else:
        raw["correlacao"] = pd.DataFrame()

    return raw


def last_val(df: pd.DataFrame, col: str) -> Optional[float]:
    if df.empty or col not in df.columns:
        return None
    s = df[col].dropna()
    return float(s.iloc[-1]) if len(s) else None


def delta_val(df: pd.DataFrame, col: str, periods: int = 1) -> Optional[float]:
    if df.empty or col not in df.columns:
        return None
    s = df[col].dropna()
    if len(s) <= periods:
        return None
    return float(s.iloc[-1] - s.iloc[-(periods + 1)])
