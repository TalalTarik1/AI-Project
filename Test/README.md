# 8-Puzzle Solver - BFS Algorithm Application

A complete Python application that solves the classic 8-Puzzle game using the Breadth-First Search (BFS) algorithm, featuring a GUI interface and database integration.

## 🎯 What You'll Learn

This project teaches you:
1. **BFS Algorithm**: How breadth-first search works for pathfinding
2. **GUI Development**: Building user interfaces with tkinter
3. **Database Integration**: Using SQLite for data persistence
4. **Object-Oriented Programming**: Clean code structure and organization
5. **Game Logic**: Implementing puzzle mechanics and validation

## 📁 Project Structure

```
Test/
├── main.py              # Entry point - run this to start the app
├── gui.py               # GUI interface (tkinter)
├── puzzle_logic.py      # 8-Puzzle game mechanics
├── bfs_solver.py        # BFS algorithm implementation
├── database.py          # SQLite database operations
├── requirements.txt     # Dependencies (none needed - uses built-in libraries!)
└── README.md           # This file
```

## 🚀 How to Run

1. **Navigate to the project directory:**
   ```bash
   cd Test
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

That's it! No installation needed - everything uses Python's built-in libraries.

## 🎮 How to Use

### Basic Controls:
- **Click tiles**: Click any tile adjacent to the empty space to move it
- **Shuffle**: Randomly shuffle the puzzle
- **Solve (BFS)**: Automatically solve using BFS algorithm
- **Step Solution**: Execute solution one move at a time
- **Auto Play**: Watch the solution play out automatically
- **Reset**: Return to solved state
- **Save Puzzle**: Save current state to database
- **Load Puzzle**: Load a previously saved puzzle

### Understanding BFS:
- BFS explores all possibilities level by level
- Guarantees finding the **shortest** solution
- Uses a queue (First In, First Out)
- Tracks visited states to avoid cycles

## 🧠 Key Concepts Explained

### 1. BFS Algorithm (`bfs_solver.py`)
```python
# BFS uses a queue to explore states level by level
queue = deque([(initial_state, [])])  # Start with initial state
visited = set()  # Track what we've seen

while queue:
    current_state, path = queue.popleft()  # Get from front
    if current_state.is_goal():
        return path  # Found solution!
    
    # Explore all neighbors
    for move in valid_moves:
        new_state = make_move(current_state, move)
        if new_state not in visited:
            visited.add(new_state)
            queue.append((new_state, path + [move]))  # Add to back
```

### 2. Database Operations (`database.py`)
- **SQLite**: Lightweight, file-based database
- **Tables**: 
  - `saved_puzzles`: Store puzzle states
  - `solve_history`: Track your solving statistics
- **JSON Storage**: Convert 2D arrays to JSON strings for storage

### 3. GUI Components (`gui.py`)
- **tkinter**: Python's built-in GUI library
- **Event-driven**: Buttons trigger functions
- **Real-time updates**: Display updates as puzzle changes

## 📊 Database Schema

### saved_puzzles
- `id`: Primary key
- `name`: User-friendly name
- `puzzle_state`: JSON string of board
- `created_at`: Timestamp

### solve_history
- `id`: Primary key
- `puzzle_state`: Initial puzzle state
- `solution_moves`: Number of moves in solution
- `solve_time`: Time taken (seconds)
- `algorithm`: Algorithm used (BFS)
- `solved_at`: Timestamp

## 🔧 Extending the Project

### Ideas for Future Enhancements:
1. **Add DFS Algorithm**: Compare BFS vs DFS
2. **A* Algorithm**: More efficient with heuristics
3. **Difficulty Levels**: Easy/Medium/Hard shuffles
4. **Timer**: Track how long you take to solve
5. **Leaderboard**: Compare solve times
6. **Custom Puzzle Size**: 15-puzzle (4x4) or larger
7. **Visual Improvements**: Better graphics, animations
8. **Sound Effects**: Audio feedback for moves

## 📚 Learning Path

### Beginner:
- Understand how the puzzle works
- Learn basic GUI concepts
- See BFS in action

### Intermediate:
- Modify the shuffle algorithm
- Add new features
- Improve the UI

### Advanced:
- Implement A* algorithm
- Add multi-threading for faster solving
- Create a web version with Flask/Django

## 🐛 Troubleshooting

**Problem**: "No module named 'tkinter'"
- **Solution**: Install tkinter: `sudo apt-get install python3-tk` (Linux) or it's included with Python on Windows/Mac

**Problem**: Database errors
- **Solution**: Delete `puzzle_solver.db` and restart - it will recreate

**Problem**: Puzzle won't solve
- **Solution**: Some puzzles are unsolvable! The app checks this automatically.

## 💡 Tips for Learning

1. **Read the comments**: Every file has detailed explanations
2. **Experiment**: Try modifying the shuffle count, add features
3. **Debug**: Add print statements to see how BFS explores states
4. **Compare**: Try solving manually vs using BFS
5. **Extend**: Add your own features to practice

## 🎓 Next Steps

After mastering this project, try:
- Building a web version
- Adding more algorithms (DFS, A*, IDA*)
- Creating a mobile app version
- Building other puzzle solvers (Sudoku, N-Queens)

---

**Happy Coding! 🚀**

Remember: The best way to learn is by doing. Don't just read the code - modify it, break it, fix it, and make it your own!



