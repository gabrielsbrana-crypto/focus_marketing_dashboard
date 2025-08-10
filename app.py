
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Focus Marketing Dashboard", page_icon="📊", layout="wide")

# Carregar dados
@st.cache_data
def load_data():
    return pd.read_csv("focus_marketing_data.csv", parse_dates=["inicio", "fim"])

df = load_data()

# Cores
FOCUS_LARANJA = "#FF6600"
FOCUS_PRETO = "#1A1A1A"

# Filtros
st.sidebar.header("Filtros")
servicos = st.sidebar.multiselect("Serviço", options=df["servico"].unique(), default=df["servico"].unique())
plataformas = st.sidebar.multiselect("Plataforma", options=df["plataforma"].unique(), default=df["plataforma"].unique())
campanhas = st.sidebar.multiselect("Campanha", options=df["campanha"].unique(), default=df["campanha"].unique())
data_inicio = st.sidebar.date_input("Data inicial", df["inicio"].min())
data_fim = st.sidebar.date_input("Data final", df["fim"].max())

df_filtrado = df[
    (df["servico"].isin(servicos)) &
    (df["plataforma"].isin(plataformas)) &
    (df["campanha"].isin(campanhas)) &
    (df["inicio"] >= pd.to_datetime(data_inicio)) &
    (df["fim"] <= pd.to_datetime(data_fim))
]

# KPIs
st.markdown(f"<h1 style='color:{FOCUS_LARANJA}'>📊 Dashboard - Focus Marketing</h1>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Investimento Total", f"R$ {df_filtrado['investimento'].sum():,.2f}")
col2.metric("Receita Total", f"R$ {df_filtrado['receita'].sum():,.2f}")
col3.metric("ROI Médio", f"{df_filtrado['roi'].mean():.2f}%")
col4.metric("Leads Totais", f"{df_filtrado['leads'].sum()}")

col5, col6, col7, col8 = st.columns(4)
col5.metric("Conversões Totais", f"{df_filtrado['conversoes'].sum()}")
col6.metric("CTR Médio", f"{df_filtrado['ctr'].mean():.2f}%")
col7.metric("CPL Médio", f"R$ {df_filtrado['cpl'].mean():.2f}")
col8.metric("CPA Médio", f"R$ {df_filtrado['cpa'].mean():.2f}")

# Gráficos
st.subheader("Investimento vs Receita")
fig1 = px.scatter(df_filtrado, x="investimento", y="receita", color="servico", size="roi", hover_data=["campanha"], template="plotly_dark")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("ROI por Serviço")
fig2 = px.bar(df_filtrado.groupby("servico")["roi"].mean().reset_index(), x="servico", y="roi", color="servico", template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("CPL por Plataforma")
fig3 = px.box(df_filtrado, x="plataforma", y="cpl", color="plataforma", template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Evolução de Investimento e Receita")
df_time = df_filtrado.groupby("inicio")[["investimento", "receita"]].sum().reset_index()
fig4 = px.line(df_time, x="inicio", y=["investimento", "receita"], template="plotly_dark")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Conversões por Campanha")
fig5 = px.bar(df_filtrado.groupby("campanha")["conversoes"].sum().reset_index(), x="campanha", y="conversoes", template="plotly_dark")
st.plotly_chart(fig5, use_container_width=True)

# Tabela
st.subheader("📋 Dados Filtrados")
st.dataframe(df_filtrado)

# Rodapé
st.markdown(f"<hr><center style='color:{FOCUS_LARANJA}'>Focus Marketing © 2025 - Todos os direitos reservados</center>", unsafe_allow_html=True)
