import os
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon

def create_sample_land_use(year: int, out_path: Path):
    """Create a simple synthetic land‑use GeoDataFrame and save as GeoJSON.

    The geometry consists of a few rectangular polygons with a `land_use`
    attribute. This is only for demonstration / testing purposes.
    """
    # Define a few polygons (simple squares) with different land‑use types
    polygons = [
        Polygon([(0, 0), (0, 100), (100, 100), (100, 0)]),
        Polygon([(120, 0), (120, 80), (200, 80), (200, 0)]),
        Polygon([(0, 120), (0, 200), (80, 200), (80, 120)]),
    ]
    # Assign land‑use categories that evolve over years
    if year == 2020:
        land_uses = ["Residenziale", "Commerciale", "Verde"]
    else:
        # Simulate a change: some residential becomes mixed‑use, green expands
        land_uses = ["Residenziale (Misto)", "Commerciale", "Verde"]
    gdf = gpd.GeoDataFrame({"land_use": land_uses, "geometry": polygons}, crs="EPSG:4326")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(out_path, driver="GeoJSON")
    print(f"Created {out_path}")

def main():
    project_root = Path(__file__).resolve().parents[2]  # jump to project root
    data_dir = project_root / "data" / "processed"
    create_sample_land_use(2020, data_dir / "land_use_2020.geojson")
    create_sample_land_use(2025, data_dir / "land_use_2025.geojson")

if __name__ == "__main__":
    main()
