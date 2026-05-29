# analysis/pedestrian_flows/flow_difference_map.py
import os
import sys
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import Point

# -----------------------------------------------------------------
# Helper – compute total/avg/max for a flow dict (kept for reference)
def compute_stats(flow: dict):
    total = sum(flow.values())
    avg   = total / len(flow) if flow else 0
    mx    = max(flow.values()) if flow else 0
    return total, avg, mx

# -----------------------------------------------------------------
# Project directories
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
walk_gpkg   = os.path.join(project_dir, 'data', 'raw', 'osm', 'streets_walk.gpkg')
corridor_fp = os.path.join(project_dir, 'data', 'raw', 'gis', 'green_corridor.geojson')

# -----------------------------------------------------------------
# Load network data (same as the scenario script)
nodes = gpd.read_file(walk_gpkg, layer='nodes')
edges = gpd.read_file(walk_gpkg, layer='edges')
if 'osmid' in nodes.columns:
    nodes = nodes.set_index('osmid')
else:
    nodes['osmid'] = nodes.index
    nodes = nodes.set_index('osmid')

# Build undirected graph (edge length → weight)
G = nx.Graph()
for _, row in edges.iterrows():
    G.add_edge(row['u'], row['v'],
               weight=float(row.get('length', 10.0)),
               geometry=row.geometry)

# -----------------------------------------------------------------
# Identify source (metro) and target (stadium) nodes – same heuristic as the scenario
metro_coords   = Point(14.8297, 40.6318)
metro_pt       = gpd.GeoSeries([metro_coords], crs='EPSG:4326').to_crs(epsg=32633).iloc[0]
nodes_m        = nodes.to_crs(epsg=32633)
source_node_id = (nodes_m.geometry.distance(metro_pt)).idxmin()

stadium_center = Point(14.8297, 40.6278)
stadium_pt    = gpd.GeoSeries([stadium_center], crs='EPSG:4326').to_crs(epsg=32633).iloc[0]
closest        = (nodes_m.geometry.distance(stadium_pt)).nsmallest(4)
target_node_ids = list(closest.index)

# -----------------------------------------------------------------
# Baseline flow (no corridor)
from pedestrian_flow_scenario import simulate_pedestrian_flow, add_green_corridor
flow_baseline = simulate_pedestrian_flow(G, source_node_id, target_node_ids)

# Scenario flow with the worst‑case corridor (weight = 0.25)
if os.path.exists(corridor_fp):
    corridor_gdf = gpd.read_file(corridor_fp)
    corridor_geom = corridor_gdf.union_all()
    G_scen = add_green_corridor(G, corridor_geom, weight_factor=0.25)
    flow_scenario = simulate_pedestrian_flow(G_scen, source_node_id, target_node_ids)
else:
    flow_scenario = flow_baseline

# -----------------------------------------------------------------
# Merge flow values into the edges GeoDataFrame
def edge_key(row):
    return (row['u'], row['v'])

edges['flow_baseline'] = edges.apply(lambda r: flow_baseline.get(edge_key(r), 0), axis=1)
edges['flow_scenario'] = edges.apply(lambda r: flow_scenario.get(edge_key(r), 0), axis=1)
edges['flow_delta']    = edges['flow_scenario'] - edges['flow_baseline']

# -----------------------------------------------------------------
# Plotting: colour‑coded by delta (red = increase, blue = decrease)
ccmap = plt.cm.seismic  # blue–white–red
# Normalise colour range symmetrically around zero
max_abs = max(abs(edges['flow_delta'].min()), edges['flow_delta'].max())
norm   = plt.Normalize(vmin=-max_abs, vmax=max_abs)

fig, ax = plt.subplots(figsize=(10, 8))
edges.plot(ax=ax,
           column='flow_delta',
           cmap=ccmap,
           linewidth=2,
           legend=True,
           legend_kwds={'label': 'Δ Pedestrian Flow (scenario – baseline)'},
           norm=norm)

# Add a thin base map of the network for context (light grey)
edges.plot(ax=ax, color='lightgrey', linewidth=0.5, alpha=0.5)

ax.set_title('Pedestrian‑Flow Difference (Green‑Corridor w = 0.25)')
ax.axis('off')

out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'visualizations', 'maps'))
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'pedestrian_flow_difference_map.png')
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close()

print(f'Difference map saved to {out_path}')
