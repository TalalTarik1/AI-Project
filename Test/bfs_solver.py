"""
BFS SOLVER MODULE - Step 3: Understanding Breadth-First Search

BFS (Breadth-First Search) is a graph traversal algorithm that:
1. Explores all nodes at the current depth before moving to the next level
2. Uses a queue (FIFO - First In, First Out)
3. Guarantees finding the SHORTEST path (minimum moves)

How it works for N-Puzzle:
- Start with initial state
- Generate all possible next states (1 move away)
- Then all states 2 moves away, then 3, etc.
- Stop when we reach the goal state
- This guarantees the solution has minimum moves!

Time Complexity: O(b^d) where b=branching factor, d=depth
Space Complexity: O(b^d) - stores all nodes at current level
"""

from collections import deque
from typing import List, Optional, Tuple
from puzzle_logic import Puzzle


class BFSSolver:
    """
    Solves the N-Puzzle using Breadth-First Search algorithm.
    Works with any puzzle size (3x3, 4x4, 5x5, etc.)
    """
    
    def __init__(self, puzzle: Puzzle):
        """
        Initialize the solver with a puzzle.
        
        Args:
            puzzle: The Puzzle instance to solve (any size)
        """
        self.initial_puzzle = puzzle.copy()
    
    def solve(self) -> Optional[List[str]]:
        """
        Solve the puzzle using BFS.
        
        Returns:
            List of moves to solve the puzzle, or None if unsolvable
        """
        # Check if already solved
        if self.initial_puzzle.is_goal():
            return []
        
        # Check if solvable
        if not self.initial_puzzle.is_solvable():
            return None
        
        # BFS uses a queue: we'll process states in order
        # Each element: (puzzle_state, path_to_reach_it)
        queue = deque([(self.initial_puzzle.copy(), [])])
        
        # Track visited states to avoid cycles
        # (We've seen this puzzle state before, don't explore again)
        visited = {self.initial_puzzle}
        
        # Counter for statistics
        nodes_explored = 0
        
        while queue:
            # Get the next state from the front of the queue (FIFO)
            current_puzzle, path = queue.popleft()
            nodes_explored += 1
            
            # Check if we've reached the goal!
            if current_puzzle.is_goal():
                print(f"✅ Solution found! Explored {nodes_explored} states.")
                return path
            
            # Generate all possible next moves
            for move in current_puzzle.get_valid_moves():
                # Create a copy to avoid modifying the original
                new_puzzle = current_puzzle.copy()
                new_puzzle.make_move(move)
                
                # Only explore if we haven't seen this state before
                if new_puzzle not in visited:
                    visited.add(new_puzzle)
                    # Add to queue with the path that led here
                    queue.append((new_puzzle, path + [move]))
        
        # If queue is empty and we haven't found solution, it's unsolvable
        return None
    
    def solve_with_stats(self) -> Tuple[Optional[List[str]], dict]:
        """
        Solve the puzzle and return statistics.
        
        Returns:
            Tuple of (solution_path, statistics_dict)
        """
        if self.initial_puzzle.is_goal():
            return [], {'nodes_explored': 0, 'solution_length': 0}
        
        if not self.initial_puzzle.is_solvable():
            return None, {'nodes_explored': 0, 'solution_length': 0}
        
        queue = deque([(self.initial_puzzle.copy(), [])])
        visited = {self.initial_puzzle}
        nodes_explored = 0
        max_queue_size = 1
        
        while queue:
            current_puzzle, path = queue.popleft()
            nodes_explored += 1
            max_queue_size = max(max_queue_size, len(queue))
            
            if current_puzzle.is_goal():
                stats = {
                    'nodes_explored': nodes_explored,
                    'solution_length': len(path),
                    'max_queue_size': max_queue_size
                }
                return path, stats
            
            for move in current_puzzle.get_valid_moves():
                new_puzzle = current_puzzle.copy()
                new_puzzle.make_move(move)
                
                if new_puzzle not in visited:
                    visited.add(new_puzzle)
                    queue.append((new_puzzle, path + [move]))
        
        return None, {'nodes_explored': nodes_explored, 'solution_length': 0}

