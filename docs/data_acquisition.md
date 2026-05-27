# Piano di Acquisizione Dati - Arechi Urban Study

Per procedere con la modellazione 3D e le analisi previste per l'area del Piazzale Gipo Viani e dello Stadio Arechi, è necessario raccogliere diversi livelli di dati. Di seguito una lista strutturata dei dati da acquisire e delle potenziali fonti.

## 1. Dati Cartografici e Geospaziali (GIS e 3D)
Questi dati sono la base per la modellazione 3D e per l'inquadramento territoriale.

*   **Ortofoto ad alta risoluzione:** Immagini aeree aggiornate dell'area.
    *   *Fonti:* Geoportale Nazionale, Google Earth (per reference visive), Regione Campania.
*   **Modelli Digitali di Elevazione (DTM / DSM):** Dati altimetrici per modellare il terreno e l'altezza degli edifici esistenti.
    *   *Fonti:* Geoportale della Regione Campania, Open Topography.
*   **Footprint degli edifici (Edificato):** Poligoni 2D degli edifici esistenti per estruderli in 3D.
    *   *Fonti:* OpenStreetMap (OSM), database topografico regionale/comunale.
*   **Limiti amministrativi e catastali:**
    *   *Fonti:* ISTAT, Agenzia delle Entrate (WMS Catasto), SIT Comune di Salerno.

## 2. Dati Mobilità e Infrastrutture
Fondamentali per l'analisi dei flussi, dei parcheggi e degli spazi pubblici.

*   **Rete Viaria:** Grafo stradale dettagliato (strade principali, svincoli tangenziale, viabilità locale).
    *   *Fonti:* OpenStreetMap.
*   **Trasporto Pubblico Locale (TPL):** Posizione delle fermate autobus e della stazione metropolitana/treno "Arechi", orari e frequenze.
    *   *Fonti:* GTFS (General Transit Feed Specification) di Busitalia Campania, Trenitalia, o estrazione da OSM.
*   **Parcheggi e Aree di Sosta:** Mappatura dei parcheggi esistenti (pubblici, privati, a servizio dello stadio).
    *   *Fonti:* Rilievi sul posto, OSM, documenti del Comune.
*   **Mobilità Dolce (Ciclopedonale):** Percorsi pedonali, piste ciclabili esistenti e in progetto.
    *   *Fonti:* OSM, PUC (Piano Urbanistico Comunale).
*   **Flussi di traffico e capienza Stadio:** Dati quantitativi sui flussi nei giorni di eventi sportivi/concerti vs giorni normali.

## 3. Strumenti Urbanistici e Normativi
Per garantire che la proposta di riqualificazione sia coerente con gli indirizzi generali della città.

*   **PUC (Piano Urbanistico Comunale) di Salerno:** Zonizzazione e destinazioni d'uso attuali per il quadrante Arechi / San Leonardo.
    *   *Fonti:* Sito istituzionale del Comune di Salerno.
*   **Vincoli (Ambientali, Paesaggistici, Idrogeologici):**
    *   *Fonti:* Autorità di Bacino, SIT Regionale.

## 4. Dati Socio-Demografici ed Economici (Opzionale ma consigliato)
Per contestualizzare l'uso degli spazi pubblici al di fuori degli eventi.

*   **Dati ISTAT su sezioni censuarie:** Popolazione residente nelle aree limitrofe.
    *   *Fonti:* Portale dati ISTAT.

---

## Prossimi Passi Consigliati
1.  **Scaricare i dati da OpenStreetMap:** Possiamo scrivere uno script Python (usando la libreria `osmnx`) per scaricare in automatico rete stradale, edifici e servizi dell'area.
2.  **Verificare il Geoportale della Regione Campania** per i dati altimetrici (DTM) e le ortofoto.
3.  **Creare una cartella GIS** all'interno di `data/` per organizzare shapefile e geopackage.
