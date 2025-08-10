
import io
import pandas as pd
import plotly.express as px
import streamlit as st

# ============ CONFIGURAÇÃO BÁSICA ============
st.set_page_config(
    page_title="Dashboard – UNIFOR | Prof. Alex",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tema (também configurado em .streamlit/config.toml)
PRIMARY_COLOR = "#FF6B00"

# ============ HEADER ============
st.markdown(
    f"""
    <div style="padding:16px 0;border-bottom:1px solid #262730;">
        <h1 style="margin:0;font-size:28px;">📊 Dashboard Interativo – Disciplina Dashboards com Python/R (UNIFOR)</h1>
        <p style="margin:4px 0 0 0;opacity:0.9;">
            Professor: Ms. Alex Lima • Projeto publicado com Streamlit • Feito com Plotly
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============ SIDEBAR ============
st.sidebar.header("⚙️ Configurações")

with st.sidebar.expander("Sobre este projeto", expanded=True):
    st.write(
        "- **Objetivo**: apresentar um dashboard interativo com pelo menos 3 gráficos, "
        "organizados em um layout e prontos para publicação."
    )
    st.write(
        "- **Como usar**: você pode usar o dataset `tips` (amostra do Plotly) "
        "ou enviar um CSV próprio (colunas livres)."
    )

dataset_source = st.sidebar.radio(
    "Escolha a fonte dos dados:",
    options=["Dataset de exemplo (tips)", "Enviar CSV"],
    index=0,
)

# ============ CARGA DE DADOS ============
@st.cache_data(show_spinner=False)
def load_tips():
    # Usa o dataset embutido do Plotly (não requer internet)
    df = px.data.tips()
    # Normaliza nomes de colunas para português amigável (mantendo originais)
    df = df.rename(columns={
        "total_bill": "total_bill",
        "tip": "tip",
        "sex": "sex",
        "smoker": "smoker",
        "day": "day",
        "time": "time",
        "size": "size",
    })
    return df

@st.cache_data(show_spinner=True)
def load_csv(file: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(file))

if dataset_source == "Dataset de exemplo (tips)":
    df = load_tips()
    origin = "tips"
else:
    uploaded = st.sidebar.file_uploader("Envie um arquivo CSV", type=["csv"])
    if uploaded is not None:
        try:
            df = load_csv(uploaded.getvalue())
            origin = "upload"
        except Exception as e:
            st.sidebar.error(f"Erro ao ler CSV: {e}")
            df = None
    else:
        df = None
        origin = "upload"

if df is None:
    st.info("⬅️ Envie um CSV na barra lateral para continuar.")
    st.stop()

# ============ PAINEL DE KPIs ============
st.subheader("📌 Visão geral")

# Tenta calcular indicadores dependendo das colunas disponíveis
def metric_format(value):
    try:
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(value)

total_registros = len(df)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Registros", f"{total_registros:,}".replace(",", "."))

# total_bill/tip podem não existir em CSVs customizados
if {"total_bill", "tip"}.issubset(df.columns):
    total_faturado = df["total_bill"].sum()
    media_gorjeta = df["tip"].mean()
    pct_tip = (df["tip"].sum() / df["total_bill"].sum()) * 100 if df["total_bill"].sum() else 0
    with col2:
        st.metric("Faturamento (Σ total_bill)", "R$ " + metric_format(total_faturado))
    with col3:
        st.metric("Média de Gorjeta", "R$ " + metric_format(media_gorjeta))
    with col4:
        st.metric("Tip % (Σ tip / Σ total_bill)", metric_format(pct_tip) + "%")
else:
    # KPIs genéricos para CSVs sem colunas padrão
    num_cols = df.select_dtypes("number").columns.tolist()
    with col2:
        st.metric("Colunas numéricas", f"{len(num_cols)}")
    with col3:
        st.metric("Colunas", f"{len(df.columns)}")
    with col4:
        st.metric("Valores ausentes", f"{int(df.isna().sum().sum()):,}".replace(",", "."))

# ============ FILTROS DINÂMICOS (apenas se colunas existirem) ============
st.subheader("🎚️ Filtros")
filters_cols = st.columns(4)

# Filtro por dia (tips)
if "day" in df.columns:
    days = sorted(df["day"].dropna().unique().tolist())
    with filters_cols[0]:
        sel_days = st.multiselect("Dia", options=days, default=days)
else:
    sel_days = None

# Filtro por time (Lunch/Dinner)
if "time" in df.columns:
    times = sorted(df["time"].dropna().unique().tolist())
    with filters_cols[1]:
        sel_time = st.multiselect("Período", options=times, default=times)
else:
    sel_time = None

# Filtro por sexo
if "sex" in df.columns:
    sexes = sorted(df["sex"].dropna().unique().tolist())
    with filters_cols[2]:
        sel_sex = st.multiselect("Sexo", options=sexes, default=sexes)
else:
    sel_sex = None

# Filtro por faixa de total_bill
if "total_bill" in df.columns:
    min_b, max_b = float(df["total_bill"].min()), float(df["total_bill"].max())
    with filters_cols[3]:
        bill_range = st.slider("Faixa de total_bill", min_b, max_b, (min_b, max_b))
else:
    bill_range = None

# Aplicação dos filtros
df_f = df.copy()
if sel_days is not None:
    df_f = df_f[df_f["day"].isin(sel_days)]
if sel_time is not None:
    df_f = df_f[df_f["time"].isin(sel_time)]
if sel_sex is not None:
    df_f = df_f[df_f["sex"].isin(sel_sex)]
if bill_range is not None:
    df_f = df_f[(df_f["total_bill"] >= bill_range[0]) & (df_f["total_bill"] <= bill_range[1])]

# ============ VISUALIZAÇÕES ============
st.subheader("📈 Visualizações")

# 1) Dispersão total_bill vs tip (se houver colunas)
if {"total_bill", "tip"}.issubset(df_f.columns):
    fig_scatter = px.scatter(
        df_f,
        x="total_bill",
        y="tip",
        color="sex" if "sex" in df_f.columns else None,
        size="size" if "size" in df_f.columns else None,
        hover_data=df_f.columns,
        title="Relação entre Conta Total (total_bill) e Gorjeta (tip)",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("Para o gráfico de dispersão, são necessárias as colunas 'total_bill' e 'tip'.")

# Layout de 2 colunas para gráficos adicionais
gcol1, gcol2 = st.columns(2)

# 2) Histograma total_bill
with gcol1:
    if "total_bill" in df_f.columns:
        fig_hist = px.histogram(
            df_f, x="total_bill",
            nbins=20,
            color="sex" if "sex" in df_f.columns else None,
            barmode="overlay",
            title="Distribuição de Total Bill"
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("Para o histograma, é necessária a coluna 'total_bill'.")

# 3) Boxplot de tip por dia
with gcol2:
    if {"tip", "day"}.issubset(df_f.columns):
        fig_box = px.box(
            df_f, x="day", y="tip",
            color="day",
            title="Distribuição de Gorjetas por Dia da Semana"
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("Para o boxplot, são necessárias as colunas 'tip' e 'day'.")

# 4) Barras agrupadas: total_bill por dia e sexo
if {"total_bill", "day"}.issubset(df_f.columns):
    fig_bar = px.bar(
        df_f, x="day", y="total_bill",
        color="sex" if "sex" in df_f.columns else None,
        barmode="group",
        title="Total de Contas por Dia e Sexo (quando disponível)",
        labels={"total_bill": "Total da Conta"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("Para o gráfico de barras, é necessária a coluna 'total_bill' e 'day'.")

# 5) Heatmap opcional (correlação) para CSVs com colunas numéricas
num_cols = df_f.select_dtypes("number").columns.tolist()
if len(num_cols) >= 2:
    corr = df_f[num_cols].corr(numeric_only=True)
    fig_heat = px.imshow(corr, text_auto=True, title="Mapa de Calor – Correlação (colunas numéricas)")
    st.plotly_chart(fig_heat, use_container_width=True)

# ============ TABELA DE DADOS ============
st.subheader("🧾 Amostra de dados")
st.dataframe(df_f.head(50), use_container_width=True)

# ============ RODAPÉ ============
st.markdown(
    f"""
    <hr style="margin-top:24px;opacity:0.3">
    <div style="display:flex;justify-content:space-between;align-items:center;opacity:0.9;">
        <div>Feito com ❤️ em Streamlit & Plotly • Projeto para UNIFOR – Prof. Alex Lima</div>
        <div style="font-size:13px;">Pronto para deploy: <code>streamlit run app.py</code></div>
    </div>
    """, unsafe_allow_html=True
)
