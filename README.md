
# IstrApp Analytics

Sistema di analisi e segmentazione della clientela sviluppato nell'ambito del Project Work del corso di laurea L-31 in Informatica per le Aziende Digitali.

## Il contesto

IstraOps è una startup simulata che offre servizi su richiesta ai proprietari di appartamenti turistici e piccole strutture ricettive dell'Istria.

La piattaforma opera in cinque località: Rovigno, Pola, Parenzo, Umago e Novigrad.

Il progetto nasce dall'esigenza di comprendere meglio i comportamenti della clientela e individuare gruppi di utenti ai quali proporre servizi e comunicazioni differenziati.

## Obiettivo del progetto

Realizzare un prototipo che permetta di:

- Generare un dataset sintetico di clienti.
- Individuare segmenti con caratteristiche simili tramite Machine Learning.
- Valutare la qualità dei raggruppamenti.
- Esplorare i risultati attraverso una dashboard interattiva.
- Assegnare un segmento a un cliente non presente nel database.

## Dataset

Il database contiene 437 clienti simulati, distribuiti nelle cinque località istriane.

Per ciascun cliente sono disponibili informazioni relative a frequenza delle richieste, spesa, data di iscrizione, ultima richiesta e categoria di servizio preferita.

Tutti i dati sono sintetici e non contengono informazioni personali reali.

## Metodo utilizzato

Per la segmentazione è stato scelto K-Means, un algoritmo di apprendimento non supervisionato.

L'analisi utilizza tre variabili:

1. Numero di richieste negli ultimi sei mesi.
2. Spesa media per richiesta.
3. Giorni trascorsi dall'ultima richiesta.

Le variabili vengono standardizzate prima dell'applicazione dell'algoritmo.

Sono state confrontate tre configurazioni, con 3, 4 e 5 cluster, utilizzando l'indice di silhouette e l'inerzia.

## Risultati

La configurazione selezionata prevede tre segmenti:

- Clienti operativi frequenti: 220 clienti.
- Clienti a spesa media elevata: 78 clienti.
- Clienti a bassa attività recente: 139 clienti.

Il valore di silhouette ottenuto è 0,3503.

I gruppi vengono interpretati considerando frequenza di utilizzo, spesa e attività recente.

## Dashboard

L'applicazione è sviluppata con Streamlit ed è organizzata in cinque pagine:

- Home: presentazione del progetto e indicatori aziendali.
- Analisi clienti: distribuzione, caratteristiche e valutazione dei cluster.
- Analisi territoriale: confronto delle cinque località istriane.
- Simulazione cliente: assegnazione automatica del segmento e confronto grafico con i clienti esistenti.
- Campagne marketing: selezione dei clienti e generazione di proposte commerciali personalizzate in base al segmento, alla località e al servizio preferito.

 Le campagne marketing sono elaborate attraverso regole commerciali definite nel programma. Il Machine Learning viene utilizzato per individuare il segmento del cliente, mentre la proposta commerciale viene adattata utilizzando le informazioni disponibili nel database.

Le comunicazioni generate sono bozze e non vengono inviate automaticamente.
## Avvio del progetto

Dopo aver scaricato il repository e aperto un terminale nella cartella principale, installare le dipendenze:

```bash
python -m pip install -r requirements.txt
```

Generare il dataset:

```bash
python 01_genera_dati.py
```

Eseguire il clustering:

```bash
python 02_analizza_cluster.py
```

Avviare la dashboard:

```bash
python -m streamlit run Home.py
```

La dashboard viene aperta nel browser attraverso il server locale di Streamlit.

## Limiti dell'analisi

Il prototipo utilizza dati simulati, pertanto i risultati non rappresentano comportamenti effettivamente osservati nel mercato turistico istriano.

Il modello considera la data dell'ultima richiesta, ma non dispone dello storico completo delle prenotazioni. Non è quindi possibile misurare direttamente la stagionalità mensile dei servizi.

Il filtro temporale della dashboard riguarda la data di iscrizione dei clienti.

Tra i possibili sviluppi futuri rientrano l'utilizzo di dati reali anonimizzati, l'analisi delle singole prenotazioni e il confronto con altri algoritmi di clustering.
