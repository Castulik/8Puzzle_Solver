// --- ZÁKLADNÍ DATOVÉ STRUKTURY (PŘEPIS Z PYTHONU) ---
class NodeDS {
    constructor(data) { this.next = null; this.prev = null; this.data = data; }
}
class Queue {
    constructor() { this.head = null; this.tail = null; this.size = 0; }
    isEmpty() { return this.head === null; }
    push(data) {
        let temp = new NodeDS(data);
        if (this.isEmpty()) { this.head = temp; this.tail = temp; }
        else { this.tail.next = temp; temp.prev = this.tail; this.tail = temp; }
        this.size++;
    }
    pop() {
        if (this.isEmpty()) return null;
        let data = this.head.data;
        if (this.size > 1) { this.head = this.head.next; this.head.prev = null; }
        else { this.head = null; this.tail = null; }
        this.size--;
        return data;
    }
}
class Stack {
    constructor() { this.head = null; this.tail = null; this.size = 0; }
    isEmpty() { return this.head === null; }
    push(data) {
        let temp = new NodeDS(data);
        if (this.isEmpty()) { this.head = temp; this.tail = temp; }
        else { this.tail.next = temp; temp.prev = this.tail; this.tail = temp; }
        this.size++;
    }
    pop() {
        if (this.isEmpty()) return null;
        let data = this.tail.data;
        if (this.size > 1) { this.tail = this.tail.prev; this.tail.next = null; }
        else { this.head = null; this.tail = null; }
        this.size--;
        return data;
    }
}

class PuzzleNode {
    constructor(data, rodic = null, pohyb = null) {
        this.data = data;
        this.rodic = rodic;
        this.pohyb = pohyb;
        this.uroven = rodic ? rodic.uroven + 1 : 0;
        this.f = 0; 
    }
}

const TARGET_POSITIONS = {
    1:[0,0], 2:[0,1], 3:[0,2], 4:[1,0], 5:[1,1], 6:[1,2], 7:[2,0], 8:[2,1], 0:[2,2]
};

