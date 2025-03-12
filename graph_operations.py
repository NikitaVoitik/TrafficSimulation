import io
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
import pygame


class GraphManager:
    def __init__(self):
        self.graph = nx.Graph()
        self.od_pairs = []
        self.link_flows = defaultdict(float)
        self.buf = io.BytesIO()

    def add_node(self, node):
        if not node:
            return False, "Node name cannot be empty"

        if node in self.graph.nodes:
            return False, f"Node '{node}' already exists"

        self.graph.add_node(node)
        return True, f"Node '{node}' added"

    def add_edge(self, node1, node2, weight=1):
        if node1 not in self.graph.nodes or node2 not in self.graph.nodes:
            return False, "One or both nodes don't exist"

        self.graph.add_edge(node1, node2, weight=weight)
        return True, f"Edge between '{node1}' and '{node2}' added"

    def add_od_pair(self, origin, destination, demand):
        if origin not in self.graph.nodes or destination not in self.graph.nodes:
            return False, "Origin or destination node doesn't exist"

        try:
            demand_value = float(demand)
            if demand_value <= 0:
                return False, "Demand must be positive"

            self.od_pairs.append((origin, destination, demand_value))
            return True, f"OD pair {origin}-{destination} with demand {demand_value} added"
        except ValueError:
            return False, "Invalid demand value"

    def clear_graph(self):
        self.graph.clear()
        self.od_pairs = []
        self.link_flows.clear()
        return "Graph cleared"

    def find_shortest_path(self, origin, destination):
        try:
            return nx.shortest_path(self.graph, source=origin, target=destination, weight='weight')
        except nx.NetworkXNoPath:
            return None

    def create_graph_image(self, width, height):
        plt.close('all')

        try:
            fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
            ax.set_facecolor('#f8f9fa')

            if self.graph.number_of_nodes() > 0:
                pos = nx.spring_layout(self.graph, seed=42)

                nx.draw_networkx_nodes(self.graph, pos, node_color='#3498db', node_size=700, alpha=0.9,
                                       edgecolors='#2980b9')

                nx.draw_networkx_edges(self.graph, pos, edge_color='#95a5a6', width=2.5, alpha=0.8, arrows=True)

                nx.draw_networkx_labels(self.graph, pos, font_color='white', font_size=14, font_weight='bold')

                edge_labels = {(u, v): f"{data['weight']}" for u, v, data in self.graph.edges(data=True)}
                nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=12,
                                             font_color='#34495e',
                                             bbox=dict(boxstyle="round,pad=0.3", ec="#cccccc", fc="white", alpha=0.8))

            ax.set_axis_off()

            buffer = io.BytesIO()
            fig.tight_layout()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            buffer.seek(0)

            image = pygame.image.load(buffer)
            scaled_image = pygame.transform.scale(image, (width, height))

            buffer.close()
            plt.close(fig)

            return scaled_image

        except Exception as e:
            print(f"Error creating graph image: {e}")
            plt.close('all')
            return None
