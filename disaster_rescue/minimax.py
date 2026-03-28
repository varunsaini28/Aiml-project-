"""
minimax.py - Minimax Algorithm with Alpha-Beta Pruning
===========================================
Minimax kya karta hai: Best rescue action decide karta hai
MAX player = Rescue Agent (zyada lives bachana chahta hai)
MIN player = Disaster (zyada damage karna chahta hai)
Alpha-Beta Pruning: Useless branches prune karta hai - faster!

Real World Use: Chess, Tic-tac-toe, Game AI, Decision making under adversity
"""

import math
from astar import manhattan_distance

# Possible actions jo agent le sakta hai
ACTION_RESCUE_NEAREST = "rescue_nearest"
ACTION_EXPLORE_DFS = "explore_dfs"
ACTION_WAIT = "wait"
ACTION_RESCUE_SAFEST = "rescue_safest"

def evaluate_state(grid_obj, agent_pos):
    """
    State ka score evaluate karo
    MAX agent ke liye positive score = better
    Factors:
    - Kitne survivors bache hain (kam = better for agent)
    - Agent danger ke kitna paas hai (door = better)
    - Kitne log rescue ho gaye (zyada = better)
    """
    survivors = grid_obj.survivors
    if not survivors:
        return 1000  # Sab rescue ho gaye - maximum score!

    # Nearest survivor ki distance
    min_dist = min(manhattan_distance(agent_pos, s) for s in survivors)

    # Danger zones se proximity check
    from grid import DANGER
    danger_penalty = 0
    r, c = agent_pos
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            nr, nc = r + dr, c + dc
            if 0 <= nr < grid_obj.rows and 0 <= nc < grid_obj.cols:
                if grid_obj.grid[nr][nc] == DANGER:
                    danger_penalty += 5

    # Score = rescued people ka value - distance penalty - danger penalty
    rescued_score = grid_obj.rescued * 100
    distance_penalty = min_dist * 10
    remaining_penalty = len(survivors) * 50

    return rescued_score - distance_penalty - remaining_penalty - danger_penalty


def get_possible_actions(grid_obj):
    """
    Current state mein possible actions return karo
    """
    actions = []
    if grid_obj.survivors:
        actions.append(ACTION_RESCUE_NEAREST)
        actions.append(ACTION_RESCUE_SAFEST)
    actions.append(ACTION_EXPLORE_DFS)
    return actions


def simulate_action(grid_obj, action):
    """
    Kisi action ka simulated outcome calculate karo (actual grid change kiye bina)
    Returns: simulated score
    """
    from astar import astar_safest_path, astar_path
    from bfs import bfs_find_nearest_survivor

    survivors = grid_obj.survivors
    agent_pos = grid_obj.agent_pos

    if action == ACTION_RESCUE_NEAREST:
        if not survivors:
            return evaluate_state(grid_obj, agent_pos)
        # BFS se nearest survivor dhundo
        nearest = min(survivors, key=lambda s: manhattan_distance(agent_pos, s))
        path, _ = astar_path(grid_obj, agent_pos, nearest)
        if path:
            # Agar path mila toh better score
            return evaluate_state(grid_obj, agent_pos) + 50 - len(path)
        return evaluate_state(grid_obj, agent_pos) - 20

    elif action == ACTION_RESCUE_SAFEST:
        if not survivors:
            return evaluate_state(grid_obj, agent_pos)
        # Safest path wala survivor prefer karo
        best_score = -math.inf
        for survivor in survivors:
            path, _ = astar_safest_path(grid_obj, agent_pos, survivor)
            if path:
                score = evaluate_state(grid_obj, agent_pos) + 30 - len(path) * 0.5
                best_score = max(best_score, score)
        return best_score if best_score != -math.inf else evaluate_state(grid_obj, agent_pos) - 10

    elif action == ACTION_EXPLORE_DFS:
        # Exploration se future mein survivors milenge
        return evaluate_state(grid_obj, agent_pos) - 5  # Thoda penalty kyunki abhi rescue nahi

    elif action == ACTION_WAIT:
        return evaluate_state(grid_obj, agent_pos) - 30  # Ruk jaana = worst action

    return evaluate_state(grid_obj, agent_pos)


