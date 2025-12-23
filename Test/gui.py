"""
GUI MODULE - Step 4: Understanding Graphical User Interfaces

This module creates the visual interface using tkinter (built into Python).
We'll create:
- Interactive puzzle board (click tiles to move)
- Control buttons (shuffle, solve, reset)
- Solution display area
- Statistics panel
- Save/Load functionality

tkinter basics:
- Tk() creates the main window
- Frames organize widgets
- Buttons trigger actions
- Labels display text
- Grid/Place/Pack arrange widgets
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
from typing import Optional, List
from puzzle_logic import Puzzle
from bfs_solver import BFSSolver
from database import PuzzleDatabase


class PuzzleGUI:
    """
    Main GUI class for the N-Puzzle Solver application.
    Supports 8-puzzle (3x3), 15-puzzle (4x4), and 24-puzzle (5x5).
    """
    
    def __init__(self):
        """Initialize the GUI and all components."""
        # Create main window
        self.root = tk.Tk()
        self.root.title("N-Puzzle Solver - BFS Algorithm")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        # Puzzle size (3=8-puzzle, 4=15-puzzle, 5=24-puzzle)
        self.puzzle_size = 3
        self.puzzle = Puzzle(size=self.puzzle_size)
        self.db = PuzzleDatabase()
        self.solution_path: Optional[List[str]] = None
        self.current_solution_step = 0
        self.tile_buttons = []  # Will be created dynamically
        
        # Create GUI components
        self.create_widgets()
        
        # Update display
        self.update_display()
    
    def create_widgets(self):
        """
        Create and arrange all GUI widgets.
        This is like building the UI layout.
        """
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="N-Puzzle Solver", 
                               font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Puzzle size selector
        size_frame = ttk.Frame(main_frame)
        size_frame.grid(row=1, column=0, columnspan=3, pady=5)
        
        ttk.Label(size_frame, text="Puzzle Size:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.size_var = tk.IntVar(value=3)
        
        size_options = [
            (3, "8-Puzzle (3×3)"),
            (4, "15-Puzzle (4×4)"),
            (5, "24-Puzzle (5×5)")
        ]
        
        for size, label in size_options:
            ttk.Radiobutton(size_frame, text=label, variable=self.size_var, 
                          value=size, command=self.change_puzzle_size).pack(side=tk.LEFT, padx=5)
        
        # Left panel: Puzzle board
        self.board_frame = ttk.LabelFrame(main_frame, text="Puzzle Board", padding="10")
        self.board_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        # Create puzzle board (will be updated when size changes)
        self.create_puzzle_board()
        
        # Control buttons frame
        controls_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        controls_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        # Button row 1 - Main actions
        generate_btn = ttk.Button(controls_frame, text="🎲 Generate New Puzzle", 
                                  command=self.generate_new_puzzle)
        generate_btn.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        generate_btn.config(width=20)  # Make it more prominent
        
        ttk.Button(controls_frame, text="Shuffle", command=self.shuffle_puzzle).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(controls_frame, text="Solve (BFS)", command=self.solve_puzzle).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(controls_frame, text="Reset", command=self.reset_puzzle).grid(row=0, column=3, padx=5, pady=5)
        
        # Button row 2 - Solution controls
        ttk.Button(controls_frame, text="Step Solution", command=self.step_solution).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(controls_frame, text="Auto Play", command=self.auto_play_solution).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(controls_frame, text="Save Puzzle", command=self.save_puzzle).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(controls_frame, text="Load Puzzle", command=self.load_puzzle).grid(row=1, column=3, padx=5, pady=5)
        
        # Right panel: Information
        info_frame = ttk.LabelFrame(main_frame, text="Information & Solution", padding="10")
        info_frame.grid(row=2, column=2, rowspan=2, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N))
        
        # Instructions/Help text at the top
        self.help_text = tk.Text(info_frame, width=30, height=5, wrap=tk.WORD, 
                           font=("Arial", 9), bg="lightyellow", relief=tk.FLAT)
        self.update_help_text()
        self.help_text.config(state=tk.DISABLED)  # Make it read-only
        self.help_text.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Solution display with label
        solution_label = ttk.Label(info_frame, text="Solution Path (BFS Algorithm):", 
                                   font=("Arial", 10, "bold"))
        solution_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.solution_text = tk.Text(info_frame, width=30, height=12, wrap=tk.WORD,
                                     font=("Courier", 9))
        self.solution_text.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.solution_text.yview)
        scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S))
        self.solution_text.configure(yscrollcommand=scrollbar.set)
        
        # Statistics
        stats_frame = ttk.LabelFrame(info_frame, text="📊 Your Progress", padding="5")
        stats_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.stats_label = ttk.Label(stats_frame, text="", font=("Arial", 9))
        self.stats_label.grid(row=0, column=0, sticky=tk.W)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Update statistics
        self.update_statistics()
    
    def update_help_text(self):
        """Update help text based on current puzzle size."""
        puzzle_names = {3: "8-Puzzle (1-8)", 4: "15-Puzzle (1-15)", 5: "24-Puzzle (1-24)"}
        max_tile = self.puzzle_size * self.puzzle_size - 1
        self.help_text.config(state=tk.NORMAL)
        self.help_text.delete(1.0, tk.END)
        self.help_text.insert(1.0, f"📚 How to Play:\n"
                              f"• Click tiles to move them\n"
                              f"• Goal: Arrange 1-{max_tile} in order\n"
                              f"• BFS finds shortest solution\n"
                              f"• Current: {puzzle_names[self.puzzle_size]}")
        self.help_text.config(state=tk.DISABLED)
    
    def create_puzzle_board(self):
        """
        Create the puzzle board with buttons based on current size.
        This is called when the puzzle size changes.
        """
        # Clear existing buttons
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        self.tile_buttons = []
        size = self.puzzle_size
        
        # Adjust button size based on puzzle size
        if size == 3:
            btn_width, btn_height, font_size = 8, 4, 24
        elif size == 4:
            btn_width, btn_height, font_size = 6, 3, 18
        else:  # size == 5
            btn_width, btn_height, font_size = 5, 2, 14
        
        # Create grid of buttons
        for i in range(size):
            row = []
            for j in range(size):
                btn = tk.Button(self.board_frame, text="", 
                              width=btn_width, height=btn_height,
                              font=("Arial", font_size, "bold"),
                              command=lambda r=i, c=j: self.on_tile_click(r, c))
                btn.grid(row=i, column=j, padx=1, pady=1)
                row.append(btn)
            self.tile_buttons.append(row)
    
    def change_puzzle_size(self):
        """
        Change the puzzle size and recreate the board.
        This is called when user selects a different size.
        """
        new_size = self.size_var.get()
        if new_size == self.puzzle_size:
            return
        
        # Confirm if there's unsaved work
        if self.solution_path is not None:
            if not messagebox.askyesno("Change Size", 
                                      "Changing puzzle size will reset the current puzzle. Continue?"):
                self.size_var.set(self.puzzle_size)  # Revert selection
                return
        
        self.puzzle_size = new_size
        self.puzzle = Puzzle(size=self.puzzle_size)
        self.solution_path = None
        self.current_solution_step = 0
        
        # Recreate board
        self.create_puzzle_board()
        self.update_display()
        self.update_solution_display()
        self.update_help_text()
        
        # Update window title
        puzzle_names = {3: "8-Puzzle", 4: "15-Puzzle", 5: "24-Puzzle"}
        self.root.title(f"{puzzle_names[self.puzzle_size]} Solver - BFS Algorithm")
        self.status_label.config(text=f"Switched to {puzzle_names[self.puzzle_size]}")
    
    def update_display(self):
        """
        Update the puzzle board display to match current state.
        This is called whenever the puzzle state changes.
        """
        size = self.puzzle_size
        for i in range(size):
            for j in range(size):
                value = self.puzzle.state[i][j]
                btn = self.tile_buttons[i][j]
                
                if value == 0:
                    # Empty space - make it invisible
                    btn.config(text="", bg="lightgray", state=tk.NORMAL)
                else:
                    # Show the number
                    btn.config(text=str(value), bg="lightblue", state=tk.NORMAL)
    
    def on_tile_click(self, row: int, col: int):
        """
        Handle clicking on a puzzle tile.
        We need to check if this tile can move (is adjacent to empty space).
        
        Args:
            row: Row of clicked tile
            col: Column of clicked tile
        """
        empty_row, empty_col = self.puzzle.find_empty()
        
        # Check if clicked tile is adjacent to empty space
        if (row == empty_row and abs(col - empty_col) == 1) or \
           (col == empty_col and abs(row - empty_row) == 1):
            
            # Determine move direction
            if row < empty_row:
                direction = 'up'
            elif row > empty_row:
                direction = 'down'
            elif col < empty_col:
                direction = 'left'
            else:
                direction = 'right'
            
            # Make the move
            self.puzzle.make_move(direction)
            self.update_display()
            self.check_win()
            
            # Clear solution if user manually moves
            self.solution_path = None
            self.current_solution_step = 0
            self.update_solution_display()
    
    def generate_new_puzzle(self):
        """
        Generate a new random puzzle by shuffling.
        This is the main entry point for starting a new game!
        """
        self.puzzle.shuffle(100)
        self.update_display()
        self.solution_path = None
        self.current_solution_step = 0
        self.update_solution_display()
        self.status_label.config(text="✨ New puzzle generated! Try to solve it or click 'Solve (BFS)' to see the solution.")
    
    def shuffle_puzzle(self):
        """Shuffle the puzzle randomly."""
        self.puzzle.shuffle(100)
        self.update_display()
        self.solution_path = None
        self.current_solution_step = 0
        self.update_solution_display()
        self.status_label.config(text="Puzzle shuffled!")
    
    def reset_puzzle(self):
        """Reset puzzle to goal state."""
        self.puzzle = Puzzle(size=self.puzzle_size)
        self.update_display()
        self.solution_path = None
        self.current_solution_step = 0
        self.update_solution_display()
        puzzle_names = {3: "8-Puzzle", 4: "15-Puzzle", 5: "24-Puzzle"}
        self.status_label.config(text=f"{puzzle_names[self.puzzle_size]} reset to goal state")
    
    def solve_puzzle(self):
        """
        Solve the puzzle using BFS algorithm.
        This is where the magic happens!
        Note: Larger puzzles (4x4, 5x5) may take significantly longer to solve!
        """
        puzzle_names = {3: "8-Puzzle", 4: "15-Puzzle", 5: "24-Puzzle"}
        puzzle_name = puzzle_names.get(self.puzzle_size, "Puzzle")
        
        if self.puzzle_size >= 4:
            if not messagebox.askyesno("Warning", 
                                      f"Solving {puzzle_name} with BFS may take a long time "
                                      f"(could be several minutes or more).\n\n"
                                      f"Continue anyway?"):
                return
        
        self.status_label.config(text=f"Solving {puzzle_name} with BFS... Please wait (this may take a while).")
        self.root.update()  # Update GUI to show status
        
        start_time = time.time()
        solver = BFSSolver(self.puzzle)
        self.solution_path, stats = solver.solve_with_stats()
        solve_time = time.time() - start_time
        
        if self.solution_path is None:
            messagebox.showerror("Error", "Puzzle is not solvable!")
            self.status_label.config(text="Error: Puzzle not solvable")
            return
        
        # Save to database
        self.db.save_solve_history(
            self.puzzle.state,
            len(self.solution_path),
            solve_time,
            'BFS'
        )
        
        # Update display
        self.current_solution_step = 0
        self.update_solution_display()
        self.update_statistics()
        
        self.status_label.config(
            text=f"Solution found! {len(self.solution_path)} moves. "
                 f"Explored {stats['nodes_explored']} states in {solve_time:.2f}s"
        )
    
    def step_solution(self):
        """Execute one step of the solution."""
        if self.solution_path is None:
            messagebox.showinfo("Info", "No solution available. Click 'Solve (BFS)' first.")
            return
        
        if self.current_solution_step < len(self.solution_path):
            move = self.solution_path[self.current_solution_step]
            self.puzzle.make_move(move)
            self.current_solution_step += 1
            self.update_display()
            self.update_solution_display()
            self.check_win()
        else:
            messagebox.showinfo("Info", "Solution complete!")
    
    def auto_play_solution(self):
        """
        Automatically play through the solution with animation.
        This is a great way to see BFS in action!
        """
        if self.solution_path is None:
            messagebox.showinfo("Info", "No solution available. Click 'Solve (BFS)' first.")
            return
        
        # Reset to initial state
        self.reset_puzzle()
        self.solve_puzzle()  # Re-solve to get solution
        
        def play_next_step():
            if self.current_solution_step < len(self.solution_path):
                move = self.solution_path[self.current_solution_step]
                self.puzzle.make_move(move)
                self.current_solution_step += 1
                self.update_display()
                self.update_solution_display()
                # Schedule next step after 500ms (creates animation effect)
                self.root.after(500, play_next_step)
            else:
                self.status_label.config(text="Auto-play complete!")
                messagebox.showinfo("Success", "Puzzle solved!")
        
        play_next_step()
    
    def update_solution_display(self):
        """
        Update the solution text display with detailed explanations.
        This helps users understand what BFS is doing!
        """
        self.solution_text.delete(1.0, tk.END)
        
        if self.solution_path is None:
            # No solution yet - provide helpful information
            self.solution_text.insert(tk.END, "🔍 BFS Algorithm Solution\n")
            self.solution_text.insert(tk.END, "=" * 28 + "\n\n")
            self.solution_text.insert(tk.END, "No solution calculated yet.\n\n")
            self.solution_text.insert(tk.END, "📌 What is BFS?\n")
            self.solution_text.insert(tk.END, "Breadth-First Search explores all\n")
            self.solution_text.insert(tk.END, "possible moves level by level.\n\n")
            self.solution_text.insert(tk.END, "✨ Key Features:\n")
            self.solution_text.insert(tk.END, "• Finds SHORTEST solution\n")
            self.solution_text.insert(tk.END, "• Guarantees optimal path\n")
            self.solution_text.insert(tk.END, "• Explores systematically\n\n")
            self.solution_text.insert(tk.END, "🚀 Click 'Solve (BFS)' to\n")
            self.solution_text.insert(tk.END, "find the solution!")
            
            # Style the text
            self.solution_text.tag_add("title", "1.0", "1.28")
            self.solution_text.tag_config("title", font=("Arial", 10, "bold"))
            self.solution_text.tag_add("subtitle", "4.0", "4.15")
            self.solution_text.tag_config("subtitle", font=("Arial", 9, "bold"))
            self.solution_text.tag_add("subtitle2", "8.0", "8.15")
            self.solution_text.tag_config("subtitle2", font=("Arial", 9, "bold"))
        else:
            # Solution found - show it with explanations
            self.solution_text.insert(tk.END, "✅ BFS Solution Found!\n")
            self.solution_text.insert(tk.END, "=" * 28 + "\n\n")
            self.solution_text.insert(tk.END, f"📊 Total Moves: {len(self.solution_path)}\n")
            self.solution_text.insert(tk.END, f"🎯 This is the SHORTEST path!\n\n")
            self.solution_text.insert(tk.END, "📋 Move Sequence:\n")
            self.solution_text.insert(tk.END, "-" * 28 + "\n")
            
            for i, move in enumerate(self.solution_path):
                marker = "→ " if i == self.current_solution_step else "  "
                move_desc = {
                    'up': 'Move tile DOWN into empty space',
                    'down': 'Move tile UP into empty space',
                    'left': 'Move tile RIGHT into empty space',
                    'right': 'Move tile LEFT into empty space'
                }
                self.solution_text.insert(tk.END, f"{marker}Step {i+1}: {move.upper()}\n")
                if i == self.current_solution_step:
                    self.solution_text.insert(tk.END, f"   ({move_desc[move]})\n")
            
            self.solution_text.insert(tk.END, "\n")
            if self.current_solution_step >= len(self.solution_path):
                self.solution_text.insert(tk.END, "🎉 Solution Complete!\n")
                self.solution_text.insert(tk.END, "Puzzle is now solved!")
            else:
                self.solution_text.insert(tk.END, f"📍 Progress: {self.current_solution_step}/{len(self.solution_path)} moves\n")
                self.solution_text.insert(tk.END, "Use 'Step Solution' to execute moves")
            
            # Style the text with colors and formatting
            self.solution_text.tag_add("header", "1.0", "1.end")
            self.solution_text.tag_config("header", font=("Arial", 10, "bold"), foreground="green")
            self.solution_text.tag_add("stats", "3.0", "4.0")
            self.solution_text.tag_config("stats", font=("Arial", 9, "bold"))
            self.solution_text.tag_add("section", "6.0", "6.end")
            self.solution_text.tag_config("section", font=("Arial", 9, "bold"))
            
            # Highlight current step - find the line dynamically
            content = self.solution_text.get(1.0, tk.END)
            lines = content.split('\n')
            current_line_num = None
            
            # Find the line with the current step marker
            for i, line in enumerate(lines):
                if f"→ Step {self.current_solution_step + 1}:" in line:
                    current_line_num = i + 1
                    break
            
            # Highlight current step if found
            if current_line_num:
                start_pos = f"{current_line_num}.0"
                end_pos = f"{current_line_num + 1}.0"
                self.solution_text.tag_add("current", start_pos, end_pos)
                self.solution_text.tag_config("current", background="yellow", font=("Courier", 9, "bold"))
    
    def check_win(self):
        """Check if puzzle is solved and show message."""
        if self.puzzle.is_goal():
            messagebox.showinfo("Congratulations!", "You solved the puzzle! 🎉")
            self.status_label.config(text="Puzzle solved!")
    
    def save_puzzle(self):
        """Save current puzzle state to database."""
        name = simpledialog.askstring("Save Puzzle", "Enter a name for this puzzle:")
        if name:
            puzzle_id = self.db.save_puzzle(name, self.puzzle.state, self.puzzle_size)
            messagebox.showinfo("Success", f"Puzzle '{name}' saved! (ID: {puzzle_id})")
            self.status_label.config(text=f"Puzzle '{name}' saved")
    
    def load_puzzle(self):
        """Load a saved puzzle from database."""
        puzzles = self.db.get_all_saved_puzzles()
        
        if not puzzles:
            messagebox.showinfo("Info", "No saved puzzles found.")
            return
        
        # Create selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Puzzle")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Select a puzzle to load:", font=("Arial", 12)).pack(pady=10)
        
        listbox = tk.Listbox(dialog, height=10)
        listbox.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        puzzle_names = {3: "8-Puzzle", 4: "15-Puzzle", 5: "24-Puzzle"}
        for puzzle in puzzles:
            size_name = puzzle_names.get(puzzle.get('size', 3), f"{puzzle.get('size', 3)}x{puzzle.get('size', 3)}")
            listbox.insert(tk.END, f"{puzzle['name']} ({size_name}) - {puzzle['created_at']}")
        
        def load_selected():
            selection = listbox.curselection()
            if selection:
                selected_puzzle = puzzles[selection[0]]
                puzzle_state = self.db.load_puzzle(selected_puzzle['id'])
                if puzzle_state:
                    # Get size from database or infer from state
                    loaded_size = selected_puzzle.get('size', len(puzzle_state))
                    if loaded_size != self.puzzle_size:
                        self.size_var.set(loaded_size)
                        self.puzzle_size = loaded_size
                        self.create_puzzle_board()
                        self.update_help_text()
                    
                    self.puzzle = Puzzle(size=self.puzzle_size, state=puzzle_state)
                    self.update_display()
                    self.solution_path = None
                    self.current_solution_step = 0
                    self.update_solution_display()
                    self.status_label.config(text=f"Loaded: {selected_puzzle['name']}")
                    dialog.destroy()
        
        ttk.Button(dialog, text="Load", command=load_selected).pack(pady=10)
    
    def update_statistics(self):
        """Update statistics display with better formatting."""
        stats = self.db.get_solve_statistics()
        stats_text = "📈 Your Statistics:\n"
        stats_text += "─" * 20 + "\n"
        stats_text += f"🎮 Puzzles Solved: {stats['total_solved']}\n"
        stats_text += f"📊 Avg Moves: {stats['average_moves']}\n"
        stats_text += f"⏱️  Avg Time: {stats['average_time']}s\n"
        if stats['best_moves'] > 0:
            stats_text += f"🏆 Best: {stats['best_moves']} moves"
        else:
            stats_text += f"🏆 Best: Not set yet"
        self.stats_label.config(text=stats_text, font=("Arial", 9))
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()

