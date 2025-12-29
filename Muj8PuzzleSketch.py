import queue1
import copy
import time
import stack1

#---------- OSNOVA
# 1. uvod, kde predstavim problem 8 puzzle
# 2. moje reseni, prvni bych tam dal toto BFS reseni, ktere funguje dobre.
# 2.1. přišel jsem na to, že né všechny zadání jdou vyřešit, proč?
# Když posuneš nulu doleva nebo doprava, pořadí čísel v řadě se nezmění (inverze zůstanou stejné). Když posuneš nulu nahoru nebo dolů, přeskočíš přesně dvě čísla. Tímto skokem se počet inverzí změní buď o $+2$, $-2$, nebo zůstane stejný. Vždycky tedy zůstaneš u lichého čísla. Nikdy z pětky neuděláš nulu, i kdyby ses rozkrájel.
# implementoval jsem tedy funkci, ktera mi podle meho goal state rekne jestli je to resitelne. Budou mi fungovat zadani se sudym poctem inverzi
# implementoval jsem to ze merim cas plus pocet stavu k vyreseni zadani
# bozi cislo u 8-puzzle je 31. [8, 6, 7], [2, 5, 4], [3, 0, 1] - 31 urovni, 181440 vissited
# vsechny moznosti - $9! = 362 880, musim podelit /2 = 181 440.
# rozdil mezi prozkoumano a vissited
# 2.2. iplmenetovat třeba DFS, ktere by mohlo byt nekdy rychlejsi.

# 2.3 pak mam napad na implementaci svojeho informovaneho algoritmu
# 2.4 udělat nějaké rozhraní kde to budu moct vyřešit ručně. Nebo použití algoritmu co chci implementovat. Nějaké časové srovnání algoritmů v aplikaci.


class Node:
    def __init__(self, data, rodic=None, pohyb=None):
        self.rodic = rodic
        self.data = data
        self.pohyb = pohyb
        self.uroven = 0

    def get_data(self):
        return self.data
    
    def set_data(self, data):
        self.data = data
        
    def get_rodic(self):
        return self.rodic
    
    def set_rodic(self, node):
        self.rodic = node
        
    def get_pohyb(self):
        return self.pohyb
    
    def set_pohyb(self, smer):
        self.pohyb = smer

