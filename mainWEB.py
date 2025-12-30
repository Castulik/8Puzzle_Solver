import mimetypes
import flet as ft
import asyncio
import time
import random
import heapq
import asyncio  # NUTNÉ PRO WEB

# Queue - FIFO - Fronta
class Node:
    def __init__(self, data):
        self.__next = None
        self.__prev = None
        self.__data = data

    def get_data(self):
        return self.__data

    def set_next(self, nextt):
        self.__next = nextt

    def set_prev(self, prev):
        self.__prev = prev

    def get_next(self):
        return self.__next

    def get_prev(self):
        return self.__prev


class Queue:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def is_empty(self):
        if self.head == None:
            return True
        else:
            return False

    def get_size(self):
        return self.size

    def push(self, data):
        temp = Node(data)

        if self.is_empty():
            self.head = temp
            self.tail = temp
        else:
            self.tail.set_next(temp)
            temp.set_prev(self.tail)
            self.tail = temp

        self.size += 1

    def pop(self):
        if self.is_empty():
            raise Exception("Queue is empty!")

        else:
            data = self.head.get_data()

            if self.size > 1:
                next_node = self.head.get_next()
                next_node.set_prev(None)
                self.head = next_node
            else:
                self.head = None
                self.tail = None

            self.size -= 1

            return data

    def print_list(self):
        current = self.head

        while current != None:
            print(current.get_data())
            current = current.get_next()
            
# Stack - LIFO - Zasobnik


class Node:
    def __init__(self, data):
        self.__next = None
        self.__prev = None
        self.__data = data

    def get_data(self):
        return self.__data

    def set_next(self, nextt):
        self.__next = nextt

    def set_prev(self, prev):
        self.__prev = prev

    def get_next(self):
        return self.__next

    def get_prev(self):
        return self.__prev


class Stack:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def is_empty(self):
        if self.head == None:
            return True
        else:
            return False

    def get_size(self):
        return self.size

    def push(self, data):
        temp = Node(data)

        if self.is_empty():
            self.head = temp
            self.tail = temp
        else:
            self.tail.set_next(temp)
            temp.set_prev(self.tail)
            self.tail = temp

        self.size += 1

    def pop(self):

        if self.is_empty():
            raise Exception("Stack is empty!")
        else:
            data = self.tail.get_data()

            if self.size > 1:
                prev = self.tail.get_prev()
                prev.set_next(None)
                self.tail = prev
            else:
                self.tail = None
                self.head = None

            self.size -= 1
            return data

    def peek(self):
        if not self.is_empty():
            return self.tail.get_data()
        else:
            raise Exception("Stack is empty!")

    def print_list(self):
        current = self.head

        while current != None:
            print(current.get_data())
            current = current.get_next()
            
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
        fifo = Queue()
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
        stack = Stack()
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
        stack = Stack()
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

# Fix pro MIME typy na Windows
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/javascript', '.mjs')

