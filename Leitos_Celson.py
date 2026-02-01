#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import streamlit as st

st.set_page_config(page_title="Análise de Higienização de Leitos", layout="wide")

st.title("📊 Análise de Higienização de Leitos - Terminal Dezembro")

uploaded_file = st.file_uploader("Carregue o arquivo Excel (.xls, .xlsx, .xlt)", type=["xls", "xlsx", "xlt"])

if uploaded_file is not None:
    # Mostrar abas disponíveis
    xls = pd.ExcelFile(uploaded_file, engine="openpyxl")
    st.write("Abas encontradas:", xls.sheet_names)

    # Ler a aba correta (ajuste se necessário)
    df = pd.read_excel(uploaded_file, engine="openpyxl", sheet_name=xls.sheet_names[0])

    # Mostrar colunas para conferência
    st.write("Colunas encontradas:", df.columns.tolist())

    # Conferir se existe a coluna FINALIZADO
    if "FINALIZADO" in df.columns:
        df["FINALIZADO"] = pd.to_datetime(df["FINALIZADO"], errors="coerce")
        df["Data"] = df["FINALIZADO"].dt.date

        # Quantidade por dia
        hig_por_dia = df.groupby("Data").size()
        percentual_por_dia = hig_por_dia / hig_por_dia.sum() * 100

        # Gráficos
        st.subheader("📈 Quantidade de higienizações por dia")
        st.line_chart(hig_por_dia)

        st.subheader("📉 Percentual de higienizações por dia")
        st.line_chart(percentual_por_dia)

    else:
        st.error("A coluna 'FINALIZADO' não foi encontrada. Verifique o nome exato no Excel.")
else:
    st.info("Por favor, carregue o arquivo 'TERMINAL DEZEMBRO' para iniciar a análise.")


# In[ ]:




