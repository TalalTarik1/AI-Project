"""
Grid data structure for pathfinding visualization.
"""

from enum import Enum
from typing import List, Tuple, Optional, Set
import random


class CellType(Enum):
    """Types of cells in the grid."""
    EMPTY = 0
    WALL = 1
    START = 2
    END = 3
    VISITED = 4
    PATH = 5
    EXPLORING = 6


class Grid:
    """Grid class for pathfinding visualization."""
    
    def __init__(self, rows: int, cols: int):
        """
        Initialize grid.
        
        Args:
            rows: Number of rows
            cols: Number of columns
        """
        self.rows = rows
        self.cols = cols
        self.grid = [[CellType.EMPTY for _ in range(cols)] for _ in range(rows)]
        self.start_pos: Optional[Tuple[int, int]] = None
        self.end_pos: Optional[Tuple[int, int]] = None
    
    def get_cell(self, row: int, col: int) -> CellType:
        """Get cell type at position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return CellType.WALL
    
    def set_cell(self, row: int, col: int, cell_type: CellType):
        """Set cell type at position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            # Don't overwrite start/end positions
            if cell_type == CellType.WALL:
                if self.grid[row][col] == CellType.START:
                    self.start_pos = None
                elif self.grid[row][col] == CellType.END:
                    self.end_pos = None
                self.grid[row][col] = CellType.WALL
            elif cell_type == CellType.START:
                # Clear old start position
                if self.start_pos:
                    old_row, old_col = self.start_pos
                    if self.grid[old_row][old_col] == CellType.START:
                        self.grid[old_row][old_col] = CellType.EMPTY
                self.start_pos = (row, col)
                if self.grid[row][col] != CellType.END:
                    self.grid[row][col] = CellType.START
            elif cell_type == CellType.END:
                # Clear old end position
                if self.end_pos:
                    old_row, old_col = self.end_pos
                    if self.grid[old_row][old_col] == CellType.END:
                        self.grid[old_row][old_col] = CellType.EMPTY
                self.end_pos = (row, col)
            if self.grid[row][col] != CellType.START and self.grid[row][col] != CellType.END:
                self.grid[row][col] = cell_type
    
    def toggle_wall(self, row: int, col: int):
        """Toggle wall at position."""
        if self.grid[row][col] == CellType.WALL:
            self.grid[row][col] = CellType.EMPTY
        elif self.grid[row][col] == CellType.EMPTY:
            self.grid[row][col] = CellType.WALL
    
    def is_valid(self, row: int, col: int) -> bool:
        """Check if position is valid and not a wall."""
        return (0 <= row < self.rows and 
                0 <= col < self.cols and 
                self.grid[row][col] != CellType.WALL)
    
    def get_neighbors(self, row: int, col: int, diagonal: bool = False) -> List[Tuple[int, int]]:
        """
        Get valid neighbors of a cell.
        
        Args:
            row: Row position
            col: Column position
            diagonal: Whether to include diagonal neighbors
            
        Returns:
            List of (row, col) tuples
        """
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 4-directional
        
        if diagonal:
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])  # 8-directional
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid(new_row, new_col):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def clear_path(self):
        """Clear path and visited cells, keep walls, start, and end."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] in [CellType.VISITED, CellType.PATH, CellType.EXPLORING]:
                    self.grid[row][col] = CellType.EMPTY
    
    def clear_all(self):
        """Clear everything including walls."""
        self.grid = [[CellType.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.start_pos = None
        self.end_pos = None
    
    def clear_walls(self):
        """Clear only walls, keep start and end."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == CellType.WALL:
                    self.grid[row][col] = CellType.EMPTY
    
    def generate_maze_dfs(self):
        """Generate a maze using DFS algorithm."""
        self.clear_all()
        
        # Initialize all cells as walls
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid[row][col] = CellType.WALL
        
        # Start from (1, 1) - must be odd coordinates
        start_row, start_col = 1, 1
        
        def carve_path(row: int, col: int, visited: Set[Tuple[int, int]]):
            """Recursive DFS to carve maze paths."""
            visited.add((row, col))
            self.grid[row][col] = CellType.EMPTY
            
            # Randomize directions
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(directions)
            
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if (0 < new_row < self.rows - 1 and 
                    0 < new_col < self.cols - 1 and 
                    (new_row, new_col) not in visited):
                    # Carve the wall between current and new cell
                    mid_row, mid_col = row + dr // 2, col + dc // 2
                    self.grid[mid_row][mid_col] = CellType.EMPTY
                    carve_path(new_row, new_col, visited)
        
        carve_path(start_row, start_col, set())
        
        # Set start and end positions
        if self.rows > 2 and self.cols > 2:
            self.set_cell(1, 1, CellType.START)
            self.set_cell(self.rows - 2, self.cols - 2, CellType.END)
    
    def get_wall_count(self) -> int:
        """Get number of walls in the grid."""
        count = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == CellType.WALL:
                    count += 1
        return count

