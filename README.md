# 🚨 AI Disaster Response & Rescue Simulator

A complete AI-powered simulation system that demonstrates 5 core algorithms working together to save lives in a disaster-affected city.

LIVE= https://aiml-project-7v2w.onrender.com

<b>Name: varun saini</b><br>
<b>Reg no: 25BCE10360</b>

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install flask

# 2. Run the server
cd disaster_rescue
python main.py

# 3. Open browser
# Go to: http://localhost:5000
```

---

## 🗂️ Project Structure

```
disaster_rescue/
├── main.py          ← Flask server + simulation loop
├── grid.py          ← City map + environment
├── bfs.py           ← BFS algorithm
├── dfs.py           ← DFS algorithm
├── astar.py         ← A* algorithm
├── minimax.py       ← Minimax + Alpha-Beta Pruning
├── requirements.txt
└── frontend/
    ├── index.html   ← Main UI
    ├── style.css    ← Dark military theme
    └── script.js    ← Frontend logic + API calls
```

---

## 🧠 Algorithm Deep Dive (Viva Guide)

---

### 1. BFS — Breadth First Search

**Question: BFS kya karta hai is project mein?**

BFS nearest survivor dhundta hai. Agent ki current position se shuru karke, layer by layer sab adjacent cells explore karta hai. Jab pehla survivor mile — wo hamesha nearest hoga kyunki BFS levels mein explore karta hai.

**Data Structure:** Queue (FIFO — First In, First Out)

**Working:**
```
Queue: [(0,0)]
Visit (0,0) → Add neighbors: (0,1), (1,0)
Visit (0,1) → Add neighbors: (0,2), (1,1)
Visit (1,0) → Add neighbors: (2,0), (1,1) [already visited]
...jab tak survivor na mile
```

**Guarantee:** Shortest path in unweighted graph (sabse kam steps mein nearest survivor)

**Time Complexity:** O(V + E) — V nodes, E edges  
**Space Complexity:** O(V) — worst case sab nodes queue mein

**Real World:** GPS shortest route, Social network "people you may know", Web crawlers

---

### 2. DFS — Depth First Search

**Question: DFS kyun use kiya?**

DFS unexplored areas explore karta hai. Jab agent ko koi direct path nahi milta ya wo naye areas dhundhna chahta hai, DFS ek direction mein jaata hai jab tak possible ho, phir backtrack karta hai.

**Data Structure:** Stack (LIFO — Last In, First Out)

**Working:**
```
Stack: [(0,0)]
Pop (0,0) → Push neighbors: (0,1), (1,0)
Pop (1,0) → Push neighbors: (2,0), (1,1)  ← Deep exploration
Pop (2,0) → Push neighbors: (3,0)
...bahut deep jaata hai pehle
```

**BFS vs DFS:**
- BFS: Wide exploration (nearest first) → Better for finding NEAREST
- DFS: Deep exploration (one path fully) → Better for MAPPING unknown areas

**Time Complexity:** O(V + E)  
**Real World:** Maze solving, File system traversal, Dependency resolution

---

### 3. A* Algorithm

**Question: A* kaise kaam karta hai?**

A* sabse intelligent pathfinding algorithm hai. Ye do cheezein combine karta hai:
- **g(n):** Start se current node tak actual cost
- **h(n):** Current node se goal tak estimated cost (heuristic = Manhattan Distance)
- **f(n) = g(n) + h(n):** Total estimated cost

Danger zones ko cost = 10 deta hai (normal = 1), isliye agent automatically safe paths prefer karta hai.

**Manhattan Distance (heuristic):**
```python
|row1 - row2| + |col1 - col2|
# Example: (0,0) to (3,4) = |3-0| + |4-0| = 7
```

**Why Manhattan Distance?** Grid mein diagonal movement nahi hai, isliye Manhattan distance hamesha correct estimate deta hai (never overestimates = admissible heuristic)

**Priority Queue use kaise:**
```
Min-Heap: [(f_cost, g_cost, position, path)]
Lowest f_cost pehle process hota hai
```

**Time Complexity:** O(b^d) where b = branching factor, d = depth  
**Real World:** Google Maps, Game AI, Robot navigation, GPS routing

---

### 4. Minimax Algorithm

**Question: Minimax kya decide karta hai?**

Minimax rescue agent ke liye best ACTION decide karta hai:
- Available actions: `rescue_nearest`, `rescue_safest`, `explore_dfs`, `wait`
- Har action ka score calculate karta hai considering future consequences
- MAX player (Agent) = score maximize karna chahta hai (zyada lives bachao)
- MIN player (Disaster) = score minimize karna chahta hai (zyada damage)

**Evaluation Function:**
```python
score = (rescued * 100) - (distance_to_nearest * 10) 
        - (remaining_survivors * 50) - (danger_proximity * 5)
```

**Tree Structure:**
```
Root (Agent - MAX)
├── rescue_nearest → score: 450
│   └── Disaster (MIN) responds
│       ├── flood spreads → score: 400
│       └── fire grows → score: 380 ← MIN chooses this
├── explore_dfs → score: 300
│   └── Disaster (MIN) responds
│       └── ...
└── wait → score: 200 ← MAX avoids this
```

Agent = MAX chooses `rescue_nearest` (score: 380) over others

**Time Complexity:** O(b^d)  
**Real World:** Chess engines, Game AI, Strategic decision making

---

### 5. Alpha-Beta Pruning

**Question: Alpha-Beta Pruning kya optimize karta hai?**

Alpha-Beta Pruning Minimax tree ke useless branches prune karta hai — jinhe dekhe bina hi pata chal jaata hai wo best choice nahi honge.

**Alpha:** MAX player ka best guaranteed score ab tak  
**Beta:** MIN player ka best guaranteed score ab tak

**Pruning condition:** `if beta <= alpha: PRUNE (break)`

**Example:**
```
MAX node exploring...
├── Branch A → score: 5 (alpha = 5)
├── Branch B → MIN exploring...
│   ├── B1 → score: 3 (beta = 3)
│   │   → beta(3) < alpha(5) → PRUNE! B ke baaki branches mat dekho
│   └── B2 → [PRUNED - never evaluated]
└── Branch C → ...
```

**Efficiency gain:**
- Without pruning: O(b^d)
- With pruning: O(b^(d/2)) → sqrt of nodes!
- Example: Chess depth 6 → 10^9 nodes → 10^4.5 nodes with pruning!

**Real World:** Chess engines (Stockfish uses this), Any adversarial game

---

## 🌍 Real World Relevance

| Algorithm | Real World Application |
|-----------|----------------------|
| BFS | GPS nearest hospital, Fire brigade routing |
| DFS | Search & Rescue drones mapping unknown terrain |
| A* | Military route planning avoiding minefields |
| Minimax | Emergency response resource allocation |
| Alpha-Beta | Real-time tactical decision systems |

---

## 📊 How Algorithms Work Together

```
STEP:
  1. Minimax decides: "Rescue the nearest survivor" (best action)
  
  2. BFS finds: Nearest survivor is at (5, 8)
  
  3. A* plots: Safest path (0,0)→(1,1)→(2,2)→...→(5,8)
              avoiding danger zones
  
  4. Agent moves one step along A* path
  
  NEXT STEP:
  5. Minimax re-evaluates based on new state
  6. If no direct path → DFS explores to find new areas
  7. Repeat until all survivors rescued
```

---




