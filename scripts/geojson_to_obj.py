# file: scripts/geojson_to_obj.py
import json
import pathlib
import sys

from shapely.geometry import shape, mapping
from shapely.ops import transform
import pyproj

def convert_geojson_to_obj(geojson_path: str, out_obj: str):
    # Carica GeoJSON
    with open(geojson_path, encoding="utf-8") as f:
        gj = json.load(f)

    features = gj["features"]
    # Costruisci mesh OBJ
    obj_lines = ["# OBJ generated from buildings_3D_ready.geojson"]
    vert_idx = 1

    for feat in features:
        geom = shape(feat["geometry"])
        # Proiezione geografica (lon/lat) → metri per estrusione
        proj = pyproj.Transformer.from_crs(
            "EPSG:4326", "EPSG:3857", always_xy=True
        ).transform
        geom_m = transform(proj, geom)

        # Estrai altezza (metri); default 5 se mancante
        height = feat["properties"].get("height", 5.0)

        # Poligono base → vertici 2D
        if geom_m.geom_type != "Polygon":
            continue
        exterior = list(geom_m.exterior.coords)

        # Scrivi vertici (z = 0)
        for x, y in exterior:
            obj_lines.append(f"v {x:.3f} {y:.3f} 0.0")
        # Vertici superiori (z = height)
        for x, y in exterior:
            obj_lines.append(f"v {x:.3f} {y:.3f} {height:.3f}")

        n = len(exterior)
        # Facce laterali
        for i in range(n):
            a = vert_idx + i
            b = vert_idx + (i + 1) % n
            a_top = a + n
            b_top = b + n
            obj_lines.append(f"f {a} {b} {b_top} {a_top}")

        # Faccia superiore (reverse order per normale verso l’alto)
        top_face = " ".join(str(vert_idx + n + i) for i in range(n - 1, -1, -1))
        obj_lines.append(f"f {top_face}")

        vert_idx += 2 * n

    pathlib.Path(out_obj).write_text("\n".join(obj_lines), encoding="utf-8")
    print(f"OBJ scritto in {out_obj}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python geojson_to_obj.py <input.geojson> <output.obj>")
        sys.exit(1)
    convert_geojson_to_obj(sys.argv[1], sys.argv[2])
