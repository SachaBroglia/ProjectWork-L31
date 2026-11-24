from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Analisi delle localita in cui opera IstraOps

BASE_DIR = Path(__file__).resolve().parent.parent
FILE_DATI = BASE_DIR / "risultati" / "clienti_con_cluster.csv"


@st.cache_data
def carica_clienti():
    return pd.read_csv(FILE_DATI, encoding="utf-8-sig")


clienti = carica_clienti()

st.title("Analisi territoriale")
st.write(
    "Confronto dei comportamenti della clientela nelle "
    "cinque località istriane servite da IstraOps."
)

st.divider()

# Filtro per categoria di servizio

categorie = ["Tutte"] + sorted(clienti["categoria_preferita"].unique().tolist())

categoria = st.selectbox("Categoria di servizio", categorie)

dati = clienti.copy()

if categoria != "Tutte":
    dati = dati[dati["categoria_preferita"] == categoria]


# Analisi dei risultati economici

riepilogo = dati.groupby("zona", as_index=False).agg(
    clienti=("id_cliente", "count"),
    richieste=("richieste_ultimi_6_mesi", "sum"),
    fatturato=("spesa_totale_euro", "sum"),
)

riepilogo = riepilogo.sort_values("fatturato", ascending=False)

st.subheader("Fatturato per località")

fig_fatturato = px.bar(
    riepilogo,
    x="zona",
    y="fatturato",
    hover_data=["clienti", "richieste"],
    labels={"zona": "Località", "fatturato": "Fatturato simulato (€)"},
)

st.plotly_chart(fig_fatturato, width="stretch")


# Composizione della clientela

st.subheader("Distribuzione dei segmenti")

nomi_segmenti = {
    0: "Clienti operativi frequenti",
    1: "Clienti a spesa media elevata",
    2: "Clienti a bassa attività recente",
}

segmenti = dati.groupby(["zona", "cluster"]).size().reset_index(name="clienti")

segmenti["segmento"] = segmenti["cluster"].map(nomi_segmenti)

totali = segmenti.groupby("zona")["clienti"].transform("sum")

segmenti["percentuale"] = (segmenti["clienti"] / totali * 100).round(1)

fig_segmenti = px.bar(
    segmenti,
    x="zona",
    y="percentuale",
    color="segmento",
    barmode="stack",
    hover_data=["clienti"],
    labels={
        "zona": "Località",
        "percentuale": "Percentuale clienti (%)",
        "segmento": "Segmento",
    },
)

fig_segmenti.update_layout(yaxis_range=[0, 100])

st.plotly_chart(fig_segmenti, width="stretch")


# Riepilogo dei dati

st.subheader("Riepilogo per località")

st.dataframe(riepilogo, hide_index=True, width="stretch")

st.caption(
    "Elaborazione basata su dati sintetici. "
    "I risultati non rappresentano statistiche reali "
    "del mercato turistico istriano."
)
