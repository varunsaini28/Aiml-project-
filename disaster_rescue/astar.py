"""
astar.py - A* (A-Star) Algorithm
===========================================
A* kya karta hai: Safest aur shortest path dhundta hai danger zones avoid karke
Heuristic use karta hai (Manhattan distance) to guide search intelligently
Priority Queue use karta hai

Real World Use: Google Maps, Game AI pathfinding, Robot navigation
Formula: f(n) = g(n) + h(n)
  g(n) = Start se current node tak ka actual cost
  h(n) = Current node se goal tak ka estimated cost (heuristic)
"""

import heapq

def manhattan_distance(pos1, pos2):
    """
    Manhattan distance - heuristic function
    Seedha line mein nahi, balki grid mein kitna door hai
    Ye hamesha admissible hai (kabhi overestimate nahi karta)
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def astar_path(grid_obj, start, goal):
    """
    A* Algorithm: Start se Goal tak safest path dhundo
    Danger zones avoid karo - unka cost bahut zyada hai
    
    Returns: (path_list, all_explored_nodes)
    """
    from grid import DANGER

    if start == goal:
        return [start], [start]

    # Priority Queue: (f_cost, g_cost, position, path)
    # f = g + h (total estimated cost)
    open_heap = []
    h_start = manhattan_distance(start, goal)
    heapq.heappush(open_heap, (h_start, 0, start, [start]))

    # Best g_cost jo hum jaante hain har node ke liye
    g_costs = {start: 0}

    # Explored nodes track karo visualization ke liye
    all_explored = []

    while open_heap:
        f, g, current, path = heapq.heappop(open_heap)

        all_explored.append(current)

        # Goal pahunch gaye!
        if current == goal:
            return path, all_explored

        # Neighbors explore karo
        for neighbor in grid_obj.get_neighbors(current, allow_danger=True):
            nr, nc = neighbor
            cell = grid_obj.grid[nr][nc]

            # Danger zone ka cost bahut zyada - agent yahan jaana nahi chahta
            # Lekin agar zaroorat ho toh ja sakta hai
            if cell == DANGER:
                move_cost = 10  # Normal cost 1 ki jagah 10 - penalty
            else:
                move_cost = 1

            new_g = g + move_cost

            # Agar ye path better hai jo hum jaante hain
            if neighbor not in g_costs or new_g < g_costs[neighbor]:
                g_costs[neighbor] = new_g
                h = manhattan_distance(neighbor, goal)
                f = new_g + h
                new_path = path + [neighbor]
                heapq.heappush(open_heap, (f, new_g, neighbor, new_path))

    # Koi path nahi mila
    return [], all_explored


def astar_safest_path(grid_obj, start, goal):
    """
    A* - Strictly safe path (danger zones bilkul avoid karo)
    Agar safe path na mile toh koi path nahi
    """
    if start == goal:
        return [start], [start]

    open_heap = []
    h_start = manhattan_distance(start, goal)
    heapq.heappush(open_heap, (h_start, 0, start, [start]))
    g_costs = {start: 0}
    all_explored = []

    while open_heap:
        f, g, current, path = heapq.heappop(open_heap)
        all_explored.append(current)

        if current == goal:
            return path, all_explored

        # Sirf safe neighbors - danger cells skip karo
        for neighbor in grid_obj.get_neighbors(current, allow_danger=False):
            new_g = g + 1
            if neighbor not in g_costs or new_g < g_costs[neighbor]:
                g_costs[neighbor] = new_g
                h = manhattan_distance(neighbor, goal)
                f = new_g + h
                heapq.heappush(open_heap, (f, new_g, neighbor, path + [neighbor]))

    return [], all_explored


def astar_full_explanation():
    """A* ka detailed explanation"""
    return {
        "algorithm": "A* (A-Star) Search",
        "use_in_project": "Survivor tak safest shortest path dhundne ke liye",
        "data_structure": "Priority Queue (Min Heap)",
        "time_complexity": "O(b^d) - b branching factor, d depth",
        "space_complexity": "O(b^d)",
        "guarantees": "Optimal path agar heuristic admissible ho",
        "formula": "f(n) = g(n) + h(n)",
        "heuristic": "Manhattan Distance",
        "steps": [
            "1. Start node priority queue mein daalo (f=h)",
            "2. Lowest f-cost node nikalo",
            "3. Agar goal hai toh return karo",
            "4. Neighbors explore karo, g_cost calculate karo",
            "5. f = g + h calculate karo aur queue mein daalo",
            "6. Danger zones ko high cost deke avoid karo"
        ]
    }
