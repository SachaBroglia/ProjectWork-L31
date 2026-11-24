# IstraOps - Dashboard di analisi clienti
# Project Work L-31

from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import joblib


BASE_DIR = Path(__file__).resolve().parent.parent
FILE_CLIENTI = BASE_DIR / "risultati" / "clienti_con_cluster.csv"


st.set_page_config(
    page_title="IstraOps | Analisi clienti",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def carica_clienti():
    return pd.read_csv(FILE_CLIENTI, encoding="utf-8-sig")

@st.cache_resource
def carica_modello():
    percorso = BASE_DIR / "modello" / "modello_istraops.joblib"
    return joblib.load(percorso)

clienti = carica_clienti()

clienti["data_iscrizione"] = pd.to_datetime(
    clienti["data_iscrizione"],
    errors="coerce"
)


# Intestazione

st.title("IstraOps")
st.subheader("Analisi e segmentazione della clientela")

st.caption(
    "Piattaforma di servizi per strutture turistiche in Istria "
    "| Dati sintetici aggiornati al 31/10/2026"
)

st.divider()


# Filtri

st.sidebar.header("Filtri di analisi")

zona = st.sidebar.selectbox(
    "Località",
    ["Tutte"] + sorted(clienti["zona"].unique().tolist())
)

categoria = st.sidebar.selectbox(
    "Categoria di servizio",
    ["Tutte"] + sorted(
        clienti["categoria_preferita"].unique().tolist()
    )
)

# Intervallo delle date di iscrizione
prima_iscrizione = clienti["data_iscrizione"].min().date()
ultima_iscrizione = clienti["data_iscrizione"].max().date()

periodo = st.sidebar.date_input(
    "Periodo di iscrizione",
    value=(prima_iscrizione, ultima_iscrizione),
    min_value=prima_iscrizione,
    max_value=pd.Timestamp("2026-10-31").date(),
    format="DD/MM/YYYY"
)

st.sidebar.caption(
    "Il periodo si riferisce all'iscrizione dei clienti."
)

dati_filtrati = clienti.copy()

if zona != "Tutte":
    dati_filtrati = dati_filtrati[
        dati_filtrati["zona"] == zona
    ]

if categoria != "Tutte":
    dati_filtrati = dati_filtrati[
        dati_filtrati["categoria_preferita"] == categoria
    ]

# Mantengo solo i clienti iscritti nell'intervallo selezionato

if len(periodo) == 2:
    data_inizio, data_fine = periodo

    dati_filtrati = dati_filtrati[
        dati_filtrati["data_iscrizione"].between(
            pd.Timestamp(data_inizio),
            pd.Timestamp(data_fine)
        )
    ]


# Indicatori aziendali

numero_clienti = len(dati_filtrati)

numero_richieste = dati_filtrati[
    "richieste_ultimi_6_mesi"
].sum()

fatturato = dati_filtrati[
    "spesa_totale_euro"
].sum()

segmenti = dati_filtrati["cluster"].nunique()


col1, col2, col3, col4 = st.columns(4)

col1.metric("Clienti", numero_clienti)

col2.metric(
    "Richieste",
    f"{int(numero_richieste):,}".replace(",", ".")
)

fatturato_formattato = (
    f"{fatturato:,.2f}"
    .replace(",", "X")
    .replace(".", ",")
    .replace("X", ".")
)

col3.metric("Fatturato", f"{fatturato_formattato} €")


col4.metric("Segmenti presenti", segmenti)


# Distribuzione dei gruppi

st.divider()

st.subheader("Distribuzione della clientela")

st.write(
    "Numero di clienti appartenenti ai segmenti "
    "individuati attraverso K-Means."
)

distribuzione = (
    dati_filtrati.groupby("cluster")
    .size()
    .rename("Clienti")
)

st.bar_chart(distribuzione)



# Analisi visiva dei segmenti

st.divider()
st.subheader("Analisi dei segmenti")

st.write(
    "Confronto tra frequenza delle richieste e spesa media "
    "dei clienti della piattaforma."
)

# Nomi assegnati ai cluster in base ai risultati dell'analisi
nomi_segmenti = {
    0: "Clienti operativi frequenti",
    1: "Clienti a spesa media elevata",
    2: "Clienti a bassa attività recente"
}

dati_grafico = dati_filtrati.copy()

dati_grafico["segmento"] = (
    dati_grafico["cluster"].map(nomi_segmenti)
)

# Ogni punto rappresenta un cliente
grafico = px.scatter(
    dati_grafico,
    x="richieste_ultimi_6_mesi",
    y="spesa_media_euro",
    color="segmento",
    hover_name="id_cliente",
    hover_data=[
        "zona",
        "categoria_preferita",
        "giorni_ultima_richiesta"
    ],
    labels={
        "richieste_ultimi_6_mesi": "Richieste negli ultimi 6 mesi",
        "spesa_media_euro": "Spesa media (€)",
        "segmento": "Segmento"
    },
    opacity=0.7
)

grafico.update_layout(
    height=500,
    legend_title_text="Segmenti IstraOps"
)

st.plotly_chart(grafico, width="stretch")

st.caption(
    "Il grafico mostra due delle tre variabili utilizzate "
    "da K-Means. La terza è il numero di giorni trascorsi "
    "dall'ultima richiesta."
)


# Valutazione del modello K-Means

st.divider()
st.subheader("Valutazione del modello")

st.write(
    "Prima di scegliere il numero di segmenti, "
    "sono state confrontate tre configurazioni di K-Means."
)

# Recupero i risultati calcolati durante l'analisi
valutazione = pd.read_csv(
    BASE_DIR / "risultati" / "valutazione_cluster.csv"
)

valutazione["configurazione"] = (
    "K = " + valutazione["numero_cluster"].astype(str)
)

# Confronto dell'indice di silhouette
grafico_valutazione = px.bar(
    valutazione,
    x="configurazione",
    y="silhouette",
    text="silhouette",
    labels={
        "configurazione": "Numero di cluster",
        "silhouette": "Indice di silhouette"
    }
)

grafico_valutazione.update_traces(
    texttemplate="%{text:.4f}",
    textposition="outside"
)

st.plotly_chart(
    grafico_valutazione,
    width="stretch"
)

# Individuo la configurazione con il valore più alto
migliore = valutazione.loc[
    valutazione["silhouette"].idxmax()
]

st.write(
    f"La configurazione con il valore di silhouette più alto "
    f"è K = {int(migliore['numero_cluster'])}, "
    f"con un indice pari a {migliore['silhouette']:.4f}."
)

st.caption(
    "La valutazione riguarda l'intero dataset di 437 clienti "
    "e non cambia quando vengono applicati i filtri della dashboard."
)


# Profili dei segmenti

st.divider()
st.subheader("Profili dei segmenti")

st.write(
    "Riepilogo delle caratteristiche dei tre gruppi "
    "individuati dal modello K-Means."
)

# Carico i profili calcolati durante l'analisi
profili = pd.read_csv(
    BASE_DIR / "risultati" / "profili_cluster.csv",
    encoding="utf-8-sig"
)

profili["segmento"] = profili["cluster"].map(nomi_segmenti)

# Rendo i nomi delle colonne più leggibili
riepilogo = profili.rename(columns={
    "segmento": "Segmento",
    "clienti": "Clienti",
    "percentuale_clienti": "Quota clienti (%)",
    "richieste_medie": "Richieste medie",
    "spesa_media_euro": "Spesa media (€)",
    "giorni_ultima_richiesta_medi": "Giorni dall'ultima richiesta",
    "quota_fatturato_pct": "Quota fatturato (%)"
})

colonne = [
    "Segmento",
    "Clienti",
    "Quota clienti (%)",
    "Richieste medie",
    "Spesa media (€)",
    "Giorni dall'ultima richiesta",
    "Quota fatturato (%)"
]

st.dataframe(
    riepilogo[colonne],
    hide_index=True,
    width="stretch"
)

st.caption(
    "I profili si riferiscono all'intero dataset di 437 clienti "
    "e non vengono modificati dai filtri della dashboard."
)


# Consultazione dei dati

st.subheader("Dettaglio clienti")

st.dataframe(
    dati_filtrati,
    width="stretch",
    hide_index=True
)

st.caption(
    "I dati rappresentano una simulazione e non "
    "contengono informazioni personali reali."
)
