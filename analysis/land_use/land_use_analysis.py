import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Risaliamo di due livelli da analysis/land_use/ a arechi-urban-study/
    project_dir = os.path.abspath(os.path.join(base_dir, "..", ".."))
    
    buildings_path = os.path.join(project_dir, "data", "raw", "osm", "buildings.gpkg")
    out_dir = os.path.join(project_dir, "visualizations", "diagrams")
    os.makedirs(out_dir, exist_ok=True)

    print("Caricamento degli edifici per l'analisi della destinazione d'uso...")
    if not os.path.exists(buildings_path):
        print(f"File {buildings_path} non trovato. Attendi il completamento del download.")
        return

    try:
        gdf = gpd.read_file(buildings_path)
        
        # Pulizia e categorizzazione delle destinazioni d'uso
        # Se non c'è la colonna 'building', creiamola con 'yes'
        if 'building' not in gdf.columns:
            gdf['building'] = 'yes'

        # Traduciamo/raggruppiamo per leggibilità
        category_map = {
            'yes': 'Non Specificato (Generico)',
            'hotel': 'Strutture Ricettive',
            'commercial': 'Uffici/Commerciale',
            'retail': 'Commercio al dettaglio',
            'industrial': 'Industriale/Logistica',
            'residential': 'Residenziale',
            'apartments': 'Residenziale (Appartamenti)',
            'house': 'Residenziale (Casa)',
            'church': 'Luogo di Culto',
            'public': 'Edifici Pubblici/Servizi',
            'civic': 'Edifici Pubblici/Servizi',
            'stadium': 'Impianto Sportivo (Stadio)',
            'sports_hall': 'Impianto Sportivo',
            'grandstand': 'Tribuna'
        }

        gdf['destinazione'] = gdf['building'].map(category_map).fillna('Altro/Servizi')

        # Calcoliamo le frequenze
        counts = gdf['destinazione'].value_counts()
        print("\n--- DISTRIBUZIONE DESTINAZIONI D'USO EDIFICI ---")
        for cat, val in counts.items():
            print(f"- {cat}: {val}")

        # Generiamo il grafico a barre orizzontali (estetica premium)
        plt.figure(figsize=(10, 6))
        
        # Colori coordinati e armoniosi
        colors = plt.cm.get_cmap('tab20c')(range(len(counts)))
        
        bars = plt.barh(counts.index[::-1], counts.values[::-1], color=colors, edgecolor='none', height=0.6)
        
        # Miglioramento estetico delle etichette e griglia
        plt.xlabel("Numero di Edifici", fontsize=12, fontweight='bold', color='#2c3e50')
        plt.title("Arechi Urban Study - Destinazioni d'uso dell'edificato", fontsize=14, fontweight='bold', color='#2c3e50', pad=15)
        
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['left'].set_color('#bdc3c7')
        plt.gca().spines['bottom'].set_color('#bdc3c7')
        plt.grid(axis='x', linestyle='--', alpha=0.5)
        
        # Aggiungiamo i valori numerici alla fine delle barre
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 2, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                     va='center', ha='left', fontsize=10, color='#34495e', fontweight='bold')

        plt.tight_layout()
        output_file = os.path.join(out_dir, "land_use_chart.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\nGrafico delle destinazioni d'uso salvato in: {output_file}")

    except Exception as e:
        print(f"Errore durante l'analisi delle destinazioni d'uso: {e}")

if __name__ == "__main__":
    main()
