# Report: Arechi Urban Study

## 1. Introduzione
Il presente documento raccoglie le analisi e le proposte per la riqualificazione urbana dell'area del Piazzale Gipo Viani e dello Stadio Arechi a Salerno.

## 2. Acquisizione Dati
I dati vettoriali di base sono stati estratti da OpenStreetMap, includendo:
- Rete stradale carrabile e pedonale
- Impronte 2D degli edifici circostanti
- Nodi di trasporto pubblico e aree destinate a parcheggio

## 3. Analisi dello Stato di Fatto
*L'analisi dei dati OSM fornisce metriche iniziali importanti sulla conformazione dell'area:*
- **Viabilità e Parcheggi:** Il perimetro d'indagine comprende circa **26 km di rete stradale carrabile**. Sono state individuate **74 aree destinate a parcheggio** (fondamentali per la gestione degli eventi sportivi) e **5 fermate per i mezzi pubblici** principali.
- **Edificato:** Nell'area sono presenti **386 impronte di edifici** censite.

*(Aggiungere la mappa in `visualizations/arechi_base_map.png` appena generata)*

## 4. Modellazione 3D
Per la costruzione del Digital Twin dell'area, i dati degli edifici OSM sono stati pre-processati. Le volumetrie mancanti dell'altezza sono state stimate assegnando un valore di default di 6 metri (circa 2 piani) oppure convertendo il numero di piani in altezza effettiva (1 piano = 3 metri). Il risultato è un file GeoJSON pronto per l'estrusione.

## 5. Proposte di Riqualificazione
*(Sezione da sviluppare a seguito delle analisi)*