class PuzzleSolver:
    
    def __init__(self, start_stav):
        self.root = Node(start_stav)
        self.goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    
    def najdi_nulu(self, matrix):
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if matrix[i][j] == 0:
                    return i, j
        return None
    
    def srovnani_matic(self, matrix):
        return matrix == self.goal

    def srovnani_matic_moje(self, matrix):
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if matrix[i][j] != self.goal[i][j]:
                    return False
        return True
    
    def pripustne_pohyby(self, r, s):
        pohyby = []
        
        # Každý prvek je (změna_r, změna_s, název_směru)
        potencialni_smery = [
            (-1, 0, "nahoru"),  # Mínus v řádku = nahoru
            (1, 0, "dolu"),     # Plus v řádku = dolu
            (0, -1, "doleva"),  # Mínus ve sloupci = doleva
            (0, 1, "doprava")   # Plus ve sloupci = doprava
        ] 
        
        for dr, ds, smer in potencialni_smery:
            novy_r, novy_s = r + dr, s + ds
            
            # Kontrola hranic matice 3x3
            if 0 <= novy_r < 3 and 0 <= novy_s < 3:
                # Uložíme souřadnice i název směru
                pohyby.append((novy_r, novy_s, smer))
                
        return pohyby
        
    def solve_puzzle_bfs(self):
        if not self.resitelnost(self.root.data):
            print("--- Neresitelne ---")
            return None
        
        start_time = time.time() # Začátek měření
        prozkoumano_stavu = 0 
            
        fifo = queue1.Queue()
        fifo.push(self.root)
        
        # Centrální evidence navštívených rozložení (křídy na zemi)
        visited = set()
        # Musíme převést startovní matici na tuple, abychom ji mohli uložit
        start_stav_tuple = tuple(map(tuple, self.root.data))
        visited.add(start_stav_tuple)
        
        while not fifo.is_empty():
            node = fifo.pop()
            prozkoumano_stavu += 1 #beru z fifo
            
            if self.srovnani_matic(node.data):
                end_time = time.time() # Konec měření
                print(f"--- Vyreseno (BFS) ---")
                print(f"Cas: {end_time - start_time:.4f} sekund")
                print(f"Delka cesty: {len(self.zpateční_cesta(node))}")
                print(f"Prozkoumano stavu: {prozkoumano_stavu}") 
                print(f"Celkem v pameti (visited): {len(visited)}")
                return node
            
            r0, s0 = self.najdi_nulu(node.data)
            pohyby = self.pripustne_pohyby(r0, s0)
            
            for r, s, smer in pohyby:
                #vytvoreni kopie
                novy_stav = copy.deepcopy(node.data)
                
                cislo = novy_stav[r][s]
                novy_stav[r0][s0] = cislo
                novy_stav[r][s] = 0
                
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                
                if stav_jako_tuple not in visited:
                    visited.add(stav_jako_tuple) #pridavam do visited dalsi stavy z fifo nody
                    
                    novy_uzel = Node(novy_stav)
                    novy_uzel.set_pohyb(smer)
                    novy_uzel.set_rodic(node)
                
                    fifo.push(novy_uzel)
                    
    def solve_puzzle_dfs(self):
        if not self.resitelnost(self.root.data):
            print("--- Neresitelne ---")
            return None
        
        start_time = time.time()
        prozkoumano_stavu = 0
        
        stack = stack1.Stack()
        stack.push(self.root)
        
        visited = set()
        visited.add(tuple(map(tuple, self.root.data)))
        
        while not stack.is_empty(): # Dokud není zásobník prázdný
            node = stack.pop() #bere POSLEDNÍ přidaný prvek
            prozkoumano_stavu += 1
            
            if self.srovnani_matic(node.data):
                end_time = time.time()
                print("--- Vyreseno (DFS) ---")
                print(f"Cas: {end_time - start_time:.4f} s")
                print(f"Delka cesty: {len(self.zpateční_cesta(node))}")
                print(f"Prozkoumano stavu: {prozkoumano_stavu}")
                print(f"Celkem v pameti (visited): {len(visited)}")
                return node
            
            r0, s0 = self.najdi_nulu(node.data)
            pohyby = self.pripustne_pohyby(r0, s0)
            
            for r, s, smer in pohyby:
                #vytvoreni kopie
                novy_stav = copy.deepcopy(node.data)
                
                cislo = novy_stav[r][s]
                novy_stav[r0][s0] = cislo
                novy_stav[r][s] = 0
                
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                
                if stav_jako_tuple not in visited:
                    visited.add(stav_jako_tuple) #pridavam do visited dalsi stavy z fifo nody
                    
                    novy_uzel = Node(novy_stav)
                    novy_uzel.set_pohyb(smer)
                    novy_uzel.set_rodic(node)
                
                    stack.push(novy_uzel)
    
    def solve_puzzle_dfs_limit(self):
        if not self.resitelnost(self.root.data):
            print("--- Neresitelne ---")
            return None
        
        start_time = time.time()
        prozkoumano_stavu = 0
        
        stack = stack1.Stack()
        stack.push(self.root)
        
        # U DFS s limitem musíme být opatrní s 'visited'. 
        # Pro jednoduchost ho necháme, ale musíme opravit logiku hloubky.
        visited = {} # Změna na slovník: stav -> hloubka
        
        while not stack.is_empty(): # Dokud není zásobník prázdný
            node = stack.pop() #bere POSLEDNÍ přidaný prvek
            prozkoumano_stavu += 1
            
            if self.srovnani_matic(node.data):
                end_time = time.time()
                print("--- Vyreseno (DFS_limit) ---")
                print(f"Cas: {end_time - start_time:.4f} s")
                print(f"Delka cesty: {len(self.zpateční_cesta(node))}")
                print(f"Prozkoumano stavu: {prozkoumano_stavu}")
                print(f"Celkem v pameti (visited): {len(visited)}")
                return node
            
            r0, s0 = self.najdi_nulu(node.data)
            pohyby = self.pripustne_pohyby(r0, s0)
            
            if node.uroven >= 31:
                continue
            
            for r, s, smer in pohyby:
                #vytvoreni kopie
                novy_stav = copy.deepcopy(node.data)
                
                cislo = novy_stav[r][s]
                novy_stav[r0][s0] = cislo
                novy_stav[r][s] = 0
                
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                nova_hloubka = node.uroven + 1
                
                # 2. Oprava: Navštívíme stav jen pokud jsme v menší nebo stejné hloubce než minule
                if stav_jako_tuple not in visited or nova_hloubka < visited[stav_jako_tuple]:
                    visited[stav_jako_tuple] = nova_hloubka
                    
                    novy_uzel = Node(novy_stav)
                    novy_uzel.set_pohyb(smer)
                    novy_uzel.set_rodic(node)
                    novy_uzel.uroven = nova_hloubka # 3. Oprava: Správné přičtení hloubky
                    
                    stack.push(novy_uzel)
    
    def zpateční_cesta(self, node):
        
        cesta = []
        
        while node.get_rodic() != None:
            cesta.append(node.get_pohyb())
            node = node.get_rodic()
        
        cesta.reverse()
        
        return cesta      
    
    def resitelnost(self, data):
        #prevedeni matice na seznam bez nuly
        seznam = []
        
        for radek in data:
            for cislo in radek:
                if cislo != 0:
                    seznam.append(cislo)
        
        #vypocet inverzi pro resitelnost
        inverze = 0
        n = len(seznam)
        for i in range(n):
            for j in range(i + 1, n):
                if seznam[i] > seznam[j]:
                    inverze += 1
        
        return inverze % 2 == 0
                
                
#puzzle = PuzzleSolver([[8, 6, 7], [2, 5, 4], [3, 0, 1]])

#puzzle = PuzzleSolver([[0, 8, 7], [6, 5, 4], [3, 2, 1]])
#puzzle = PuzzleSolver([[3, 1, 2], [6, 5, 4], [8 , 7, 0]])

#vysledek = puzzle.solve_puzzle_dfs()
#vysledek = puzzle.solve_puzzle_dfs_limit()

#cesta = puzzle.zpateční_cesta(vysledek)
#print(cesta)
#print(len(cesta))