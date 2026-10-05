import os

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sabor do Sertão", layout="wide")
st.title("Painel de Vendas: Sabor do Sertão")

ARQUIVO_LOCAL = "vendas_sabor_do_sertao.csv"
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


@st.cache_data
def carregar(arquivo):
    return pd.read_csv(arquivo, parse_dates=["data"])


arquivo = st.sidebar.file_uploader("Envie o CSV de vendas", type=["csv"])
if arquivo is None and os.path.exists(ARQUIVO_LOCAL):
    arquivo = ARQUIVO_LOCAL
    st.sidebar.caption(f"Usando o arquivo local `{ARQUIVO_LOCAL}`.")
if arquivo is None:
    st.info("Envie o arquivo para começar.")
    st.stop()

df = carregar(arquivo)

# ---------------------------------------------------------------------------
# Nível 1: Exploração
# ---------------------------------------------------------------------------
with st.expander("Nível 1: Exploração dos dados", expanded=False):
    st.subheader("Primeiras linhas")
    st.dataframe(df.head(10), width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Resumo estatístico")
        st.dataframe(df.select_dtypes("number").describe(), width="stretch")
    with c2:
        st.subheader("Valores ausentes por coluna")
        st.dataframe(df.isna().sum().rename("ausentes"), width="stretch")

    # Tratamento dos ausentes em 'avaliacao': preenchemos com a mediana.
    st.caption(
        "Tratamento de 'avaliacao': os ausentes foram preenchidos com a mediana. "
        "A nota é uma escala ordinal de 1 a 5 (valores inteiros), então a mediana "
        "mantém uma nota real da escala e não é afetada por valores extremos. "
        "Remover as linhas descartaria vendas válidas e distorceria faturamento "
        "e número de vendas; a média criaria notas fracionadas que ninguém deu."
    )

df["avaliacao"] = df["avaliacao"].fillna(df["avaliacao"].median())

# ---------------------------------------------------------------------------
# Nível 3: Filtros (barra lateral)
# ---------------------------------------------------------------------------
st.sidebar.header("Filtros")
cidades = sorted(df["cidade"].unique())
categorias = sorted(df["categoria"].unique())

sel_cidades = st.sidebar.multiselect("Cidade", cidades, default=cidades)
sel_categorias = st.sidebar.multiselect("Categoria", categorias, default=categorias)

data_min, data_max = df["data"].min().date(), df["data"].max().date()
intervalo = st.sidebar.date_input(
    "Período", value=(data_min, data_max), min_value=data_min, max_value=data_max
)
if isinstance(intervalo, (tuple, list)) and len(intervalo) == 2:
    inicio, fim = intervalo
elif isinstance(intervalo, (tuple, list)) and len(intervalo) == 1:
    inicio = fim = intervalo[0]
else:
    inicio = fim = intervalo

dff = df[
    df["cidade"].isin(sel_cidades)
    & df["categoria"].isin(sel_categorias)
    & (df["data"].dt.date >= inicio)
    & (df["data"].dt.date <= fim)
].copy()

if dff.empty:
    st.warning("Nenhuma venda com os filtros selecionados. Ajuste os filtros.")
    st.stop()

# ---------------------------------------------------------------------------
# Nível 2: Indicadores
# ---------------------------------------------------------------------------
faturamento = dff["total"].sum()
n_vendas = len(dff)
ticket = faturamento / n_vendas
aval = dff["avaliacao"].mean()


def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


k1, k2, k3, k4 = st.columns(4)
k1.metric("Faturamento total", brl(faturamento))
k2.metric("Número de vendas", f"{n_vendas:,}".replace(",", "."))
k3.metric("Ticket médio", brl(ticket))
k4.metric("Avaliação média", f"{aval:.2f} / 5")

# ---------------------------------------------------------------------------
# Nível 4: Gráficos em abas (+ explorador livre)
# ---------------------------------------------------------------------------
dff["mes"] = dff["data"].dt.to_period("M")
dff["dia_semana"] = dff["data"].dt.dayofweek.map(dict(enumerate(DIAS)))

abas = st.tabs([
    "Faturamento mensal",
    "Por cidade",
    "Top 5 produtos",
    "Pagamento",
    "Mapa de calor",
    "Explorador livre",
])

with abas[0]:
    mensal = dff.groupby("mes")["total"].sum().reset_index()
    mensal["mes"] = mensal["mes"].astype(str)
    fig = px.line(
        mensal, x="mes", y="total", markers=True,
        title="Faturamento mensal",
        labels={"mes": "Mês", "total": "Faturamento (R$)"},
    )
    st.plotly_chart(fig, width="stretch")

with abas[1]:
    por_cidade = (
        dff.groupby("cidade")["total"].sum().sort_values(ascending=False).reset_index()
    )
    fig = px.bar(
        por_cidade, x="cidade", y="total", text_auto=".2s",
        title="Faturamento por cidade",
        labels={"cidade": "Cidade", "total": "Faturamento (R$)"},
    )
    st.plotly_chart(fig, width="stretch")

with abas[2]:
    top5 = (
        dff.groupby("produto")["quantidade"].sum().nlargest(5)
        .sort_values().reset_index()
    )
    fig = px.bar(
        top5, x="quantidade", y="produto", orientation="h", text="quantidade",
        title="Top 5 produtos mais vendidos (quantidade)",
        labels={"quantidade": "Unidades vendidas", "produto": "Produto"},
    )
    st.plotly_chart(fig, width="stretch")

with abas[3]:
    pag = dff.groupby("pagamento")["total"].sum().reset_index()
    fig = px.pie(
        pag, names="pagamento", values="total", hole=0.4,
        title="Participação de cada forma de pagamento no faturamento",
    )
    st.plotly_chart(fig, width="stretch")

with abas[4]:
    fig = px.density_heatmap(
        dff, x="hora", y="dia_semana", z="total", histfunc="sum",
        category_orders={"dia_semana": DIAS},
        title="Faturamento por dia da semana e hora",
        labels={"hora": "Hora do dia", "dia_semana": "Dia da semana",
                "total": "Faturamento (R$)"},
        nbinsx=15,
    )
    st.plotly_chart(fig, width="stretch")

# Desafio bônus: explorador livre
with abas[5]:
    st.write("Envie qualquer CSV (ou use os dados filtrados do painel) e monte seu gráfico.")
    up = st.file_uploader("CSV para explorar", type=["csv"], key="explorador")
    base = pd.read_csv(up) if up is not None else dff.drop(columns=["mes"]).copy()

    colunas = list(base.columns)
    numericas = list(base.select_dtypes("number").columns)
    c1, c2, c3 = st.columns(3)
    x = c1.selectbox("Eixo X", colunas, key="x")
    y = c2.selectbox("Eixo Y", numericas or colunas, key="y")
    tipo = c3.selectbox(
        "Tipo de gráfico", ["Barras", "Linha", "Dispersão", "Histograma", "Boxplot"],
        key="tipo",
    )

    if tipo == "Barras":
        dados = base.groupby(x, as_index=False)[y].sum() if y in numericas else base
        fig = px.bar(dados, x=x, y=y, title=f"{y} por {x} (soma)")
    elif tipo == "Linha":
        dados = base.groupby(x, as_index=False)[y].sum().sort_values(x) if y in numericas else base
        fig = px.line(dados, x=x, y=y, title=f"{y} por {x} (soma)")
    elif tipo == "Dispersão":
        fig = px.scatter(base, x=x, y=y, title=f"{y} vs {x}")
    elif tipo == "Histograma":
        fig = px.histogram(base, x=x, title=f"Distribuição de {x}")
    else:
        fig = px.box(base, x=x, y=y, title=f"{y} por {x}")
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------------------
# Nível 5: Insights e exportação (calculados a partir dos dados filtrados)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Insights para a gestão")

melhor_cidade = dff.groupby("cidade")["total"].sum().idxmax()
part_cidade = dff.groupby("cidade")["total"].sum().max() / faturamento
pico = dff.groupby("hora")["total"].sum().idxmax()
produto_top = dff.groupby("produto")["quantidade"].sum().idxmax()
categoria_top = dff.groupby("categoria")["total"].sum().idxmax()
pag_top = dff.groupby("pagamento")["total"].sum().idxmax()
part_pag = dff.groupby("pagamento")["total"].sum().max() / faturamento
mes_top = dff.groupby("mes")["total"].sum().idxmax()

st.markdown(
    f"""
1. **Onde vendemos mais:** {melhor_cidade} concentra {part_cidade:.0%} do faturamento
   no recorte atual, e o melhor mês foi {mes_top}.
2. **O que vendemos mais:** o produto mais vendido em unidades é **{produto_top}**,
   mas a categoria que mais fatura é **{categoria_top}** (pratos têm preço alto,
   então pesam mais no faturamento do que nas unidades).
3. **Quando e como:** o horário de pico é às **{pico}h** e **{pag_top}** é a forma de
   pagamento dominante, com {part_pag:.0%} do faturamento. Vale reforçar a equipe
   nesse horário e priorizar a estabilidade dos pagamentos por esse meio.
"""
)

csv_filtrado = dff.drop(columns=["mes", "dia_semana"]).to_csv(index=False).encode("utf-8")
st.download_button(
    "Baixar CSV filtrado",
    data=csv_filtrado,
    file_name="vendas_filtradas.csv",
    mime="text/csv",
)




