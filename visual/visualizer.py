import pygame
import pygame.gfxdraw
from typing import Dict, List, Tuple
from parser import Network


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARKBLUE = (34, 40, 49)

ZONE_COLORS = {
    'normal': BLUE,
    'blocked': RED,
    'restricted': YELLOW,
    'priority': GREEN
}


class Visualizer:
    """Interactive pygame-based visualiser for the drone routing simulation."""

    def __init__(self, network: Network, turn_history: List[Dict]) -> None:
        """Initialise the visualiser window and pre compute zone positions."""
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        pygame.display.set_caption("Drone Routing Simulation")

        self.network = network
        self.turn_history = turn_history
        self.current_turn_index = 0

        # Scale visual parameters to the number of zones in the network.
        num_zones = len(network.zones)
        if num_zones > 20:
            self.zone_radius = 25
            self.padding = 80
        elif num_zones > 10:
            self.zone_radius = 35
            self.padding = 100
        else:
            self.zone_radius = 40
            self.padding = 120

        self.font = pygame.font.SysFont("Arial", 20, bold=False)
        self.small_font = pygame.font.Font(None, 16)
        self.zone_positions = self._calculate_positions(self.padding)

        self.clock = pygame.time.Clock()
        self.running = True

    def _calculate_positions(self, padding: int) -> Dict[str, Tuple[int, int]]:
        """Map each zone's logical coordinates to pixel positions on screen."""
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

        y_offset = 100
        for zone_name, zone in self.network.zones.items():
            try:
                shifted_x = zone.x - min_x
                shifted_y = zone.y - min_y

                shifted_x = shifted_x * 1.0
                if len(self.network.zones) > 30:
                    shifted_y = shifted_y * 1.5
                else:
                    shifted_y = shifted_y * 0.9

                spacing_multiplier = 1
                shifted_x = shifted_x * spacing_multiplier
                shifted_y = shifted_y * spacing_multiplier
                screen_x = padding + (shifted_x * scale)
                screen_y = self.height - (
                    padding + y_offset + (shifted_y * scale)
                )

                positions[zone_name] = (int(screen_x), int(screen_y))
            except (AttributeError, TypeError) as e:
                raise ValueError(f"Error processing zone {zone_name}: {e}")

        return positions

    def run(self) -> None:
        """Start the main event loop.

        Displays the control instructions overlay, then enters a 60 fps
        render loop until self.running is set to False
        """
        self._show_instructions()

        while self.running:
            self._handle_events()
            self._draw()
            self.clock.tick(60)
        pygame.quit()

    def _handle_events(self) -> None:
        """Process the pygame event queue for the current frame."""
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

    def _draw_connections(self) -> None:
        """Draw all network connections as grey lines between zone positions."""
        for connection in self.network.connection:
            zone1_name = connection.zone1.name
            zone2_name = connection.zone2.name

            pos1 = self.zone_positions[zone1_name]
            pos2 = self.zone_positions[zone2_name]

            pygame.draw.line(self.screen, GRAY, pos1, pos2, 4)

    def _draw_zones(self) -> None:
        """Draw all zones as anti aliased filled circles with name labels."""
        for zone_name, zone in self.network.zones.items():
            pos = self.zone_positions[zone_name]
            color = ZONE_COLORS.get(zone.zone_type, BLUE)

            pygame.gfxdraw.filled_circle(
                self.screen, pos[0], pos[1], self.zone_radius, color
            )
            pygame.gfxdraw.aacircle(
                self.screen, pos[0], pos[1], self.zone_radius, color
            )
            text = self.font.render(zone_name, True, WHITE)
            text_rect = text.get_rect(
                center=(pos[0], pos[1] + self.zone_radius + 15)
            )
            self.screen.blit(text, text_rect)

    def _draw_drones(self) -> None:
        """Draw all drones at their current positions for the displayed turn."""
        if self.current_turn_index >= len(self.turn_history):
            return

        current_state = self.turn_history[self.current_turn_index]
        drone_positions = current_state['drone_positions']

        for drone_id, zone_name in drone_positions.items():
            zone_pos = self.zone_positions[zone_name]
            pygame.draw.circle(self.screen, RED, zone_pos, 15)

            text = self.small_font.render(f"D{drone_id}", True, WHITE)
            text_rect = text.get_rect(center=zone_pos)
            self.screen.blit(text, text_rect)

    def _draw_ui(self) -> None:
        """Render the HUD overlay showing the cumulative turn cost."""
        if self.current_turn_index < len(self.turn_history):
            total_cost = sum(
                t.get("turn_cost", 1)
                for t in self.turn_history[:self.current_turn_index + 1]
            )
            text = self.font.render(f"Turn: {total_cost}", True, WHITE)
            self.screen.blit(text, (10, 10))

    def _draw(self) -> None:
        """Compose and render a complete frame to the display."""
        self.screen.fill(DARKBLUE)
        self._draw_connections()
        self._draw_zones()
        self._draw_drones()
        self._draw_ui()
        pygame.display.flip()

    def _show_instructions(self) -> None:
        """Display a full-screen instructions overlay and wait for a keypress."""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)

        instructions = [
            "=== DRONE SIMULATION CONTROLS ===",
            "",
            "→ (Right Arrow): Advance to next turn",
            "← (Left Arrow): Go back to previous turn",
            "ESC: Exit simulation",
            "",
            "Press any key to start..."
        ]

        self.screen.fill(WHITE)
        self.screen.blit(overlay, (0, 0))

        y_offset = self.height // 2 - (len(instructions) * 30) // 2
        for line in instructions:
            text = self.font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 35

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    waiting = False
