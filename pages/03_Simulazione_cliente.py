from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st


# Percorsi dei dati e del modello
BASE_DIR = Path(__file__).resolve().parent.parent
FILE_CLIENTI = BASE_DIR / "risultati" / "clienti_con_cluster.csv"
FILE_MODELLO = BASE_DIR / "modello" / "modello_istraops.joblib"


@st.cache_data
def carica_clienti():
    return pd.read_csv(FILE_CLIENTI, encoding="utf-8-sig")


@st.cache_resource
def carica_modello():
    return joblib.load(FILE_MODELLO)


clienti = carica_clienti()
dati_modello = carica_modello()

nomi_segmenti = {
    0: "Clienti operativi frequenti",
    1: "Clienti a spesa media elevata",
    2: "Clienti a bassa attività recente",
}

strategie = {
    0: (
        "Valutare pacchetti di servizi ricorrenti, "
        "come pulizie e gestione degli appartamenti."
    ),
    1: ("Proporre servizi premium o pacchetti personalizzati per strutture ricettive."),
    2: (
        "Verificare se la riduzione delle richieste "
        "dipende dalla stagionalità turistica, "
        "prima di proporre offerte di riattivazione."
    ),
}


st.title("Simulazione cliente")

st.write(
    "Inserisci le caratteristiche di un cliente con uno storico "
    "di utilizzo della piattaforma. Il modello K-Means di IstraOps "
    "individuerà il segmento con comportamento più simile."
)

st.divider()


# Inserimento dei dati

with st.form("simulazione_cliente"):
    c1, c2, c3 = st.columns(3)

    richieste = c1.number_input(
        "Richieste negli ultimi 6 mesi", min_value=1, max_value=100, value=8
    )

    spesa = c2.number_input(
        "Spesa media per richiesta (€)", min_value=1.0, max_value=500.0, value=75.0
    )

    giorni = c3.number_input(
        "Giorni dall'ultima richiesta", min_value=0, max_value=365, value=30
    )

    analizza = st.form_submit_button("Analizza cliente")


if analizza:
    # Preparo le variabili richieste dal modello
    nuovo_cliente = pd.DataFrame(
        [
            {
                "richieste_ultimi_6_mesi": richieste,
                "spesa_media_euro": spesa,
                "giorni_ultima_richiesta": giorni,
            }
        ]
    )

    # Utilizzo lo stesso scaler dell'addestramento
    dati_normalizzati = dati_modello["scaler"].transform(
        nuovo_cliente[dati_modello["variabili"]]
    )

    cluster = int(dati_modello["modello"].predict(dati_normalizzati)[0])

    segmento = nomi_segmenti.get(cluster, f"Cluster {cluster}")

    st.divider()
    st.success(f"Segmento individuato: {segmento}")

    # Confronto con il segmento di riferimento
    profilo = clienti[clienti["cluster"] == cluster]

    st.subheader("Caratteristiche del segmento")

    st.write(
        f"Il segmento comprende {len(profilo)} clienti su un totale di {len(clienti)}."
    )

    m1, m2, m3 = st.columns(3)

    m1.metric("Richieste medie", f"{profilo['richieste_ultimi_6_mesi'].mean():.1f}")

    m2.metric("Spesa media", f"{profilo['spesa_media_euro'].mean():.2f} €")

    m3.metric(
        "Giorni dall'ultima richiesta",
        f"{profilo['giorni_ultima_richiesta'].mean():.0f}",
    )

    # Indicazione commerciale per il segmento
    st.subheader("Opportunità commerciale")
    st.write(strategie.get(cluster, "Segmento da approfondire."))

    # Confronto grafico con i clienti esistenti
    st.subheader("Posizionamento del cliente")

    confronto = clienti.copy()
    confronto["segmento"] = confronto["cluster"].map(nomi_segmenti)

    grafico = px.scatter(
        confronto,
        x="richieste_ultimi_6_mesi",
        y="spesa_media_euro",
        color="segmento",
        hover_name="id_cliente",
        hover_data=["zona", "giorni_ultima_richiesta"],
        opacity=0.35,
        labels={
            "richieste_ultimi_6_mesi": "Richieste negli ultimi 6 mesi",
            "spesa_media_euro": "Spesa media (€)",
            "segmento": "Segmento",
        },
    )

    # La stella rappresenta il cliente simulato
    grafico.add_scatter(
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
            "line": {"color": "white", "width": 1},
        },
        hovertemplate=(
            f"Richieste: {richieste}<br>"
            f"Spesa media: {spesa:.2f} €<br>"
            f"Giorni ultima richiesta: {giorni}<br>"
            f"Segmento: {segmento}"
            "<extra></extra>"
        ),
    )

    grafico.update_layout(height=500, legend_title_text="Segmenti IstraOps")

    st.plotly_chart(grafico, width="stretch")

    st.caption(
        "Il grafico mostra frequenza e spesa media. "
        "Il modello considera anche i giorni trascorsi "
        "dall'ultima richiesta."
    )

    st.info(
        "La classificazione utilizza dati sintetici e non "
        "prevede con certezza il comportamento futuro. "
        "Il cliente simulato non viene salvato nel database."
    )
