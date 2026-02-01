#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import streamlit as st

st.title("Análise de Gargalos por Andar - Modelo Dezembro")

uploaded_file = st.file_uploader("Carregue o arquivo Excel (.xls ou .xlt)", type=["xls", "xlsx", "xlt"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, parse_dates=["FINALIZADO"])
    df['Data'] = df['FINALIZADO'].dt.date

    # Definir limites de desvio
    q10 = df['TEMPO_TOTAL'].quantile(0.1)
    q90 = df['TEMPO_TOTAL'].quantile(0.9)

    # Classificação de conformidade
    df['Conformidade'] = df['TEMPO_TOTAL'].apply(
        lambda x: "Muito Rápido" if x < q10 else ("Muito Lento" if x > q90 else "Dentro do Padrão")
    )

    # Agrupar por andar (LUGAR)
    resumo = df.groupby('LUGAR')['Conformidade'].value_counts(normalize=True).unstack().fillna(0)

    # Identificar maior gargalo
    gargalo = resumo['Muito Lento'].idxmax()
    percentual_gargalo = resumo['Muito Lento'].max() * 100

    # Gráfico
    st.subheader("Distribuição de conformidade por andar")
    st.bar_chart(resumo)

    # Resultado
    st.success(f"O andar com maior gargalo é **{gargalo}**, com {percentual_gargalo:.2f}% dos casos classificados como 'Muito Lento'.")
else:
    st.info("Por favor, carregue o arquivo 'TERMINAL DEZEMBRO.xlt' para iniciar a análise.")


# In[ ]:




