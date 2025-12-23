"""
Pathfinding Algorithm Visualizer - Main Application
A comprehensive GUI application for visualizing pathfinding algorithms.
"""

import pygame
import sys
import time
from typing import Optional, Tuple, List
from grid import Grid, CellType
from algorithms import get_algorithm, PathfindingResult


# Color schemes
COLOR_SCHEMES = {
    'default': {
        'background': (40, 44, 52),
        'empty': (255, 255, 255),
        'wall': (30, 30, 30),
        'start': (50, 205, 50),
        'end': (220, 20, 60),
        'visited': (135, 206, 250),
        'path': (255, 215, 0),
        'exploring': (255, 165, 0),
        'text': (255, 255, 255),
        'button': (70, 130, 180),
        'button_hover': (100, 149, 237),
        'panel': (50, 50, 50)
    },
    'dark': {
        'background': (20, 20, 20),
        'empty': (240, 240, 240),
        'wall': (10, 10, 10),
        'start': (0, 255, 127),
        'end': (255, 0, 0),
        'visited': (100, 149, 237),
        'path': (255, 255, 0),
        'exploring': (255, 140, 0),
        'text': (255, 255, 255),
        'button': (60, 60, 60),
        'button_hover': (80, 80, 80),
        'panel': (30, 30, 30)
    },
    'light': {
        'background': (245, 245, 245),
        'empty': (255, 255, 255),
        'wall': (100, 100, 100),
        'start': (34, 139, 34),
        'end': (220, 20, 60),
        'visited': (173, 216, 230),
        'path': (255, 215, 0),
        'exploring': (255, 165, 0),
        'text': (0, 0, 0),
        'button': (200, 200, 200),
        'button_hover': (220, 220, 220),
        'panel': (220, 220, 220)
    }
}


