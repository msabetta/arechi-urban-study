import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
from shapely.geometry import Point


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(base_dir, "..", ".."))
    
    parking_path = os.path.join(project_dir, "data", "processed", "parking_processed.geojson")
    buffers_path = os.path.join(project_dir, "data", "processed", "stadium_buffers.geojson")
    streets_path = os.path.join(project_dir, "data", "raw", "osm", "streets_drive.gpkg")
    out_dir = os.path.join(project_dir, "visualizations", "maps")
    os.makedirs(out_dir, exist_ok=True)

    print("Analisi dell'accessibilità e della mobilità dell'area Stadio...")
    if not os.path.exists(parking_path) or not os.path.exists(buffers_path):
        print("I file di input elaborati non sono presenti. Assicurati di aver eseguito scripts/process_gis.py.")
        return

    try:
        # Carichiamo i file necessari
        parkings = gpd.read_file(parking_path)
        buffers = gpd.read_file(buffers_path)
        streets = gpd.read_file(streets_path, layer="edges")

        # Riproiettiamo tutto nel sistema metrico per i calcoli spaziali
        parkings_m = parkings.to_crs(epsg=32633)
        buffers_m = buffers.to_crs(epsg=32633)
        streets_m = streets.to_crs(epsg=32633)

        # Calcolo statistiche parcheggi all'interno di ciascun anello
        # Gli anelli sono: 200m, 500m, 800m
        # Possiamo calcolare quanti posti auto rientrano in ciascuna fascia
        
        # Ordiniamo i buffer per raggio crescente
        buffers_m = buffers_m.sort_values(by='dist_val')
        
        print("\n--- CAPACITÀ DI SOSTA PER FASCIA DI DISTANZA DALLO STADIO ---")
        cumulative_capacity = 0
        cumulative_parkings = 0
        
        last_geom = None
        for idx, row in buffers_m.iterrows():
            geom = row.geometry
            dist_name = row['distance']
            
            # Selezioniamo i parcheggi all'interno di questo buffer
            if last_geom is None:
                # Per il primo buffer (200m)
                in_buffer = parkings_m[parkings_m.geometry.centroid.within(geom)]
            else:
                # Per i successivi, facciamo la differenza rispetto al buffer precedente
                in_buffer = parkings_m[parkings_m.geometry.centroid.within(geom) & ~parkings_m.geometry.centroid.within(last_geom)]
                
            num_park = len(in_buffer)
            cap_est = in_buffer['estimated_capacity'].sum()
            cumulative_capacity += cap_est
            cumulative_parkings += num_park
            
            print(f"Fascia {dist_name}: {num_park} parcheggi, {cap_est} posti auto stimati.")
            last_geom = geom
            
        print(f"Totale complessivo entro 800m: {cumulative_parkings} parcheggi con {cumulative_capacity} posti auto.")

        # GENERAZIONE DELLA CARTA DI ACCESSIBILITÀ
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Disegniamo la rete stradale di sfondo
        streets_m.plot(ax=ax, color='#eef2f3', linewidth=1.0, zorder=1)

        # Disegniamo le fasce di accessibilità (buffer) con trasparenza
        # Usiamo colori coordinati (dal verde per vicino al rosso per lontano)
        buffer_colors = {
            '200m': '#2ecc71', # vicino - verde
            '500m': '#f1c40f', # intermedio - giallo
            '800m': '#e67e22'  # lontano - arancione
        }
        
        for idx, row in buffers_m.sort_values(by='dist_val', ascending=False).iterrows():
            gpd.GeoSeries([row.geometry]).plot(
                ax=ax, 
                color=buffer_colors.get(row['distance'], 'blue'), 
                alpha=0.2, 
                edgecolor=buffer_colors.get(row['distance'], 'blue'), 
                linewidth=1.5,
                zorder=2,
                label=f"Isocrona {row['distance']}"
            )

        # Disegniamo i parcheggi evidenziandone la capacità con la dimensione del cerchio
        # Troviamo il centro di ciascun parcheggio
        parkings_centroids = parkings_m.copy()
        parkings_centroids.geometry = parkings_centroids.geometry.centroid
        
        # Scala delle dimensioni in base alla capacità stimata
        sizes = 20 + (parkings_centroids['estimated_capacity'] / parkings_centroids['estimated_capacity'].max()) * 300
        parkings_centroids.plot(
            ax=ax, 
            color='#2c3e50', 
            markersize=sizes, 
            alpha=0.85, 
            edgecolor='#ffffff', 
            linewidth=1.0,
            zorder=3,
            label='Aree di Sosta'
        )

        # Evidenziamo il centro dello Stadio
        # Troviamo il centro dell'area di studio (punto centrale dei buffer)
        stadium_center_pt = buffers_m.iloc[0].geometry.centroid
        gpd.GeoSeries([stadium_center_pt]).plot(
            ax=ax, 
            color='#e74c3c', 
            markersize=250, 
            marker='*', 
            edgecolor='yellow', 
            linewidth=1.5, 
            zorder=4,
            label='Stadio Arechi (Centro)'
        )

        # Legenda personalizzata
        import matplotlib.patches as mpatches
        from matplotlib.lines import Line2D
        legend_elements = [
            mpatches.Patch(color='#2ecc71', alpha=0.3, label='Fascia Pedonale Alta (0-200m)'),
            mpatches.Patch(color='#f1c40f', alpha=0.3, label='Fascia Pedonale Media (200-500m)'),
            mpatches.Patch(color='#e67e22', alpha=0.3, label='Fascia Pedonale Bassa (500-800m)'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#2c3e50', markersize=10, markeredgecolor='white', label='Parcheggi (Area prop. a posti auto)'),
            Line2D([0], [0], marker='*', color='w', markerfacecolor='#e74c3c', markeredgecolor='yellow', markersize=15, label='Stadio Arechi (Centro)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True, facecolor='white', edgecolor='#bdc3c7')
        
        plt.title("Arechi Urban Study - Isocrone e Accessibilità Aree di Sosta", fontsize=15, fontweight='bold', color='#2c3e50', pad=15)
        ax.set_axis_off()
        
        plt.tight_layout()
        output_map = os.path.join(out_dir, "accessibility_map.png")
        plt.savefig(output_map, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Mappa di accessibilità salvata con successo in:\n{output_map}")

    except Exception as e:
        print(f"Errore durante l'analisi della mobilità: {e}")

if __name__ == "__main__":
    main()
