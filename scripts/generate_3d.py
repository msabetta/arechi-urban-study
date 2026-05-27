import geopandas as gpd
import pandas as pd
import numpy as np
import os
from shapely.geometry import Polygon, MultiPolygon

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    geojson_path = os.path.join(base_dir, "..", "data", "processed", "buildings_3D_ready.geojson")
    out_buildings_dir = os.path.join(base_dir, "..", "models", "buildings")
    out_terrain_dir = os.path.join(base_dir, "..", "models", "terrain")
    os.makedirs(out_buildings_dir, exist_ok=True)
    os.makedirs(out_terrain_dir, exist_ok=True)

    print("Caricamento dei dati degli edifici per la modellazione 3D...")
    if not os.path.exists(geojson_path):
        print(f"File {geojson_path} non trovato. Provo a generarlo con prepare_3d_buildings.py...")
        # Esegui prepare_3d_buildings se necessario
        from prepare_3d_buildings import main as prep_main
        prep_main()

    try:
        gdf = gpd.read_file(geojson_path)
        # Riproiettiamo in UTM 33N (EPSG:32633) per lavorare in metri
        gdf_metric = gdf.to_crs(epsg=32633)
        
        # Filtriamo solo le geometrie di tipo Polygon o MultiPolygon
        gdf_metric = gdf_metric[gdf_metric.geometry.type.isin(['Polygon', 'MultiPolygon'])]
        
        if gdf_metric.empty:
            print("Nessun edificio poligonale trovato.")
            return

        # Calcoliamo il centro dell'area di studio per usarlo come origine locale (0,0,0)
        bounds = gdf_metric.total_bounds # [minx, miny, maxx, maxy]
        center_x = (bounds[0] + bounds[2]) / 2
        center_y = (bounds[1] + bounds[3]) / 2

        print(f"Origine locale impostata a: X={center_x:.2f}, Y={center_y:.2f} (UTM 33N)")

        # Liste per vertici e facce dell'OBJ degli edifici
        vertices = []
        faces = []
        vert_index = 1 # Gli indici dei vertici in OBJ partono da 1

        print("Generazione delle mesh 3D per gli edifici...")
        for idx, row in gdf_metric.iterrows():
            geom = row.geometry
            height = float(row.get('height', 6.0))
            if pd.isna(height) or height <= 0:
                height = 6.0

            # Estraiamo i singoli poligoni
            polygons = []
            if isinstance(geom, Polygon):
                polygons.append(geom)
            elif isinstance(geom, MultiPolygon):
                polygons.extend(geom.geoms)

            for poly in polygons:
                # Coordinate dell'anello esterno (ignoriamo i fori interni per semplicità d'estrusione)
                coords = list(poly.exterior.coords)
                # Di solito l'ultimo punto coincide con il primo, lo rimuoviamo per non duplicare i vertici
                if coords[0] == coords[-1] and len(coords) > 1:
                    coords = coords[:-1]
                
                n = len(coords)
                if n < 3:
                    continue

                # Aggiungiamo i vertici della base (z=0) e del tetto (z=height)
                start_vert = vert_index
                for x, y in coords:
                    local_x = x - center_x
                    local_y = y - center_y
                    # Vertice base
                    vertices.append(f"v {local_x:.4f} {local_y:.4f} 0.0000")
                    # Vertice tetto
                    vertices.append(f"v {local_x:.4f} {local_y:.4f} {height:.4f}")
                    vert_index += 2

                # Creazione delle facce laterali (pareti)
                # Per ogni segmento i -> i+1, creiamo un quadrilatero
                for i in range(n):
                    # Indice dei vertici base e tetto per il punto corrente e successivo
                    v_base_curr = start_vert + 2 * i
                    v_roof_curr = v_base_curr + 1
                    
                    next_i = (i + 1) % n
                    v_base_next = start_vert + 2 * next_i
                    v_roof_next = v_base_next + 1
                    
                    # Faccia laterale (quadrilatero): base_curr -> base_next -> roof_next -> roof_curr
                    faces.append(f"f {v_base_curr} {v_base_next} {v_roof_next} {v_roof_curr}")

                # Faccia base (inversa/verso il basso)
                base_face_indices = [str(start_vert + 2 * i) for i in reversed(range(n))]
                faces.append("f " + " ".join(base_face_indices))

                # Faccia tetto (verso l'alto)
                roof_face_indices = [str(start_vert + 2 * i + 1) for i in range(n)]
                faces.append("f " + " ".join(roof_face_indices))

        # Scrittura del file OBJ degli edifici
        obj_buildings_path = os.path.join(out_buildings_dir, "buildings.obj")
        with open(obj_buildings_path, "w") as f:
            f.write("# Arechi Urban Study - 3D Buildings Model\n")
            f.write(f"# Origine locale: X={center_x:.2f}, Y={center_y:.2f}\n\n")
            f.write("\n".join(vertices) + "\n\n")
            f.write("\n".join(faces) + "\n")
        print(f"Modello 3D degli edifici salvato con successo in:\n{os.path.abspath(obj_buildings_path)}")

        # Generazione di un terreno 3D (un piano mesh con griglia)
        print("Generazione del modello 3D del terreno...")
        terrain_vertices = []
        terrain_faces = []
        
        # Estendiamo il bounding box di 100 metri in tutte le direzioni
        t_minx = bounds[0] - center_x - 100
        t_maxx = bounds[2] - center_x + 100
        t_miny = bounds[1] - center_y - 100
        t_maxy = bounds[3] - center_y + 100

        # Creiamo una griglia 10x10
        grid_res = 10
        xs = np.linspace(t_minx, t_maxx, grid_res)
        ys = np.linspace(t_miny, t_maxy, grid_res)
        
        # Vertici del terreno
        for y in ys:
            for x in xs:
                # Terreno quasi pianeggiante con una lieve ondulazione (sinusoide) per dare realismo
                z = np.sin(x/200.0) * np.cos(y/200.0) * 1.5
                terrain_vertices.append(f"v {x:.4f} {y:.4f} {z:.4f}")

        # Facce del terreno (griglia di quadrilateri)
        for j in range(grid_res - 1):
            for i in range(grid_res - 1):
                # Calcolo indici vertici (1-based)
                v1 = j * grid_res + i + 1
                v2 = j * grid_res + (i + 1) + 1
                v3 = (j + 1) * grid_res + (i + 1) + 1
                v4 = (j + 1) * grid_res + i + 1
                terrain_faces.append(f"f {v1} {v2} {v3} {v4}")

        obj_terrain_path = os.path.join(out_terrain_dir, "terrain.obj")
        with open(obj_terrain_path, "w") as f:
            f.write("# Arechi Urban Study - 3D Terrain Model\n")
            f.write(f"# Origine locale: X={center_x:.2f}, Y={center_y:.2f}\n\n")
            f.write("\n".join(terrain_vertices) + "\n\n")
            f.write("\n".join(terrain_faces) + "\n")
        print(f"Modello 3D del terreno salvato con successo in:\n{os.path.abspath(obj_terrain_path)}")

    except Exception as e:
        print(f"Errore durante la generazione 3D: {e}")

if __name__ == "__main__":
    main()
