# Data Acquisition Plan – Arechi Urban Study

To carry out the 3‑D modelling and the analyses planned for the Gipo Viani Square and Arechi Stadium area, a range of data layers must be collected. Below is a structured list of the  required data and potential sources.

## 1. Cartographic and Geospatial Data (GIS & 3D)
These datasets form the backbone for 3‑D modelling and territorial framing.

- **High‑resolution ortho‑photos:** Updated aerial images of the site.
  - *Sources:* National Geoportal, Google Earth (for visual reference), Regione Campania.
  - *Link:* https://dati.comune.salerno.it/dataset/ortofoto
- **Digital Elevation Models (DTM / DSM):** Altimetric data to model terrain and existing building heights.
  - *Sources:* Regione Campania Geoportal, Open Topography.
  - *Link:* https://dati.comune.salerno.it/dataset/modello-digitale-del-terreno
- **Building footprints:** 2‑D polygons of existing buildings for extrusion to 3‑D.
  - *Sources:* OpenStreetMap (OSM), regional/municipal topographic databases.
  - *Link:* https://dati.comune.salerno.it/dataset/edifici
- **Administrative and cadastral limits:** Boundaries for the study area.
  - *Sources:* ISTAT, Agenzia delle Entrate (WMS Catasto), SIT Comune di Salerno.
  - *Link:* https://dati.comune.salerno.it/dataset/vincoli

## 2. Mobility and Infrastructure Data

Essential for analysing flows, parking, and public spaces.

- **Road network:** Detailed street graph (major roads, highway connections, local streets).
  - *Source:* OpenStreetMap.
- **Public transport (TPL):** Locations of bus stops and the Arechi metro/train station, timetable and frequency information.
  - *Sources:* GTFS feeds from Busitalia Campania, Trenitalia, or OSM extraction.
- **Parking and stopping areas:** Mapping of existing public, private, and stadium‑related parking.
  - *Sources:* On‑site surveys, OSM, municipal documents.
- **Active mobility (pedestrian & cycling):** Existing and planned walking routes, bike lanes.
  - *Sources:* OSM, PUC (Piano Urbanistico Comunale).
- **Traffic flows & stadium capacity:** Quantitative data on vehicle and pedestrian flows during event days versus normal days.

## 3. Urban Planning and Regulatory Tools

To ensure the redesign aligns with city‑wide guidelines.

- **PUC (Piano Urbanistico Comunale) of Salerno:** Zoning and current land‑use designations for the Arechi / San Leonardo sector.
  - *Source:* Official Salerno municipality website.
  - *Link:* https://dati.comune.salerno.it/dataset/puc-piano-urbanistico-comunale-approvato-con-delibera-di-giunta-regionale-n-254-del-19-maggio-2014
- **Constraints (environmental, landscape, hydro‑geological):**
  - *Sources:* Basin Authority, Regional SIT.
  - *Link:* https://dati.comune.salerno.it/dataset/vincoli
  
## 4. Socio‑Demographic and Economic Data (Optional but Recommended)

Provides context for public‑space usage outside event periods.

- **ISTAT census sections:** Resident population data for adjacent neighborhoods.
  - *Source:* ISTAT data portal.
  - *Link:* https://dati.istat.it/Index.aspx?DataSetCode=DCIS_POPRES1
  - *Data:*
    - Population by age and sex
    - Population density
    - Total population
    - Population by marital status
---

## Recommended Next Steps

1. **Download OSM data:** Write a Python script (using `osmnx`) to automatically retrieve the street network, building footprints, and amenities for the target area.
2. **Verify regional Geoportal datasets:** Obtain DTM/DSM and ortho‑photos from the Regione Campania Geoportal.
3. **Create a GIS folder:** Inside `data/`, set up subfolders for shapefiles and GeoPackages to keep the acquired data organised.
4. **Create a simulation folder:** Inside `data/`, set up subfolders for simulation data (e.g., `sim_inputs`, `sim_outputs`).
5. **Create a documentation folder:** Inside `docs/`, set up subfolders for documentation (e.g., `technical_specs`, `user_guides`).
6. **Create a scripts folder:** Inside `scripts/`, set up subfolders for scripts (e.g., `preprocessing`, `simulation`).
7. **Create a results folder:** Inside `results/`, set up subfolders for results (e.g., `figures`, `tables`).