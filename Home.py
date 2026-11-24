from pathlib import Path

import pandas as pd
import streamlit as st


# IstrApp Analytics - Pagina iniziale

BASE_DIR = Path(__file__).resolve().parent
FILE_CLIENTI = BASE_DIR / "risultati" / "clienti_con_cluster.csv"

st.set_page_config(page_title="IstrApp Analytics", page_icon="📊", layout="wide")


@st.cache_data
def carica_dati():
    return pd.read_csv(FILE_CLIENTI, encoding="utf-8-sig")


clienti = carica_dati()

st.title("IstrApp Analytics")
st.subheader("Analisi intelligente della clientela turistica")

st.write(
    "Sistema di supporto alle decisioni commerciali sviluppato "
    "per IstraOps, una startup simulata che offre servizi "
    "alle strutture ricettive dell'Istria."
)

st.divider()

st.header("Panoramica aziendale")

totale_clienti = len(clienti)
totale_richieste = int(clienti["richieste_ultimi_6_mesi"].sum())
fatturato = clienti["spesa_totale_euro"].sum()

fatturato_formattato = (
    f"{fatturato:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

c1, c2, c3 = st.columns(3)

c1.metric("Clienti analizzati", totale_clienti)
c2.metric("Richieste registrate", f"{totale_richieste:,}".replace(",", "."))
c3.metric("Fatturato simulato", f"{fatturato_formattato} €")

st.divider()

st.header("Esplora il progetto")

st.write(
    "L'applicazione utilizza l'algoritmo K-Means per individuare "
    "gruppi di clienti con comportamenti simili. "
    "È possibile esplorare i segmenti, confrontare le località "
    "e simulare la classificazione di un nuovo cliente."
)

st.divider()

st.caption(
    "Project Work L-31 | Dati interamente sintetici "
    "| Periodo di riferimento: 31 ottobre 2026"
)