class PuzzleSolver {
    constructor(startStav) {
        this.root = new PuzzleNode(startStav);
        this.goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]];
        this.prozkoumano = 0;
        this.navstiveno = 0;
    }
    najdiNulu(m) { for(let i=0; i<3; i++) for(let j=0; j<3; j++) if(m[i][j]===0) return [i,j]; }
    srovnaniMatic(m1) { return JSON.stringify(m1) === JSON.stringify(this.goal); }
    pripustnePohyby(r, s) {
        let res = [];
        let dirs = [[-1, 0, "U"], [1, 0, "D"], [0, -1, "L"], [0, 1, "R"]];
        for (let [dr, ds, label] of dirs) {
            let nr = r + dr, ns = s + ds;
            if (nr>=0 && nr<3 && ns>=0 && ns<3) res.push([nr, ns, label]);
        }
        return res;
    }
    manhattan(m) {
        let h = 0;
        for(let i=0; i<3; i++) for(let j=0; j<3; j++) {
            let v = m[i][j];
            if(v!==0) { let [ti, tj] = TARGET_POSITIONS[v]; h += Math.abs(i-ti) + Math.abs(j-tj); }
        }
        return h;
    }
    manhattanLC(m) {
        let h = this.manhattan(m);
        for(let i=0; i<3; i++) {
            let row = [];
            for(let j=0; j<3; j++) if(m[i][j]!==0 && TARGET_POSITIONS[m[i][j]][0] === i) row.push([m[i][j], j]);
            for(let k=0; k<row.length; k++) for(let l=k+1; l<row.length; l++)
                if(TARGET_POSITIONS[row[k][0]][1] > TARGET_POSITIONS[row[l][0]][1]) h += 2;
        }
        for(let j=0; j<3; j++) {
            let col = [];
            for(let i=0; i<3; i++) if(m[i][j]!==0 && TARGET_POSITIONS[m[i][j]][1] === j) col.push([m[i][j], i]);
            for(let k=0; k<col.length; k++) for(let l=k+1; l<col.length; l++)
                if(TARGET_POSITIONS[col[k][0]][0] > TARGET_POSITIONS[col[l][0]][0]) h += 2;
        }
        return h;
    }
    resitelnost(data) {
        let flat = data.flat().filter(x => x !== 0);
        let inv = 0;
        for(let i=0; i<flat.length; i++) for(let j=i+1; j<flat.length; j++) if(flat[i]>flat[j]) inv++;
        return inv % 2 === 0;
    }

    // --- ALGORITMY ---
    async solveBFS() {
        let fifo = new Queue(); fifo.push(this.root);
        let visited = new Set([JSON.stringify(this.root.data)]);
        while(!fifo.isEmpty()) {
            if(this.prozkoumano % 500 === 0) await new Promise(r => setTimeout(r, 0));
            let node = fifo.pop(); this.prozkoumano++;
            if(this.srovnaniMatic(node.data)) { this.navstiveno = visited.size; return node; }
            let [r0, s0] = this.najdiNulu(node.data);
            for(let [r, s, label] of this.pripustnePohyby(r0, s0)) {
                let ns = node.data.map(row => [...row]); [ns[r0][s0], ns[r][s]] = [ns[r][s], 0];
                let sStr = JSON.stringify(ns);
                if(!visited.has(sStr)) { visited.add(sStr); fifo.push(new PuzzleNode(ns, node, label)); }
            }
        }
    }
    async solveDFS() {
        let stack = new Stack(); stack.push(this.root);
        let visited = new Set([JSON.stringify(this.root.data)]);
        while(!stack.isEmpty()) {
            if(this.prozkoumano % 500 === 0) await new Promise(r => setTimeout(r, 0));
            let node = stack.pop(); this.prozkoumano++;
            if(this.srovnaniMatic(node.data)) { this.navstiveno = visited.size; return node; }
            let [r0, s0] = this.najdiNulu(node.data);
            for(let [r, s, label] of this.pripustnePohyby(r0, s0)) {
                let ns = node.data.map(row => [...row]); [ns[r0][s0], ns[r][s]] = [ns[r][s], 0];
                let sStr = JSON.stringify(ns);
                if(!visited.has(sStr)) { visited.add(sStr); stack.push(new PuzzleNode(ns, node, label)); }
            }
        }
    }
    async solveDFSLimit(limit = 31) {
        let stack = new Stack(); stack.push(this.root);
        let visited = new Map([[JSON.stringify(this.root.data), 0]]);
        while(!stack.isEmpty()) {
            if(this.prozkoumano % 500 === 0) await new Promise(r => setTimeout(r, 0));
            let node = stack.pop(); this.prozkoumano++;
            if(this.srovnaniMatic(node.data)) { this.navstiveno = visited.size; return node; }
            if(node.uroven >= limit) continue;
            let [r0, s0] = this.najdiNulu(node.data);
            for(let [r, s, label] of this.pripustnePohyby(r0, s0)) {
                let ns = node.data.map(row => [...row]); [ns[r0][s0], ns[r][s]] = [ns[r][s], 0];
                let sStr = JSON.stringify(ns);
                let nH = node.uroven + 1;
                if(!visited.has(sStr) || nH < visited.get(sStr)) {
                    visited.set(sStr, nH); stack.push(new PuzzleNode(ns, node, label));
                }
            }
        }
    }
    async solveAStar(w = 1, useLC = false, greedy = false, weighted = false) {
        let pq = [this.root];
        let visited = new Set([JSON.stringify(this.root.data)]);
        while(pq.length > 0) {
            if(this.prozkoumano % 500 === 0) await new Promise(r => setTimeout(r, 0));
            pq.sort((a,b) => a.f - b.f);
            let node = pq.shift(); this.prozkoumano++;
            if(this.srovnaniMatic(node.data)) { this.navstiveno = visited.size; return node; }
            let [r0, s0] = this.najdiNulu(node.data);
            for(let [r, s, label] of this.pripustnePohyby(r0, s0)) {
                let ns = node.data.map(row => [...row]); [ns[r0][s0], ns[r][s]] = [ns[r][s], 0];
                let sStr = JSON.stringify(ns);
                if(!visited.has(sStr)) {
                    visited.add(sStr);
                    let newNode = new PuzzleNode(ns, node, label);
                    let h = useLC ? this.manhattanLC(ns) : this.manhattan(ns);
                    if(greedy) newNode.f = h;
                    else if(weighted) newNode.f = newNode.uroven + (h > 10 ? 2 * h : h);
                    else newNode.f = newNode.uroven + (h * w);
                    pq.push(newNode);
                }
            }
        }
    }
}

