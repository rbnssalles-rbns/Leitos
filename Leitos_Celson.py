#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import streamlit as st

st.set_page_config(page_title="Análise de Higienização de Leitos", layout="wide")

st.title("📊 Análise de Higienização de Leitos - Terminal Dezembro")

# Upload do arquivo Excel
uploaded_file = st.file_uploader("Carregue o arquivo Excel (.xls, .xlsx, .xlt)", type=["xls", "xlsx", "xlt"])

if uploaded_file is not None:
    # Carregar dados
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    # Garantir que a coluna FINALIZADO seja datetime
    if "FINALIZADO" in df.columns:
        df["FINALIZADO"] = pd.to_datetime(df["FINALIZADO"], errors="coerce")
        df["Data"] = df["FINALIZADO"].dt.date
    else:
        st.error("A coluna 'FINALIZADO' não foi encontrada no arquivo.")
        st.stop()

    # --- Filtros ---
    col1, col2 = st.columns(2)
    with col1:
        datas = sorted(df["Data"].dropna().unique())
        data_inicio = st.date_input("Data inicial", min(datas))
        data_fim = st.date_input("Data final", max(datas))
    with col2:
        lugares = df["LUGAR"].dropna().unique()
        lugar_selecionado = st.selectbox("Selecione o LUGAR", options=lugares)

    # Aplicar filtros
    df_filtrado = df[(df["Data"] >= data_inicio) &
                     (df["Data"] <= data_fim) &
                     (df["LUGAR"] == lugar_selecionado)]

    # --- Análises ---
    hig_por_dia = df_filtrado.groupby("Data").size()
    percentual_por_dia = hig_por_dia / hig_por_dia.sum() * 100

    # Cálculo de desvios (gargalo)
    q10 = df_filtrado["TEMPO_T"].quantile(0.1)
    q90 = df_filtrado["TEMPO_T"].quantile(0.9)

    df_filtrado["Conformidade"] = df_filtrado["TEMPO_T"].apply(
        lambda x: "Muito Rápido" if x < q10 else ("Muito Lento" if x > q90 else "Dentro do Padrão")
    )

    resumo = df_filtrado.groupby("LUGAR")["Conformidade"].value_counts(normalize=True).unstack().fillna(0)
    gargalo = resumo["Muito Lento"].idxmax()
    percentual_gargalo = resumo["Muito Lento"].max() * 100

    # --- Dashboard ---
    st.subheader("📈 Quantidade de higienizações por dia")
    st.line_chart(hig_por_dia)

    st.subheader("📉 Percentual de higienizações por dia")
    st.line_chart(percentual_por_dia)

    st.subheader("📊 Distribuição de conformidade por andar")
    st.bar_chart(resumo)

    # Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Média diária (quantidade)", f"{hig_por_dia.mean():.2f}")
    col2.metric("Tempo médio total (min)", f"{df_filtrado['TEMPO_T'].mean() * 24 * 60:.2f}")
    col3.metric("Andar com maior gargalo", f"{gargalo} ({percentual_gargalo:.2f}%)")

else:
    st.info("Por favor, carregue o arquivo 'TERMINAL DEZEMBRO' para iniciar a análise.")


# In[ ]:




