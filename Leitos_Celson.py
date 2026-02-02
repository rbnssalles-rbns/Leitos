#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import streamlit as st

st.set_page_config(page_title="Análise de Higienização de Leitos", layout="wide")

st.title("📊 Análise de Higienização de Leitos - Processo de Conformidades")

uploaded_file = st.file_uploader("Carregue o arquivo Excel (.xls, .xlsx, .xlt)", type=["xls", "xlsx", "xlt"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    # Padronizar nomes de colunas
    df.columns = df.columns.str.strip().str.upper()

    # Conferir colunas obrigatórias
    obrigatorias = ["FINALIZADO", "TEMPO_TOTAL", "LUGAR",
                    "AGUARDANDO_LIMPEZA_51", "EM_LIMPEZA_53", "CAMAREIRA_54"]
    for col in obrigatorias:
        if col not in df.columns:
            st.error(f"A coluna obrigatória '{col}' não foi encontrada.")
            st.write("Colunas disponíveis:", df.columns.tolist())
            st.stop()

    # Converter FINALIZADO para datetime
    df["FINALIZADO"] = pd.to_datetime(df["FINALIZADO"], errors="coerce")
    df["DATA"] = df["FINALIZADO"].dt.date

    # Conversão robusta de tempos para segundos
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
                return float(x) * 24 * 3600
        except:
            return None
        return None

    # Converter colunas para segundos
    df["TEMPO_TOTAL"] = df["TEMPO_TOTAL"].astype(str)
    df["TEMPO_SEGUNDOS"] = df["TEMPO_TOTAL"].apply(converter_tempo)
    df["AGUARDANDO_SEGUNDOS"] = df["AGUARDANDO_LIMPEZA_51"].astype(str).apply(converter_tempo)
    df["LIMPEZA_SEGUNDOS"] = df["EM_LIMPEZA_53"].astype(str).apply(converter_tempo)
    df["CAMAREIRA_SEGUNDOS"] = df["CAMAREIRA_54"].astype(str).apply(converter_tempo)

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

    # --- Quantidade e Percentual por dia ---
    hig_por_dia = df_filtrado.groupby("DATA").size()
    percentual_por_dia = hig_por_dia / hig_por_dia.sum() * 100

    st.subheader("📈 Quantidade de higienizações por dia")
    st.line_chart(hig_por_dia)

    st.subheader("📉 Percentual de higienizações por dia (%)")
    st.line_chart(percentual_por_dia.round(2))
    st.dataframe(percentual_por_dia.round(2).astype(str) + "%")

    # --- Classificação por percentis ---
    q10 = df["TEMPO_SEGUNDOS"].quantile(0.1)
    q90 = df["TEMPO_SEGUNDOS"].quantile(0.9)

    df["CONFORMIDADE"] = df["TEMPO_SEGUNDOS"].apply(
        lambda x: "Muito Rápido" if x < q10 else ("Muito Lento" if x > q90 else "Dentro do Padrão")
    )

    # --- Distribuição por andar ---
    resumo_andar = df.groupby("LUGAR")["CONFORMIDADE"].value_counts(normalize=True).unstack().fillna(0) * 100
    st.subheader("📊 Distribuição de conformidade por andar (%)")
    st.bar_chart(resumo_andar.round(2))
    st.dataframe(resumo_andar.round(2).astype(str) + "%")

    if "Muito Lento" in resumo_andar.columns:
        gargalo_lento = resumo_andar["Muito Lento"].idxmax()
        perc_lento = resumo_andar["Muito Lento"].max()
        st.warning(f"⚠️ Andar com maior lentidão: **{gargalo_lento}** ({perc_lento:.2f}%)")
    if "Muito Rápido" in resumo_andar.columns:
        gargalo_rapido = resumo_andar["Muito Rápido"].idxmax()
        perc_rapido = resumo_andar["Muito Rápido"].max()
        st.warning(f"⚠️ Andar com maior rapidez excessiva: **{gargalo_rapido}** ({perc_rapido:.2f}%)")

    # --- Distribuição por dia ---
    resumo_dia = df.groupby("DATA")["CONFORMIDADE"].value_counts(normalize=True).unstack().fillna(0) * 100
    st.subheader("📊 Distribuição de conformidade por dia (%)")
    st.bar_chart(resumo_dia.round(2))
    st.dataframe(resumo_dia.round(2).astype(str) + "%")

    if "Muito Lento" in resumo_dia.columns:
        dia_lento = resumo_dia["Muito Lento"].idxmax()
        perc_lento_dia = resumo_dia["Muito Lento"].max()
        st.warning(f"⚠️ Dia com maior lentidão: **{dia_lento}** ({perc_lento_dia:.2f}%)")
    if "Muito Rápido" in resumo_dia.columns:
        dia_rapido = resumo_dia["Muito Rápido"].idxmax()
        perc_rapido_dia = resumo_dia["Muito Rápido"].max()
        st.warning(f"⚠️ Dia com maior rapidez excessiva: **{dia_rapido}** ({perc_rapido_dia:.2f}%)")

    # --- Tempo médio por status ---
    medias_status = df.groupby("CONFORMIDADE")["TEMPO_SEGUNDOS"].mean()
    medias_formatadas = {status: segundos_para_hhmmss(valor) for status, valor in medias_status.items()}

    st.subheader("⏱️ Tempo médio por classificação")
    for status, tempo in medias_formatadas.items():
        st.write(f"**{status}** → {tempo}")

    # --- Distribuição por faixas de tempo ---
    bins = [0, 600, 900, 1200, 1800, 2700, 3600, float("inf")]
    labels = [
        "EM ATÉ 10 MINUTOS",
        "EM ATÉ 15 MINUTOS",
        "EM ATÉ 20 MINUTOS",
        "EM ATÉ 30 MINUTOS",
        "EM ATÉ 45 MINUTOS",
        "EM ATÉ 1 HORA",
        "MAIS DE 1 HORA"
    ]

    def analisar_coluna(df_base, coluna_segundos, titulo):
        if coluna_segundos not in df_base.columns:
            st.warning(f"Coluna {coluna_segundos} não encontrada nos dados filtrados.")
            return

        df_base[f"FAIXA_{titulo}"] = pd.cut(df_base[coluna_segundos], bins=bins, labels=labels, right=True)
        resumo = df_base[f"FAIXA_{titulo}"].value_counts().sort_index()
        percentuais = (resumo / resumo.sum()) * 100

        st.subheader(f"📊 Distribuição - {titulo.replace('_SEGUNDOS','').replace('_',' ')}")
        for faixa in labels:
            qtd = resumo.get(faixa, 0)
            perc = percentuais.get(faixa, 0)
            st.write(f"**{faixa}** → {qtd} ({perc:.2f}%)")

    # --- Chamadas para cada coluna ---
    analisar_coluna(df_filtrado, "TEMPO_SEGUNDOS", "TEMPO_TOTAL")
    analisar_coluna(df_filtrado, "AGUARDANDO_SEGUNDOS", "AGUARDANDO_LIMPEZA_51")
    analisar_coluna(df_filtrado, "LIMPEZA_SEGUNDOS", "EM_LIMPEZA_53")
    analisar_coluna(df_filtrado, "CAMAREIRA_SEGUNDOS", "CAMAREIRA_54")

else:
    st.info("Por favor, carregue o arquivo 'TERMINAL DEZEMBRO' para iniciar a análise.")


# In[ ]:




