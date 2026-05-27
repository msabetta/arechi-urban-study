import sys
import os

# Aggiunge il percorso dello script corrente al path per l'importazione
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from download_osm_data import main as download_main

if __name__ == "__main__":
    print("Avvio del download dei dati OpenStreetMap per l'area Arechi...")
    download_main()
