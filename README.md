# 🧩 8-Puzzle Solver

A powerful web-based application that solves the classic 8-puzzle game using various search algorithms. Originally developed in Python (Flet), now running on a lightning-fast JavaScript engine for the web.

🔗 **[Live Demo / Spustit aplikaci](https://castulik.github.io/8Puzzle_Solver/)**

---

## 📸 Preview
![8-Puzzle Solver Preview](animace.gif) 

## 🧐 About the Project
The **8-puzzle** consists of a 3x3 grid with 8 numbered tiles and one empty space. The goal is to move the tiles until they reach the target configuration: `[[1, 2, 3], [4, 5, 6], [7, 8, 0]]`.

This application allows you to:
* **Manually play** the puzzle by clicking on tiles.
* **Shuffle** the board into a guaranteed solvable state.
* **Visualize** how different algorithms find the path to the solution.
* **Track statistics** like calculation time, nodes explored, and memory usage.

---

## 🧠 Algorithms Explained

The solver implements a variety of pathfinding and search algorithms to demonstrate their efficiency:

| Algorithm | Description | Guaranteed Shortest? |
| :--- | :--- | :--- |
| **BFS** (Breadth-First Search) | Explores all possible states level by level. | ✅ Yes |
| **DFS** (Depth-First Search) | Goes deep into a single branch. Can be very slow on puzzles. | ❌ No |
| **DFS Limit** | DFS with a depth limit (31 moves) to prevent infinite loops. | ❌ No |
| **A*** (A-Star) | Uses the Manhattan distance heuristic to find the goal efficiently. | ✅ Yes |
| **A* LC** (Linear Conflict) | An advanced A* that accounts for tiles blocking each other in the same row/column. | ✅ Yes |
| **A* Weighted** | Prioritizes the heuristic for faster (though potentially longer) solutions. | ❌ No |
| **Greedy Search** | Focuses solely on the distance to the goal, ignoring path cost. | ❌ No |

---

## 💻 Local Execution (Python version)

If you prefer to run the original desktop version of the application, you can do so using Python and the Flet library.

### Prerequisites
* Python 3.10+ installed
* Flet library installed: `pip install flet`

### How to run:
1. Clone this repository or download the source files.
2. Navigate to the project folder.
3. Run the main application file:
   ```bash
   python mainAPP.py

### 🛠️ Built With
* Frontend: Clean JavaScript, HTML5, CSS3 (for instant loading).
* Original Engine: Python with Flet (Flutter for Python).
* Deployment: GitHub Actions & GitHub Pages.

### 🎓 Author
Developed by Castulik