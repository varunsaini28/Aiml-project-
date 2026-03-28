"""
dfs.py - Depth First Search Algorithm
===========================================
DFS kya karta hai: Deep unexplored areas explore karta hai
Ek direction mein jaata hai jab tak possible ho, phir backtrack karta hai
Stack use karta hai (LIFO - Last In First Out)

Real World Use: Maze solving, File system traversal, Cycle detection in graphs
"""

def dfs_explore_area(grid_obj, max_steps=30):
    """
    DFS se unvisited area explore karo
    Ye function un cells ko explore karta hai jo abhi tak visited nahi
    
    Returns: (explored_path, all_visited_nodes)
    """
    from grid import EMPTY, VISITED, DANGER, SURVIVOR, PATH, AGENT, RESCUE_BASE

    start = grid_obj.agent_pos
    
    # Stack: (position, path_so_far)
    stack = [(start, [start])]
    visited = set()
    visited.add(start)
    all_visited = [start]
    best_path = [start]
    steps = 0

    # Unvisited cells prefer karo - jo abhi explore nahi hue
    def unvisited_neighbors_first(pos):
        neighbors = grid_obj.get_neighbors(pos, allow_danger=False)
        # Unvisited (EMPTY) cells ko priority do
        unvisited = []
        visited_cells = []
        for n in neighbors:
            r, c = n
            cell = grid_obj.grid[r][c]
            if cell == EMPTY or cell == SURVIVOR:
                unvisited.append(n)
            elif cell in [VISITED, PATH, AGENT, RESCUE_BASE]:
                visited_cells.append(n)
        return unvisited + visited_cells

    while stack and steps < max_steps:
        current, path = stack.pop()  # Stack se pop (LIFO)
        steps += 1

        if len(path) > len(best_path):
            best_path = path

        # Neighbors ko stack mein push karo (unvisited pehle)
        for neighbor in unvisited_neighbors_first(current):
            if neighbor not in visited:
                visited.add(neighbor)
                all_visited.append(neighbor)
                stack.append((neighbor, path + [neighbor]))

    return best_path, all_visited


def dfs_find_survivor(grid_obj):
    """
    DFS se koi bhi survivor dhundo (BFS se alag - depth-first)
    Longer paths explore karta hai pehle
    
    Returns: (survivor_pos, path, visited_nodes)
    """
    start = grid_obj.agent_pos
    survivors_set = set(map(tuple, grid_obj.survivors))
    
    if not survivors_set:
        return None, [], []

    # Stack use karo DFS ke liye
    stack = [(start, [start])]
    visited = set()
    visited.add(start)
    all_visited = [start]

    while stack:
        current, path = stack.pop()

        if current in survivors_set and current != start:
            return current, path, all_visited

        for neighbor in grid_obj.get_neighbors(current, allow_danger=False):
            if neighbor not in visited:
                visited.add(neighbor)
                all_visited.append(neighbor)
                stack.append((neighbor, path + [neighbor]))

    return None, [], all_visited


def dfs_full_explanation():
    """DFS ka step-by-step explanation"""
    return {
        "algorithm": "Depth First Search (DFS)",
        "use_in_project": "Unexplored areas explore karne ke liye",
        "data_structure": "Stack (LIFO)",
        "time_complexity": "O(V + E)",
        "space_complexity": "O(V)",
        "guarantees": "Will find a path if it exists (not necessarily shortest)",
        "steps": [
            "1. Start node stack mein daalo",
            "2. Stack se node nikalo (top se - LIFO)",
            "3. Agar goal hai toh return karo",
            "4. Neighbors ko stack mein push karo",
            "5. Repeat karo - deep mein jaata hai pehle"
        ]
    }
