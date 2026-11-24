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

# Registro temporaneo dei clienti analizzati

if "registro_prova" not in st.session_state:
    st.session_state["registro_prova"] = []

if "cliente_pronto" not in st.session_state:
    st.session_state["cliente_pronto"] = None

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


st.title("Gestione nuovi clienti")

st.write(
    "Inserisci le caratteristiche di un cliente con uno storico "
    "di utilizzo della piattaforma. Il modello K-Means di IstraOps "
    "individuerà il segmento con comportamento più simile."
)

st.divider()


# Inserimento dei dati
# Scelta della modalità di inserimento

st.subheader("Dati del cliente")

modalita = st.radio(
    "Come vuoi inserire i dati?",
    ["Inserimento manuale", "Carica file CSV"],
    horizontal=True,
)

analizza = False

if modalita == "Inserimento manuale":
    with st.form("simulazione_cliente"):
        c1, c2, c3 = st.columns(3)

        richieste = c1.number_input(
            "Richieste negli ultimi 6 mesi",
            min_value=1,
            max_value=100,
            value=8,
        )

        spesa = c2.number_input(
            "Spesa media per richiesta (€)",
            min_value=1.0,
            max_value=500.0,
            value=75.0,
        )

        giorni = c3.number_input(
            "Giorni dall'ultima richiesta",
            min_value=0,
            max_value=365,
            value=30,
        )

        analizza = st.form_submit_button("Analizza cliente")

else:
    st.write(
        "Carica un file CSV contenente un cliente. "
        "Il file deve riportare le tre variabili "
        "utilizzate dal modello K-Means."
    )

    # File di esempio per provare la funzionalità
    esempio_csv = (
        "richieste_ultimi_6_mesi;spesa_media_euro;giorni_ultima_richiesta\n"
        "3;31,33;144\n"
    )

    st.download_button(
        "Scarica CSV di esempio",
        data=esempio_csv,
        file_name="esempio_cliente.csv",
        mime="text/csv",
    )

    file_csv = st.file_uploader(
        "Seleziona il file del nuovo cliente",
        type=["csv"],
    )

    if file_csv is not None:
        try:
            dati_csv = pd.read_csv(
                file_csv,
                sep=None,
                engine="python",
                encoding="utf-8-sig",
            )

            dati_csv.columns = dati_csv.columns.str.strip()

            colonne = [
                "richieste_ultimi_6_mesi",
                "spesa_media_euro",
                "giorni_ultima_richiesta",
            ]

            mancanti = [
                colonna for colonna in colonne if colonna not in dati_csv.columns
            ]

            if mancanti:
                st.error(
                    "Il file non contiene tutte le colonne richieste: "
                    + ", ".join(mancanti)
                )

            elif len(dati_csv) != 1:
                st.error("Il file deve contenere esattamente un cliente.")

            else:
                record = dati_csv.iloc[0]

                valore_richieste = float(
                    str(record["richieste_ultimi_6_mesi"]).replace(",", ".")
                )

                valore_spesa = float(str(record["spesa_media_euro"]).replace(",", "."))

                valore_giorni = float(
                    str(record["giorni_ultima_richiesta"]).replace(",", ".")
                )

                valori_validi = (
                    valore_richieste.is_integer()
                    and valore_giorni.is_integer()
                    and 1 <= valore_richieste <= 100
                    and 1 <= valore_spesa <= 500
                    and 0 <= valore_giorni <= 365
                )

                if not valori_validi:
                    st.error(
                        "I valori del cliente non sono validi. "
                        "Controlla richieste, spesa e giorni."
                    )

                else:
                    richieste = int(valore_richieste)
                    spesa = valore_spesa
                    giorni = int(valore_giorni)

                    st.success("File CSV caricato correttamente!")

                    st.dataframe(
                        dati_csv,
                        hide_index=True,
                        width="stretch",
                    )

                    analizza = st.button(
                        "Analizza cliente CSV",
                        type="primary",
                    )

        except (
            ValueError,
            TypeError,
            pd.errors.ParserError,
            pd.errors.EmptyDataError,
        ):
            st.error(
                "Impossibile leggere i dati del file CSV. "
                "Verifica il formato e i valori inseriti."
            )


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

    # Preparo il cliente per l'eventuale registrazione

    st.session_state["cliente_pronto"] = {
        "richieste_ultimi_6_mesi": int(richieste),
        "spesa_media_euro": float(spesa),
        "giorni_ultima_richiesta": int(giorni),
        "cluster": cluster,
        "segmento": segmento,
    }

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


# Registro temporaneo dei nuovi clienti

st.divider()
st.subheader("Registro nuovi clienti")

st.write(
    "In questa sezione puoi registrare temporaneamente "
    "i clienti analizzati ed esportare i risultati."
)

ultimo = st.session_state["cliente_pronto"]

if ultimo is not None:
    st.info(f"Cliente pronto per la registrazione: {ultimo['segmento']}")

# Aggiungo il cliente al registro temporaneo

if st.button("Aggiungi al registro di prova", disabled=ultimo is None):
    registro = st.session_state["registro_prova"]

    codice = f"TEST-{len(registro) + 1:04d}"

    nuovo_record = {
        "id_cliente": codice,
        **ultimo,
    }

    registro.append(nuovo_record)

    st.session_state["cliente_pronto"] = None

    st.success(f"Cliente {codice} aggiunto al registro!")


# Visualizzo i clienti registrati

registro = st.session_state["registro_prova"]

if registro:
    tabella_registro = pd.DataFrame(registro)

    st.dataframe(tabella_registro, hide_index=True, width="stretch")

    # Esportazione del registro in formato CSV

    csv_registro = tabella_registro.to_csv(index=False, sep=";", decimal=",")

    st.download_button(
        "Scarica registro CSV",
        data=csv_registro.encode("utf-8-sig"),
        file_name="istrapp_registro_prova.csv",
        mime="text/csv",
    )

else:
    st.write("Non sono ancora stati aggiunti clienti al registro.")


st.caption(
    "Il registro è temporaneo e non modifica "
    "il database originale dei 437 clienti. "
    "Scarica il CSV per conservarne una copia."
)
