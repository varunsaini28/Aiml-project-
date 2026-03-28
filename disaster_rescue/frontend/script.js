/**
 * script.js - Frontend Logic
 * ===========================
 * Backend se data fetch karo aur grid render karo
 * Buttons ko API se connect karo
 */

// Cell types (backend se match karte hain)
const CELL = {
  EMPTY: 0,
  DANGER: 1,
  SURVIVOR: 2,
  RESCUE_BASE: 3,
  AGENT: 4,
  VISITED: 5,
  PATH: 6
};

const CELL_EMOJI = {
  0: '',
  1: '🔥',
  2: '🙋',
  3: '🏥',
  4: '🤖',
  5: '',
  6: ''
};

const CELL_CLASS = {
  0: 'cell-empty',
  1: 'cell-danger',
  2: 'cell-survivor',
  3: 'cell-base',
  4: 'cell-agent',
  5: 'cell-visited',
  6: 'cell-path'
};

let autoInterval = null;
let simStarted = false;
let currentState = null;

// Speed slider
const speedSlider = document.getElementById('speed-slider');
const speedVal = document.getElementById('speed-val');
speedSlider.addEventListener('input', () => {
  speedVal.textContent = speedSlider.value + 'ms';
  if (autoInterval) {
    clearInterval(autoInterval);
    autoInterval = setInterval(runStep, parseInt(speedSlider.value));
  }
});

// ---- GRID RENDER ----
function renderGrid(state) {
  const gridEl = document.getElementById('grid');
  gridEl.style.gridTemplateColumns = `repeat(${state.cols}, 38px)`;
  gridEl.innerHTML = '';

  const visitedSet = new Set((state.visited_nodes || []).map(p => p[0] + ',' + p[1]));
  const pathSet = new Set((state.path_history || []).map(p => p[0] + ',' + p[1]));

  for (let r = 0; r < state.rows; r++) {
    for (let c = 0; c < state.cols; c++) {
      const basePos = state.base_pos && state.base_pos[0] === r && state.base_pos[1] === c;
      const agentPos = state.agent_pos && state.agent_pos[0] === r && state.agent_pos[1] === c;
      let val = state.grid[r][c];

      // Overlay rule: Agent position always shows agent; base stays visible when agent not there.
      if (agentPos) {
        val = CELL.AGENT;
      } else if (basePos && val !== CELL.AGENT) {
        val = 3; // RESCUE_BASE
      }

      const cell = document.createElement('div');
      cell.className = 'cell ' + (CELL_CLASS[val] || 'cell-empty');
      cell.textContent = CELL_EMOJI[val] || '';
      cell.title = `(${r}, ${c})`;

      // Hover effect
      cell.addEventListener('mouseenter', () => {
        document.getElementById('hover-coords').textContent =
          `Row: ${r} | Col: ${c} | Type: ${getCellName(val)}`;
      });

      gridEl.appendChild(cell);
    }
  }
}

function getCellName(val) {
  const names = { 0:'Empty', 1:'Danger Zone', 2:'Survivor', 3:'Rescue Base', 4:'AI Agent', 5:'Explored', 6:'Path' };
  return names[val] || 'Unknown';
}

