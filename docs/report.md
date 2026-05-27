# Report Finale: Arechi Urban Study

*Studio di inquadramento territoriale, analisi spaziali e proposta di rigenerazione urbana per il Piazzale Gipo Viani e lo Stadio Arechi (Salerno)*

---

## 1. Introduzione
Il presente documento raccoglie le analisi quantitative e le proposte progettuali per la riqualificazione urbanistica e infrastrutturale dell'area del **Piazzale Gipo Viani** e dello **Stadio Arechi** a Salerno. L'obiettivo è trasformare questo importante nodo urbano da "vuoto" cementificato e isola di calore a un polo attrattivo, sostenibile ed energetico attivo tutto l'anno.

---

## 2. Acquisizione Dati e Inquadramento
I dati vettoriali geospaziali sono stati estratti da **OpenStreetMap (OSM)**, utilizzando la libreria `OSMnx`, centrandosi sulle coordinate dello Stadio Arechi `(40.6278, 14.8297)` con un raggio di 1.200 metri per comprendere gli svincoli autostradali, la stazione metropolitana ed il vicino litorale.

I layer acquisiti comprendono:
*   **Edificato:** 386 poligoni corrispondenti alle impronte a terra degli edifici.
*   **Viabilità:** Rete carrabile (drive) e rete pedonale (walk) modellate come grafi stradali.
*   **Servizi e Infrastrutture:** Aree di sosta (parcheggi) e fermate del trasporto pubblico (autobus e metropolitana).

### Inquadramento dello Stato di Fatto
L'analisi automatizzata dei dati geospaziali ha rilevato le seguenti metriche di base per l'area:
*   **Lunghezza della rete stradale carrabile:** ~26.00 km.
*   **Numero di edifici censiti:** 386 impronte.
*   **Numero di aree destinate a parcheggio:** 74 aree di sosta.

![Mappa Stato di Fatto](../visualizations/arechi_base_map.png)
*Figura 1: Mappa dello Stato di Fatto con l'inquadramento di viabilità, edifici e parcheggi nell'area d'indagine.*

---

## 3. Analisi del Territorio

### A. Destinazioni d'Uso (Land Use)
La classificazione degli edifici estratti evidenzia una forte presenza di edilizia residenziale e industriale/logistica (zona artigianale e industriale adiacente allo stadio), oltre alla presenza monumentale dello Stadio Arechi (classificato come Impianto Sportivo).
La maggior parte degli edifici di contorno presenta un uso non specificato nei dati OSM, ma lo studio evidenzia una chiara vocazione mista e di servizi per il quadrante est.

![Grafico Land Use](../visualizations/diagrams/land_use_chart.png)
*Figura 2: Ripartizione delle destinazioni d'uso dell'edificato censito.*

### B. Accessibilità e Isocrone della Sosta
L'analisi di prossimità stradale ha valutato la distanza pedonale dei parcheggi rispetto all'ingresso dello stadio.
*   **Fascia 0-200m (Alta accessibilità):** Parcheggi immediatamente adiacenti allo stadio.
*   **Fascia 200-500m (Media accessibilità):** 2 parcheggi con una capacità stimata di **369 posti auto**.
*   **Fascia 500-800m (Bassa accessibilità):** Parcheggi più esterni, utili per lo smistamento del traffico nei grandi eventi.
La capacità di sosta complessiva censita nell'area di studio è stimata in oltre **670 posti auto** standard (senza contare le aree sterrate non mappate come parcheggi ufficiali), che coprono ampiamente la domanda ordinaria ma creano un enorme impatto visivo e ambientale.

![Mappa Accessibilità](../visualizations/maps/accessibility_map.png)
*Figura 3: Carta delle isocrone di accessibilità pedonale alle aree di sosta dallo Stadio.*

### C. Simulazione dei Flussi Pedonali (Metro -> Stadio)
Tramite l'analisi di camminabilità lungo il grafo stradale, abbiamo simulato il flusso di 10.000 spettatori in uscita dalla **Stazione Metropolitana Arechi** verso i 4 varchi d'accesso principali dello stadio.
I risultati identificano un forte carico pedonale sul viale diagonale di connessione, evidenziando la necessità di creare un corridoio pedonale sicuro, protetto e adeguatamente dimensionato per evitare congestionamenti e interferenze con i veicoli in manovra nei parcheggi.

![Mappa Flussi Pedonali](../visualizations/maps/pedestrian_flow_map.png)
*Figura 4: Simulazione del carico sui rami della rete pedonale durante l'afflusso degli spettatori.*

### D. Simulazione Microclimatica e Comfort Termico
Piazzale Gipo Viani, essendo interamente asfaltato e privo di alberature, agisce come una forte isola di calore urbana (UHI). Durante il pomeriggio estivo, le temperature superficiali stimate dell'asfalto raggiungono i **42°C - 48°C**.
La modellazione del concept progettuale (introduzione di pensiline fotovoltaiche e alberature) riduce la radiazione solare diretta incidente e abbassa le temperature superficiali a valori confortevoli di **26°C - 34°C**, migliorando drasticamente la vivibilità dello spazio pubblico.

![Mappa Comfort Termico](../visualizations/maps/comfort_map.png)
*Figura 5: Analisi comparativa delle temperature superficiali stimate: Stato di Fatto vs Progetto Riqualificato.*

---

## 4. Modellazione 3D (Digital Twin)
Per la costruzione del Digital Twin dell'area, i dati degli edifici sono stati riproiettati nel sistema metrico **EPSG:32633** (UTM 33N) e georeferenziati rispetto a un'origine locale `X=486126.12, Y=4497774.89` in metri.
*   **Edifici:** Le impronte 2D sono state estruse in 3D in base al numero di piani (`building:levels` × 3.0 metri) o assegnando un'altezza di default di 6.0 metri (circa 2 piani) per le altezze non censite. Il file finale è memorizzato in `models/buildings/buildings.obj`.
*   **Terreno:** È stata creata una mesh a maglia regolare (griglia 10x10) con una lieve ondulazione matematica per simulare il piano di posa altimetrico, memorizzata in `models/terrain/terrain.obj`.

---

## 5. Proposta di Riqualificazione Urbana
La proposta progettuale si articola su tre interventi principali:
1.  **Solar Carports (Pensiline Fotovoltaiche):** Copertura degli stalli di sosta del Piazzale Viani con pensiline fotovoltaiche per la produzione di energia pulita (CER - Comunità Energetica Rinnovabile) e l'ombreggiamento delle auto.
2.  **Parco dello Sport e Tempo Libero:** Conversione di porzioni di asfalto in aree verdi drenanti, campi da gioco multidisciplinari e chioschi per attività ricreative giornaliere.
3.  **Green Corridor:** Un viale ciclopedonale alberato, attrezzato e ombreggiato, per connettere in sicurezza la stazione della metropolitana con l'impianto sportivo.

![Render Concettuale Progetto](../visualizations/renders/arechi_concept_render.png)
*Figura 6: Render fotorealistico concettuale del Piazzale Gipo Viani rigenerato, con pensiline solari moderne, aree verdi e percorsi pedonali.*
