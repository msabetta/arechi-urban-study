import osmnx as ox
import geopandas as gpd
import os
import warnings

warnings.filterwarnings('ignore')

def prepare_for_gpkg(gdf):
    """
    I file GeoPackage (GPKG) non supportano colonne con liste. 
    Questa funzione converte eventuali liste in stringhe.
    """
    for col in gdf.columns:
        if gdf[col].apply(lambda x: isinstance(x, list)).any():
            gdf[col] = gdf[col].apply(lambda x: str(x) if isinstance(x, list) else x)
    return gdf

def main():
    # Coordinate centrate sullo Stadio Arechi e Piazzale Gipo Viani
    center_point = (40.6278, 14.8297) 
    # Raggio di ricerca in metri (1.2 km copre abbondantemente piazzale, stazione e svincoli)
    dist = 1200 

    # Creiamo la cartella di output
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw", "osm")
    os.makedirs(output_dir, exist_ok=True)

    print("1/3 Scaricamento della rete stradale (drive & walk)...")
    try:
        G_drive = ox.graph_from_point(center_point, dist=dist, network_type='drive')
        ox.save_graph_geopackage(G_drive, filepath=os.path.join(output_dir, "streets_drive.gpkg"))
        print("  -> Rete carrabile salvata.")
        
        G_walk = ox.graph_from_point(center_point, dist=dist, network_type='walk')
        ox.save_graph_geopackage(G_walk, filepath=os.path.join(output_dir, "streets_walk.gpkg"))
        print("  -> Rete pedonale salvata.")
    except Exception as e:
        print(f"Errore nello scaricamento della rete stradale: {e}")

    print("\n2/3 Scaricamento dei footprint degli edifici...")
    try:
        tags_buildings = {"building": True}
        buildings = ox.features_from_point(center_point, tags_buildings, dist=dist)
        buildings = prepare_for_gpkg(buildings)
        buildings.to_file(os.path.join(output_dir, "buildings.gpkg"), driver="GPKG")
        print("  -> Edifici salvati.")
    except Exception as e:
        print(f"Errore nello scaricamento degli edifici: {e}")

    print("\n3/3 Scaricamento parcheggi e nodi di trasporto pubblico...")
    try:
        tags_amenities = {
            "amenity": ["parking", "parking_space"],
            "public_transport": ["stop_position", "platform", "station"],
            "highway": ["bus_stop"]
        }
        amenities = ox.features_from_point(center_point, tags_amenities, dist=dist)
        amenities = prepare_for_gpkg(amenities)
        amenities.to_file(os.path.join(output_dir, "amenities.gpkg"), driver="GPKG")
        print("  -> Parcheggi e servizi salvati.")
    except Exception as e:
        print(f"Errore nello scaricamento dei servizi: {e}")

    print(f"\nOperazione completata! I file .gpkg sono in:\n{os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
