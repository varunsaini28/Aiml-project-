"""
grid.py - Disaster-affected city ka environment
Ye module grid banata hai jisme sab kuch hota hai
"""

import random

# Cell types ke constants
EMPTY = 0
DANGER = 1      # Fire/Flood zones - Red
SURVIVOR = 2    # Log jo bachaye jane chahiye - Yellow
RESCUE_BASE = 3 # Agent ka ghar - Blue
AGENT = 4       # Rescue agent khud - Blue
VISITED = 5     # Jo areas explore ho gaye
PATH = 6        # Jo path agent ne liya

CELL_NAMES = {
    EMPTY: "Empty",
    DANGER: "Danger",
    SURVIVOR: "Survivor",
    RESCUE_BASE: "Rescue Base",
    AGENT: "Agent",
    VISITED: "Visited",
    PATH: "Path"
}

class Grid:
    """
    City ka map - ek grid jisme disaster scene hai
    Har cell ek location represent karta hai
    """

    def __init__(self, rows=12, cols=16, danger_pct=0.18, survivor_count=8):
        self.rows = rows
        self.cols = cols
        self.danger_pct = danger_pct
        self.survivor_count = survivor_count
        self.grid = []
        self.agent_pos = None
        self.base_pos = None
        self.survivors = []
        self.rescued = 0
        self.total_survivors = survivor_count
        self.path_history = []       # Agent ne kaunse paths liye
        self.visited_nodes = []      # Kaunse nodes explore hue
        self.decisions = []          # Minimax ne kya decide kiya
        self.step_count = 0
        self.generate()

    def generate(self):
        """
        Naya city map generate karo
        Danger zones, survivors, aur rescue base place karo
        """
        # Pehle sab empty karo
        self.grid = [[EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.survivors = []
        self.path_history = []
        self.visited_nodes = []
        self.decisions = []
        self.rescued = 0
        self.step_count = 0

        # Rescue base top-left corner pe - agent ka starting point
        self.base_pos = (0, 0)
        self.grid[0][0] = RESCUE_BASE

        # Agent ko base pe rakho
        self.agent_pos = (0, 0)

        # Danger zones randomly scatter karo - lekin base ke paas nahi
        danger_cells = int(self.rows * self.cols * self.danger_pct)
        placed = 0
        attempts = 0
        while placed < danger_cells and attempts < 1000:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            # Base aur uske neighbors ko safe rakho
            if (r, c) not in [(0,0),(0,1),(1,0),(1,1)] and self.grid[r][c] == EMPTY:
                self.grid[r][c] = DANGER
                placed += 1
            attempts += 1

        # Survivors ko random empty cells pe rakho
        placed = 0
        attempts = 0
        while placed < self.survivor_count and attempts < 1000:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if self.grid[r][c] == EMPTY and (r, c) != self.base_pos:
                self.grid[r][c] = SURVIVOR
                self.survivors.append((r, c))
                placed += 1
            attempts += 1

        self.total_survivors = len(self.survivors)

    def get_neighbors(self, pos, allow_danger=False):
        """
        Kisi position ke valid neighbors return karo (4-directional)
        allow_danger=True matlab danger zones mein bhi ja sakte ho
        """
        r, c = pos
        directions = [(-1,0),(1,0),(0,-1),(0,1)]  # Up, Down, Left, Right
        neighbors = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                cell = self.grid[nr][nc]
                if allow_danger or cell != DANGER:
                    neighbors.append((nr, nc))
        return neighbors

    def to_dict(self):
        """Frontend ke liye grid data JSON format mein"""
        return {
            "grid": self.grid,
            "rows": self.rows,
            "cols": self.cols,
            "agent_pos": self.agent_pos,
            "base_pos": self.base_pos,
            "survivors": self.survivors,
            "rescued": self.rescued,
            "total_survivors": self.total_survivors,
            "path_history": self.path_history,
            "visited_nodes": self.visited_nodes,
            "decisions": self.decisions,
            "step_count": self.step_count
        }

    def mark_visited(self, pos):
        r, c = pos
        if self.grid[r][c] == EMPTY:
            self.grid[r][c] = VISITED

    def mark_path(self, path):
        for pos in path:
            r, c = pos
            if self.grid[r][c] in [EMPTY, VISITED]:
                self.grid[r][c] = PATH

    def move_agent(self, new_pos):
        """Agent ko purani jagah se hatao aur nai jagah pe rakho"""
        if self.agent_pos:
            r, c = self.agent_pos
            if (r, c) == self.base_pos:
                # Base pe agent thi, wapas base dikhani hai
                self.grid[r][c] = RESCUE_BASE
            elif self.grid[r][c] == AGENT:
                # Normal tracking path update
                self.grid[r][c] = PATH

        self.agent_pos = new_pos
        r, c = new_pos
        if self.grid[r][c] == SURVIVOR:
            self.rescued += 1
            if (r, c) in self.survivors:
                self.survivors.remove((r, c))
            self.decisions.append(f"Step {self.step_count}: Survivor rescued at ({r},{c})! Total rescued: {self.rescued}")

        # Ensure agent overlay is always visible
        self.grid[r][c] = AGENT

    def is_simulation_done(self):
        return len(self.survivors) == 0 or self.step_count > 200
