import pathlib
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium

# Coordinates of Stadio Arechi, Salerno
STADIO_LAT = 40.640330772
STADIO_LON = 14.820996716
RADIUS_KM = 10  # radius of interest

def main():
    # Load the aggregated population CSV
    project_root = pathlib.Path(__file__).resolve().parents[1]
    pop_path = project_root / "data" / "processed" / "popolazione_1951_2021.csv"
    df = pd.read_csv(pop_path)
    geolocator = Nominatim(user_agent="arechi_population_analysis")
    selected = []
    for _, row in df.iterrows():
        # Build a query string for the comune (city) + province + Italy
        query = f"{row['area_name']}, Salerno, Italy"
        try:
            location = geolocator.geocode(query, timeout=10)
        except Exception:
            location = None
        if location is None:
            continue
        # Compute distance from the stadium
        dist_km = geodesic((STADIO_LAT, STADIO_LON), (location.latitude, location.longitude)).km
        if dist_km <= RADIUS_KM:
            selected.append({
                "id": row["id"],
                "area_name": row["area_name"],
                "population": row["population"],
                "distance_km": round(dist_km, 2),
                "density": row.get("density", pd.NA),
                "lat": location.latitude,
                "lon": location.longitude,
            })
    # Create a DataFrame with the results
    result_df = pd.DataFrame(selected)
    out_csv = project_root / "data" / "processed" / "population_near_arechi.csv"
    result_df.to_csv(out_csv, index=False)
    print(f"✅  CSV created: {out_csv}")
    # Build an interactive Folium map
    m = folium.Map(location=[STADIO_LAT, STADIO_LON], zoom_start=12)
    # Buffer circle (10 km)
    folium.Circle(
        location=[STADIO_LAT, STADIO_LON],
        radius=RADIUS_KM * 1000,
        color="blue",
        fill=False,
        tooltip=f"{RADIUS_KM} km buffer",
    ).add_to(m)
    # Add markers for each selected comune
    for _, r in result_df.iterrows():
        folium.Marker(
            location=[r["lat"], r["lon"]],
            popup=(
                f"<b>{r['area_name']}</b><br>"
                f"Popolazione: {int(r['population'])}<br>"
                f"Distanza: {r['distance_km']} km"
            ),
            icon=folium.Icon(color="green", icon="info-sign"),
        ).add_to(m)
    out_html = project_root / "data" / "processed" / "population_near_arechi.html"
    m.save(out_html)
    print(f"🗺️  Folium map saved: {out_html}")
if __name__ == "__main__":
    main()