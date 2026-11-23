# IstraOps - Dashboard di analisi clienti
# Project Work L-31

from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import joblib


BASE_DIR = Path(__file__).resolve().parent
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

dati_filtrati = clienti.copy()

if zona != "Tutte":
    dati_filtrati = dati_filtrati[
        dati_filtrati["zona"] == zona
    ]

if categoria != "Tutte":
    dati_filtrati = dati_filtrati[
        dati_filtrati["categoria_preferita"] == categoria
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

# Classificazione di un nuovo cliente

st.divider()
st.subheader("Simulazione nuovo cliente")

st.write(
    "Inserisci i dati di un cliente per individuare "
    "il segmento a cui appartiene."
)

with st.form("nuovo_cliente"):

    col1, col2, col3 = st.columns(3)

    richieste = col1.number_input(
        "Richieste negli ultimi 6 mesi",
        min_value=1,
        max_value=100,
        value=8
    )

    spesa = col2.number_input(
        "Spesa media per richiesta (€)",
        min_value=1.0,
        max_value=500.0,
        value=75.0
    )

    giorni = col3.number_input(
        "Giorni dall'ultima richiesta",
        min_value=0,
        max_value=365,
        value=30
    )

    verifica = st.form_submit_button(
        "Analizza cliente"
    )


if verifica:

    dati_modello = carica_modello()

    nuovo_cliente = pd.DataFrame([{
        "richieste_ultimi_6_mesi": richieste,
        "spesa_media_euro": spesa,
        "giorni_ultima_richiesta": giorni
    }])

    # Applico la stessa normalizzazione usata
    # durante l'addestramento di K-Means.
    dati_normalizzati = dati_modello["scaler"].transform(
        nuovo_cliente[dati_modello["variabili"]]
    )

    cluster = int(
        dati_modello["modello"].predict(
            dati_normalizzati
        )[0]
    )

    segmento = nomi_segmenti.get(
        cluster,
        f"Cluster {cluster}"
    )

    st.success(f"Segmento individuato: {segmento}")

        # Confronto con i clienti già presenti nel segmento

    profilo = clienti[clienti["cluster"] == cluster]

    st.subheader("Caratteristiche del segmento")

    st.write(
        f"Questo gruppo comprende {len(profilo)} "
        f"dei {len(clienti)} clienti analizzati."
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Richieste medie",
        f"{profilo['richieste_ultimi_6_mesi'].mean():.1f}"
    )

    c2.metric(
        "Spesa media",
        f"{profilo['spesa_media_euro'].mean():.2f} €"
    )

    c3.metric(
        "Giorni dall'ultima richiesta",
        f"{profilo['giorni_ultima_richiesta'].mean():.0f}"
    )

    # Possibili strategie commerciali per IstraOps
    strategie = {
        0: (
            "Valutare pacchetti di servizi ricorrenti, "
            "come pulizie e gestione degli appartamenti."
        ),
        1: (
            "Proporre servizi premium o pacchetti "
            "personalizzati per strutture ricettive."
        ),
        2: (
            "Verificare se la riduzione delle richieste "
            "dipende dalla stagionalità turistica, "
            "prima di proporre offerte di riattivazione."
        )
    }

    st.subheader("Opportunità commerciale")
    st.write(strategie.get(cluster, "Segmento da approfondire."))

        # Posizionamento del cliente rispetto ai segmenti esistenti

    st.subheader("Posizionamento del cliente")

    st.write(
        "La stella nera rappresenta il cliente appena analizzato. "
        "Gli altri punti sono i 437 clienti del database IstraOps."
    )

    # Preparo i dati per il confronto
    confronto = clienti.copy()

    confronto["segmento"] = confronto["cluster"].map(
        nomi_segmenti
    )

    # Grafico dei clienti già analizzati
    grafico_cliente = px.scatter(
        confronto,
        x="richieste_ultimi_6_mesi",
        y="spesa_media_euro",
        color="segmento",
        hover_name="id_cliente",
        hover_data=["giorni_ultima_richiesta"],
        opacity=0.35,
        labels={
            "richieste_ultimi_6_mesi": "Richieste negli ultimi 6 mesi",
            "spesa_media_euro": "Spesa media (€)",
            "segmento": "Segmento"
        }
    )

    # Evidenzio il nuovo cliente con una stella
    grafico_cliente.add_scatter(
        x=[richieste],
        y=[spesa],
        mode="markers+text",
        name="Cliente analizzato",
        text=["Nuovo cliente"],
        textposition="top center",
        marker={
            "symbol": "star",
            "size": 20,
            "color": "black",
            "line": {
                "color": "white",
                "width": 1
            }
        },
        hovertemplate=(
            f"Richieste: {richieste}<br>"
            f"Spesa media: {spesa:.2f} €<br>"
            f"Giorni ultima richiesta: {giorni}<br>"
            f"Segmento: {segmento}"
            "<extra></extra>"
        )
    )

    grafico_cliente.update_layout(
        height=500,
        legend_title_text="Segmenti IstraOps"
    )

    st.plotly_chart(
        grafico_cliente,
        width="stretch",
        key="grafico_nuovo_cliente"
    )

    st.caption(
        "Il grafico rappresenta frequenza e spesa media. "
        "L'assegnazione del segmento considera anche "
        "i giorni trascorsi dall'ultima richiesta."
    )

    st.info(
        "Il risultato è basato sui comportamenti "
        "simulati dei clienti IstraOps. "
        "Non rappresenta una previsione certa "
        "del comportamento futuro."
    )