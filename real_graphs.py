import matplotlib.pyplot as plt
import networkx as nx


def bpr(free_time, volume, capacity, alpha=0.15, beta=4):
    return free_time * (1 + alpha * (volume / capacity) ** beta)


def calculate_paths_dijkstra(graph, od_pairs):
    paths = []
    for origin, destination, demand in od_pairs:
        if origin in graph and destination in graph:
            try:
                path = nx.shortest_path(graph, origin, destination, weight='travel_time')
                paths.append((path, demand))
            except nx.NetworkXNoPath:
                paths.append(([], 0))
        else:
            paths.append(([], 0))
    return paths


def msa(graph, od_pairs, max_iter=100, convergence_threshold=0.001):
    g = graph.copy()

    for u, v, data in g.edges(data=True):
        data["volume"] = 0

    prev_total_cost = 0

    for n_iter in range(1, max_iter + 1):
        for u, v, data in g.edges(data=True):
            free_time = data["weight"]
            volume = data["volume"]
            capacity = data["capacity"]
            data["travel_time"] = bpr(free_time, volume, capacity)

        path_assignments = calculate_paths_dijkstra(g, od_pairs)

        auxiliary_flows = {(u, v): 0 for u, v in g.edges()}

        for path, demand in path_assignments:
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                auxiliary_flows[(u, v)] += demand

        total_cost = 0
        max_diff = 0

        for u, v, data in g.edges(data=True):
            old_volume = data["volume"]
            aux_volume = auxiliary_flows.get((u, v), 0)

            new_volume = (1 - 1 / n_iter) * old_volume + (1 / n_iter) * aux_volume
            data["volume"] = new_volume

            diff = abs(new_volume - old_volume)
            max_diff = max(max_diff, diff)

            total_cost += new_volume * data["travel_time"]

        rel_gap = abs(total_cost - prev_total_cost) / (prev_total_cost + 1e-10)
        prev_total_cost = total_cost

        print(f"Iteration {n_iter}: Max flow difference = {max_diff:.6f}, Relative gap = {rel_gap:.6f}")

        if max_diff < convergence_threshold:
            print(f"Converged after {n_iter} iterations")
            break

    return g


def draw_msa_result(graph: nx.Graph):
    plt.figure(figsize=(10, 8), dpi=100)
    plt.title("MSA Traffic Assignment Results", fontsize=14)

    pos = nx.spring_layout(graph, seed=42)  # Fixed seed for consistent layout

    # Draw nodes with better visibility
    nx.draw_networkx_nodes(graph, pos,
                          node_color="#66b3ff",
                          edgecolors="#1f78b4",
                          node_size=700)

    # Draw edges with width proportional to volume
    edge_widths = [data.get("volume", 0)/5 + 1 for _, _, data in graph.edges(data=True)]
    nx.draw_networkx_edges(graph, pos,
                          width=edge_widths,
                          edge_color="#808080",
                          alpha=0.7)

    # Draw labels
    nx.draw_networkx_labels(graph, pos, font_size=12, font_color="white", font_weight="bold")

    # Create detailed edge labels
    edge_labels = {}
    for u, v, data in graph.edges(data=True):
        vol = data.get("volume", 0)
        ttime = data.get("travel_time", 0)
        cap = data.get("capacity", "N/A")
        edge_labels[(u, v)] = f"v={vol:.1f}\nt={ttime:.1f}\nc={cap}"

    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels,
                                font_size=9,
                                bbox=dict(facecolor="white", edgecolor="gray", alpha=0.7))

    plt.axis("off")
    plt.tight_layout()
    plt.get_current_fig_manager().set_window_title("MSA Traffic Assignment")
    plt.show(block=False)  # Non-blocking to allow Pygame to continue


def create_test_graph():
    G = nx.DiGraph()

    G.add_nodes_from(range(4))

    edges = [
        (0, 1, {'weight': 5, 'capacity': 10}),
        (0, 2, {'weight': 3, 'capacity': 15}),
        (1, 2, {'weight': 2, 'capacity': 20}),
        (1, 3, {'weight': 6, 'capacity': 25}),
        (2, 3, {'weight': 4, 'capacity': 5})
    ]
    G.add_edges_from(edges)

    return G


print(msa(create_test_graph(), [[0, 3, 10]]))
