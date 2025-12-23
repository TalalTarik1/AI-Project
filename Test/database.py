"""
DATABASE MODULE - Step 1: Understanding Data Storage

This module handles all database operations using SQLite (built into Python).
We'll store:
1. Puzzle states (for saving/loading puzzles)
2. Solve history (to track your progress and statistics)

Why SQLite?
- No installation needed (built into Python)
- Perfect for single-user applications
- Stores data in a local file
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional


class PuzzleDatabase:
    """
    This class manages our database connection and operations.
    Think of it as a helper that talks to the database for us.
    """
    
    def __init__(self, db_name: str = "puzzle_solver.db"):
        """
        Initialize the database connection.
        
        Args:
            db_name: Name of the database file (SQLite stores in a file)
        """
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Create and return a database connection."""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """
        Create tables if they don't exist.
        This is like creating folders to organize our data.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table 1: Saved Puzzles
        # Stores puzzle states that users want to save for later
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_puzzles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                puzzle_state TEXT NOT NULL,  -- JSON string of the board
                puzzle_size INTEGER DEFAULT 3,  -- Grid size (3, 4, or 5)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table 2: Solve History
        # Tracks every puzzle you solve - for statistics and learning!
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solve_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                puzzle_state TEXT NOT NULL,
                solution_moves INTEGER,  -- Number of moves in solution
                solve_time REAL,  -- Time taken to solve (seconds)
                algorithm TEXT DEFAULT 'BFS',  -- Which algorithm was used
                solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    def save_puzzle(self, name: str, puzzle_state: List[List[int]], puzzle_size: int = 3) -> int:
        """
        Save a puzzle state to the database.
        
        Args:
            name: A friendly name for this puzzle
            puzzle_state: The NxN board as a list of lists
            puzzle_size: The grid size (3, 4, or 5)
            
        Returns:
            The ID of the saved puzzle
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert the 2D list to JSON string for storage
        puzzle_json = json.dumps(puzzle_state)
        
        cursor.execute('''
            INSERT INTO saved_puzzles (name, puzzle_state, puzzle_size)
            VALUES (?, ?, ?)
        ''', (name, puzzle_json, puzzle_size))
        
        puzzle_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return puzzle_id
    
    def load_puzzle(self, puzzle_id: int) -> Optional[List[List[int]]]:
        """
        Load a saved puzzle from the database.
        
        Args:
            puzzle_id: The ID of the puzzle to load
            
        Returns:
            The puzzle state as a 2D list, or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT puzzle_state FROM saved_puzzles WHERE id = ?
        ''', (puzzle_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def get_all_saved_puzzles(self) -> List[Dict]:
        """
        Get all saved puzzles with their info.
        
        Returns:
            List of dictionaries with puzzle information
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, puzzle_size, created_at FROM saved_puzzles
            ORDER BY created_at DESC
        ''')
        
        puzzles = []
        for row in cursor.fetchall():
            puzzles.append({
                'id': row[0],
                'name': row[1],
                'size': row[2],
                'created_at': row[3]
            })
        
        conn.close()
        return puzzles
    
    def save_solve_history(self, puzzle_state: List[List[int]], 
                          solution_moves: int, solve_time: float, 
                          algorithm: str = 'BFS'):
        """
        Record that a puzzle was solved.
        This helps us track your progress!
        
        Args:
            puzzle_state: The initial puzzle state
            solution_moves: Number of moves in the solution
            solve_time: Time taken to solve (seconds)
            algorithm: Which algorithm was used
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        puzzle_json = json.dumps(puzzle_state)
        
        cursor.execute('''
            INSERT INTO solve_history (puzzle_state, solution_moves, solve_time, algorithm)
            VALUES (?, ?, ?, ?)
        ''', (puzzle_json, solution_moves, solve_time, algorithm))
        
        conn.commit()
        conn.close()
    
    def get_solve_statistics(self) -> Dict:
        """
        Get statistics about your solving history.
        
        Returns:
            Dictionary with statistics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total puzzles solved
        cursor.execute('SELECT COUNT(*) FROM solve_history')
        total_solved = cursor.fetchone()[0]
        
        # Average moves
        cursor.execute('SELECT AVG(solution_moves) FROM solve_history')
        avg_moves = cursor.fetchone()[0] or 0
        
        # Average time
        cursor.execute('SELECT AVG(solve_time) FROM solve_history')
        avg_time = cursor.fetchone()[0] or 0
        
        # Best (shortest) solution
        cursor.execute('SELECT MIN(solution_moves) FROM solve_history')
        best_moves = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_solved': total_solved,
            'average_moves': round(avg_moves, 2),
            'average_time': round(avg_time, 2),
            'best_moves': best_moves
        }

