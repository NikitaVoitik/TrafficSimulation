import pygame


class InputBox:
    def __init__(self, x, y, w, h, text='', placeholder=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color(180, 180, 180)
        self.color_active = pygame.Color(41, 128, 185)
        self.bg_color = pygame.Color(240, 240, 240)
        self.placeholder_color = pygame.Color(150, 150, 150)
        self.color = self.color_inactive
        self.text = text
        self.placeholder = placeholder
        self.font = pygame.font.SysFont('Arial', 16)
        self.active = False
        self.border_radius = 5
        self._update_surface()

    def _update_surface(self):
        if self.text:
            self.txt_surface = self.font.render(self.text, True, self.color)
        else:
            self.txt_surface = self.font.render(self.placeholder, True, self.placeholder_color)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos) if self.rect.collidepoint(event.pos) else False
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self._update_surface()
        return None

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=self.border_radius)
        screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 7))


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.normal_color = pygame.Color(52, 152, 219)
        self.hover_color = pygame.Color(41, 128, 185)
        self.color = self.normal_color
        self.text = text
        self.font = pygame.font.SysFont('Arial', 16)
        self.txt_surface = self.font.render(text, True, pygame.Color(255, 255, 255))
        self.border_radius = 5
        self.hovered = False

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.color = self.hover_color if self.hovered else self.normal_color

        shadow_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.w, self.rect.h)
        pygame.draw.rect(screen, pygame.Color(30, 30, 30, 100), shadow_rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, self.color, self.rect, border_radius=self.border_radius)

        text_x = self.rect.x + (self.rect.w - self.txt_surface.get_width()) // 2
        text_y = self.rect.y + (self.rect.h - self.txt_surface.get_height()) // 2
        screen.blit(self.txt_surface, (text_x, text_y))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Window:
    def __init__(self, graph_manager):
        pygame.init()
        self.graph_manager = graph_manager
        self.window = pygame.display.set_mode((1200, 1000))
        self.screen = pygame.display.get_surface()
        pygame.display.set_caption('Road Network Visualizer')
        self.font = pygame.font.SysFont('Arial', 16)

        self.bg_color = pygame.Color(245, 246, 250)
        self.panel_color = pygame.Color(225, 225, 230)
        self.accent_color = pygame.Color(52, 152, 219)
        self.text_color = pygame.Color(30, 30, 30)
        self.success_color = pygame.Color(46, 204, 113)
        self.error_color = pygame.Color(231, 76, 60)

        self.graph_area = pygame.Rect(20, 20, 1160, 700)
        self.ui_area = pygame.Rect(20, 740, 1160, 240)
        self.status_message = ""
        self.status_color = self.text_color
        self.graph_image = None

        self._init_ui_elements()

    def _init_ui_elements(self):
        self.node_input = InputBox(150, 770, 200, 35, placeholder="Enter node name")
        self.node1_input = InputBox(150, 810, 200, 35, placeholder="From node")
        self.node2_input = InputBox(150, 850, 200, 35, placeholder="To node")
        self.weight_input = InputBox(150, 890, 200, 35, placeholder="Time value")

        self.origin_input = InputBox(800, 770, 200, 35, placeholder="Origin node")
        self.destination_input = InputBox(800, 810, 200, 35, placeholder="Destination node")
        self.demand_input = InputBox(800, 850, 200, 35, placeholder="Demand value")

        self.add_node_button = Button(400, 770, 170, 35, "Add Node")
        self.add_edge_button = Button(400, 830, 170, 35, "Add Edge")
        self.clear_button = Button(400, 890, 170, 35, "Clear Graph")
        self.add_od_button = Button(800, 890, 170, 35, "Add OD Pair")

        self.filename_input = InputBox(1020, 770, 150, 35, placeholder="Graph")
        self.save_button = Button(1020, 810, 150, 35, "Save Graph")
        self.load_button = Button(1020, 850, 150, 35, "Load Graph")

    def draw_graph(self):
        self.graph_image = self.graph_manager.create_graph_image(self.graph_area.width, self.graph_area.height)
        self.screen.blit(self.graph_image, (self.graph_area.x, self.graph_area.y))
        pygame.draw.rect(self.screen, self.accent_color, self.graph_area, 2, border_radius=10)

    def add_node(self, node):
        success, message = self.graph_manager.add_node(node)
        self._set_status(message, not success)
        if success:
            self.draw_graph()
        return success

    def add_edge(self, node1, node2, weight=1):
        success, message = self.graph_manager.add_edge(node1, node2, weight)
        self._set_status(message, not success)
        if success:
            self.draw_graph()
        return success

    def clear_graph(self):
        message = self.graph_manager.clear_graph()
        self._set_status(message, None)
        self.draw_graph()

    def add_od_pair(self, origin, destination, demand):
        success, message = self.graph_manager.add_od_pair(origin, destination, demand)
        self._set_status(message, not success)
        return success

    def _set_status(self, message, is_error=None):
        self.status_message = message
        if is_error is None:
            self.status_color = self.text_color
        elif is_error:
            self.status_color = self.error_color
        else:
            self.status_color = self.success_color

    def draw_ui(self):
        self.screen.fill(self.bg_color)

        if self.graph_image:
            self.screen.blit(self.graph_image, (self.graph_area.x, self.graph_area.y))
        else:
            pygame.draw.rect(self.screen, self.panel_color, self.graph_area, border_radius=10)
            pygame.draw.rect(self.screen, self.accent_color, self.graph_area, 2, border_radius=10)

        pygame.draw.rect(self.screen, self.panel_color, self.ui_area, border_radius=10)
        pygame.draw.rect(self.screen, self.accent_color, self.ui_area, 2, border_radius=10)

        self._draw_text("NODE MANAGEMENT", 50, 745, self.accent_color)
        self._draw_text("O-D PAIR CONFIGURATION", 700, 745, self.accent_color)

        self._draw_text("Node Name:", 50, 775)
        self.node_input.draw(self.screen)

        self._draw_text("Node 1:", 50, 815)
        self.node1_input.draw(self.screen)

        self._draw_text("Node 2:", 50, 855)
        self.node2_input.draw(self.screen)

        self._draw_text("Travel Time:", 50, 895)
        self.weight_input.draw(self.screen)

        self.add_node_button.draw(self.screen)
        self.add_edge_button.draw(self.screen)
        self.clear_button.draw(self.screen)

        self._draw_text("Origin:", 700, 775)
        self.origin_input.draw(self.screen)

        self._draw_text("Destination:", 700, 815)
        self.destination_input.draw(self.screen)

        self._draw_text("Demand:", 700, 855)
        self.demand_input.draw(self.screen)

        self.add_od_button.draw(self.screen)

        self._draw_text(f"OD Pairs: {len(self.graph_manager.od_pairs)}", 600, 950)
        self._draw_text(self.status_message, 50, 950, self.status_color)

        self._draw_text("SAVE & LOAD", 600, 745, self.accent_color)
        self.filename_input.draw(self.screen)
        self.save_button.draw(self.screen)
        self.load_button.draw(self.screen)

    def _draw_text(self, text, x, y, color=None):
        text_surface = self.font.render(text, True, color or self.text_color)
        self.screen.blit(text_surface, (x, y))

    def save_current_graph(self, filename):
        success, message = self.graph_manager.save_graph(filename)
        self._set_status(message, not success)
        return success

    def load_saved_graph(self, filename):
        success, message = self.graph_manager.load_graph(filename)
        if success:
            self.draw_graph()  # Redraw the graph after loading
        self._set_status(message, not success)
        return success
