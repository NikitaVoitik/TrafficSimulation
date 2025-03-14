import io

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pygame


class ResultOverlay:
    def __init__(self):
        self.visible = False
        self.surface = None
        self.close_button = None
        self.bg_color = pygame.Color(245, 246, 250)
        self.font = pygame.font.SysFont('Arial', 16)

    def prepare_result(self, graph, window_width, window_height):
        self.width = window_width
        self.height = window_height
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(self.bg_color)

        result_surface = self.create_result_surface(graph)

        img_w, img_h = result_surface.get_size()
        scale = min(self.width / img_w * 0.9, self.height / img_h * 0.75)
        new_w, new_h = int(img_w * scale), int(img_h * scale)

        scaled_surface = pygame.transform.smoothscale(result_surface, (new_w, new_h))

        pos_x = (self.width - new_w) // 2
        pos_y = (self.height - new_h) // 2 - 50
        self.surface.blit(scaled_surface, (pos_x, pos_y))

        stats_y = pos_y + new_h + 10
        self.draw_statistics(graph, stats_y)

        button_width, button_height = 150, 35
        button_x = (self.width - button_width) // 2
        button_y = self.height - button_height - 40
        self.close_button = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(self.surface, pygame.Color(52, 152, 219), self.close_button, border_radius=5)

        txt_surface = self.font.render("Close Results", True, pygame.Color(255, 255, 255))
        text_x = button_x + (button_width - txt_surface.get_width()) // 2
        text_y = button_y + (button_height - txt_surface.get_height()) // 2
        self.surface.blit(txt_surface, (text_x, text_y))

        self.visible = True

    def draw_statistics(self, graph, start_y):
        title_font = pygame.font.SysFont('Arial', 20, bold=True)
        stats_font = pygame.font.SysFont('Arial', 16)

        edge_costs = []
        total_cost = 0
        total_volume = 0
        total_time = 0

        for u, v, data in graph.edges(data=True):
            volume = data.get("volume", 0)
            travel_time = data.get("travel_time", 0)
            edge_cost = volume * travel_time

            edge_costs.append((u, v, travel_time, volume, edge_cost))
            total_cost += edge_cost
            total_volume += volume
            total_time += travel_time

        if edge_costs:
            min_edge = min(edge_costs, key=lambda x: x[2])
            max_edge = max(edge_costs, key=lambda x: x[2])
            min_cost_edge = min(edge_costs, key=lambda x: x[4])
            max_cost_edge = max(edge_costs, key=lambda x: x[4])
            avg_cost = total_cost / total_volume if total_volume > 0 else 0
        else:
            min_edge = max_edge = min_cost_edge = max_cost_edge = (None, None, 0, 0, 0)
            avg_cost = 0

        title = title_font.render("Network Statistics", True, pygame.Color(30, 30, 30))
        title_x = (self.width - title.get_width()) // 2
        self.surface.blit(title, (title_x, start_y))

        stats_texts = [
            f"Min travel time: {min_edge[2]:.2f} (Edge {min_edge[0]}-{min_edge[1]})",
            f"Max travel time: {max_edge[2]:.2f} (Edge {max_edge[0]}-{max_edge[1]})",
            f"Min cost path: {min_cost_edge[4]:.2f} (Edge {min_cost_edge[0]}-{min_cost_edge[1]})",
            f"Max cost path: {max_cost_edge[4]:.2f} (Edge {max_cost_edge[0]}-{max_cost_edge[1]})",
            f"Total network cost: {total_cost:.2f}",
            f"Average travel cost: {avg_cost:.2f}",
            f"Total travel time: {round(total_time, 2)}"
        ]

        y_offset = start_y + 30
        i = 0
        cur_width = self.width // 2
        for text in stats_texts:
            i += 1
            txt_surface = stats_font.render(text, True, pygame.Color(30, 30, 30))
            txt_x = (cur_width - txt_surface.get_width()) // 2
            self.surface.blit(txt_surface, (txt_x, y_offset))
            y_offset += 25
            if i == 3:
                y_offset -= 25 * i
                cur_width = self.width + self.width // 2

    def create_result_surface(self, graph):
        fig = plt.figure(figsize=(10, 8), dpi=100)
        plt.title("MSA Traffic Assignment Results", fontsize=14)

        pos = nx.spring_layout(graph, seed=42)

        nx.draw_networkx_nodes(graph, pos,
                               node_color="#66b3ff",
                               edgecolors="#1f78b4",
                               node_size=700)

        volumes = [data.get("volume", 0) for _, _, data in graph.edges(data=True)]
        max_volume = max(volumes) if volumes else 1
        min_volume = min(volumes) if volumes else 0

        if max_volume - min_volume > 100:
            edge_widths = [1 + 5 * (np.log1p(data.get("volume", 0)) / np.log1p(max_volume))
                           for _, _, data in graph.edges(data=True)]
        else:
            edge_widths = []
            for _, _, data in graph.edges(data=True):
                vol = data.get("volume", 0)
                if max_volume == min_volume:
                    width = 2
                else:
                    width = 1 + 7 * ((vol - min_volume) / (max_volume - min_volume))
                edge_widths.append(width)

        nx.draw_networkx_edges(graph, pos,
                               width=edge_widths,
                               edge_color="#808080",
                               alpha=0.7)

        nx.draw_networkx_labels(graph, pos, font_size=12, font_color="white", font_weight="bold")

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

        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image = pygame.image.load(buffer)
        buffer.close()
        plt.close(fig)

        return image

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.close_button and self.close_button.collidepoint(event.pos):
                self.visible = False
                return True

        return False

    def draw(self, screen):
        if self.visible and self.surface:
            screen.blit(self.surface, (0, 0))
