import io
import json
import os

import matplotlib.pyplot as plt
import networkx as nx
import pygame


class GraphManager:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.od_pairs = []
        self.buf = io.BytesIO()
        self.save_directory = "saved_graphs"

    def add_node(self, node):
        if not node:
            return False, "Node name cannot be empty"

        if node in self.graph.nodes:
            return False, f"Node '{node}' already exists"

        self.graph.add_node(node)
        return True, f"Node '{node}' added"

    def add_edge(self, node1, node2, weight=1, capacity=100):
        if node1 not in self.graph.nodes or node2 not in self.graph.nodes:
            return False, "One or both nodes don't exist"

        self.graph.add_edge(node1, node2, weight=weight, capacity=capacity)
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
                nx.draw_networkx_nodes(self.graph, pos, node_color='#3498db', node_size=700,
                                       edgecolors='#2980b9')

                nx.draw_networkx_edges(self.graph, pos, edge_color='#95a5a6', width=2.5, arrows=True)

                for origin, destination, demand in self.od_pairs:
                    if origin in pos and destination in pos:
                        rad = 0.3
                        edge_color = '#e74c3c'

                        nx.draw_networkx_edges(
                            nx.DiGraph([((origin, destination))]),
                            pos,
                            edge_color=edge_color,
                            width=2.0,
                            arrows=True,
                            arrowstyle='-|>',
                            arrowsize=15,
                            connectionstyle=f'arc3,rad={rad}',
                            alpha=0.8
                        )

                        edge_x = (pos[origin][0] + pos[destination][0]) / 2
                        edge_y = (pos[origin][1] + pos[destination][1]) / 2
                        offset_x = (pos[destination][1] - pos[origin][1]) * rad / 2
                        offset_y = (pos[origin][0] - pos[destination][0]) * rad / 2

                        plt.text(edge_x + offset_x, edge_y + offset_y,
                                 f"D={demand}",
                                 color=edge_color,
                                 fontsize=10,
                                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=edge_color, alpha=0.8))

                nx.draw_networkx_labels(self.graph, pos, font_color='white', font_size=14, font_weight='bold')

                edge_labels = {(u, v): f"t={data['weight']}\nc={data.get('capacity', 'N/A')}"
                               for u, v, data in self.graph.edges(data=True)}
                nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=12,
                                             font_color='#34495e',
                                             bbox=dict(boxstyle="round,pad=0.3", ec="#cccccc", fc="white"))

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

    def save_graph(self, filename):
        if not filename:
            return False, "Filename cannot be empty"

        if not filename.endswith('.json'):
            filename += '.json'

        filepath = os.path.join(self.save_directory, filename)

        graph_data = {
            'nodes': list(self.graph.nodes()),
            'edges': [(u, v, d) for u, v, d in self.graph.edges(data=True)],
            'od_pairs': self.od_pairs
        }

        try:
            with open(filepath, 'w') as f:
                json.dump(graph_data, f, indent=2)
            return True, f"Graph saved to {filename}"
        except Exception as e:
            return False, f"Error saving graph: {str(e)}"

    def load_graph(self, filename):
        if not filename:
            return False, "Filename cannot be empty"

        if not filename.endswith('.json'):
            filename += '.json'

        filepath = os.path.join(self.save_directory, filename)

        if not os.path.exists(filepath):
            return False, f"File {filename} not found"

        try:
            with open(filepath, 'r') as f:
                graph_data = json.load(f)

            self.graph.clear()
            self.od_pairs = []

            self.graph.add_nodes_from(graph_data['nodes'])

            for u, v, d in graph_data['edges']:
                self.graph.add_edge(u, v, **d)

            self.od_pairs = graph_data['od_pairs']

            return True, f"Graph loaded from {filename}"
        except Exception as e:
            return False, f"Error loading graph: {str(e)}"

    def get_saved_graphs(self):
        if not os.path.exists(self.save_directory):
            return []
        return [f for f in os.listdir(self.save_directory) if f.endswith('.json')]
