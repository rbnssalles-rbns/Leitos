#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import streamlit as st

st.set_page_config(page_title="Análise de Higienização de Leitos", layout="wide")

st.title("📊 Análise de Higienização de Leitos - Terminal Dezembro")

uploaded_file = st.file_uploader("Carregue o arquivo Excel (.xls, .xlsx, .xlt)", type=["xls", "xlsx", "xlt"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    # Padronizar nomes de colunas
    df.columns = df.columns.str.strip().str.upper()

    # Conferir colunas obrigatórias
    if "FINALIZADO" not in df.columns or "TEMPO_TOTAL" not in df.columns or "LUGAR" not in df.columns:
        st.error("As colunas 'FINALIZADO', 'TEMPO_TOTAL' e 'LUGAR' não foram encontradas.")
        st.write("Colunas disponíveis:", df.columns.tolist())
        st.stop()

    # Converter FINALIZADO para datetime
    df["FINALIZADO"] = pd.to_datetime(df["FINALIZADO"], errors="coerce")
    df["DATA"] = df["FINALIZADO"].dt.date

    # Converter TEMPO_TOTAL para minutos numéricos
    def converter_tempo(x):
        try:
            if isinstance(x, pd.Timedelta):
                return x.total_seconds() / 60
            elif isinstance(x, str):
                partes = x.split(":")
                if len(partes) == 3:
                    h, m, s = map(int, partes)
                    return h*60 + m + s/60
            elif isinstance(x, (int, float)):
                return x * 24 * 60
        except:
            return None
        return None

    df["TEMPO_MINUTOS"] = df["TEMPO_TOTAL"].apply(converter_tempo)

    # --- Filtros ---
    col1, col2 = st.columns(2)
    with col1:
        datas = sorted(df["DATA"].dropna().unique())
        data_inicio = st.date_input("Data inicial", min(datas))
        data_fim = st.date_input("Data final", max(datas))
    with col2:
        lugares = df["LUGAR"].dropna().unique().tolist()
        lugares.insert(0, "Todos")
        lugar_selecionado = st.selectbox("Selecione o LUGAR", options=lugares)

    # Aplicar filtros
    df_filtrado = df[(df["DATA"] >= data_inicio) & (df["DATA"] <= data_fim)]
    if lugar_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["LUGAR"] == lugar_selecionado]

    # --- Métricas principais ---
    qtd_ocorrencias = len(df_filtrado)
    total_horas = df_filtrado["TEMPO_MINUTOS"].sum() / 60
    media_por_ocorrencia = df_filtrado["TEMPO_MINUTOS"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Ocorrências finalizadas", qtd_ocorrencias)
    col2.metric("Total de horas no período", f"{total_horas:.2f} h")
    col3.metric("Média por ocorrência", f"{media_por_ocorrencia:.2f} min")

    # --- Quantidade e Percentual por dia ---
    hig_por_dia = df_filtrado.groupby("DATA").size()
    percentual_por_dia = hig_por_dia / hig_por_dia.sum() * 100

    st.subheader("📈 Quantidade de higienizações por dia")
    st.line_chart(hig_por_dia)

    st.subheader("📉 Percentual de higienizações por dia")
    st.line_chart(percentual_por_dia)

    # --- Gargalo por andar ---
    q10 = df["TEMPO_MINUTOS"].quantile(0.1)
    q90 = df["TEMPO_MINUTOS"].quantile(0.9)

    df["CONFORMIDADE"] = df["TEMPO_MINUTOS"].apply(
        lambda x: "Muito Rápido" if x < q10 else ("Muito Lento" if x > q90 else "Dentro do Padrão")
    )

    resumo = df.groupby("LUGAR")["CONFORMIDADE"].value_counts(normalize=True).unstack().fillna(0)

    st.subheader("📊 Distribuição de conformidade por andar")
    st.bar_chart(resumo)

    gargalo = resumo["Muito Lento"].idxmax()
    percentual_gargalo = resumo["Muito Lento"].max() * 100

    st.success(f"O andar com maior gargalo é **{gargalo}**, com {percentual_gargalo:.2f}% dos casos classificados como 'Muito Lento'.")
else:
    st.info("Por favor, carregue o arquivo 'TERMINAL DEZEMBRO' para iniciar a análise.")


# In[ ]:




