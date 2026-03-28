"""
main.py - Flask Backend Server
===========================================
Ye file frontend aur backend ko connect karta hai
Flask ka use karke REST API banate hain
Simulation ka main loop yahan manage hota hai
"""

from flask import Flask, jsonify, request, send_from_directory
import os
import json

# Apne modules import karo
from grid import Grid
from bfs import bfs_find_nearest_survivor
from dfs import dfs_explore_area, dfs_find_survivor
from astar import astar_path, astar_safest_path
from minimax import decide_best_action, ACTION_RESCUE_NEAREST, ACTION_RESCUE_SAFEST, ACTION_EXPLORE_DFS

app = Flask(__name__, static_folder='frontend')

# Global simulation state
simulation = None

def create_simulation():
    """Naya simulation banao"""
    global simulation
    simulation = Grid(rows=12, cols=16, danger_pct=0.18, survivor_count=8)
    return simulation


@app.route('/')
def index():
    """Frontend serve karo"""
    return send_from_directory('frontend', 'index.html')


@app.route('/<path:filename>')
def frontend_static(filename):
    """Serve frontend assets directly from frontend folder"""
    return send_from_directory('frontend', filename)


@app.route('/api/reset', methods=['POST'])
def reset():
    """Simulation reset karo - naya map banao"""
    create_simulation()
    return jsonify({
        "status": "reset",
        "state": simulation.to_dict(),
        "message": "🔄 Naya simulation shuru! City map regenerate hua."
    })


@app.route('/api/state', methods=['GET'])
def get_state():
    """Current simulation state return karo"""
    global simulation
    if simulation is None:
        create_simulation()
    return jsonify(simulation.to_dict())


@app.route('/api/step', methods=['POST'])
def next_step():
    """
    Ek step simulate karo:
    1. Minimax se decide karo kya karna hai
    2. Decision ke hisab se algorithm run karo
    3. Agent ko move karo
    4. State return karo
    """
    global simulation

    if simulation is None:
        create_simulation()

    if simulation.is_simulation_done():
        return jsonify({
            "status": "done",
            "state": simulation.to_dict(),
            "message": "✅ Simulation complete! Sab survivors rescue ho gaye ya maximum steps reach ho gaye.",
            "algorithm_used": "None",
            "step_info": {}
        })

    simulation.step_count += 1

    # --- MINIMAX: Best action decide karo ---
    best_action, action_scores, nodes_pruned = decide_best_action(simulation, depth=3)

    step_info = {
        "step": simulation.step_count,
        "action_decided": best_action,
        "action_scores": action_scores,
        "nodes_explored_minimax": nodes_pruned,
        "survivors_remaining": len(simulation.survivors),
        "rescued_so_far": simulation.rescued,
    }

    algorithm_used = ""
    message = ""
    visited_nodes = []
    path_taken = []

    # --- ACTION EXECUTE KARO ---

    if best_action in [ACTION_RESCUE_NEAREST, ACTION_RESCUE_SAFEST] and simulation.survivors:

        # --- BFS: Nearest survivor dhundo ---
        nearest_survivor, bfs_path, bfs_visited = bfs_find_nearest_survivor(simulation)
        step_info["bfs_nearest"] = nearest_survivor
        step_info["bfs_nodes_explored"] = len(bfs_visited)

        if nearest_survivor:
            # --- A*: Safest path dhundo ---
            if best_action == ACTION_RESCUE_SAFEST:
                path, astar_visited = astar_safest_path(simulation, simulation.agent_pos, nearest_survivor)
                algorithm_used = "BFS (nearest) + A* (safest path)"
            else:
                path, astar_visited = astar_path(simulation, simulation.agent_pos, nearest_survivor)
                algorithm_used = "BFS (nearest) + A* (shortest path)"

            step_info["astar_path_length"] = len(path)
            step_info["astar_nodes_explored"] = len(astar_visited)

            if path and len(path) > 1:
                # Agent ko path pe move karo (ek step at a time)
                next_pos = path[1]  # Path ka next step
                simulation.mark_path(path[1:-1])  # Middle steps mark karo
                simulation.move_agent(next_pos)
                path_taken = path
                visited_nodes = bfs_visited[:20]  # First 20 visited nodes

                message = f"🚁 Step {simulation.step_count}: {algorithm_used} | Survivor at {nearest_survivor} | Path length: {len(path)}"

                if simulation.agent_pos == nearest_survivor:
                    message = f"🎉 Step {simulation.step_count}: Survivor RESCUED at {nearest_survivor}! Total rescued: {simulation.rescued}"
            else:
                # Direct neighbor ya path nahi mila - DFS explore karo
                dfs_path, dfs_visited = dfs_explore_area(simulation, max_steps=15)
                algorithm_used = "DFS (exploration - no path found)"
                if len(dfs_path) > 1:
                    simulation.mark_path(dfs_path[1:])
                    simulation.move_agent(dfs_path[1])
                visited_nodes = dfs_visited[:20]
                message = f"🔍 Step {simulation.step_count}: DFS exploring (no direct path) | Nodes explored: {len(dfs_visited)}"
        else:
            message = f"✅ Step {simulation.step_count}: No more survivors to rescue!"

    else:
        # --- DFS: Unexplored area explore karo ---
        dfs_path, dfs_visited = dfs_explore_area(simulation, max_steps=20)
        algorithm_used = "DFS (exploration)"
        step_info["dfs_nodes_explored"] = len(dfs_visited)

        if len(dfs_path) > 1:
            simulation.mark_path(dfs_path[1:])
            simulation.move_agent(dfs_path[1])
            path_taken = dfs_path
        visited_nodes = dfs_visited[:20]
        message = f"🗺️ Step {simulation.step_count}: DFS exploring unvisited areas | Nodes: {len(dfs_visited)}"

    # Visited nodes update karo (visualization ke liye)
    simulation.visited_nodes = visited_nodes
    simulation.path_history = path_taken

    # Decision log mein add karo
    decision_msg = f"Step {simulation.step_count}: Minimax chose '{best_action}' | Scores: {json.dumps(action_scores)}"
    if decision_msg not in simulation.decisions:
        simulation.decisions.insert(0, decision_msg)
        simulation.decisions = simulation.decisions[:15]  # Last 15 decisions rakhte hain

    return jsonify({
        "status": "running" if not simulation.is_simulation_done() else "done",
        "state": simulation.to_dict(),
        "message": message,
        "algorithm_used": algorithm_used,
        "step_info": step_info
    })


