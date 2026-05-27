import geopandas as gpd
import matplotlib.pyplot as plt
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data", "raw", "osm")
    vis_dir = os.path.join(base_dir, "..", "visualizations")
    os.makedirs(vis_dir, exist_ok=True)

    print("Caricamento dati...")
    try:
        buildings = gpd.read_file(os.path.join(data_dir, "buildings.gpkg"))
        streets = gpd.read_file(os.path.join(data_dir, "streets_drive.gpkg"), layer="edges")
        amenities = gpd.read_file(os.path.join(data_dir, "amenities.gpkg"))
        
        print("\n--- STATISTICHE AREA ARECHI ---")
        print(f"Numero di edifici mappati: {len(buildings)}")
        
        if not streets.empty:
            # Riproiezione nel sistema UTM 33N (EPSG:32633, specifico per la Campania) per calcolare la lunghezza in metri
            streets_metric = streets.to_crs(epsg=32633)
            tot_len_km = streets_metric.length.sum() / 1000
            print(f"Lunghezza totale della rete carrabile: {tot_len_km:.2f} km")

        parkings = amenities[amenities['amenity'].isin(['parking', 'parking_space'])]
        print(f"Numero di aree parcheggio individuate: {len(parkings)}")
        
        bus_stops = amenities[amenities['highway'] == 'bus_stop']
        print(f"Numero di fermate autobus: {len(bus_stops)}")

        print("\nGenerazione mappa...")
        fig, ax = plt.subplots(figsize=(10, 10))
        
        if not streets.empty:
            streets.plot(ax=ax, linewidth=0.8, color='gray', zorder=1, label="Strade")
        if not buildings.empty:
            buildings.plot(ax=ax, color='#2c3e50', alpha=0.8, zorder=2, label="Edifici")
        if not parkings.empty:
            parkings.plot(ax=ax, color='#27ae60', alpha=0.5, zorder=3, label="Parcheggi")
        if not bus_stops.empty:
            bus_stops.plot(ax=ax, color='#e74c3c', markersize=30, zorder=4, label="Fermate Bus")

        plt.title("Arechi Urban Study - Stato di Fatto", fontsize=16)
        # Legenda custom
        import matplotlib.patches as mpatches
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='gray', lw=2, label='Viabilità'),
            mpatches.Patch(color='#2c3e50', label='Edifici'),
            mpatches.Patch(color='#27ae60', alpha=0.5, label='Parcheggi'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#e74c3c', markersize=10, label='Fermate Bus')
        ]
        ax.legend(handles=legend_elements, loc='upper left')
        ax.set_axis_off()
        
        plt.tight_layout()
        output_map = os.path.join(vis_dir, "arechi_base_map.png")
        plt.savefig(output_map, dpi=300, bbox_inches='tight')
        print(f"Mappa salvata con successo in: {output_map}")

    except Exception as e:
        print(f"Errore durante l'analisi: {e}")

if __name__ == "__main__":
    main()
