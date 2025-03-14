import pygame

from graph_operations import GraphManager
from interface import Window
from real_graphs import msa
from result_overlay import ResultOverlay


def clear_input_boxes(boxes):
    for box in boxes:
        box.text = ""
        box._update_surface()


def run_msa_calculation(graph, od_pairs, result_overlay, window):
    calculation_graph = graph.copy()

    formatted_od_pairs = [(origin, destination, demand) for origin, destination, demand in od_pairs]

    result_graph = msa(calculation_graph, formatted_od_pairs)

    result_overlay.prepare_result(result_graph, window.window.get_width(), window.window.get_height())


def main():
    graph_manager = GraphManager()

    window = Window(graph_manager)
    result_overlay = ResultOverlay()
    window.draw_graph()

    node_inputs = [window.node_input]
    edge_inputs = [window.node1_input, window.node2_input, window.weight_input, window.capacity_input]
    od_inputs = [window.origin_input, window.destination_input, window.demand_input]
    file_inputs = [window.filename_input]
    all_inputs = node_inputs + edge_inputs + od_inputs + file_inputs

    running = True
    while running:
        # Draw UI based on whether results are visible
        if not result_overlay.visible:
            window.draw_ui()
        else:
            window.screen.fill(window.bg_color)
            result_overlay.draw(window.screen)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle result overlay events first
            if result_overlay.visible:
                if result_overlay.handle_event(event):
                    continue

            # Only handle UI events when overlay is not visible
            if not result_overlay.visible:
                for box in all_inputs:
                    box.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if window.add_node_button.is_clicked(event.pos):
                        if window.add_node(window.node_input.text):
                            clear_input_boxes(node_inputs)

                    elif window.add_edge_button.is_clicked(event.pos):
                        try:
                            weight = float(window.weight_input.text) if window.weight_input.text else 1
                            capacity = float(window.capacity_input.text) if window.capacity_input.text else 100
                            if window.add_edge(window.node1_input.text, window.node2_input.text, weight, capacity):
                                clear_input_boxes(edge_inputs)
                        except ValueError:
                            window._set_status("Invalid weight or capacity value", is_error=True)

                    elif window.clear_button.is_clicked(event.pos):
                        window.clear_graph()

                    elif window.add_od_button.is_clicked(event.pos):
                        try:
                            demand = float(window.demand_input.text) if window.demand_input.text else 0
                            if window.add_od_pair(window.origin_input.text, window.destination_input.text, demand):
                                clear_input_boxes(od_inputs)
                        except ValueError:
                            window._set_status("Invalid demand value", is_error=True)

                    elif window.save_button.is_clicked(event.pos):
                        window.save_current_graph(window.filename_input.text)

                    elif window.load_button.is_clicked(event.pos):
                        if window.load_saved_graph(window.filename_input.text):
                            clear_input_boxes([window.filename_input])

                    elif window.calculate_button.is_clicked(event.pos):
                        if graph_manager.graph.number_of_nodes() > 0 and len(graph_manager.od_pairs) > 0:
                            window._set_status("Running MSA calculation...")
                            run_msa_calculation(graph_manager.graph, graph_manager.od_pairs, result_overlay, window)
                        else:
                            window._set_status("Cannot calculate: Graph or OD pairs missing", is_error=True)

                for box in all_inputs:
                    box.update()

    pygame.quit()


if __name__ == "__main__":
    main()