/* ... (Třídy NodeDS, Queue, Stack a PuzzleSolver zůstávají stejné) ... */

// --- UI CONTROL ---
let stavSeznam = [8, 6, 7, 2, 5, 4, 3, 0, 1];
let stavShuffledStart = [...stavSeznam];
let isAnimating = false;
let isBusy = false;

function renderGrid() {
    const grid = document.getElementById('grid'); grid.innerHTML = '';
    const isGoal = JSON.stringify(stavSeznam) === JSON.stringify([1,2,3,4,5,6,7,8,0]);
    stavSeznam.forEach((n, idx) => {
        const d = document.createElement('div');
        d.className = `tile ${n===0?'empty':''} ${isGoal && n!==0?'solved':''}`;
        d.textContent = n===0?'':n;
        d.onclick = () => klikNaDlazdici(idx);
        grid.appendChild(d);
    });
}

function klikNaDlazdici(idxKlik) {
    if(isAnimating || isBusy) return;
    let idxNula = stavSeznam.indexOf(0);
    let rK = Math.floor(idxKlik / 3), cK = idxKlik % 3;
    let rN = Math.floor(idxNula / 3), cN = idxNula % 3;
    if(Math.abs(rK - rN) + Math.abs(cK - cN) === 1) {
        [stavSeznam[idxKlik], stavSeznam[idxNula]] = [stavSeznam[idxNula], stavSeznam[idxKlik]];
        renderGrid();
    }
}

function setUIBusy(busy) {
    isBusy = busy;
    document.getElementById('btnSolve').disabled = busy;
    document.getElementById('btnShuffle').disabled = busy;
    document.getElementById('btnReset').disabled = busy;
    document.getElementById('algoSelect').disabled = busy;
    document.getElementById('btnStop').style.display = busy ? 'inline-block' : 'none';
}

