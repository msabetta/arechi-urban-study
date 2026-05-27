import geopandas as gpd
import shapely
import os
import pandas as pd

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data", "raw", "osm")
    out_dir = os.path.join(base_dir, "..", "data", "processed")
    os.makedirs(out_dir, exist_ok=True)

    print("Caricamento dei file GIS per l'elaborazione...")
    try:
        buildings_path = os.path.join(data_dir, "buildings.gpkg")
        amenities_path = os.path.join(data_dir, "amenities.gpkg")
        
        if not os.path.exists(buildings_path) or not os.path.exists(amenities_path):
            print("I file raw GPKG non sono presenti in data/raw/osm. Esegui prima scripts/download_osm.py.")
            return

        buildings = gpd.read_file(buildings_path)
        amenities = gpd.read_file(amenities_path)

        # Riproiettiamo in metrico EPSG:32633 (Campania UTM 33N)
        buildings_m = buildings.to_crs(epsg=32633)
        amenities_m = amenities.to_crs(epsg=32633)

        # 1. Identificazione dello Stadio Arechi
        stadium = None
        # Ricerca per nome
        name_cols = [c for c in buildings_m.columns if 'name' in c]
        for col in name_cols:
            matches = buildings_m[buildings_m[col].astype(str).str.contains("Arechi|Stadio", case=False, na=False)]
            if not matches.empty:
                stadium = matches.iloc[0]
                print(f"Stadio Arechi individuato tramite colonna '{col}': {stadium.get('name', 'Senza Nome')}")
                break

        # Se non trovato tramite nome, prendiamo l'edificio con l'area più grande (che nello studio è sicuramente lo stadio)
        if stadium is None:
            buildings_m['area'] = buildings_m.geometry.area
            stadium = buildings_m.sort_values(by='area', ascending=False).iloc[0]
            print(f"Stadio Arechi individuato come edificio con area maggiore: {stadium.geometry.area:.1f} mq")

        stadium_geom = stadium.geometry
        stadium_centroid = stadium_geom.centroid

        # 2. Generazione Buffer di Rispetto/Accessibilità dello Stadio
        # Creiamo anelli di buffer di 200m, 500m e 800m
        buffer_distances = [200, 500, 800]
        buffers_list = []
        for dist in buffer_distances:
            buf_geom = stadium_centroid.buffer(dist)
            buffers_list.append({
                'distance': f"{dist}m",
                'dist_val': dist,
                'geometry': buf_geom
            })
        
        buffers_gdf = gpd.GeoDataFrame(buffers_list, crs="EPSG:32633")
        # Riconvertiamo in WGS84 per l'esportazione GeoJSON standard
        buffers_gdf_wgs = buffers_gdf.to_crs(epsg=4326)
        
        buffers_out = os.path.join(out_dir, "stadium_buffers.geojson")
        buffers_gdf_wgs.to_file(buffers_out, driver="GeoJSON")
        print(f"Buffer dello stadio salvati in: {buffers_out}")

        # 3. Elaborazione dei parcheggi
        # Filtriamo le aree adibite a parcheggio
        parkings = amenities_m[amenities_m['amenity'].isin(['parking', 'parking_space'])]
        if not parkings.empty:
            # Calcolo dell'area di ciascun parcheggio in mq
            parkings = parkings.copy()
            parkings['area_mq'] = parkings.geometry.area
            # Distanza dal centro dello stadio in metri
            parkings['distance_to_stadium'] = parkings.geometry.centroid.distance(stadium_centroid)
            
            # Stima posti auto (ipotizzando in media 25 mq a posto auto incluse corsie di manovra)
            parkings['estimated_capacity'] = (parkings['area_mq'] / 25.0).astype(int)

            # Riconvertiamo in WGS84 ed esportiamo
            parkings_wgs = parkings.to_crs(epsg=4326)
            # Rimuoviamo colonne con liste che danno errore in esportazione
            for col in parkings_wgs.columns:
                if parkings_wgs[col].apply(lambda x: isinstance(x, list)).any():
                    parkings_wgs[col] = parkings_wgs[col].apply(lambda x: str(x) if isinstance(x, list) else x)

            parking_out = os.path.join(out_dir, "parking_processed.geojson")
            parkings_wgs.to_file(parking_out, driver="GeoJSON")
            print(f"Parcheggi elaborati salvati in: {parking_out}")
            print(f"Capacità totale stimata dei parcheggi mappati: {parkings['estimated_capacity'].sum()} posti auto.")
        else:
            print("Nessun parcheggio trovato da elaborare.")

    except Exception as e:
        print(f"Errore durante l'elaborazione GIS: {e}")

if __name__ == "__main__":
    main()
