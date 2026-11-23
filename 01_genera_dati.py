# PROJECT WORK L-31
# IstraOps - Generazione dataset clienti
#
# Il programma genera dati sintetici relativi
# a una startup di servizi per strutture turistiche.

import csv
import random
from datetime import date, timedelta
from pathlib import Path


# ------------------------------------------
# 1. CONFIGURAZIONE GENERALE
# ------------------------------------------

DATA_RIFERIMENTO = date(2026, 10, 31)
SEED = 2026

# Distribuzione geografica dei clienti
ZONE = {
    "Rovigno": 112,
    "Pola": 105,
    "Parenzo": 91,
    "Umago": 72,
    "Novigrad": 57
}

# Servizi disponibili sulla piattaforma
# I valori rappresentano intervalli di spesa simulati.

SERVIZI = {
    "Pulizie e cambio ospiti": (50, 115),
    "Check-in e accoglienza": (25, 65),
    "Manutenzione": (70, 210),
    "Biancheria e forniture": (35, 95),
    "Assistenza tecnologica": (40, 135)
}


# ------------------------------------------
# 2. COMPORTAMENTI DEI CLIENTI
# ------------------------------------------

# Questi profili servono soltanto per simulare
# clienti con abitudini differenti.
# Non saranno inseriti nel dataset finale.

PROFILI = {
    "intensivi": {
        "iscrizione": (160, 295),
        "richieste": (18, 42),
        "ultima": (0, 20)
    },
    "abituali": {
        "iscrizione": (120, 295),
        "richieste": (7, 20),
        "ultima": (4, 49)
    },
    "stagionali": {
        "iscrizione": (190, 295),
        "richieste": (7, 25),
        "ultima": (35, 120)
    },
    "saltuari": {
        "iscrizione": (100, 295),
        "richieste": (1, 6),
        "ultima": (15, 150)
    },
    "inattivi": {
        "iscrizione": (200, 295),
        "richieste": (1, 3),
        "ultima": (105, 175)
    },
    "nuovi": {
        "iscrizione": (10, 65),
        "richieste": (1, 5),
        "ultima": (0, 30)
    }
}


# ------------------------------------------
# 3. GENERAZIONE DEL SINGOLO CLIENTE
# ------------------------------------------

def genera_cliente(numero, zona, rng):

    # Seleziona un comportamento simulato
    tipo = rng.choices(
        list(PROFILI.keys()),
        weights=[18, 23, 21, 18, 10, 10],
        k=1
    )[0]

    profilo = PROFILI[tipo]

    # Giorni trascorsi dall'iscrizione
    giorni_iscrizione = rng.randint(
        *profilo["iscrizione"]
    )

    # Numero di richieste negli ultimi sei mesi
    richieste = rng.randint(
        *profilo["richieste"]
    )

    # Giorni dall'ultima richiesta
    giorni_ultima = rng.randint(
        *profilo["ultima"]
    )

    # Controllo di coerenza delle date
    giorni_ultima = min(
        giorni_ultima,
        giorni_iscrizione
    )

    data_iscrizione = (
        DATA_RIFERIMENTO -
        timedelta(days=giorni_iscrizione)
    )

    # Categoria di servizio preferita
    categoria = rng.choice(list(SERVIZI.keys()))

    # Prezzo medio coerente con il servizio
    prezzo_min, prezzo_max = SERVIZI[categoria]

    spesa_media = round(
        rng.uniform(prezzo_min, prezzo_max),
        2
    )

    # Calcolo della spesa totale
    spesa_totale = round(
        richieste * spesa_media,
        2
    )

    # Record del cliente
    return {
        "id_cliente": f"CLI-{numero:04d}",
        "zona": zona,
        "data_iscrizione": data_iscrizione.isoformat(),
        "richieste_ultimi_6_mesi": richieste,
        "spesa_totale_euro": spesa_totale,
        "spesa_media_euro": round(
            spesa_totale / richieste, 2
        ),
        "giorni_ultima_richiesta": giorni_ultima,
        "categoria_preferita": categoria
    }


# ------------------------------------------
# 4. CREAZIONE DEL DATASET
# ------------------------------------------

def main():

    rng = random.Random(SEED)

    # Crea l'elenco delle localita
    elenco_zone = []

    for zona, quantita in ZONE.items():
        elenco_zone.extend([zona] * quantita)

    # Mescola i clienti
    rng.shuffle(elenco_zone)

    clienti = []

    for numero, zona in enumerate(elenco_zone, 1):

        cliente = genera_cliente(
            numero,
            zona,
            rng
        )

        clienti.append(cliente)

    # Crea automaticamente la cartella dati
    cartella = Path(__file__).resolve().parent / "dati"
    cartella.mkdir(exist_ok=True)

    percorso = cartella / "clienti_sintetici.csv"

    # Salva il dataset in formato CSV
    with open(
        percorso,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        colonne = list(clienti[0].keys())

        writer = csv.DictWriter(
            file,
            fieldnames=colonne
        )

        writer.writeheader()
        writer.writerows(clienti)

    # Messaggi di controllo
    print("--------------------------------")
    print("ISTRAOPS - GENERATORE CLIENTI")
    print("--------------------------------")
    print(f"Clienti generati: {len(clienti)}")
    print(f"Localita analizzate: {len(ZONE)}")
    print(f"Data riferimento: {DATA_RIFERIMENTO}")
    print(f"Dataset salvato: {percorso}")
    print("--------------------------------")
    print("Generazione completata!")


if __name__ == "__main__":
    main()