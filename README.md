# 📊 Macro Brasil PRO

Dashboard macroeconômico de segunda geração — tema escuro profissional, análises exclusivas e visualizações de nível institucional.

Stack: **Python · Plotly Dash · BCB SGS API · Relatório Focus**

---

## Diferenciais vs v1

| Recurso | v1 (Streamlit) | v2 PRO (Dash) |
|---|---|---|
| Tema | Light | Dark profissional |
| Câmbio | Linha simples | Candlestick semanal + volatilidade |
| KPI cards | Métricas simples | Sparklines integrados |
| Análise de juros | Selic histórica | **Taxa Real ex-post + zona neutra** |
| Correlação | Não | **Heatmap entre 6 indicadores** |
| Ancoragem Focus | Não | **Evolução das expectativas por ano** |
| Navegação | Sidebar radio | Header tabs (SPA) |
| Gauge IPCA | Não | ✅ com zonas meta/teto/perigo |

---

## Análises exclusivas

### 1. Taxa de Juro Real Ex-Post
`Taxa Real = Selic Meta − IPCA acumulado 12m`

Compara com a taxa neutra estimada do Brasil (r* ~4–5% a.a.) para classificar o ciclo monetário como contracionista ou expansionista.

### 2. Correlação entre Indicadores Macro
Heatmap com correlação de Pearson (últimos 3 anos, dados mensais) entre IPCA 12m, Selic, USD/BRL, Resultado Primário, Inadimplência PF e Produção Industrial.

### 3. Ancoragem das Expectativas Focus
Mostra como o mercado foi revisando suas projeções de IPCA para cada ano-calendário ao longo dos últimos 12 meses. Proxy direto da credibilidade do Banco Central.

---

## Como rodar

```bash
git clone https://github.com/valvitorsantos/macro-brasil-pro.git
cd macro-brasil-pro

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Acesse em `http://localhost:8502`

---

## Deploy

**Render (recomendado):**
- Build command: `pip install -r requirements.txt`
- Start command: `python app.py`
- Environment: Python 3.11

---

## Fontes

| Dado | Série BCB |
|---|---|
| IPCA | SGS 433 |
| INPC | SGS 188 |
| IGP-M | SGS 189 |
| Selic Meta | SGS 432 |
| USD/BRL | SGS 10813 |
| Resultado Primário | SGS 5793 |
| Dívida Bruta | SGS 4537 |
| Dívida Líquida | SGS 4513 |
| Inadimplência PF | SGS 21082 |
| Concessões de Crédito | SGS 20631 |
| Crédito/PIB | SGS 20626 |
| Produção Industrial | SGS 21859 |
| Expectativas Focus | BCB Olinda API |

---

**Valvitor Santos** · Consultoria de Dados para Gestoras  
valvitorscf@gmail.com
