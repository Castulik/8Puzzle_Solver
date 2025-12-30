import queue1
import stack1
import heapq
import asyncio  # NUTNÉ PRO WEB

TARGET_POSITIONS = {
    1: (0, 0), 2: (0, 1), 3: (0, 2),
    4: (1, 0), 5: (1, 1), 6: (1, 2),
    7: (2, 0), 8: (2, 1), 0: (2, 2)
}

class Node:
    def __init__(self, data, rodic=None, pohyb=None):
        self.rodic = rodic
        self.data = data
        self.pohyb = pohyb
        self.uroven = 0

    def get_data(self): return self.data
    def get_rodic(self): return self.rodic
    def set_pohyb(self, smer): self.pohyb = smer
    def set_rodic(self, node): self.rodic = node

class PuzzleSolver:
    def __init__(self, start_stav):
        self.root = Node(start_stav)
        self.goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        self.prozkoumano = 0
        self.navstiveno = 0
    
    def najdi_nulu(self, matrix):
        for i in range(3):
            for j in range(3):
                if matrix[i][j] == 0: return i, j
        return None
    
    def srovnani_matic(self, matrix):
        return matrix == self.goal

    def pripustne_pohyby(self, r, s):
        pohyby = []
        potencialni_smery = [(-1, 0, "nahoru"), (1, 0, "dolu"), (0, -1, "doleva"), (0, 1, "doprava")] 
        for dr, ds, smer in potencialni_smery:
            novy_r, novy_s = r + dr, s + ds
            if 0 <= novy_r < 3 and 0 <= novy_s < 3:
                pohyby.append((novy_r, novy_s, smer))
        return pohyby

    # --- ASYNCHRONNÍ ALGORITMY ---

    async def solve_puzzle_bfs(self):
        self.prozkoumano = 0 
        fifo = queue1.Queue()
        fifo.push(self.root)
        visited = {tuple(map(tuple, self.root.data))}
        
        while not fifo.is_empty():
            # KAŽDÝCH 500 UZLŮ UVOLNÍME VLÁKNO PRO PROHLÍŽEČ
            if self.prozkoumano % 500 == 0:
                await asyncio.sleep(0)

            node = fifo.pop()
            self.prozkoumano += 1
            
            if self.srovnani_matic(node.data):
                self.navstiveno = len(visited)
                return node
            
            r0, s0 = self.najdi_nulu(node.data)
            for r, s, smer in self.pripustne_pohyby(r0, s0):
                novy_stav = [row[:] for row in node.data]
                novy_stav[r0][s0], novy_stav[r][s] = novy_stav[r][s], 0
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                
                if stav_jako_tuple not in visited:
                    visited.add(stav_jako_tuple)
                    novy_uzel = Node(novy_stav, rodic=node, pohyb=smer)
                    fifo.push(novy_uzel)
        return None

    async def solve_puzzle_dfs(self):
        self.prozkoumano = 0
        stack = stack1.Stack()
        stack.push(self.root)
        visited = {tuple(map(tuple, self.root.data))}
        
        while not stack.is_empty():
            if self.prozkoumano % 500 == 0:
                await asyncio.sleep(0)

            node = stack.pop()
            self.prozkoumano += 1
            
            if self.srovnani_matic(node.data):
                self.navstiveno = len(visited)
                return node
            
            r0, s0 = self.najdi_nulu(node.data)
            for r, s, smer in self.pripustne_pohyby(r0, s0):
                novy_stav = [row[:] for row in node.data]
                novy_stav[r0][s0], novy_stav[r][s] = novy_stav[r][s], 0
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                
                if stav_jako_tuple not in visited:
                    visited.add(stav_jako_tuple)
                    stack.push(Node(novy_stav, rodic=node, pohyb=smer))
        return None

    async def solve_puzzle_dfs_limit(self):
        self.prozkoumano = 0
        stack = stack1.Stack()
        stack.push(self.root)
        visited = {tuple(map(tuple, self.root.data)): 0}
        
        while not stack.is_empty():
            if self.prozkoumano % 500 == 0:
                await asyncio.sleep(0)

            node = stack.pop()
            self.prozkoumano += 1
            
            if self.srovnani_matic(node.data):
                self.navstiveno = len(visited)
                return node
            
            if node.uroven >= 31: continue
            
            r0, s0 = self.najdi_nulu(node.data)
            for r, s, smer in self.pripustne_pohyby(r0, s0):
                novy_stav = [row[:] for row in node.data]
                novy_stav[r0][s0], novy_stav[r][s] = novy_stav[r][s], 0
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                nova_hloubka = node.uroven + 1
                
                if stav_jako_tuple not in visited or nova_hloubka < visited[stav_jako_tuple]:
                    visited[stav_jako_tuple] = nova_hloubka
                    novy_uzel = Node(novy_stav, rodic=node, pohyb=smer)
                    novy_uzel.uroven = nova_hloubka 
                    stack.push(novy_uzel)
        return None

    async def informovany_algortimus_a_star(self):
        self.prozkoumano = 0
        count = 0
        priority_queue = []
        heapq.heappush(priority_queue, (0, 0, count, self.root))
        visited = {tuple(map(tuple, self.root.data))}
        
        while priority_queue:
            if self.prozkoumano % 500 == 0:
                await asyncio.sleep(0)

            f, h, c, node = heapq.heappop(priority_queue)
            self.prozkoumano += 1
            
            if self.srovnani_matic(node.data):
                self.navstiveno = len(visited)
                return node
            
            r0, s0 = self.najdi_nulu(node.data)
            for r, s, smer in self.pripustne_pohyby(r0, s0):
                novy_stav = [row[:] for row in node.data]
                novy_stav[r0][s0], novy_stav[r][s] = novy_stav[r][s], 0
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                
                if stav_jako_tuple not in visited:
                    visited.add(stav_jako_tuple)
                    novy_uzel = Node(novy_stav, rodic=node, pohyb=smer)
                    novy_uzel.uroven = node.uroven + 1
                    h_val = self.manhaton(novy_stav)
                    f_val = novy_uzel.uroven + h_val
                    count += 1
                    heapq.heappush(priority_queue, (f_val, h_val, count, novy_uzel))
        return None

    # Ostatní algoritmy (LC, Weighted, Greedy) upravíš STEJNÝM způsobem:
    # 1. Přidat 'async' před 'def'
    # 2. Dovnitř 'while' přidat: if self.prozkoumano % 500 == 0: await asyncio.sleep(0)

    async def informovany_algortimus_a_star_LC(self):
        self.prozkoumano = 0
        count = 0
        priority_queue = []
        heapq.heappush(priority_queue, (0, 0, count, self.root))
        visited = {tuple(map(tuple, self.root.data))}
        while priority_queue:
            if self.prozkoumano % 500 == 0: await asyncio.sleep(0)
            f, h, c, node = heapq.heappop(priority_queue)
            self.prozkoumano += 1
            if self.srovnani_matic(node.data):
                self.navstiveno = len(visited)
                return node
            r0, s0 = self.najdi_nulu(node.data)
            for r, s, smer in self.pripustne_pohyby(r0, s0):
                novy_stav = [row[:] for row in node.data]
                novy_stav[r0][s0], novy_stav[r][s] = novy_stav[r][s], 0
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                if stav_jako_tuple not in visited:
                    visited.add(stav_jako_tuple)
                    novy_uzel = Node(novy_stav, rodic=node, pohyb=smer)
                    novy_uzel.uroven = node.uroven + 1
                    h_val = self.manhaton_LC(novy_stav)
                    count += 1
                    heapq.heappush(priority_queue, (novy_uzel.uroven + h_val, h_val, count, novy_uzel))
        return None

    async def informovany_algortimus_a_star_weighted(self):
        self.prozkoumano = 0
        count = 0
        priority_queue = []
        heapq.heappush(priority_queue, (0, 0, count, self.root))
        visited = set()
        visited.add(tuple(map(tuple, self.root.data)))
        while priority_queue:
            if self.prozkoumano % 500 == 0: await asyncio.sleep(0)
            f, h, c, node = heapq.heappop(priority_queue)
            self.prozkoumano += 1
            if self.srovnani_matic(node.data):
                self.navstiveno = len(visited)
                return node
            if node.uroven >= 31: continue
            r0, s0 = self.najdi_nulu(node.data)
            for r, s, smer in self.pripustne_pohyby(r0, s0):
                novy_stav = [row[:] for row in node.data]
                novy_stav[r0][s0], novy_stav[r][s] = novy_stav[r][s], 0
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                if stav_jako_tuple not in visited:
                    visited.add(stav_jako_tuple)
                    novy_uzel = Node(novy_stav, rodic=node, pohyb=smer)
                    novy_uzel.uroven = node.uroven + 1
                    h_v = self.manhaton(novy_stav)
                    f_v = novy_uzel.uroven + (2 * h_v if h_v > 10 else h_v)
                    count += 1
                    heapq.heappush(priority_queue, (f_v, h_v, count, novy_uzel))
        return None

    async def informovany_algortimus_greedy(self):
        self.prozkoumano = 0
        count = 0
        priority_queue = []
        heapq.heappush(priority_queue, (0, count, self.root))
        visited = {tuple(map(tuple, self.root.data))}
        while priority_queue:
            if self.prozkoumano % 500 == 0: await asyncio.sleep(0)
            f, c, node = heapq.heappop(priority_queue)
            self.prozkoumano += 1
            if self.srovnani_matic(node.data):
                self.navstiveno = len(visited)
                return node
            r0, s0 = self.najdi_nulu(node.data)
            for r, s, smer in self.pripustne_pohyby(r0, s0):
                novy_stav = [row[:] for row in node.data]
                novy_stav[r0][s0], novy_stav[r][s] = novy_stav[r][s], 0
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                if stav_jako_tuple not in visited:
                    visited.add(stav_jako_tuple)
                    novy_uzel = Node(novy_stav, rodic=node, pohyb=smer)
                    novy_uzel.uroven = node.uroven + 1
                    count += 1
                    heapq.heappush(priority_queue, (self.manhaton(novy_stav), count, novy_uzel))
        return None

    # Heuristiky zůstávají synchronní (jsou rychlé, volají se uvnitř loopu)
    def manhaton(self, matrix):
        total_h = 0
        for i in range(3):
            for j in range(3):
                val = matrix[i][j]
                if val != 0:
                    ti, tj = TARGET_POSITIONS[val]
                    total_h += abs(i - ti) + abs(j - tj)
        return total_h
    
    def manhaton_LC(self, matrix):
        total_h = self.manhaton(matrix)
        # Horizontální konflikty
        for i in range(3):
            v_radku = [(matrix[i][j], j) for j in range(3) if matrix[i][j] != 0 and TARGET_POSITIONS[matrix[i][j]][0] == i]
            for k in range(len(v_radku)):
                for l in range(k + 1, len(v_radku)):
                    if TARGET_POSITIONS[v_radku[k][0]][1] > TARGET_POSITIONS[v_radku[l][0]][1]:
                        total_h += 2
        # Vertikální konflikty
        for j in range(3):
            v_sloupci = [(matrix[i][j], i) for i in range(3) if matrix[i][j] != 0 and TARGET_POSITIONS[matrix[i][j]][1] == j]
            for k in range(len(v_sloupci)):
                for l in range(k + 1, len(v_sloupci)):
                    if TARGET_POSITIONS[v_sloupci[k][0]][0] > TARGET_POSITIONS[v_sloupci[l][0]][0]:
                        total_h += 2
        return total_h

    def zpateční_cesta(self, node):
        cesta = []
        aktualni = node
        while aktualni:
            cesta.append(aktualni.get_data())
            aktualni = aktualni.get_rodic()
        cesta.reverse()
        return cesta

    def resitelnost(self, data):
        seznam = [c for r in data for c in r if c != 0]
        inverze = sum(1 for i in range(len(seznam)) for j in range(i+1, len(seznam)) if seznam[i] > seznam[j])
        return inverze % 2 == 0