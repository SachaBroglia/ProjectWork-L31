from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent
FILE_CLIENTI = BASE_DIR / "risultati" / "clienti_con_cluster.csv"


@st.cache_data
def carica_clienti():
    return pd.read_csv(FILE_CLIENTI, encoding="utf-8-sig")


clienti = carica_clienti()

nomi_segmenti = {
    0: "Clienti operativi frequenti",
    1: "Clienti a spesa media elevata",
    2: "Clienti a bassa attività recente",
}


st.title("Campagne marketing")

st.write(
    "Seleziona un cliente per visualizzare il suo profilo "
    "e individuare una possibile iniziativa commerciale."
)

st.divider()


# Selezione del cliente

elenco_clienti = sorted(clienti["id_cliente"].tolist())

# Recupero il cliente selezionato nella pagina di analisi
cliente_richiesto = st.session_state.get(
    "cliente_da_marketing",
    "CLI-0005"
)

# Controllo che il codice esista nel database
if cliente_richiesto not in elenco_clienti:
    cliente_richiesto = elenco_clienti[0]

posizione = elenco_clienti.index(cliente_richiesto)

id_selezionato = st.selectbox(
    "Seleziona il cliente",
    elenco_clienti,
    index=posizione
)

cliente = clienti.loc[
    clienti["id_cliente"] == id_selezionato
].iloc[0]


# Informazioni del cliente

st.subheader("Profilo cliente")

cluster = int(cliente["cluster"])
segmento = nomi_segmenti.get(cluster, f"Cluster {cluster}")

zona = cliente["zona"]
servizio = cliente["categoria_preferita"]
richieste = int(cliente["richieste_ultimi_6_mesi"])
giorni = int(cliente["giorni_ultima_richiesta"])
spesa = float(cliente["spesa_media_euro"])

st.write(f"**Cliente:** {id_selezionato}")
st.write(f"**Località:** {zona}")
st.write(f"**Servizio preferito:** {servizio}")
st.write(f"**Segmento:** {segmento}")

c1, c2, c3 = st.columns(3)

c1.metric("Richieste negli ultimi 6 mesi", richieste)
c2.metric("Spesa media", f"{spesa:.2f} €")
c3.metric("Giorni dall'ultima richiesta", giorni)

st.divider()


# Strategie commerciali associate ai segmenti

if cluster == 0:

    campagna = "Programma servizi ricorrenti"

    obiettivo = (
        "Fidelizzare il cliente e semplificare "
        "la programmazione dei servizi."
    )

    proposta = (
        f"Proporre un pacchetto periodico di {servizio.lower()} "
        f"per le strutture gestite a {zona}."
    )

    canale = "Email personalizzata"

    messaggio = (
        f"Buongiorno,\n\n"
        f"vorremmo proporti una soluzione per organizzare "
        f"con maggiore semplicità i servizi della tua struttura "
        f"a {zona}.\n\n"
        f"Possiamo valutare insieme un pacchetto periodico "
        f"dedicato a {servizio.lower()}, adattato alle tue esigenze.\n\n"
        f"Se sei interessato, saremo felici di preparare "
        f"una proposta personalizzata.\n\n"
        f"Il team IstraOps"
    )

elif cluster == 1:

    campagna = "Servizi premium su misura"

    obiettivo = (
        "Valorizzare la relazione commerciale "
        "attraverso servizi personalizzati."
    )

    proposta = (
        f"Presentare un'offerta premium che includa "
        f"{servizio.lower()} e servizi complementari."
    )

    canale = "Email con proposta commerciale"

    messaggio = (
        f"Buongiorno,\n\n"
        f"IstraOps sta sviluppando nuove soluzioni dedicate "
        f"alle strutture turistiche dell'Istria.\n\n"
        f"Per la tua attività a {zona}, vorremmo proporti "
        f"un servizio personalizzato che includa "
        f"{servizio.lower()} e ulteriori opzioni "
        f"di assistenza.\n\n"
        f"Possiamo preparare una proposta in base "
        f"alle necessità della tua struttura.\n\n"
        f"Il team IstraOps"
    )

else:

    campagna = "Prepariamo insieme la prossima stagione"

    obiettivo = (
        "Verificare le esigenze del cliente "
        "e favorire un possibile ritorno alla piattaforma."
    )

    proposta = (
        f"Contattare il cliente per verificare il periodo "
        f"di apertura della struttura e proporre "
        f"servizi di {servizio.lower()}."
    )

    canale = "Email di ricontatto"

    messaggio = (
        f"Buongiorno,\n\n"
        f"stai già organizzando la prossima stagione "
        f"turistica della tua struttura a {zona}?\n\n"
        f"Il team IstraOps può aiutarti nella gestione "
        f"dei servizi di {servizio.lower()}, "
        f"con soluzioni adattabili al tuo calendario "
        f"di apertura.\n\n"
        f"Se desideri, possiamo preparare insieme "
        f"un piano per la prossima stagione.\n\n"
        f"Il team IstraOps"
    )


# Risultato dell'analisi commerciale

st.subheader("Campagna consigliata")

st.success(campagna)

st.write(f"**Obiettivo commerciale:** {obiettivo}")

st.write(f"**Proposta:** {proposta}")

st.write(f"**Canale suggerito:** {canale}")

if cluster == 2:
    st.warning(
        "Un periodo prolungato senza richieste non indica "
        "necessariamente l'abbandono della piattaforma. "
        "Il cliente potrebbe gestire una struttura stagionale."
    )


# Bozza della comunicazione

st.divider()

st.subheader("Messaggio commerciale")

st.write(
    "Bozza personalizzata in base al segmento, "
    "alla località e al servizio preferito."
)

testo_email = st.text_area(
    "Testo del messaggio",
    value=messaggio,
    height=280,
)

st.caption(
    "La campagna è una proposta simulata. "
    "Il programma non invia messaggi e non modifica "
    "il database dei clienti."
)