import os
import matplotlib.pyplot as plt
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point

# Local imports from the simulation package
from pedestrian_flow_scenario import add_green_corridor, simulate_pedestrian_flow

# ---------- Helper functions ----------
def compute_stats(flow_dict):
    """Return total, average per edge, and max flow values."""
    total = sum(flow_dict.values())
    avg = total / len(flow_dict) if flow_dict else 0
    max_val = max(flow_dict.values()) if flow_dict else 0
    return total, avg, max_val

# ---------- Project paths ----------
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
walk_gpkg = os.path.join(project_dir, 'data', 'raw', 'osm', 'streets_walk.gpkg')
green_corridor_geojson = os.path.join(project_dir, 'data', 'raw', 'gis', 'green_corridor.geojson')

# ---------- Load network data ----------
nodes = gpd.read_file(walk_gpkg, layer='nodes')
edges = gpd.read_file(walk_gpkg, layer='edges')
# Ensure osmid is the index
if 'osmid' in nodes.columns:
    nodes = nodes.set_index('osmid')
else:
    nodes['osmid'] = nodes.index
    nodes = nodes.set_index('osmid')

# Build undirected graph with length as weight
G = nx.Graph()
for _, row in edges.iterrows():
    G.add_edge(row['u'], row['v'], weight=float(row.get('length', 10.0)), geometry=row.geometry)

# ---------- Identify source and target nodes (same as scenario) ----------
metro_coords = Point(14.8297, 40.6318)
metro_pt = gpd.GeoSeries([metro_coords], crs='EPSG:4326').to_crs(epsg=32633).iloc[0]
nodes_m = nodes.to_crs(epsg=32633)
source_node_id = (nodes_m.geometry.distance(metro_pt)).idxmin()

stadium_center = Point(14.8297, 40.6278)
stadium_pt = gpd.GeoSeries([stadium_center], crs='EPSG:4326').to_crs(epsg=32633).iloc[0]
closest = (nodes_m.geometry.distance(stadium_pt)).nsmallest(4)
target_node_ids = list(closest.index)

# ---------- Baseline flow ----------
flow_baseline = simulate_pedestrian_flow(G, source_node_id, target_node_ids)
base_total, base_avg, base_max = compute_stats(flow_baseline)

# ---------- Load corridor geometry ----------
if os.path.exists(green_corridor_geojson):
    corridor_gdf = gpd.read_file(green_corridor_geojson)
    corridor_geom = corridor_gdf.union_all()
else:
    corridor_geom = None

# ---------- Evaluate various weight factors ----------
weight_factors = [0.1, 0.25, 0.5, 0.75, 1.0]
scenario_totals = []
scenario_avgs = []
scenario_maxs = []

for wf in weight_factors:
    if corridor_geom is not None:
        G_scen = add_green_corridor(G, corridor_geom, weight_factor=wf)
        flow_scen = simulate_pedestrian_flow(G_scen, source_node_id, target_node_ids)
    else:
        flow_scen = flow_baseline
    tot, avg, mx = compute_stats(flow_scen)
    scenario_totals.append(tot)
    scenario_avgs.append(avg)
    scenario_maxs.append(mx)

# ---------- Plot comparison ----------
labels = ['Baseline'] + [str(wf) for wf in weight_factors]
fig, axs = plt.subplots(1, 3, figsize=(18, 5))

# Total pedestrians
axs[0].bar(labels, [base_total] + scenario_totals, color='#3498db')
axs[0].set_title('Total Pedestrians')
axs[0].set_xlabel('Weight factor')
axs[0].set_ylabel('Pedestrians')

# Average per edge
axs[1].bar(labels, [base_avg] + scenario_avgs, color='#2ecc71')
axs[1].set_title('Average per Edge')
axs[1].set_xlabel('Weight factor')

# Max edge flow
axs[2].bar(labels, [base_max] + scenario_maxs, color='#e74c3c')
axs[2].set_title('Max Edge Flow')
axs[2].set_xlabel('Weight factor')

# Annotate bar values
for ax in axs:
    for rect in ax.patches:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, h, f'{h:.0f}', ha='center', va='bottom')

plt.suptitle('Impact of Green‑Corridor Weight Factor on Pedestrian Flow')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'visualizations', 'maps'))
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'pedestrian_flow_weight_factor_comparison.png')
plt.savefig(out_path, dpi=300)
plt.close()
print(f'Bar chart saved to {out_path}')
