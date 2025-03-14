import io

import matplotlib.pyplot as plt
import networkx as nx
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
        scale = min(self.width / img_w * 0.9, self.height / img_h * 0.8)
        new_w, new_h = int(img_w * scale), int(img_h * scale)

        scaled_surface = pygame.transform.smoothscale(result_surface, (new_w, new_h))

        pos_x = (self.width - new_w) // 2
        pos_y = (self.height - new_h) // 2 - 20
        self.surface.blit(scaled_surface, (pos_x, pos_y))

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

    def create_result_surface(self, graph):
        fig = plt.figure(figsize=(10, 8), dpi=100)
        plt.title("MSA Traffic Assignment Results", fontsize=14)

        pos = nx.spring_layout(graph, seed=42)

        nx.draw_networkx_nodes(graph, pos,
                               node_color="#66b3ff",
                               edgecolors="#1f78b4",
                               node_size=700)

        edge_widths = [data.get("volume", 0) / 5 + 1 for _, _, data in graph.edges(data=True)]
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
