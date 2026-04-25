# 📊 Macro Brasil PRO

## 🗂 Estrutura do Dashboard

O app conta com as seguintes visualizações dinâmicas:

*   **Visão Geral:** Cartões de métricas (KPIs corrediços) e *Sparklines* super responsivos do Dólar, Juro, e IPCA.
*   **Inflação:** Gráficos com funil de expectativas Focus ao longo do tempo + Monitor clássico de curva do IPCA/IGP-M e o clássico velocímetro do centro da meta.
*   **Juros:** Avaliação de todo aperto monetário via Curva Real versus Nominal.
*   **Câmbio:** *Candlestick* robusto de Forex (USD/BRL) mesclado num sub-gráfico de volatilidade absoluta.
*   **Atividade:** Crescimento do **IBC-Br** acompanhando tendência por Médias Móveis + subsetor de Produção IBGE.
*   **Fiscal & Crédito:** Monitor de endividamento da nação e as fatias de Concessões em Bilhões e %PIB contra inadimplência em duplo-eixo.
*   **Análises Principais:** Cérebro da Inteligência de cruzamento num Heatmap multivariável e Correlações.

---

## 💻 Como Rodar e Testar Localmente

Certifique-se de que tenha o **Python 3.9+** instalado.

```bash
# 1. Clone o repositório para o seu computador
git clone https://github.com/Valvitor/macro-brasil-pro.git
cd macro-brasil-pro

# 2. (Opcional) Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate # ou `.venv\Scripts\activate` no Windows

# 3. Instale as dependências requisitadas
pip install -r requirements.txt

# 4. Inicie o servidor em modo de desenvolvimento local
python app.py
```
> Acesse o Dashboard imediatamente pelo seu navegador em **`http://localhost:8502`**.

---

## 🚀 Publicação Pública (Deploy Nuvem)

> [!WARNING]
> **O GitHub Pages NÃO exibe dashboards de Python.** Ferramentas como o GitHub Pages foram feitas para *arquivos Estáticos* (HTML puro css sem backend). Por esse aplicativo requerer uma computação Python por baixo do capô para consultar OData/APIs, ele deve ser hospedado em um serviço em nuvem específico (PaaS) que rodará o Python 24 horas por dia!

Para publicar seu App diretamente atrelado ao código do seu GitHub de graça para que qualquer pessoa possar ver através de um Link (ex: `https://meu-brasil-macro.onrender.com`), recomendamos a **Render.com**.

### **Passo a Passo na Render:**

1. Suba/Aperte *Push* de todos os seus arquivos (incluindo o modificador `app.py` atualizado e o `requirements.txt`) para o seu GitHub.
2. Crie uma conta gratuita em [Render.com](https://render.com/).
3. Crie um novo **"Web Service"**. Conecte a sua conta do GitHub e selecione o repositório `macro-brasil-pro`.
4. Configure assim o serviço:
   *   **Environment:** `Python 3`
   *   **Build Command:** `pip install -r requirements.txt`
   *   **Start Command:** `gunicorn app:server --bind 0.0.0.0:$PORT`
   *   **Plan:** `Free`
5. Clique em **Deploy**! A Render criará o "servidor", instalará as bibliotecas e te fornecerá uma URL pública pra você acessar do celular ou do notebook de qualquer lugar do mundo!

---

**Valvitor Santos** · Consultoria de Dados
*valvitorscf@gmail.com*
