import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import networkx as nx
from shapely.geometry import Point

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(base_dir, "..", ".."))
    
    walk_gpkg = os.path.join(project_dir, "data", "raw", "osm", "streets_walk.gpkg")
    out_dir = os.path.join(project_dir, "visualizations", "maps")
    os.makedirs(out_dir, exist_ok=True)

    print("Inizializzazione simulazione dei flussi pedonali...")
    if not os.path.exists(walk_gpkg):
        print(f"File {walk_gpkg} non trovato. Attendi il download.")
        return

    try:
        # Carichiamo i nodi e gli archi della rete pedonale
        nodes = gpd.read_file(walk_gpkg, layer="nodes")
        edges = gpd.read_file(walk_gpkg, layer="edges")
        
        # Impostiamo osmid come indice nei nodi per un veloce lookup
        if 'osmid' in nodes.columns:
            nodes = nodes.set_index('osmid')
        else:
            # Se osmid non è presente, usiamo la colonna indice
            nodes['osmid'] = nodes.index
            nodes = nodes.set_index('osmid')

        # Costruiamo il grafo NetworkX
        print("Costruzione del grafo pedonale...")
        G = nx.Graph()
        for idx, row in edges.iterrows():
            u = row['u']
            v = row['v']
            length = float(row.get('length', 10.0))
            # Memorizziamo geometria e peso
            G.add_edge(u, v, weight=length, geometry=row.geometry, flow=0.0)

        # Definiamo la sorgente principale (Stazione Metro Arechi)
        # Coordinate approssimative: Lat 40.6318, Lon 14.8297
        metro_coords = Point(14.8297, 40.6318)
        # Troviamo il nodo più vicino alla stazione metro
        # Riproiettiamo temporaneamente i nodi in metrico per calcolare la distanza corretta
        nodes_m = nodes.to_crs(epsg=32633)
        metro_pt_m = gpd.GeoSeries([metro_coords], crs="EPSG:4326").to_crs(epsg=32633).iloc[0]
        
        distances_to_metro = nodes_m.geometry.distance(metro_pt_m)
        source_node_id = distances_to_metro.idxmin()
        print(f"Nodo sorgente (Stazione Metro) individuato con ID: {source_node_id}")

        # Definiamo i nodi di destinazione (Varchi dello Stadio)
        # Troviamo i nodi vicino al perimetro dello stadio
        stadium_center = Point(14.8297, 40.6278)
        stadium_pt_m = gpd.GeoSeries([stadium_center], crs="EPSG:4326").to_crs(epsg=32633).iloc[0]
        
        # Selezioniamo 4 nodi distribuiti intorno allo stadio (es. Nord, Sud, Est, Ovest)
        # come i 4 varchi d'accesso principali dello stadio
        distances_to_stadium = nodes_m.geometry.distance(stadium_pt_m)
        # Selezioniamo i nodi che sono a circa 100-180 metri dal centro dello stadio
        stadium_perimeter_nodes = nodes_m[(distances_to_stadium >= 100) & (distances_to_stadium <= 220)]
        
        if stadium_perimeter_nodes.empty:
            # Fallback ai nodi più vicini in assoluto
            target_node_ids = list(distances_to_stadium.nsmallest(4).index)
        else:
            # Scegliamo 4 varchi sparsi
            target_node_ids = list(stadium_perimeter_nodes.sample(min(4, len(stadium_perimeter_nodes)), random_state=42).index)
            
        print(f"Nodi destinazione (Varchi Stadio) individuati: {target_node_ids}")

        # Eseguiamo la simulazione di flusso: instradiamo 10.000 pedoni
        # che escono dalla metropolitana e si dirigono uniformemente verso i varchi dello stadio
        total_pedestrians = 10000
        pedestrians_per_gate = total_pedestrians / len(target_node_ids)

        flow_dict = {(u, v): 0.0 for u, v in G.edges()}

        print("Calcolo dei percorsi minimi e simulazione del carico pedonale...")
        for target_node in target_node_ids:
            try:
                # Calcolo del percorso più breve lungo la rete stradale
                path = nx.shortest_path(G, source=source_node_id, target=target_node, weight='weight')
                # Assegniamo il flusso agli archi del percorso
                for i in range(len(path) - 1):
                    edge = (path[i], path[i+1])
                    if edge in flow_dict:
                        flow_dict[edge] += pedestrians_per_gate
                    else:
                        flow_dict[(path[i+1], path[i])] += pedestrians_per_gate
            except nx.NetworkXNoPath:
                print(f"Nessun percorso trovato tra la metro e il varco {target_node}")

        # Assegniamo i flussi calcolati al GeoDataFrame degli archi
        edges['flow'] = 0.0
        for idx, row in edges.iterrows():
            u = row['u']
            v = row['v']
            edges.at[idx, 'flow'] = flow_dict.get((u, v), flow_dict.get((v, u), 0.0))

        # Generazione della mappa dei flussi pedonali
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Disegniamo tutti i percorsi pedonali in grigio chiaro di sfondo
        edges.plot(ax=ax, color='#e0e0e0', linewidth=1.5, zorder=1)
        
        # Disegniamo i percorsi attivi con larghezza e colore proporzionale al flusso
        active_edges = edges[edges['flow'] > 0]
        if not active_edges.empty:
            # Normalizziamo il flusso per la visualizzazione dello spessore
            max_flow = active_edges['flow'].max()
            linewidths = 1.5 + (active_edges['flow'] / max_flow) * 6.0
            
            active_edges.plot(
                ax=ax, 
                column='flow', 
                cmap='YlOrRd', 
                linewidth=linewidths, 
                legend=True,
                legend_kwds={'label': 'Flusso Pedoni Stimato (Uscita Metro -> Stadio)', 'orientation': 'horizontal', 'pad': 0.05},
                zorder=2
            )

        # Evidenziamo Sorgente e Destinazioni
        metro_node_geom = nodes.loc[[source_node_id]].geometry
        stadium_nodes_geom = nodes.loc[target_node_ids].geometry
        
        metro_node_geom.plot(ax=ax, color='#2980b9', markersize=150, marker='s', label='Metro Stazione Arechi', zorder=3)
        stadium_nodes_geom.plot(ax=ax, color='#27ae60', markersize=120, marker='o', label='Varchi Accesso Stadio', zorder=3)

        plt.title("Arechi Urban Study - Simulazione dei Flussi Pedonali", fontsize=15, fontweight='bold', color='#2c3e50', pad=15)
        ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#bdc3c7')
        ax.set_axis_off()

        plt.tight_layout()
        output_map = os.path.join(out_dir, "pedestrian_flow_map.png")
        plt.savefig(output_map, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Simulazione pedonale completata con successo! Mappa dei flussi salvata in:\n{output_map}")

    except Exception as e:
        print(f"Errore nella simulazione dei flussi pedonali: {e}")

if __name__ == "__main__":
    main()
