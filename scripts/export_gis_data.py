import os
import geopandas as gpd

def export_layer(gpkg_path: str, layer_name: str, export_dir: str) -> None:
    """Read a layer from a GeoPackage and export it to Shapefile and GeoJSON.

    Args:
        gpkg_path: Full path to the .gpkg file.
        layer_name: Name for the exported files (no extension).
        export_dir: Directory where the exported files will be written.
    """
    try:
        gdf = gpd.read_file(gpkg_path)
    except Exception as e:
        print(f"[ERROR] Could not read {gpkg_path}: {e}")
        return

    # Ensure output directory exists
    os.makedirs(export_dir, exist_ok=True)

    # Export to Shapefile
    shp_path = os.path.join(export_dir, f"{layer_name}.shp")
    try:
        gdf.to_file(shp_path, driver="ESRI Shapefile")
        print(f"[INFO] Shapefile written to {shp_path}")
    except Exception as e:
        print(f"[ERROR] Could not write Shapefile for {layer_name}: {e}")

    # Export to GeoJSON
    geojson_path = os.path.join(export_dir, f"{layer_name}.geojson")
    try:
        gdf.to_file(geojson_path, driver="GeoJSON")
        print(f"[INFO] GeoJSON written to {geojson_path}")
    except Exception as e:
        print(f"[ERROR] Could not write GeoJSON for {layer_name}: {e}")


def main():
    # Base directory of the project
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_osm_dir = os.path.join(project_root, "data", "raw", "osm")
    export_dir = os.path.join(project_root, "data", "processed", "gis_exports")

    # Mapping of source GPKG files to a friendly layer name
    layers = {
        "streets_drive.gpkg": "streets_drive",
        "streets_walk.gpkg": "streets_walk",
        "buildings.gpkg": "buildings",
        "amenities.gpkg": "amenities",
    }

    for filename, layer_name in layers.items():
        gpkg_path = os.path.join(raw_osm_dir, filename)
        if os.path.isfile(gpkg_path):
            print(f"[INFO] Exporting {filename} as {layer_name} …")
            export_layer(gpkg_path, layer_name, export_dir)
        else:
            print(f"[WARNING] Expected file {gpkg_path} not found. Skipping.")

    print("[DONE] GIS export complete. Files are located in:")
    print(export_dir)

if __name__ == "__main__":
    main()