// ---- UPDATE UI ----
function updateUI(data) {
  currentState = data.state;
  const state = data.state;

  // Grid render
  renderGrid(state);

  // Stats
  document.getElementById('rescued-count').textContent = state.rescued;
  document.getElementById('remaining-count').textContent = state.survivors.length;
  document.getElementById('total-count').textContent = state.total_survivors;
  document.getElementById('step-num').textContent = String(state.step_count).padStart(3, '0');

  // Rescue bar
  const pct = state.total_survivors > 0 ? (state.rescued / state.total_survivors * 100) : 0;
  document.getElementById('rescue-bar').style.width = pct + '%';
  document.getElementById('rescue-pct').textContent = Math.round(pct) + '%';

  // Status pill
  const pill = document.getElementById('sim-status');
  if (data.status === 'done') {
    pill.textContent = '✅ MISSION COMPLETE';
    pill.className = 'status-pill done';
  } else if (simStarted) {
    pill.textContent = '🔴 ACTIVE';
    pill.className = 'status-pill running';
  }

  // Message
  if (data.message) {
    document.getElementById('msg-text').textContent = data.message;
  }

  // Algorithm display
  if (data.algorithm_used) {
    const parts = data.algorithm_used.split('+').map(s => s.trim());
    document.getElementById('algo-name').textContent = parts[0] || 'ACTIVE';
    document.getElementById('algo-desc').textContent = data.algorithm_used;
  }

  // Metrics
  const si = data.step_info || {};
  if (si.bfs_nodes_explored !== undefined) document.getElementById('bfs-nodes').textContent = si.bfs_nodes_explored;
  if (si.astar_path_length !== undefined) document.getElementById('astar-path').textContent = si.astar_path_length;
  if (si.nodes_explored_minimax !== undefined) document.getElementById('minimax-nodes').textContent = si.nodes_explored_minimax;
  if (si.astar_nodes_explored !== undefined) document.getElementById('astar-explored').textContent = si.astar_nodes_explored;

  // Minimax action scores
  if (si.action_scores && Object.keys(si.action_scores).length > 0) {
    const bestAction = si.action_decided;
    const scoresEl = document.getElementById('action-scores');
    scoresEl.innerHTML = '';
    const sorted = Object.entries(si.action_scores).sort((a,b) => b[1]-a[1]);
    sorted.forEach(([action, score]) => {
      const row = document.createElement('div');
      row.className = 'score-row' + (action === bestAction ? ' best' : '');
      const cleanName = action.replace(/_/g, ' ').toUpperCase();
      row.innerHTML = `<span class="action-name">${cleanName}</span><span class="action-score">${score}</span>`;
      scoresEl.appendChild(row);
    });
  }

  // Decision log
  if (state.decisions && state.decisions.length > 0) {
    const logEl = document.getElementById('decision-log');
    logEl.innerHTML = '';
    state.decisions.slice(0, 12).forEach((d, i) => {
      const entry = document.createElement('div');
      const isRescue = d.includes('rescued') || d.includes('Survivor');
      entry.className = 'log-entry ' + (i === 0 ? 'new-entry' : '') + (isRescue ? ' rescue-entry' : '');
      entry.textContent = d.length > 100 ? d.substring(0, 100) + '...' : d;
      logEl.appendChild(entry);
    });
  }

  // Stop auto if done
  if (data.status === 'done') {
    if (autoInterval) {
      clearInterval(autoInterval);
      autoInterval = null;
    }
    document.getElementById('btn-auto').textContent = '⚡ AUTO RUN';
    document.getElementById('btn-step').disabled = true;
    document.getElementById('btn-auto').disabled = true;
    document.getElementById('sim-status').textContent = '✅ MISSION COMPLETE';
    document.getElementById('sim-status').className = 'status-pill done';
  }
}

// ---- API CALLS ----
async function startSim() {
  const res = await fetch('/api/reset', { method: 'POST' });
  const data = await res.json();
  simStarted = true;
  document.getElementById('btn-step').disabled = false;
  document.getElementById('btn-auto').disabled = false;
  document.getElementById('sim-status').textContent = '🟢 INITIALIZED';
  document.getElementById('sim-status').className = 'status-pill running';

  // Clear metrics
  ['bfs-nodes','astar-path','minimax-nodes','astar-explored'].forEach(id => {
    document.getElementById(id).textContent = '-';
  });
  document.getElementById('action-scores').innerHTML = '<div class="scores-placeholder">Step through to see decisions...</div>';
  document.getElementById('decision-log').innerHTML = '<div class="log-entry">Simulation initialized. Press Next Step.</div>';

  updateUI({ ...data, algorithm_used: 'STANDBY', step_info: {}, message: '🚨 Simulation initialized! Press NEXT STEP or AUTO RUN to begin rescue operations.' });
  document.getElementById('msg-text').textContent = '🚨 City map generated. AI agents ready for deployment. Press NEXT STEP!';
}

async function runStep() {
  if (!simStarted) return;
  const res = await fetch('/api/step', { method: 'POST' });
  const data = await res.json();
  updateUI(data);

  if (data.status === 'done') {
    if (autoInterval) { clearInterval(autoInterval); autoInterval = null; }
    document.getElementById('btn-auto').textContent = '⚡ AUTO RUN';
    showCompletionEffect();
  }
}

function nextStep() {
  if (!simStarted) { alert('Please press START SIM first!'); return; }
  runStep();
}

function autoRun() {
  if (!simStarted) { alert('Please press START SIM first!'); return; }
  if (autoInterval) {
    clearInterval(autoInterval);
    autoInterval = null;
    document.getElementById('btn-auto').innerHTML = '<span class="btn-icon">⚡</span> AUTO RUN';
  } else {
    const speed = parseInt(speedSlider.value);
    autoInterval = setInterval(runStep, speed);
    document.getElementById('btn-auto').innerHTML = '<span class="btn-icon">⏸</span> PAUSE';
  }
}