async function startSolver() {
    let matrix = [stavSeznam.slice(0,3), stavSeznam.slice(3,6), stavSeznam.slice(6,9)];
    let solver = new PuzzleSolver(matrix);
    if(!solver.resitelnost(matrix)) {
        document.getElementById('statusTxt').textContent = "UNSOLVABLE!";
        document.getElementById('statusTxt').style.color = "red";
        return;
    }
    
    setUIBusy(true);
    document.getElementById('statusTxt').textContent = "CPU Calculating...";
    document.getElementById('statusTxt').style.color = "white";
    document.getElementById('loader').style.display = "block";
    
    let startT = performance.now();
    let algo = document.getElementById('algoSelect').value;
    let res;

    if(algo === "BFS") res = await solver.solveBFS();
    else if(algo === "DFS") res = await solver.solveDFS();
    else if(algo === "DFS Limit") res = await solver.solveDFSLimit(31);
    else if(algo === "A*") res = await solver.solveAStar(1);
    else if(algo === "A* LC") res = await solver.solveAStar(1, true);
    else if(algo === "A* Weighted") res = await solver.solveAStar(1, false, false, true);
    else if(algo === "Greedy") res = await solver.solveAStar(1, false, true);

    document.getElementById('loader').style.display = "none";

    if(res) {
        let path = []; let curr = res; while(curr) { path.push(curr); curr = curr.rodic; }
        path.reverse();
        let pathStr = path.map(n => n.pohyb).filter(x=>x).join('-');
        
        document.getElementById('statusTxt').textContent = "Solution Found! Animating...";
        document.getElementById('statusTxt').style.color = "green";
        document.getElementById('statCas').textContent = `Calculation Time: ${((performance.now()-startT)/1000).toFixed(4)}s`;
        document.getElementById('statKroky').textContent = `Steps (CPU): ${path.length-1}`;
        document.getElementById('statCesta').textContent = pathStr;
        document.getElementById('statProzkoumano').textContent = `Nodes Explored: ${solver.prozkoumano}`;
        document.getElementById('statNavstiveno').textContent = `Visited (in memory): ${solver.navstiveno}`;

        // --- ADD TO HISTORY ---
        let hItem = document.createElement('div'); 
        hItem.className = 'history-item';
        
        // Výpočet času pro historii
        let totalTime = ((performance.now() - startT) / 1000).toFixed(3);

        hItem.innerHTML = `
            <b style="color:#90CAF9">${algo}</b><br>
            <small style="color:#BDBDBD">Start: [${matrix.flat()}]</small><br>
            <span style="color:#FFB300; font-size:11px; font-style:italic">Path: ${pathStr}</span><br>
            <div style="font-size:12px; margin-top:5px; font-weight: bold;">
                Moves: ${path.length - 1} | Time: ${totalTime}s
            </div>
            <div style="font-size:11px; color:#AAAAAA; margin-top:2px;">
                Explored: ${solver.prozkoumano} | Visited: ${solver.navstiveno}
            </div>
        `;
        document.getElementById('historyList').prepend(hItem);

        isAnimating = true;
        for(let node of path) { 
            if(!isAnimating) break; 
            stavSeznam = node.data.flat(); renderGrid(); 
            await new Promise(r=>setTimeout(r, 250)); 
        }
        isAnimating = false;
        document.getElementById('statusTxt').textContent = "GOAL REACHED!";
    } else {
        document.getElementById('statusTxt').textContent = "Path not found.";
        document.getElementById('statusTxt').style.color = "orange";
    }
    setUIBusy(false);
}

document.getElementById('btnSolve').onclick = startSolver;
document.getElementById('btnStop').onclick = () => { isAnimating = false; document.getElementById('statusTxt').textContent = "Animation Stopped"; };
document.getElementById('btnShuffle').onclick = () => {
    let s = new PuzzleSolver();
    do { stavSeznam.sort(()=>Math.random()-0.5); } while(!s.resitelnost([stavSeznam.slice(0,3), stavSeznam.slice(3,6), stavSeznam.slice(6,9)]));
    stavShuffledStart = [...stavSeznam]; 
    document.getElementById('statusTxt').textContent = "New puzzle generated";
    document.getElementById('statusTxt').style.color = "white";
    renderGrid();
};
document.getElementById('btnReset').onclick = () => { 
    stavSeznam = [...stavShuffledStart]; 
    isAnimating=false; 
    document.getElementById('statusTxt').textContent = "Back to start configuration";
    renderGrid(); 
};

renderGrid();

// Funkce pro vykreslení malého cílového stavu
function renderTargetGrid() {
    const targetGrid = document.getElementById('targetGrid');
    const goalState = [1, 2, 3, 4, 5, 6, 7, 8, 0];
    
    targetGrid.innerHTML = '';
    goalState.forEach(n => {
        const d = document.createElement('div');
        d.className = `target-tile ${n === 0 ? 'empty' : ''}`;
        d.textContent = n === 0 ? '' : n;
        targetGrid.appendChild(d);
    });
}

// Nezapomeň ji zavolat hned při startu (např. pod renderGrid())
renderGrid();
renderTargetGrid();