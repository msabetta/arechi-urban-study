import geopandas as gpd
import pandas as pd
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data", "raw", "osm")
    out_dir = os.path.join(base_dir, "..", "data", "processed")
    os.makedirs(out_dir, exist_ok=True)

    print("Preparazione dati 3D...")
    try:
        buildings = gpd.read_file(os.path.join(data_dir, "buildings.gpkg"))
        
        # Gestione dell'altezza. Se la colonna 'height' non esiste, la creiamo.
        if 'height' not in buildings.columns:
            buildings['height'] = None
            
        # Se c'è il numero di piani (building:levels), lo convertiamo in altezza (1 piano = 3m)
        if 'building:levels' in buildings.columns:
            levels = pd.to_numeric(buildings['building:levels'], errors='coerce')
            buildings.loc[buildings['height'].isna() & levels.notna(), 'height'] = levels * 3.0
            
        # Per tutti gli altri edifici dove non c'è l'altezza, assegniamo 6 metri (due piani) di default
        buildings['height'] = pd.to_numeric(buildings['height'], errors='coerce')
        buildings['height'] = buildings['height'].fillna(6.0)

        # Salviamo il file in GeoJSON, perfetto per BlenderGIS o per web (three.js)
        out_file = os.path.join(out_dir, "buildings_3D_ready.geojson")
        buildings.to_file(out_file, driver='GeoJSON')
        
        print(f"File per la modellazione 3D pronto in:\n{os.path.abspath(out_file)}")
        print("Il file contiene le impronte con un'altezza stimata per l'estrusione.")

    except Exception as e:
        print(f"Errore durante la preparazione 3D: {e}")

if __name__ == "__main__":
    main()