class Button:
    """Button widget for GUI."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 colors: dict, font: pygame.font.Font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.colors = colors
        self.font = font
        self.hovered = False
        self.pressed = False
        self.press_timer = 0
    
    def draw(self, screen: pygame.Surface):
        """Draw the button."""
        # Determine color based on state
        if self.pressed:
            # Pressed state - darker color
            color = tuple(max(0, c - 30) for c in self.colors['button'])
            border_color = tuple(max(0, c - 20) for c in self.colors['text'])
            # Slight offset to show pressed effect
            draw_rect = pygame.Rect(self.rect.x + 1, self.rect.y + 1, self.rect.width, self.rect.height)
        elif self.hovered:
            color = self.colors['button_hover']
            border_color = self.colors['text']
            draw_rect = self.rect
        else:
            color = self.colors['button']
            border_color = self.colors['text']
            draw_rect = self.rect
        
        pygame.draw.rect(screen, color, draw_rect)
        pygame.draw.rect(screen, border_color, draw_rect, 2)
        
        # Adjust text position when pressed
        text_offset = (1, 1) if self.pressed else (0, 0)
        text_surface = self.font.render(self.text, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=(draw_rect.centerx + text_offset[0], 
                                                   draw_rect.centery + text_offset[1]))
        screen.blit(text_surface, text_rect)
        
        # Update press timer
        if self.pressed:
            self.press_timer += 1
            if self.press_timer > 10:  # Reset after ~10 frames
                self.pressed = False
                self.press_timer = 0
    
    def check_hover(self, pos: Tuple[int, int]):
        """Check if mouse is hovering over button."""
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
    
    def check_click(self, pos: Tuple[int, int]) -> bool:
        """Check if button is clicked."""
        if self.rect.collidepoint(pos):
            self.pressed = True
            self.press_timer = 0
            return True
        return False

class PathfindingVisualizer:
    """Main application class."""
    
    def __init__(self):
        pygame.init()
        
        # Window settings
        self.WINDOW_WIDTH = 1400
        self.WINDOW_HEIGHT = 900
        self.GRID_X_OFFSET = 300
        self.GRID_Y_OFFSET = 50
        self.PANEL_WIDTH = 280
        
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Pathfinding Algorithm Visualizer")
        
        # Grid settings
        self.grid_rows = 30
        self.grid_cols = 40
        self.grid_sizes = {
            'small': (20, 30),
            'medium': (30, 40),
            'large': (40, 50)
        }
        self.current_grid_size = 'medium'
        self.update_cell_size()
        
        rows, cols = self.grid_sizes[self.current_grid_size]
        self.grid_rows = rows
        self.grid_cols = cols
        self.grid = Grid(self.grid_rows, self.grid_cols)
        self.update_cell_size()
        self.grid.set_cell(1, 1, CellType.START)
        self.grid.set_cell(self.grid_rows - 2, self.grid_cols - 2, CellType.END)
        
        # Algorithm settings
        self.current_algorithm = 'bfs'
        self.algorithms = ['bfs', 'dfs', 'astar', 'dijkstra']
        self.algorithm_names = {
            'bfs': 'BFS (Breadth-First Search)',
            'dfs': 'DFS (Depth-First Search)',
            'astar': 'A* (A-Star)',
            'dijkstra': "Dijkstra's Algorithm"
        }
        
        # Visualization state
        self.is_visualizing = False
        self.visualization_speed = 5  # Steps per frame (higher = faster)
        self.result: Optional[PathfindingResult] = None
        self.visited_cells: List[Tuple[int, int]] = []
        self.path_cells: List[Tuple[int, int]] = []
        self.exploring_cells: List[Tuple[int, int]] = []
        
        # Color scheme
        self.color_scheme = 'default'
        self.colors = COLOR_SCHEMES[self.color_scheme]
        
        # Fonts
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 32)
        self.font_title = pygame.font.Font(None, 36)
        
        # UI state
        self.drawing_walls = False
        self.erasing_walls = False
        self.selected_algorithm_index = 0
        
        # Statistics
        self.stats = {
            'path_length': 0,
            'nodes_explored': 0,
            'execution_time': 0.0
        }
        
        # Create buttons
        self.create_buttons()
    
    def update_cell_size(self):
        """Update cell size based on current grid dimensions."""
        available_width = max(1, self.WINDOW_WIDTH - self.GRID_X_OFFSET - 20)
        available_height = max(1, self.WINDOW_HEIGHT - self.GRID_Y_OFFSET - 20)
        self.cell_size = max(1, min(
            available_width // self.grid_cols,
            available_height // self.grid_rows
        ))
    
    def handle_resize(self, size: Tuple[int, int]):
        """Handle window resize event."""
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = size
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.RESIZABLE)
        self.update_cell_size()
    
    def resize_grid(self, size: str):
        """Resize the grid."""
        if size in self.grid_sizes and not self.is_visualizing:
            rows, cols = self.grid_sizes[size]
            old_start = self.grid.start_pos
            old_end = self.grid.end_pos
            
            # Create new grid
            self.grid = Grid(rows, cols)
            self.grid_rows = rows
            self.grid_cols = cols
            self.current_grid_size = size
            self.update_cell_size()
            
            # Restore start and end positions if they fit
            if old_start and old_start[0] < rows and old_start[1] < cols:
                self.grid.set_cell(old_start[0], old_start[1], CellType.START)
            else:
                self.grid.set_cell(1, 1, CellType.START)
            
            if old_end and old_end[0] < rows and old_end[1] < cols:
                self.grid.set_cell(old_end[0], old_end[1], CellType.END)
            else:
                self.grid.set_cell(rows - 2, cols - 2, CellType.END)
            
            # Clear visualization
            self.visited_cells.clear()
            self.path_cells.clear()
            self.exploring_cells.clear()
            self.result = None
    
    def create_buttons(self):
        """Create UI buttons."""
        self.buttons = {}
        button_height = 35
        button_spacing = 8
        section_spacing = 25  # Space between sections
        
        # Algorithm selection buttons (start at y=85, label at 60)
        button_y = 85
        for i, alg in enumerate(self.algorithms):
            self.buttons[f'alg_{alg}'] = Button(
                10, button_y, 130, button_height,
                alg.upper(), self.colors, self.font_small
            )
            button_y += button_height + button_spacing
        
        # Control buttons (start after algorithms with spacing)
        control_start_y = button_y + section_spacing
        control_buttons = [
            ('start', 'Start'),
            ('clear', 'Clear Path'),
            ('reset', 'Reset Grid'),
            ('maze', 'Generate Maze'),
            ('clear_walls', 'Clear Walls')
        ]
        
        control_y = control_start_y
        for key, text in control_buttons:
            self.buttons[key] = Button(10, control_y, 130, button_height, text, self.colors, self.font_small)
            control_y += button_height + button_spacing
        
        # Speed control buttons (below controls with spacing)
        speed_start_y = control_y + section_spacing
        self.buttons['speed_down'] = Button(10, speed_start_y, 60, button_height, '-', self.colors, self.font_medium)
        self.buttons['speed_up'] = Button(80, speed_start_y, 60, button_height, '+', self.colors, self.font_medium)
        
        # Color scheme buttons (below speed with spacing)
        color_start_y = speed_start_y + button_height + section_spacing
        self.buttons['color_default'] = Button(10, color_start_y, 80, button_height, 'Default', self.colors, self.font_small)
        self.buttons['color_dark'] = Button(95, color_start_y, 80, button_height, 'Dark', self.colors, self.font_small)
        self.buttons['color_light'] = Button(180, color_start_y, 80, button_height, 'Light', self.colors, self.font_small)
        
        # Grid size buttons (below color with spacing)
        grid_start_y = color_start_y + button_height + section_spacing
        self.buttons['grid_small'] = Button(10, grid_start_y, 80, button_height, 'Small', self.colors, self.font_small)
        self.buttons['grid_medium'] = Button(95, grid_start_y, 80, button_height, 'Medium', self.colors, self.font_small)
        self.buttons['grid_large'] = Button(180, grid_start_y, 80, button_height, 'Large', self.colors, self.font_small)
        
        # Store label positions for drawing
        self.label_positions = {
            'algorithm': 60,
            'controls': control_start_y - 20,
            'speed': speed_start_y - 20,
            'color': color_start_y - 20,
            'grid': grid_start_y - 20
        }
    
    def get_grid_pos(self, mouse_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert mouse position to grid coordinates."""
        x, y = mouse_pos
        x -= self.GRID_X_OFFSET
        y -= self.GRID_Y_OFFSET
        
        if x < 0 or y < 0:
            return None
        
        col = x // self.cell_size
        row = y // self.cell_size
        
        if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
            return (row, col)
        return None
    
    def draw_grid(self):
        """Draw the grid."""
        grid_surface = pygame.Surface((
            self.grid_cols * self.cell_size,
            self.grid_rows * self.cell_size
        ))
        grid_surface.fill(self.colors['background'])
        
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                cell_type = self.grid.get_cell(row, col)
                x = col * self.cell_size
                y = row * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size - 1, self.cell_size - 1)
                
                # Determine color based on cell type
                if cell_type == CellType.WALL:
                    color = self.colors['wall']
                elif cell_type == CellType.START:
                    color = self.colors['start']
                elif cell_type == CellType.END:
                    color = self.colors['end']
                elif cell_type == CellType.PATH or (row, col) in self.path_cells:
                    color = self.colors['path']
                elif cell_type == CellType.VISITED or (row, col) in self.visited_cells:
                    color = self.colors['visited']
                elif cell_type == CellType.EXPLORING or (row, col) in self.exploring_cells:
                    color = self.colors['exploring']
                else:
                    color = self.colors['empty']
                
                pygame.draw.rect(grid_surface, color, rect)
        
        self.screen.blit(grid_surface, (self.GRID_X_OFFSET, self.GRID_Y_OFFSET))
    
    def draw_panel(self):
        """Draw the control panel."""
        panel_rect = pygame.Rect(0, 0, self.PANEL_WIDTH, self.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, self.colors['panel'], panel_rect)
        pygame.draw.line(self.screen, self.colors['text'], 
                        (self.PANEL_WIDTH, 0), (self.PANEL_WIDTH, self.WINDOW_HEIGHT), 2)
        
        # Title
        title = self.font_title.render("Pathfinding Visualizer", True, self.colors['text'])
        self.screen.blit(title, (10, 10))
        
        # Algorithm selection
        alg_text = self.font_medium.render("Algorithm:", True, self.colors['text'])
        self.screen.blit(alg_text, (10, self.label_positions['algorithm']))
        
        # Draw algorithm buttons
        for i, alg in enumerate(self.algorithms):
            button = self.buttons[f'alg_{alg}']
            if alg == self.current_algorithm:
                # Highlight selected algorithm
                pygame.draw.rect(self.screen, self.colors['path'], button.rect, 3)
            button.draw(self.screen)
        
        # Draw control buttons
        control_text = self.font_medium.render("Controls:", True, self.colors['text'])
        self.screen.blit(control_text, (10, self.label_positions['controls']))
        
        for key in ['start', 'clear', 'reset', 'maze', 'clear_walls']:
            self.buttons[key].draw(self.screen)
        
        # Speed control (label above buttons)
        speed_text = self.font_medium.render(f"Speed: {self.visualization_speed}", True, self.colors['text'])
        self.screen.blit(speed_text, (10, self.label_positions['speed']))
        self.buttons['speed_down'].draw(self.screen)
        self.buttons['speed_up'].draw(self.screen)
        
        # Color scheme (label above buttons)
        color_text = self.font_medium.render("Color Scheme:", True, self.colors['text'])
        self.screen.blit(color_text, (10, self.label_positions['color']))
        self.buttons['color_default'].draw(self.screen)
        self.buttons['color_dark'].draw(self.screen)
        self.buttons['color_light'].draw(self.screen)
        
        # Grid size (label above buttons)
        grid_text = self.font_medium.render("Grid Size:", True, self.colors['text'])
        self.screen.blit(grid_text, (10, self.label_positions['grid']))
        self.buttons['grid_small'].draw(self.screen)
        self.buttons['grid_medium'].draw(self.screen)
        self.buttons['grid_large'].draw(self.screen)
        
        # Statistics (positioned after grid buttons with spacing)
        stats_y = self.label_positions['grid'] + 60
        stats_text = self.font_medium.render("Statistics:", True, self.colors['text'])
        self.screen.blit(stats_text, (10, stats_y))
        
        stats_y += 30
        if self.result:
            stats = [
                f"Path Length: {self.stats['path_length']}",
                f"Nodes Explored: {self.stats['nodes_explored']}",
                f"Time: {self.stats['execution_time']:.3f}s"
            ]
            if not self.result.found:
                stats.insert(0, "Path: Not Found")
            else:
                stats.insert(0, "Path: Found")
            
            for stat in stats:
                stat_surface = self.font_small.render(stat, True, self.colors['text'])
                self.screen.blit(stat_surface, (10, stats_y))
                stats_y += 25
        
        # Instructions (positioned after statistics with spacing)
        instructions_y = stats_y + 100
        inst_text = self.font_medium.render("Instructions:", True, self.colors['text'])
        self.screen.blit(inst_text, (10, instructions_y))
        
        instructions = [
            "Left Click: Draw walls",
            "Right Click: Set start",
            "Middle Click: Set end",
            "Space: Start visualization",
            "C: Clear path",
            "R: Reset grid",
            "M: Generate maze"
        ]
        
        instructions_y += 30
        for inst in instructions:
            inst_surface = self.font_small.render(inst, True, self.colors['text'])
            self.screen.blit(inst_surface, (10, instructions_y))
            instructions_y += 20
    
    def visualize_algorithm(self):
        """Run the selected algorithm with visualization."""
        if not self.grid.start_pos or not self.grid.end_pos:
            return
        
        self.is_visualizing = True
        self.grid.clear_path()
        self.visited_cells.clear()
        self.path_cells.clear()
        self.exploring_cells.clear()
        
        start_time = time.time()
        
        # Get algorithm function
        algorithm = get_algorithm(self.current_algorithm)
        
        # Run algorithm
        self.result = algorithm(
            self.grid,
            self.grid.start_pos,
            self.grid.end_pos
        )
        
        end_time = time.time()
        self.stats['execution_time'] = end_time - start_time
        self.stats['path_length'] = self.result.path_length
        self.stats['nodes_explored'] = self.result.nodes_explored
        
        # Animate the result
        self.animate_result()
        
        self.is_visualizing = False
    
    def animate_result(self):
        """Animate the algorithm result."""
        if not self.result:
            return
        
        # Animate visited cells
        visited_index = 0
        exploring_index = 0
        path_index = 0
        
        clock = pygame.time.Clock()
        max_frames = 10000  # Safety limit to prevent infinite loops
        frame_count = 0
        
        while (frame_count < max_frames and 
               (visited_index < len(self.result.visited) or 
                exploring_index < len(self.result.exploring) or
                path_index < len(self.result.path))):
            
            # Process events to keep app responsive
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Skip to end of animation
                        exploring_index = len(self.result.exploring)
                        visited_index = len(self.result.visited)
                        path_index = len(self.result.path) if self.result.found else 0
                        break
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.size)
            
            # Add exploring cells
            for _ in range(self.visualization_speed):
                if exploring_index < len(self.result.exploring):
                    cell = self.result.exploring[exploring_index]
                    if cell not in self.visited_cells:
                        self.exploring_cells.append(cell)
                    exploring_index += 1
                else:
                    break
            
            # Move exploring to visited
            for _ in range(self.visualization_speed):
                if self.exploring_cells:
                    cell = self.exploring_cells.pop(0)
                    if cell not in self.visited_cells:
                        self.visited_cells.append(cell)
                else:
                    break
            
            # Draw path if found
            if self.result.found:
                # Check if all visited cells are shown before showing path
                if exploring_index >= len(self.result.exploring) and not self.exploring_cells:
                    for _ in range(self.visualization_speed * 2):
                        if path_index < len(self.result.path):
                            cell = self.result.path[path_index]
                            if cell not in self.path_cells:
                                self.path_cells.append(cell)
                            path_index += 1
                        else:
                            break
            
            self.draw()
            clock.tick(60)
            frame_count += 1
            
            # Check if animation is complete
            if (exploring_index >= len(self.result.exploring) and
                not self.exploring_cells and
                (not self.result.found or path_index >= len(self.result.path))):
                break
        
        # Ensure all cells are shown at the end
        if self.result:
            for cell in self.result.visited:
                if cell not in self.visited_cells:
                    self.visited_cells.append(cell)
            if self.result.found:
                for cell in self.result.path:
                    if cell not in self.path_cells:
                        self.path_cells.append(cell)
        
        self.draw()
    
    def draw(self):
        """Draw everything."""
        self.screen.fill(self.colors['background'])
        self.draw_grid()
        self.draw_panel()
        pygame.display.flip()
    
    def handle_mouse_click(self, pos: Tuple[int, int], button: int):
        """Handle mouse click events."""
        # Check button clicks (only left button for buttons)
        if button == 1:  # Left mouse button only for UI buttons
            for key, btn in self.buttons.items():
                if btn.check_click(pos):
                    if key.startswith('alg_'):
                        self.current_algorithm = key.split('_')[1]
                    elif key == 'start':
                        if not self.is_visualizing:
                            self.visualize_algorithm()
                    elif key == 'clear':
                        if not self.is_visualizing:
                            self.grid.clear_path()
                            self.visited_cells.clear()
                            self.path_cells.clear()
                            self.exploring_cells.clear()
                            self.result = None
                    elif key == 'reset':
                        if not self.is_visualizing:
                            self.grid.clear_all()
                            self.grid.set_cell(1, 1, CellType.START)
                            self.grid.set_cell(self.grid_rows - 2, self.grid_cols - 2, CellType.END)
                            self.visited_cells.clear()
                            self.path_cells.clear()
                            self.exploring_cells.clear()
                            self.result = None
                    elif key == 'maze':
                        if not self.is_visualizing:
                            self.grid.generate_maze_dfs()
                    elif key == 'clear_walls':
                        if not self.is_visualizing:
                            self.grid.clear_walls()
                    elif key == 'speed_down':
                        self.visualization_speed = max(1, self.visualization_speed - 1)
                    elif key == 'speed_up':
                        self.visualization_speed = min(50, self.visualization_speed + 1)
                    elif key == 'color_default':
                        self.color_scheme = 'default'
                        self.colors = COLOR_SCHEMES[self.color_scheme]
                        self.create_buttons()
                    elif key == 'color_dark':
                        self.color_scheme = 'dark'
                        self.colors = COLOR_SCHEMES[self.color_scheme]
                        self.create_buttons()
                    elif key == 'color_light':
                        self.color_scheme = 'light'
                        self.colors = COLOR_SCHEMES[self.color_scheme]
                        self.create_buttons()
                    elif key == 'grid_small':
                        self.resize_grid('small')
                    elif key == 'grid_medium':
                        self.resize_grid('medium')
                    elif key == 'grid_large':
                        self.resize_grid('large')
                    return
        
        # Handle grid clicks
        grid_pos = self.get_grid_pos(pos)
        if grid_pos and not self.is_visualizing:
            row, col = grid_pos
            
            if button == 1:  # Left click - toggle wall
                if self.grid.get_cell(row, col) not in [CellType.START, CellType.END]:
                    self.grid.toggle_wall(row, col)
            elif button == 3:  # Right click - set start
                self.grid.set_cell(row, col, CellType.START)
            elif button == 2:  # Middle click - set end
                self.grid.set_cell(row, col, CellType.END)
    
    def handle_mouse_drag(self, pos: Tuple[int, int], button: int):
        """Handle mouse drag for drawing walls."""
        if button == 1 and not self.is_visualizing:  # Left mouse button
            grid_pos = self.get_grid_pos(pos)
            if grid_pos:
                row, col = grid_pos
                if self.grid.get_cell(row, col) not in [CellType.START, CellType.END]:
                    self.grid.set_cell(row, col, CellType.WALL)
    
    def run(self):
        """Main application loop."""
        clock = pygame.time.Clock()
        running = True
        mouse_down = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.is_visualizing:
                        self.visualize_algorithm()
                    elif event.key == pygame.K_c:
                        self.grid.clear_path()
                        self.visited_cells.clear()
                        self.path_cells.clear()
                        self.exploring_cells.clear()
                        self.result = None
                    elif event.key == pygame.K_r:
                        self.grid.clear_all()
                        self.grid.set_cell(1, 1, CellType.START)
                        self.grid.set_cell(self.grid_rows - 2, self.grid_cols - 2, CellType.END)
                        self.visited_cells.clear()
                        self.path_cells.clear()
                        self.exploring_cells.clear()
                        self.result = None
                    elif event.key == pygame.K_m:
                        if not self.is_visualizing:
                            self.grid.generate_maze_dfs()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_down = True
                    self.handle_mouse_click(event.pos, event.button)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_down = False
                
                elif event.type == pygame.MOUSEMOTION:
                    # Check button hovers
                    for btn in self.buttons.values():
                        btn.check_hover(event.pos)
                    
                    # Handle mouse drag for drawing
                    if mouse_down:
                        self.handle_mouse_drag(event.pos, event.buttons[0])
                
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.size)
            
            self.draw()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    """Main entry point."""
    app = PathfindingVisualizer()
    app.run()


if __name__ == "__main__":
    main()

