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

    # Debug: mostrar como o pandas está lendo TEMPO_TOTAL
    st.write("Primeiros valores de TEMPO_TOTAL:", df["TEMPO_TOTAL"].head())
    st.write("Tipo de dados da coluna TEMPO_TOTAL:", df["TEMPO_TOTAL"].dtype)

    # Converter FINALIZADO para datetime
    df["FINALIZADO"] = pd.to_datetime(df["FINALIZADO"], errors="coerce")
    df["DATA"] = df["FINALIZADO"].dt.date

    # Conversão robusta de TEMPO_TOTAL para segundos
    def converter_tempo(x):
        try:
            if isinstance(x, pd.Timedelta):
                return x.total_seconds()
            elif isinstance(x, str):
                partes = x.split(":")
                if len(partes) == 3:
                    h, m, s = map(int, partes)
                    return h*3600 + m*60 + s
            elif isinstance(x, (int, float)):
                return float(x) * 24 * 3600  # fração de dia
        except:
            return None
        return None

    df["TEMPO_SEGUNDOS"] = df["TEMPO_TOTAL"].apply(converter_tempo)

    # Função para formatar em hh:mm:ss
    def segundos_para_hhmmss(segundos):
        if pd.isna(segundos):
            return "-"
        h = int(segundos // 3600)
        m = int((segundos % 3600) // 60)
        s = int(segundos % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

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
    total_segundos = df_filtrado["TEMPO_SEGUNDOS"].sum()
    media_segundos = df_filtrado["TEMPO_SEGUNDOS"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Ocorrências finalizadas", qtd_ocorrencias)
    col2.metric("Tempo total no período", segundos_para_hhmmss(total_segundos))
    col3.metric("Média por ocorrência", segundos_para_hhmmss(media_segundos))
else:
    st.info("Por favor, carregue o arquivo 'TERMINAL DEZEMBRO' para iniciar a análise.")


# In[ ]:




