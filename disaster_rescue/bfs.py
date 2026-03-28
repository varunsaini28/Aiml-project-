"""
bfs.py - Breadth First Search Algorithm
===========================================
BFS kya karta hai: Nearest survivor dhundta hai
Layer by layer explore karta hai - pehle paas ke nodes, phir door ke
Queue use karta hai (FIFO - First In First Out)

Real World Use: GPS mein shortest path, Social networks mein closest friends
"""

from collections import deque

def bfs_find_nearest_survivor(grid_obj):
    """
    BFS se nearest survivor dhundo
    Starting point: Agent ki current position
    Goal: Koi bhi survivor cell
    
    Returns: (nearest_survivor_pos, path_to_it, all_visited_nodes)
    """
    start = grid_obj.agent_pos
    survivors_set = set(map(tuple, grid_obj.survivors))

    # Agar koi survivor nahi toh None return karo
    if not survivors_set:
        return None, [], []

    # BFS Queue: (current_position, path_so_far)
    queue = deque()
    queue.append((start, [start]))

    # Visited set - jo nodes dekh liye unhe dobara mat dekho
    visited = set()
    visited.add(start)
    all_visited = [start]  # Frontend ko dikhane ke liye

    while queue:
        current, path = queue.popleft()

        # Survivor mila! Wapas return karo
        if current in survivors_set and current != start:
            return current, path, all_visited

        # Neighbors explore karo
        for neighbor in grid_obj.get_neighbors(current, allow_danger=False):
            if neighbor not in visited:
                visited.add(neighbor)
                all_visited.append(neighbor)
                new_path = path + [neighbor]
                queue.append((neighbor, new_path))

    # Koi reachable survivor nahi mila
    return None, [], all_visited


def bfs_full_explanation():
    """BFS ka step-by-step explanation"""
    return {
        "algorithm": "Breadth First Search (BFS)",
        "use_in_project": "Nearest survivor dhundne ke liye",
        "data_structure": "Queue (FIFO)",
        "time_complexity": "O(V + E) - V vertices, E edges",
        "space_complexity": "O(V)",
        "guarantees": "Shortest path in unweighted graph",
        "steps": [
            "1. Start node queue mein daalo",
            "2. Queue se node nikalo (front se)",
            "3. Agar survivor hai toh path return karo",
            "4. Neighbors ko queue mein daalo (agar visited nahi)",
            "5. Repeat karo jab tak survivor na mile ya queue empty ho"
        ]
    }