async def main(page: ft.Page):
    page.title = "8-Puzzle: Solver"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.window_width = 1100
    page.window_height = 850 # Trochu zvýšíme pro text cesty

    # --- STAVOVÉ PROMĚNNÉ ---
    CILOVY_STAV = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    stav_seznam = [8, 6, 7, 2, 5, 4, 3, 0, 1]
    stav_shuffled_start = list(stav_seznam) 
    is_animating = False 

    # --- UI KOMPONENTY ---
    txt_status = ft.Text("Připraven", size=18, weight=ft.FontWeight.BOLD)
    txt_kroky_cpu = ft.Text("Kroky (CPU): 0", color="blue", weight="bold")
    txt_cas = ft.Text("Čas výpočtu: 0s")
    txt_prozkoumano = ft.Text("Prozkoumáno uzlů: 0")
    txt_visited = ft.Text("Navštíveno (v paměti): 0")
    
    # NOVÉ: Zobrazení cesty jako řetězec písmen
    txt_cesta_pismena = ft.Text("", color="amber", weight="bold", size=16, selectable=True)
    
    history_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    loader = ft.ProgressBar(width=400, color="blue", visible=False)
    mrizka = ft.GridView(expand=False, runs_count=3, max_extent=110, spacing=8, width=350)

    # --- POMOCNÉ FUNKCE ---
    def je_vyreseno():
        return stav_seznam == CILOVY_STAV

    # Funkce pro převod cesty matic na řetězec R-L-U-D
    def ziskej_path_string(cesta_matic):
        path_str = ""
        for i in range(len(cesta_matic) - 1):
            m1 = cesta_matic[i]
            m2 = cesta_matic[i+1]
            
            # Najdeme pozici nuly v obou maticích
            r1, c1, r2, c2 = 0, 0, 0, 0
            for r in range(3):
                for c in range(3):
                    if m1[r][c] == 0: r1, c1 = r, c
                    if m2[r][c] == 0: r2, c2 = r, c
            
            # Porovnáme pohyb prázdného pole
            if r2 < r1: path_str += "U" # Up
            elif r2 > r1: path_str += "D" # Down
            elif c2 < c1: path_str += "L" # Left
            elif c2 > c1: path_str += "R" # Right
        return path_str

    def vytvor_dlazdici(cislo, index):
        vyreseno = je_vyreseno()
        barva = "green700" if vyreseno and cislo != 0 else ("blue700" if cislo != 0 else "grey800")
        return ft.Container(
            content=ft.Text(str(cislo) if cislo != 0 else "", size=25, weight="bold"),
            alignment=ft.Alignment(0, 0),
            width=100, height=100,
            bgcolor=barva,
            border_radius=10,
            on_click=lambda _: klik_na_dlazdici(index),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

    def vykresli_ui():
        mrizka.controls.clear()
        for i, cislo in enumerate(stav_seznam):
            mrizka.controls.append(vytvor_dlazdici(cislo, i))
        if je_vyreseno():
            txt_status.value = "CÍL DOSAŽEN!"
            txt_status.color = "green"
        page.update()

    def set_ui_busy(busy: bool):
        btn_vyresit.disabled = busy
        btn_zamichat.disabled = busy
        btn_reset.disabled = busy
        dropdown_algo.disabled = busy
        btn_stop.visible = busy
        loader.visible = busy
        page.update()

    def klik_na_dlazdici(idx_klik):
        nonlocal stav_seznam
        if is_animating or btn_vyresit.disabled: return
        idx_nula = stav_seznam.index(0)
        r_k, c_k = divmod(idx_klik, 3)
        r_n, c_n = divmod(idx_nula, 3)
        if abs(r_k - r_n) + abs(c_k - c_n) == 1:
            stav_seznam[idx_klik], stav_seznam[idx_nula] = stav_seznam[idx_nula], stav_seznam[idx_klik]
            vykresli_ui()

    async def stop_animace(e):
        nonlocal is_animating
        is_animating = False
        txt_status.value = "Animace zastavena"
        page.update()

    async def reset_na_start(e):
        nonlocal stav_seznam
        stav_seznam = list(stav_shuffled_start)
        txt_status.value = "Zpět na začátku zadání"
        txt_status.color = "white"
        txt_cesta_pismena.value = "" # Smazat cestu při resetu
        vykresli_ui()

    async def spust_vypocet(e):
        nonlocal stav_seznam, is_animating
        if je_vyreseno(): return
        
        pocatecni_stav_pro_historii = str(list(stav_seznam))

        mapovani_funkci = {
            "BFS": "solve_puzzle_bfs",
            "DFS": "solve_puzzle_dfs",
            "DFS Limit": "solve_puzzle_dfs_limit",
            "A*": "informovany_algortimus_a_star",
            "A* LC": "informovany_algortimus_a_star_LC",
            "A* Weighted": "informovany_algortimus_a_star_weighted",
            "Greedy": "informovany_algortimus_greedy"
        }

        matice_start = [stav_seznam[i:i+3] for i in range(0, 9, 3)]
        solver = PuzzleSolver(matice_start)
        
        if not solver.resitelnost(matice_start):
            txt_status.value, txt_status.color = "NEŘEŠITELNÉ!", "red"
            page.update()
            return
        
        set_ui_busy(True)
        txt_status.value, txt_status.color = "CPU počítá...", "blue"
        txt_cesta_pismena.value = ""
        await asyncio.sleep(0.1)

        start_t = time.time()
        vybrany_text = dropdown_algo.value
        algo_name = mapovani_funkci.get(vybrany_text)

        uzol = await getattr(solver, algo_name)()
        trvani = time.time() - start_t

        if uzol:
            cesta_matic = solver.zpateční_cesta(uzol)
            tahy_pocet = len(cesta_matic) - 1
            
            # --- TADY GENEROVÁNÍ PÍSMEN ---
            pismena_cesty = ziskej_path_string(cesta_matic)
            txt_cesta_pismena.value = f"Cesta ({tahy_pocet}): {pismena_cesty}"
            
            txt_status.value, txt_status.color = "Nalezeno! Animuji...", "green"
            txt_cas.value = f"Čas výpočtu: {trvani:.4f} s"
            txt_kroky_cpu.value = f"Kroky (CPU): {tahy_pocet}"
            txt_prozkoumano.value = f"Prozkoumáno: {solver.prozkoumano}"
            txt_visited.value = f"Navštíveno: {solver.navstiveno}"
            
            # Historie
            # --- PŘIDÁNÍ DO HISTORIE (OPRAVENÁ VERZE) ---
            history_item = ft.Container(
                content=ft.Column([
                    # Název algoritmu
                    ft.Text(f"{vybrany_text}", weight="bold", color="blue200", size=14),
                    
                    # Původní startovní stav
                    ft.Text(f"Start: {pocatecni_stav_pro_historii}", size=9, color="grey400", font_family="monospace"),
                    
                    # NOVÉ: Cesta písmeny
                    ft.Text(f"Cesta: {pismena_cesty}", size=9, color="amber", italic=True),
                    
                    # Tahy a Čas
                    ft.Row([
                        ft.Text(f"Tahy: {tahy_pocet}", size=11),
                        ft.Text(f"Čas: {trvani:.3f}s", size=11),
                    ], spacing=15),
                    
                    # Statistiky Prozkoumáno / Navštíveno
                    ft.Text(f"P/V: {solver.prozkoumano} / {solver.navstiveno}", size=11, color="grey500"),
                ], spacing=2),
                padding=10,
                border=ft.border.all(1, "grey700"),
                border_radius=8,
                bgcolor=ft.Colors.with_opacity(0.1, "white")
            )
            history_column.controls.insert(0, history_item)
            if len(history_column.controls) > 8: history_column.controls.pop()
            page.update()

            is_animating = True
            for matice in cesta_matic:
                if not is_animating: break
                await asyncio.sleep(0.25)
                stav_seznam = [p for r in matice for p in r]
                vykresli_ui()
            
            is_animating = False
            set_ui_busy(False)
        else:
            txt_status.value, txt_status.color = "Cesta nenalezena.", "orange"
            set_ui_busy(False)

    def zamichej(e):
        nonlocal stav_seznam, stav_shuffled_start
        temp_solver = PuzzleSolver([[0]*3]*3)
        while True:
            random.shuffle(stav_seznam)
            if temp_solver.resitelnost([stav_seznam[i:i+3] for i in range(0, 9, 3)]) and not je_vyreseno():
                break
        stav_shuffled_start = list(stav_seznam)
        txt_kroky_cpu.value = "Kroky (CPU): 0"
        txt_status.value = "Nové zadání"
        txt_status.color = "white"
        txt_cesta_pismena.value = ""
        vykresli_ui()

    # --- UI LAYOUT ---
    dropdown_algo = ft.Dropdown(
        label="Algoritmus", 
        value="A* Weighted",
        width=200,
        options=[ft.dropdown.Option(k) for k in ["BFS", "DFS", "DFS Limit", "A*", "A* LC", "A* Weighted", "Greedy"]],
    )

    btn_vyresit = ft.FilledButton("VYŘEŠIT", on_click=spust_vypocet, icon=ft.Icons.AUTO_FIX_HIGH, bgcolor=ft.Colors.BLUE_700)
    btn_zamichat = ft.FilledButton("ZAMÍCHAT", on_click=zamichej, icon=ft.Icons.SHUFFLE, bgcolor=ft.Colors.AMBER_800)
    btn_reset = ft.OutlinedButton("ZPĚT NA START", on_click=reset_na_start, icon=ft.Icons.RESTART_ALT)
    btn_stop = ft.FilledTonalButton("STOP", on_click=stop_animace, icon=ft.Icons.STOP, visible=False, bgcolor=ft.Colors.RED_700)

    page.add(
        ft.Column([
            ft.Text("8-Puzzle: Solver", size=32, weight="bold"),
            loader,
            ft.Row([dropdown_algo, btn_vyresit, btn_reset, btn_zamichat, btn_stop], alignment="center"),
            ft.Divider(),
            ft.Row([
                # 1. Hrací pole
                ft.Container(mrizka, padding=10, border=ft.Border.all(1, "grey300"), border_radius=10),
                
                # 2. Statistiky
                ft.Column([
                    ft.Text("AKTUÁLNÍ VÝSLEDEK", weight="bold", color="blue"),
                    txt_status,
                    ft.Divider(height=10),
                    txt_kroky_cpu,
                    txt_cas,
                    # Vložíme text pro cestu sem
                    ft.Text("Směry (díra):", size=12, color="grey"),
                    txt_cesta_pismena, 
                    ft.Divider(height=10),
                    txt_prozkoumano,
                    txt_visited,
                ], width=250), # Trochu jsme rozšířili sloupec
                
                # 3. Historie
                ft.VerticalDivider(width=20),
                # 3. Historie

                ft.VerticalDivider(width=20),

                # 3. Historie
                ft.VerticalDivider(width=20),
                ft.Column([
                    ft.Text("HISTORIE", weight="bold", color="orange"),
                    ft.Container(content=history_column, width=300, height=450, padding=10)
                ])
            ], alignment="center", vertical_alignment="start")
        ], horizontal_alignment="center")
    )
    vykresli_ui()

if __name__ == "__main__":
    ft.app(target=main)