# scripts/prepare_gis_for_sim.py
import geopandas as gpd
import os

def reproject(src_path, dst_path, crs="EPSG:32633"):
    gdf = gpd.read_file(src_path)
    gdf = gdf.to_crs(crs)
    gdf.to_file(dst_path)
    print(f"[INFO] Re‑projected {os.path.basename(src_path)} → {dst_path}")

def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_dir = os.path.join(project_root, "data", "processed", "gis_exports")
    out_dir = os.path.join(project_root, "data", "processed", "gis_prepared")
    os.makedirs(out_dir, exist_ok=True)

    for fname in os.listdir(src_dir):
        if fname.endswith(".shp"):
            src = os.path.join(src_dir, fname)
            dst = os.path.join(out_dir, fname)      # same name, new folder
            reproject(src, dst)

if __name__ == "__main__":
    main()