@app.route('/api/auto_run', methods=['POST'])
def auto_run():
    """Multiple steps ek saath run karo"""
    global simulation
    if simulation is None:
        create_simulation()

    steps = request.json.get('steps', 5)
    results = []

    for _ in range(steps):
        if simulation.is_simulation_done():
            break
        # Step logic yahan call karo
        simulation.step_count += 1
        best_action, action_scores, _ = decide_best_action(simulation, depth=2)

        if best_action in [ACTION_RESCUE_NEAREST, ACTION_RESCUE_SAFEST] and simulation.survivors:
            from astar import astar_path as ap
            from bfs import bfs_find_nearest_survivor as bfs_nn
            nearest, _, _ = bfs_nn(simulation)
            if nearest:
                path, _ = ap(simulation, simulation.agent_pos, nearest)
                if path and len(path) > 1:
                    simulation.mark_path(path[1:-1])
                    simulation.move_agent(path[1])
        else:
            dfs_path, _ = dfs_explore_area(simulation, max_steps=15)
            if len(dfs_path) > 1:
                simulation.mark_path(dfs_path[1:])
                simulation.move_agent(dfs_path[1])

        results.append(f"Step {simulation.step_count}: Action={best_action}")

    return jsonify({
        "status": "done" if simulation.is_simulation_done() else "running",
        "state": simulation.to_dict(),
        "steps_run": len(results),
        "message": f"⚡ {len(results)} steps completed! Rescued: {simulation.rescued}/{simulation.total_survivors}"
    })


@app.route('/api/algorithms_info', methods=['GET'])
def algorithms_info():
    """Sab algorithms ki information return karo"""
    from bfs import bfs_full_explanation
    from dfs import dfs_full_explanation
    from astar import astar_full_explanation
    from minimax import minimax_full_explanation

    return jsonify({
        "bfs": bfs_full_explanation(),
        "dfs": dfs_full_explanation(),
        "astar": astar_full_explanation(),
        "minimax": minimax_full_explanation()
    })


if __name__ == '__main__':
    # Simulation shuru karo
    create_simulation()
    print("🚨 AI Disaster Response Simulator Starting...")
    print("📡 Server: http://localhost:5000")
    print("🤖 Algorithms: BFS + DFS + A* + Minimax + Alpha-Beta Pruning")
    app.run(debug=True, host='0.0.0.0', port=5000)
