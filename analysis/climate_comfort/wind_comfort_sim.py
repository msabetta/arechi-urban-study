import matplotlib
import os
import sys
import rasterio
from rasterio.features import rasterize
from rasterio.plot import show
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore', category=rasterio.errors.NotGeoreferencedWarning)
from shapely.geometry import box


# Ensure the virtual environment site-packages is prioritized
venv_site = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "venv", "lib", "python3.12", "site-packages"))
if venv_site not in sys.path:
    sys.path.insert(0, venv_site)

# Optional imports with fallbacks
try:
    import geopandas as gpd
except Exception:
    gpd = None
    print("Warning: geopandas not available, building rasterization will be skipped.")


# Ensure the virtual environment site-packages is prioritized
venv_site = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "venv", "lib", "python3.12", "site-packages"))
if venv_site not in sys.path:
    sys.path.insert(0, venv_site)


def rasterize_buildings(buildings_gdf, out_shape, transform, default_height=6.0):
    """Rasterize building footprints to a height raster.
    
    Parameters
    ----------
    buildings_gdf : GeoDataFrame
        Must contain a geometry column with polygon footprints.
    out_shape : tuple[int, int]
        (height, width) of the output raster.
    transform : affine.Affine
        Rasterio transform mapping pixel coordinates to world coordinates.
    default_height : float, optional
        Height (m) to assign when building levels are missing.
    """
    # Determine height per building (levels * 3m, fallback to default)
    def get_height(row):
        levels = row.get('building:levels')
        try:
            return float(levels) * 3.0 if levels else default_height
        except Exception:
            return default_height

    heights = buildings_gdf.apply(get_height, axis=1).values
    shapes = ((geom, height) for geom, height in zip(buildings_gdf.geometry, heights))

    raster = rasterize(
        shapes,
        out_shape=out_shape,
        transform=transform,
        fill=0,
        dtype='float32',
        all_touched=True,
    )
    return raster


def compute_wind_speed(surface_raster, wind_speed_ref, wind_dir_deg, shelter_coeff=0.5):
    """Very simplified wind attenuation model.
    
    * wind_speed_ref: reference wind speed at reference height (e.g., 5 m s⁻¹ at 10 m).
    * wind_dir_deg: wind direction in degrees (0 = North, clockwise).
    * shelter_coeff: factor that reduces wind speed per meter of obstacle height.
    """
    # Convert building heights to a shelter factor (higher = more reduction)
    # Simple exponential decay: v = v_ref * exp(-k * h)
    k = shelter_coeff / 10.0  # scaling factor
    attenuation = np.exp(-k * surface_raster)
    wind_speed = wind_speed_ref * attenuation
    return wind_speed


def classify_comfort(wind_speed_raster):
    """Classify wind speed into EN 16890 comfort categories.
    Returns an integer array: 0=discomfort, 1=moderate, 2=comfortable.
    """
    categories = np.zeros_like(wind_speed_raster, dtype=np.uint8)
    categories[wind_speed_raster < 1.5] = 0  # low wind – discomfort for pedestrians
    categories[(wind_speed_raster >= 1.5) & (wind_speed_raster < 3.5)] = 1  # moderate
    categories[wind_speed_raster >= 3.5] = 2  # comfortable
    return categories


def plot_wind_comfort(categories, transform, out_path, title):
    #cmap = plt.cm.get_cmap('RdYlGn', 3)
    cmap = matplotlib.colormaps['RdYlGn']
    bounds = [-0.5, 0.5, 1.5, 2.5]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    fig, ax = plt.subplots(figsize=(10, 8))
    show(categories, transform=transform, ax=ax, cmap=cmap, norm=norm)
    # Add a legend/colorbar with category labels
    cbar = plt.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, ticks=[0, 1, 2])
    cbar.set_ticklabels(['Discomfort', 'Moderate', 'Comfortable'])
    cbar.set_label('Wind Comfort Category')
    ax.set_title(title, fontsize=14, fontweight='bold', color='#2c3e50')
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(base_dir, "..", ".."))
    out_dir = os.path.join(project_dir, "visualizations", "maps")
    os.makedirs(out_dir, exist_ok=True)

    # Paths to input data (adjust if needed)
    buildings_fp = os.path.join(project_dir, "data", "raw", "osm", "buildings.gpkg")
    dem_fp = os.path.join(project_dir, "data", "raw", "osm", "dem.tif")

    # Load inputs
    if gpd:
        buildings = gpd.read_file(buildings_fp)
    else:
        print("Warning: geopandas not available, skipping building rasterization.")
        buildings = None
    if not os.path.exists(dem_fp):
        # Create a synthetic DEM raster (e.g., 100x100 with zero elevation)
        import rasterio
        from rasterio.transform import from_origin
        width, height = 100, 100
        # Use a realistic origin and pixel size to avoid identity affine
        transform = from_origin(0, 1000, 10, 10)  # origin at (0,1000), 10‑unit pixel size
        new_meta = {
            "driver": "GTiff",
            "height": height,
            "width": width,
            "count": 1,
            "dtype": "float32",
            "crs": "EPSG:4326",
            "transform": transform,
        }
        synthetic_path = os.path.join(os.path.dirname(dem_fp), "synthetic_dem.tif")
        with rasterio.open(synthetic_path, "w", **new_meta) as dst:
            dst.write(np.zeros((1, height, width), dtype="float32"))
        dem_fp_to_use = synthetic_path
    else:
        dem_fp_to_use = dem_fp
    with rasterio.open(dem_fp_to_use) as src:
        dem = src.read(1)
        transform = src.transform
        out_shape = src.shape

    # Rasterize building heights and add to DEM to get surface model
    if buildings is not None:
        building_heights = rasterize_buildings(buildings, out_shape, transform)
    else:
        building_heights = np.zeros(out_shape, dtype='float32')
    surface = dem + building_heights

    # ---- Baseline (no trees) ----
    wind_baseline = compute_wind_speed(surface, wind_speed_ref=5.0, wind_dir_deg=315)
    categories_baseline = classify_comfort(wind_baseline)
    out_png_baseline = os.path.join(out_dir, "wind_comfort_baseline.png")
    plot_wind_comfort(categories_baseline, transform, out_png_baseline,
                      "Wind Comfort – Baseline (Asphalt only)")

    # ---- Design (add tree canopy) ----
    # Approximate tree canopy as a 8 m high uniform layer over the whole study area
    tree_layer = np.full(out_shape, 8.0, dtype='float32')
    surface_design = surface + tree_layer
    wind_design = compute_wind_speed(surface_design, wind_speed_ref=5.0, wind_dir_deg=315)
    categories_design = classify_comfort(wind_design)
    out_png_design = os.path.join(out_dir, "wind_comfort_design.png")
    plot_wind_comfort(categories_design, transform, out_png_design,
                      "Wind Comfort – Design (Trees added)")

    print(f"Wind‑comfort maps saved in {out_dir}")

if __name__ == "__main__":
    main()
