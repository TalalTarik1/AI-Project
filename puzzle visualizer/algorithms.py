"""
Pathfinding algorithms: BFS, DFS, A*, and Dijkstra.
"""

from collections import deque
import heapq
from typing import List, Tuple, Optional, Callable, Dict
from grid import Grid, CellType


class PathfindingResult:
    """Result of a pathfinding algorithm."""
    
    def __init__(self):
        self.path: List[Tuple[int, int]] = []
        self.visited: List[Tuple[int, int]] = []
        self.exploring: List[Tuple[int, int]] = []
        self.found = False
        self.path_length = 0
        self.nodes_explored = 0


def bfs(grid: Grid, start: Tuple[int, int], end: Tuple[int, int],
        on_visit: Optional[Callable] = None) -> PathfindingResult:
    """
    Breadth-First Search algorithm.
    
    Args:
        grid: Grid instance
        start: Start position (row, col)
        end: End position (row, col)
        on_visit: Optional callback function called when visiting a node
        
    Returns:
        PathfindingResult object
    """
    result = PathfindingResult()
    
    if not grid.is_valid(*start) or not grid.is_valid(*end):
        return result
    
    queue = deque([start])
    visited = {start}
    parent = {start: None}
    
    while queue:
        current = queue.popleft()
        result.exploring.append(current)
        
        if on_visit:
            on_visit(current)
        
        if current == end:
            # Reconstruct path
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = parent[node]
            result.path = path[::-1]
            result.found = True
            result.path_length = len(result.path) - 1
            result.nodes_explored = len(visited)
            return result
        
        for neighbor in grid.get_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
                result.visited.append(neighbor)
    
    result.nodes_explored = len(visited)
    return result


def dfs(grid: Grid, start: Tuple[int, int], end: Tuple[int, int],
        on_visit: Optional[Callable] = None) -> PathfindingResult:
    """
    Depth-First Search algorithm.
    
    Args:
        grid: Grid instance
        start: Start position (row, col)
        end: End position (row, col)
        on_visit: Optional callback function called when visiting a node
        
    Returns:
        PathfindingResult object
    """
    result = PathfindingResult()
    
    if not grid.is_valid(*start) or not grid.is_valid(*end):
        return result
    
    stack = [start]
    visited = {start}
    parent = {start: None}
    
    while stack:
        current = stack.pop()
        result.exploring.append(current)
        
        if on_visit:
            on_visit(current)
        
        if current == end:
            # Reconstruct path
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = parent[node]
            result.path = path[::-1]
            result.found = True
            result.path_length = len(result.path) - 1
            result.nodes_explored = len(visited)
            return result
        
        for neighbor in grid.get_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)
                result.visited.append(neighbor)
    
    result.nodes_explored = len(visited)
    return result


def heuristic(row1: int, col1: int, row2: int, col2: int) -> float:
    """
    Manhattan distance heuristic for A* algorithm.
    
    Args:
        row1, col1: First position
        row2, col2: Second position
        
    Returns:
        Manhattan distance
    """
    return abs(row1 - row2) + abs(col1 - col2)


def astar(grid: Grid, start: Tuple[int, int], end: Tuple[int, int],
          on_visit: Optional[Callable] = None) -> PathfindingResult:
    """
    A* (A-Star) algorithm with Manhattan distance heuristic.
    
    Args:
        grid: Grid instance
        start: Start position (row, col)
        end: End position (row, col)
        on_visit: Optional callback function called when visiting a node
        
    Returns:
        PathfindingResult object
    """
    result = PathfindingResult()
    
    if not grid.is_valid(*start) or not grid.is_valid(*end):
        return result
    
    open_set = [(0, start)]  # (f_score, position)
    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    g_score: Dict[Tuple[int, int], float] = {start: 0}
    f_score: Dict[Tuple[int, int], float] = {start: heuristic(*start, *end)}
    visited_set = set()
    
    while open_set:
        current_f, current = heapq.heappop(open_set)
        
        if current in visited_set:
            continue
        
        visited_set.add(current)
        result.exploring.append(current)
        
        if on_visit:
            on_visit(current)
        
        if current == end:
            # Reconstruct path
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = came_from[node]
            result.path = path[::-1]
            result.found = True
            result.path_length = len(result.path) - 1
            result.nodes_explored = len(visited_set)
            return result
        
        for neighbor in grid.get_neighbors(*current):
            if neighbor in visited_set:
                continue
            
            tentative_g = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(*neighbor, *end)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
                if neighbor not in result.visited:
                    result.visited.append(neighbor)
    
    result.nodes_explored = len(visited_set)
    return result


def dijkstra(grid: Grid, start: Tuple[int, int], end: Tuple[int, int],
             on_visit: Optional[Callable] = None) -> PathfindingResult:
    """
    Dijkstra's algorithm (all edges have weight 1 in this implementation).
    
    Args:
        grid: Grid instance
        start: Start position (row, col)
        end: End position (row, col)
        on_visit: Optional callback function called when visiting a node
        
    Returns:
        PathfindingResult object
    """
    result = PathfindingResult()
    
    if not grid.is_valid(*start) or not grid.is_valid(*end):
        return result
    
    distances: Dict[Tuple[int, int], float] = {start: 0}
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    pq = [(0, start)]
    visited = set()
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        if current in visited:
            continue
        
        visited.add(current)
        result.exploring.append(current)
        
        if on_visit:
            on_visit(current)
        
        if current == end:
            # Reconstruct path
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = parent[node]
            result.path = path[::-1]
            result.found = True
            result.path_length = len(result.path) - 1
            result.nodes_explored = len(visited)
            return result
        
        for neighbor in grid.get_neighbors(*current):
            if neighbor in visited:
                continue
            
            new_dist = current_dist + 1  # All edges have weight 1
            
            if neighbor not in distances or new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                parent[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))
                if neighbor not in result.visited:
                    result.visited.append(neighbor)
    
    result.nodes_explored = len(visited)
    return result


def get_algorithm(name: str):
    """
    Get algorithm function by name.
    
    Args:
        name: Algorithm name ('bfs', 'dfs', 'astar', 'dijkstra')
        
    Returns:
        Algorithm function
    """
    algorithms = {
        'bfs': bfs,
        'dfs': dfs,
        'astar': astar,
        'dijkstra': dijkstra
    }
    return algorithms.get(name.lower(), bfs)

