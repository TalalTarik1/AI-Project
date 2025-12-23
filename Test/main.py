"""
MAIN ENTRY POINT - Step 5: Running the Application

This is the main file that starts the application.
It's the entry point - when you run this file, everything starts!

To run: python main.py
"""

from gui import PuzzleGUI


def main():
    """
    Main function - creates and runs the GUI application.
    """
    print("=" * 50)
    print("N-Puzzle Solver - Starting Application")
    print("=" * 50)
    print("\nFeatures:")
    print("  ✓ Multiple puzzle sizes (8, 15, 24 puzzles)")
    print("  ✓ Interactive puzzle board")
    print("  ✓ BFS algorithm solver")
    print("  ✓ Step-by-step solution display")
    print("  ✓ Save/Load puzzles")
    print("  ✓ Statistics tracking")
    print("\n" + "=" * 50 + "\n")
    
    # Create and run the GUI
    app = PuzzleGUI()
    app.run()


if __name__ == "__main__":
    main()

