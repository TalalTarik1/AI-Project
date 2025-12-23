"""
PUZZLE LOGIC MODULE - Step 2: Understanding the Game Rules

This module handles the N-Puzzle game mechanics (supports 8, 15, 24 puzzles):
- Board representation (NxN grid with numbers and one empty space)
- Valid moves (up, down, left, right)
- Goal state checking
- Puzzle validation

Supported Sizes:
- 8-Puzzle: 3x3 grid (8 tiles + 1 empty)
- 15-Puzzle: 4x4 grid (15 tiles + 1 empty)
- 24-Puzzle: 5x5 grid (24 tiles + 1 empty)
"""

from typing import List, Tuple, Optional
import random


class Puzzle:
    """
    Represents the N-Puzzle game state and operations.
    Supports multiple grid sizes dynamically.
    """
    
    def __init__(self, size: int = 3, state: Optional[List[List[int]]] = None):
        """
        Initialize the puzzle.
        
        Args:
            size: Grid size (3 for 8-puzzle, 4 for 15-puzzle, 5 for 24-puzzle)
            state: Optional initial state. If None, starts with goal state.
        """
        if size < 3 or size > 5:
            raise ValueError("Size must be between 3 and 5")
        
        self.size = size
        self.total_tiles = size * size - 1  # e.g., 3x3 = 8 tiles, 4x4 = 15 tiles
        
        if state is None:
            self.state = self._generate_goal_state()
        else:
            self.state = [row[:] for row in state]  # Deep copy
            self.size = len(state)  # Infer size from state
    
    def _generate_goal_state(self) -> List[List[int]]:
        """
        Generate the goal state for the current puzzle size.
        
        Returns:
            2D list representing the solved puzzle
        """
        goal = []
        num = 1
        for i in range(self.size):
            row = []
            for j in range(self.size):
                if num <= self.total_tiles:
                    row.append(num)
                    num += 1
                else:
                    row.append(0)  # Empty space at the end
            goal.append(row)
        return goal
    
    @property
    def GOAL_STATE(self) -> List[List[int]]:
        """Return the goal state for this puzzle size."""
        return self._generate_goal_state()
    
    def find_empty(self) -> Tuple[int, int]:
        """
        Find the position of the empty space (0).
        
        Returns:
            Tuple (row, col) of empty space position
        """
        for i in range(self.size):
            for j in range(self.size):
                if self.state[i][j] == 0:
                    return (i, j)
        return (-1, -1)  # Should never happen
    
    def is_goal(self) -> bool:
        """
        Check if the current state is the goal state.
        
        Returns:
            True if puzzle is solved
        """
        goal = self._generate_goal_state()
        return self.state == goal
    
    def get_valid_moves(self) -> List[str]:
        """
        Get list of valid moves from current state.
        Moves: 'up', 'down', 'left', 'right' (relative to empty space)
        
        Returns:
            List of valid move directions
        """
        row, col = self.find_empty()
        valid_moves = []
        
        # Can move up if empty space is not in top row
        if row > 0:
            valid_moves.append('up')
        
        # Can move down if empty space is not in bottom row
        if row < self.size - 1:
            valid_moves.append('down')
        
        # Can move left if empty space is not in left column
        if col > 0:
            valid_moves.append('left')
        
        # Can move right if empty space is not in right column
        if col < self.size - 1:
            valid_moves.append('right')
        
        return valid_moves
    
    def make_move(self, direction: str) -> bool:
        """
        Make a move in the specified direction.
        
        Args:
            direction: 'up', 'down', 'left', or 'right'
            
        Returns:
            True if move was successful, False otherwise
        """
        if direction not in self.get_valid_moves():
            return False
        
        row, col = self.find_empty()
        
        # Calculate new position based on direction
        # Remember: moving the empty space is like moving a tile in opposite direction
        if direction == 'up':
            new_row, new_col = row - 1, col
        elif direction == 'down':
            new_row, new_col = row + 1, col
        elif direction == 'left':
            new_row, new_col = row, col - 1
        elif direction == 'right':
            new_row, new_col = row, col + 1
        
        # Swap empty space with tile
        self.state[row][col], self.state[new_row][new_col] = \
            self.state[new_row][new_col], self.state[row][col]
        
        return True
    
    def shuffle(self, moves: Optional[int] = None):
        """
        Shuffle the puzzle by making random valid moves.
        This ensures the puzzle is always solvable!
        
        Args:
            moves: Number of random moves to make. If None, uses size-appropriate default.
        """
        if moves is None:
            # More moves for larger puzzles
            moves = self.size * 50  # 3x3=150, 4x4=200, 5x5=250
        
        for _ in range(moves):
            valid_moves = self.get_valid_moves()
            if valid_moves:
                random_move = random.choice(valid_moves)
                self.make_move(random_move)
    
    def copy(self):
        """
        Create a deep copy of this puzzle.
        Important for BFS - we don't want to modify the original!
        
        Returns:
            New Puzzle instance with same state
        """
        return Puzzle(size=self.size, state=self.state)
    
    def __eq__(self, other):
        """Check if two puzzles have the same state."""
        if not isinstance(other, Puzzle):
            return False
        return self.state == other.state and self.size == other.size
    
    def __hash__(self):
        """Make puzzle hashable (needed for sets in BFS)."""
        return hash(tuple(tuple(row) for row in self.state))
    
    def __str__(self):
        """String representation for debugging."""
        return '\n'.join([' '.join(map(str, row)) for row in self.state])
    
    def is_solvable(self) -> bool:
        """
        Check if the puzzle is solvable.
        A puzzle is solvable if the number of inversions is even (for odd-sized grids).
        For even-sized grids, we also need to consider the row of the empty space.
        
        Returns:
            True if puzzle can be solved
        """
        # Flatten the 2D array
        flat = [self.state[i][j] for i in range(self.size) 
                for j in range(self.size) if self.state[i][j] != 0]
        
        # Count inversions
        inversions = 0
        for i in range(len(flat)):
            for j in range(i + 1, len(flat)):
                if flat[i] > flat[j]:
                    inversions += 1
        
        # For odd-sized grids (3x3, 5x5), solvable if inversions are even
        if self.size % 2 == 1:
            return inversions % 2 == 0
        else:
            # For even-sized grids (4x4), also consider empty space row
            empty_row, _ = self.find_empty()
            # Count from bottom (size - 1 is bottom row)
            empty_row_from_bottom = self.size - 1 - empty_row
            return (inversions + empty_row_from_bottom) % 2 == 0


# Alias for backward compatibility
Puzzle8 = Puzzle

