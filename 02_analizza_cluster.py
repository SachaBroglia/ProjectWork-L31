# PROJECT WORK L-31
# IstraOps - Segmentazione automatica della clientela
#
# Analisi dei comportamenti dei clienti attraverso
# l'algoritmo K-Means (Machine Learning non supervisionato).

from pathlib import Path

import joblib
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


# --------------------------------------------------
# 1. CONFIGURAZIONE
# --------------------------------------------------

CARTELLA_PROGETTO = Path(__file__).resolve().parent

FILE_DATI = CARTELLA_PROGETTO / "dati" / "clienti_sintetici.csv"

CARTELLA_RISULTATI = CARTELLA_PROGETTO / "risultati"
CARTELLA_MODELLO = CARTELLA_PROGETTO / "modello"

SEED = 2026

# Variabili utilizzate per il clustering
VARIABILI = ["richieste_ultimi_6_mesi", "spesa_media_euro", "giorni_ultima_richiesta"]

# Confrontiamo tre possibili configurazioni
NUMERI_CLUSTER = [3, 4, 5]


# --------------------------------------------------
# 2. CARICAMENTO E PREPARAZIONE DEI DATI
# --------------------------------------------------


def prepara_dati():

    print("Caricamento del database IstraOps...")

    df = pd.read_csv(FILE_DATI, encoding="utf-8-sig")

    print(f"Clienti caricati: {len(df)}")

    # Verifica della presenza delle colonne necessarie
    colonne_mancanti = set(VARIABILI) - set(df.columns)

    if colonne_mancanti:
        raise ValueError(f"Colonne mancanti: {colonne_mancanti}")

    # Controllo dei valori numerici
    for variabile in VARIABILI:
        df[variabile] = pd.to_numeric(df[variabile], errors="coerce")

        # I valori negativi non sono validi
        df.loc[df[variabile] < 0, variabile] = float("nan")

        # Frequenza e spesa devono essere positive
        if variabile != "giorni_ultima_richiesta":
            df.loc[df[variabile] == 0, variabile] = float("nan")

        # Gestione dei valori mancanti
        mediana = df[variabile].median()

        if pd.isna(mediana):
            raise ValueError(f"Nessun valore valido per {variabile}")

        df[variabile] = df[variabile].fillna(mediana)

    print("Preparazione dei dati completata.")

    return df


# --------------------------------------------------
# 3. NORMALIZZAZIONE
# --------------------------------------------------


def normalizza_dati(df):

    # Le variabili hanno scale differenti.
    # StandardScaler le rende confrontabili.

    scaler = StandardScaler()

    dati_normalizzati = scaler.fit_transform(df[VARIABILI])

    print("Normalizzazione completata.")

    return dati_normalizzati, scaler


# --------------------------------------------------
# 4. ANALISI K-MEANS
# --------------------------------------------------


def analizza_cluster(dati_normalizzati):

    risultati = []

    modello_migliore = None
    silhouette_migliore = -1
    numero_migliore = None

    print("\nConfronto delle configurazioni K-Means:")

    for k in NUMERI_CLUSTER:
        modello = KMeans(n_clusters=k, random_state=SEED, n_init=20)

        gruppi = modello.fit_predict(dati_normalizzati)

        # Valutazione della separazione dei gruppi
        silhouette = silhouette_score(dati_normalizzati, gruppi)

        # Inerzia utile per il metodo del gomito
        inerzia = modello.inertia_

        risultati.append(
            {
                "numero_cluster": k,
                "silhouette": round(silhouette, 4),
                "inerzia": round(inerzia, 2),
            }
        )

        print(f"K={k} | Silhouette={silhouette:.4f} | Inerzia={inerzia:.2f}")

        # Selezione della configurazione migliore
        if silhouette > silhouette_migliore:
            silhouette_migliore = silhouette
            modello_migliore = modello
            numero_migliore = k

    print("\nConfigurazione selezionata:")
    print(f"Numero cluster: {numero_migliore}")
    print(f"Indice silhouette: {silhouette_migliore:.4f}")

    valutazioni = pd.DataFrame(risultati)

    return modello_migliore, valutazioni


# --------------------------------------------------
# 5. CREAZIONE DEI PROFILI DEI CLUSTER
# --------------------------------------------------


def crea_profili(df):

    profili = (
        df.groupby("cluster")
        .agg(
            clienti=("id_cliente", "count"),
            richieste_medie=("richieste_ultimi_6_mesi", "mean"),
            spesa_media_euro=("spesa_media_euro", "mean"),
            spesa_totale_euro=("spesa_totale_euro", "sum"),
            giorni_ultima_richiesta_medi=("giorni_ultima_richiesta", "mean"),
        )
        .reset_index()
    )

    # Percentuale dei clienti appartenenti a ogni gruppo
    profili["percentuale_clienti"] = (profili["clienti"] / len(df) * 100).round(2)

    # Oltre al numero di clienti, voglio capire
    # quanto ogni gruppo contribuisce al fatturato di IstraOps.

    fatturato_complessivo = df["spesa_totale_euro"].sum()

    profili["quota_fatturato_pct"] = (
        profili["spesa_totale_euro"] / fatturato_complessivo * 100
    ).round(2)

    # Categoria più frequente per ciascun cluster
    categorie = df.groupby("cluster")["categoria_preferita"].agg(
        lambda x: x.mode().iloc[0]
    )

    profili["categoria_prevalente"] = profili["cluster"].map(categorie)

    return profili.round(2)


# --------------------------------------------------
# 6. SALVATAGGIO DEI RISULTATI
# --------------------------------------------------


def salva_risultati(df, profili, valutazioni, scaler, modello):

    CARTELLA_RISULTATI.mkdir(exist_ok=True)
    CARTELLA_MODELLO.mkdir(exist_ok=True)

    # Dataset con cluster assegnato
    df.to_csv(
        CARTELLA_RISULTATI / "clienti_con_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Caratteristiche medie dei gruppi
    profili.to_csv(
        CARTELLA_RISULTATI / "profili_cluster.csv", index=False, encoding="utf-8-sig"
    )

    # Confronto dei differenti numeri di cluster
    valutazioni.to_csv(
        CARTELLA_RISULTATI / "valutazione_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Salvataggio del modello per la dashboard
    joblib.dump(
        {
            "modello": modello,
            "scaler": scaler,
            "variabili": VARIABILI,
            "data_riferimento": "2026-10-31",
        },
        CARTELLA_MODELLO / "modello_istraops.joblib",
    )

    print("\nFile dei risultati salvati correttamente!")


# --------------------------------------------------
# 7. PROGRAMMA PRINCIPALE
# --------------------------------------------------


def main():

    print("-------------------------------------")
    print("ISTRAOPS - ANALISI MACHINE LEARNING")
    print("-------------------------------------")

    df = prepara_dati()

    dati_normalizzati, scaler = normalizza_dati(df)

    modello, valutazioni = analizza_cluster(dati_normalizzati)

    # Assegna a ogni cliente il cluster individuato
    df["cluster"] = modello.labels_

    profili = crea_profili(df)

    salva_risultati(df, profili, valutazioni, scaler, modello)

    print("\nPROFILI DEI CLUSTER:")
    print(profili.to_string(index=False))

    print("\nAnalisi completata!")


if __name__ == "__main__":
    main()