async function resetSim() {
  if (autoInterval) { clearInterval(autoInterval); autoInterval = null; }
  simStarted = false;
  document.getElementById('btn-step').disabled = true;
  document.getElementById('btn-auto').disabled = true;
  document.getElementById('btn-auto').innerHTML = '<span class="btn-icon">⚡</span> AUTO RUN';
  document.getElementById('sim-status').textContent = '⬛ STANDBY';
  document.getElementById('sim-status').className = 'status-pill';
  document.getElementById('algo-name').textContent = 'STANDBY';
  document.getElementById('algo-desc').textContent = 'Awaiting simulation start...';
  document.getElementById('action-scores').innerHTML = '<div class="scores-placeholder">Run simulation to see decisions...</div>';
  document.getElementById('decision-log').innerHTML = '<div class="log-entry placeholder-log">Simulation not started yet...</div>';
  ['bfs-nodes','astar-path','minimax-nodes','astar-explored'].forEach(id => {
    document.getElementById(id).textContent = '-';
  });

  const res = await fetch('/api/reset', { method: 'POST' });
  const data = await res.json();
  renderGrid(data.state);
  document.getElementById('rescued-count').textContent = 0;
  document.getElementById('remaining-count').textContent = data.state.survivors.length;
  document.getElementById('total-count').textContent = data.state.total_survivors;
  document.getElementById('step-num').textContent = '000';
  document.getElementById('rescue-bar').style.width = '0%';
  document.getElementById('rescue-pct').textContent = '0%';
  document.getElementById('msg-text').textContent = 'Press START SIM to begin a new rescue operation.';
}

// ---- ALGO INFO MODAL ----
async function toggleAlgoInfo() {
  const overlay = document.getElementById('algo-info-overlay');
  overlay.classList.toggle('open');

  if (overlay.classList.contains('open')) {
    const cardsEl = document.getElementById('algo-cards-content');
    if (cardsEl.textContent === 'Loading...') {
      try {
        const res = await fetch('/api/algorithms_info');
        const info = await res.json();
        cardsEl.innerHTML = '';
        const algos = [
          { key: 'bfs', color: '#00ffe0' },
          { key: 'dfs', color: '#ffd600' },
          { key: 'astar', color: '#00b4ff' },
          { key: 'minimax', color: '#ff6b00' }
        ];
        algos.forEach(({ key, color }) => {
          const a = info[key];
          const card = document.createElement('div');
          card.className = 'algo-card';
          const steps = (a.steps || []).map(s => `<li style="margin-bottom:3px;">${s}</li>`).join('');
          card.innerHTML = `
            <h3 style="color:${color}">${a.algorithm}</h3>
            <p><strong>Use:</strong> ${a.use_in_project}</p>
            <p><strong>Time:</strong> ${a.time_complexity}</p>
            <p><strong>DS Used:</strong> ${a.data_structure}</p>
            <p style="margin-top:8px; font-size:0.65rem; color:#2a4a6b;">${a.guarantees}</p>
            <ul style="margin-top:8px; font-size:0.65rem; color:#4a7a9b; padding-left:14px; line-height:1.8;">${steps}</ul>
            <span class="tag">${key.toUpperCase()}</span>
          `;
          cardsEl.appendChild(card);
        });
      } catch(e) {
        document.getElementById('algo-cards-content').innerHTML = '<p>Could not load algorithm info. Make sure Flask server is running.</p>';
      }
    }
  }
}

function showCompletionEffect() {
  document.getElementById('msg-text').textContent = '🎉 MISSION COMPLETE! All survivors have been rescued by the AI agents!';
  document.getElementById('msg-text').style.color = '#00ff88';
}

// ---- INIT: Load initial grid ----
window.addEventListener('load', async () => {
  try {
    const res = await fetch('/api/state');
    const state = await res.json();
    renderGrid(state);
    document.getElementById('remaining-count').textContent = state.survivors.length;
    document.getElementById('total-count').textContent = state.total_survivors;
  } catch(e) {
    document.getElementById('msg-text').textContent = '⚠️ Cannot connect to Flask server. Run: python main.py';
    document.getElementById('msg-text').style.color = '#ff2244';
  }
});