def minimax(grid_obj, depth, is_maximizing, alpha, beta, nodes_explored):
    """
    Minimax Algorithm with Alpha-Beta Pruning
    
    Parameters:
    - depth: Kitna deep jaana hai (3-4 usually enough)
    - is_maximizing: True = Agent ki turn, False = Disaster ki turn
    - alpha: MAX player ka best guaranteed score (pruning ke liye)
    - beta: MIN player ka best guaranteed score (pruning ke liye)
    - nodes_explored: List to track how many nodes explored (for display)
    
    Returns: Best score
    """
    nodes_explored[0] += 1  # Counter increment

    # Base case: Depth 0 ya game khatam
    if depth == 0 or grid_obj.is_simulation_done():
        return evaluate_state(grid_obj, grid_obj.agent_pos)

    actions = get_possible_actions(grid_obj)

    if is_maximizing:
        # Agent ki turn - score maximize karo
        max_eval = -math.inf
        for action in actions:
            eval_score = simulate_action(grid_obj, action)
            # Recursive call (simplified - real mein state copy karni padti)
            eval_score = eval_score + minimax_helper(depth - 1, False, alpha, beta, nodes_explored)
            max_eval = max(max_eval, eval_score)

            # Alpha update karo
            alpha = max(alpha, eval_score)

            # ALPHA-BETA PRUNING: Agar beta <= alpha, branch prune karo
            # MIN player yahan kabhi nahi aayega
            if beta <= alpha:
                nodes_explored[0] += 1  # Pruned node count
                break  # Pruning! Baaki branches mat dekho

        return max_eval

    else:
        # Disaster ki turn - score minimize karo (agent ke liye worst)
        min_eval = math.inf
        for action in actions:
            eval_score = simulate_action(grid_obj, action)
            eval_score = eval_score - minimax_helper(depth - 1, True, alpha, beta, nodes_explored)
            min_eval = min(min_eval, eval_score)

            # Beta update karo
            beta = min(beta, eval_score)

            # ALPHA-BETA PRUNING: MAX player yahan kabhi nahi aayega
            if beta <= alpha:
                nodes_explored[0] += 1
                break  # Pruning!

        return min_eval


def minimax_helper(depth, is_maximizing, alpha, beta, nodes_explored):
    """Helper for simplified recursive calls without full state copy"""
    nodes_explored[0] += 1
    if depth == 0:
        return 0
    if is_maximizing:
        return 10 * depth  # Simplified reward
    else:
        return -5 * depth  # Simplified penalty


def decide_best_action(grid_obj, depth=3):
    """
    Minimax + Alpha-Beta se best action decide karo
    
    Returns: (best_action, scores_dict, nodes_explored_count)
    """
    actions = get_possible_actions(grid_obj)
    if not actions:
        return ACTION_WAIT, {}, 0

    nodes_explored = [0]  # List as mutable counter
    action_scores = {}

    alpha = -math.inf
    beta = math.inf

    for action in actions:
        # Har action ka score calculate karo
        base_score = simulate_action(grid_obj, action)
        future_score = minimax(grid_obj, depth - 1, False, alpha, beta, nodes_explored)
        total_score = base_score + future_score * 0.5
        action_scores[action] = round(total_score, 2)

        # Alpha update
        alpha = max(alpha, total_score)

    # Best action = highest score wala
    best_action = max(action_scores, key=action_scores.get)

    return best_action, action_scores, nodes_explored[0]


def minimax_full_explanation():
    """Minimax ka detailed explanation"""
    return {
        "algorithm": "Minimax with Alpha-Beta Pruning",
        "use_in_project": "Best rescue action decide karne ke liye",
        "players": {
            "MAX": "Rescue Agent - zyada lives bachana chahta hai",
            "MIN": "Disaster - zyada damage karna chahta hai"
        },
        "alpha_beta": "Useless branches prune karta hai - 50-90% faster!",
        "time_complexity": "O(b^d) without pruning, O(b^(d/2)) with pruning",
        "steps": [
            "1. Possible actions identify karo",
            "2. Har action ke liye tree expand karo",
            "3. Leaf nodes evaluate karo (score function)",
            "4. MAX nodes: maximum child select karo",
            "5. MIN nodes: minimum child select karo",
            "6. Alpha-Beta: Branch prune karo agar alpha >= beta",
            "7. Best score wala action choose karo"
        ]
    }
