import pygame
from typing import Dict, List, Tuple
from parser import Network


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

ZONE_COLORS = {
    'normal': BLUE,
    'blocked': RED,
    'restricted': YELLOW,
    'priority': GREEN
}


class Visualizer:
    def __init__(self, network: Network, turn_history: List[Dict]) -> None:
        pygame.init()
        self.width = 1024
        self.height = 768
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Drone Routing Simulation")

        self.network = network
        self.turn_history = turn_history
        self.current_turn_index = 0

        self.zone_radius = 40
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.zone_positions = self._calculate_positions()

        self.clock = pygame.time.Clock()
        self.running = True

    def _calculate_positions(self) -> Dict[str, Tuple[int, int]]:
        positions = {}

        if not self.network.zones:
            raise ValueError("Network has not zones to visualize")

        try:
            all_x = [zone.x for zone in self.network.zones.values()]
            all_y = [zone.y for zone in self.network.zones.values()]
        except AttributeError as e:
            raise ValueError(f"Zone missing coordinate attributes: {e}")

        if not all_x or not all_y:
            raise ValueError("No valid zone coordinates found")

        min_x = min(all_x)
        max_x = max(all_x)
        min_y = min(all_y)
        max_y = max(all_y)

        padding = 100

        available_width = self.width - (2 * padding)
        available_height = self.height - (2 * padding)

        if available_width <= 0 or available_height <= 0:
            raise ValueError("Window size too small for padding")

        map_width = max_x - min_x
        map_height = max_y - min_y

        if map_width == 0:
            map_width = 1
        if map_height == 0:
            map_height = 1

        scale_x = available_width / map_width
        scale_y = available_height / map_height
        scale = min(scale_x, scale_y)
        for zone_name, zone in self.network.zones.items():
            try:
                shifted_x = zone.x - min_x
                shifted_y = zone.y - min_y

                screen_x = padding + (shifted_x * scale)
                screen_y = padding + (shifted_y * scale)

                positions[zone_name] = (int(screen_x), int(screen_y))
            except (AttributeError, TypeError) as e:
                raise ValueError(f"Error processing zone {zone_name}: {e}")

        return positions

    def run(self):
        self._show_instructions()

        while self.running:
            self._handle_events()
            self._draw()
            self.clock.tick(60)
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if self.current_turn_index < len(self.turn_history) - 1:
                        self.current_turn_index += 1
                elif event.key == pygame.K_LEFT:
                    if self.current_turn_index > 0:
                        self.current_turn_index -= 1
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def _draw_connections(self):
        for connection in self.network.connection:
            zone1_name = connection.zone1.name
            zone2_name = connection.zone2.name

            pos1 = self.zone_positions[zone1_name]
            pos2 = self.zone_positions[zone2_name]

            pygame.draw.line(self.screen, GRAY, pos1, pos2)

    def _draw_zones(self):
        for zone_name, zone in self.network.zones.items():
            pos = self.zone_positions[zone_name]
            color = ZONE_COLORS.get(zone.zone_type, BLUE)

            pygame.draw.circle(self.screen, color, pos, self.zone_radius)

            text = self.font.render(zone_name, True, BLACK)
            text_rect = text.get_rect(center=pos)
            self.screen.blit(text, text_rect)

    def _draw_drones(self):
        if self.current_turn_index >= len(self.turn_history):
            return

        current_state = self.turn_history[self.current_turn_index]
        drone_positions = current_state['drone_positions']

        for drone_id, zone_name in drone_positions.items():
            zone_pos = self.zone_positions[zone_name]
            pygame.draw.circle(self.screen, RED, zone_pos, 10)

            text = self.small_font.render(f"D{drone_id}", True, WHITE)
            text_rect = text.get_rect(center=zone_pos)
            self.screen.blit(text, text_rect)
