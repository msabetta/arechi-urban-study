import os
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString


def add_green_corridor(G, corridor_geom, weight_factor=0.5):
    """Add a low‑resistance green corridor to the graph.
    The corridor is provided as a LineString (or MultiLineString).
    All edges intersecting the corridor will have their weight multiplied
    by *weight_factor* (default = 0.5, i.e. half the original cost).
    """
    if corridor_geom.is_empty:
        return G
    # Ensure we work on a copy to avoid side‑effects
    G = G.copy()
    for u, v, data in G.edges(data=True):
        edge_geom = data.get('geometry')
        if edge_geom is None:
            continue
        if corridor_geom.intersects(edge_geom):
            original_weight = data.get('weight', 1.0)
            data['weight'] = original_weight * weight_factor
    return G


def simulate_pedestrian_flow(G, source_node_id, target_node_ids, total_pedestrians=10000):
    """Run a simple shortest‑path flow simulation.
    Returns a dictionary mapping edge tuples to the accumulated pedestrian count.
    """
    flow_dict = {(u, v): 0.0 for u, v in G.edges()}
    pedestrians_per_gate = total_pedestrians / len(target_node_ids)
    for target_node in target_node_ids:
        try:
            path = nx.shortest_path(G, source=source_node_id, target=target_node, weight='weight')
            for i in range(len(path) - 1):
                edge = (path[i], path[i + 1])
                # NetworkX stores edges undirected; ensure canonical ordering
                if edge not in flow_dict:
                    edge = (path[i + 1], path[i])
                flow_dict[edge] += pedestrians_per_gate
        except nx.NetworkXNoPath:
            print(f"No path between source {source_node_id} and target {target_node}")
    return flow_dict


def plot_flow(edges_gdf, flow_dict, source_node_geom, target_node_geoms, out_path, title):
    """Create a flow map visualising the pedestrian volumes.
    Edges with zero flow are drawn in light grey; active edges are coloured
    according to the magnitude of the flow.
    """
    # Attach flow values to the GeoDataFrame
    edges_gdf['flow'] = edges_gdf.apply(
        lambda row: flow_dict.get((row['u'], row['v']), flow_dict.get((row['v'], row['u']), 0.0)),
        axis=1,
    )
    # Plot background network
    fig, ax = plt.subplots(figsize=(10, 10))
    edges_gdf.plot(ax=ax, color='#e0e0e0', linewidth=1.0, zorder=1)

    active = edges_gdf[edges_gdf['flow'] > 0]
    if not active.empty:
        max_flow = active['flow'].max()
        linewidths = 1.5 + (active['flow'] / max_flow) * 6.0
        active.plot(
            ax=ax,
            column='flow',
            cmap='YlOrRd',
            linewidth=linewidths,
            legend=True,
            legend_kwds={'label': 'Pedestrian Flow', 'orientation': 'horizontal', 'pad': 0.05},
            zorder=2,
        )
    # Highlight source & destinations
    gpd.GeoSeries([source_node_geom]).plot(ax=ax, color='#2980b9', markersize=150, marker='s', label='Metro Stazione', zorder=3)
    gpd.GeoSeries(target_node_geoms).plot(ax=ax, color='#27ae60', markersize=120, marker='o', label='Varchi Stadio', zorder=3)
    ax.set_title(title, fontsize=14, fontweight='bold', color='#2c3e50')
    ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#bdc3c7')
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(base_dir, '..', '..'))
    out_dir = os.path.join(project_dir, 'visualizations', 'maps')
    os.makedirs(out_dir, exist_ok=True)

    # Input files – adjust paths if your data layout differs
    walk_gpkg = os.path.join(project_dir, 'data', 'raw', 'osm', 'streets_walk.gpkg')
    green_corridor_geojson = os.path.join(project_dir, 'data', 'raw', 'gis', 'green_corridor.geojson')

    # Load network
    nodes = gpd.read_file(walk_gpkg, layer='nodes')
    edges = gpd.read_file(walk_gpkg, layer='edges')
    # Ensure osmid index
    if 'osmid' in nodes.columns:
        nodes = nodes.set_index('osmid')
    else:
        nodes['osmid'] = nodes.index
        nodes = nodes.set_index('osmid')

    # Build graph
    G = nx.Graph()
    for _, row in edges.iterrows():
        G.add_edge(row['u'], row['v'], weight=float(row.get('length', 10.0)), geometry=row.geometry)

    # Source (Metro Arechi)
    metro_coords = Point(14.8297, 40.6318)
    nodes_m = nodes.to_crs(epsg=32633)
    metro_pt_m = gpd.GeoSeries([metro_coords], crs='EPSG:4326').to_crs(epsg=32633).iloc[0]
    distances_to_metro = nodes_m.geometry.distance(metro_pt_m)
    source_node_id = distances_to_metro.idxmin()
    source_geom = nodes.loc[[source_node_id]].geometry.iloc[0]

    # Destination nodes (stadium gates)
    stadium_center = Point(14.8297, 40.6278)
    stadium_pt_m = gpd.GeoSeries([stadium_center], crs='EPSG:4326').to_crs(epsg=32633).iloc[0]
    distances_to_stadium = nodes_m.geometry.distance(stadium_pt_m)
    stadium_perimeter_nodes = nodes_m[(distances_to_stadium >= 100) & (distances_to_stadium <= 220)]
    if stadium_perimeter_nodes.empty:
        target_node_ids = list(distances_to_stadium.nsmallest(4).index)
    else:
        target_node_ids = list(stadium_perimeter_nodes.sample(min(4, len(stadium_perimeter_nodes)), random_state=42).index)
    target_geoms = nodes.loc[target_node_ids].geometry.tolist()

    # ---------- Baseline simulation (no green corridor) ----------
    flow_baseline = simulate_pedestrian_flow(G, source_node_id, target_node_ids)
    out_png_baseline = os.path.join(out_dir, 'pedestrian_flow_baseline.png')
    plot_flow(edges, flow_baseline, source_geom, target_geoms, out_png_baseline,
              'Pedestrian Flow – Baseline (Current Network)')
    # Compute baseline flow statistics
    total_baseline = sum(flow_baseline.values())
    avg_baseline = total_baseline / len(flow_baseline)
    max_baseline = max(flow_baseline.values())
    print(f"Baseline total pedestrians: {total_baseline:.0f}, average per edge: {avg_baseline:.2f}, max edge flow: {max_baseline:.0f}")

    # ---------- Scenario with green corridor ----------
    if os.path.exists(green_corridor_geojson):
        corridor_gdf = gpd.read_file(green_corridor_geojson)
        corridor_geom = corridor_gdf.union_all()
        G_scenario = add_green_corridor(G, corridor_geom, weight_factor=0.25)
        flow_scenario = simulate_pedestrian_flow(G_scenario, source_node_id, target_node_ids)
        out_png_scenario = os.path.join(out_dir, 'pedestrian_flow_green_corridor.png')
        plot_flow(edges, flow_scenario, source_geom, target_geoms, out_png_scenario,
                  'Pedestrian Flow – Scenario (Green Corridor Added)')
        # Compute scenario flow statistics
        total_scenario = sum(flow_scenario.values())
        avg_scenario = total_scenario / len(flow_scenario)
        max_scenario = max(flow_scenario.values())
        print(f"Scenario total pedestrians: {total_scenario:.0f}, average per edge: {avg_scenario:.2f}, max edge flow: {max_scenario:.0f}")
        print(f"Scenario maps saved in {out_dir}")
    else:
        print('Green corridor file not found – only baseline map generated.')

if __name__ == '__main__':
    main()
