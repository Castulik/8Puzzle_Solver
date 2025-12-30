import queue1
import copy
import time
import stack1
import heapq

TARGET_POSITIONS = {
    1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (0, 3),
    5: (1, 0), 6: (1, 1), 7: (1, 2), 8: (1, 3),
    9: (2, 0), 10: (2, 1), 11: (2, 2), 12: (2, 3),
    13: (3, 0), 14: (3, 1), 15: (3, 2), 0: (3, 3)
}
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

# 2.4 implementoval jsem A* - nejprve jsem klasicky pouzil haldu - prioritni frontu. Do teto fronty jsem mimo node ukladal take f = h + g.
# 2.4 udělat nějaké rozhraní kde to budu moct vyřešit ručně. Nebo použití algoritmu co chci implementovat. Nějaké časové srovnání algoritmů v aplikaci.


class Node:
    def __init__(self, data, rodic=None, pohyb=None):
        self.rodic = rodic
        self.data = data
        self.pohyb = pohyb
        self.uroven = 0
        self.h = 0

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
        self.goal = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
    
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
        n = len(self.goal) # 3 nebo 4
        potencialni_smery = [(-1, 0, "nahoru"), (1, 0, "dolu"), (0, -1, "doleva"), (0, 1, "doprava")] 
        for dr, ds, smer in potencialni_smery:
            novy_r, novy_s = r + dr, s + ds
            if 0 <= novy_r < n and 0 <= novy_s < n:
                pohyby.append((novy_r, novy_s, smer))
        return pohyby
    
    def informovany_algortimus_a_star_tiebreaking_LC(self):
        if not self.resitelnost(self.root.data):
            print("--- Neresitelne ---")
            return None
        
        start_time = time.time()
        prozkoumano_stavu = 0
        count = 0 # 1. OPRAVA: Počítadlo pro řešení shod v haldě
        priority_queue = []
        
        heapq.heappush(priority_queue, (0, 0, count, self.root))
        
        visited = set()
        visited.add(tuple(map(tuple, self.root.data)))
        
        while priority_queue: # Dokud není zásobník prázdný
            f, h, c, node = heapq.heappop(priority_queue) #nejnizsi f
            prozkoumano_stavu += 1
            
            if self.srovnani_matic(node.data):
                end_time = time.time()
                print("--- Vyreseno (a*_tiebreaking_LC) ---")
                print(f"Cas: {end_time - start_time:.4f} s")
                print(f"Delka cesty: {len(self.zpateční_cesta(node))}")
                print(f"Prozkoumano stavu: {prozkoumano_stavu}")
                print(f"Celkem v pameti (visited): {len(visited)}")
                return node
            
            if node.uroven >= 200: continue
            
            r0, s0 = self.najdi_nulu(node.data)
            pohyby = self.pripustne_pohyby(r0, s0)
            
            for r, s, smer in pohyby:
                #vytvoreni kopie
                novy_stav = [row[:] for row in node.data]
                
                cislo = novy_stav[r][s]
                novy_stav[r0][s0] = cislo
                novy_stav[r][s] = 0
                
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                
                if stav_jako_tuple not in visited:
                    visited.add(stav_jako_tuple)
                    
                    novy_uzel = Node(novy_stav)
                    novy_uzel.set_pohyb(smer)
                    novy_uzel.set_rodic(node)
                    
                    novy_uzel.uroven = node.uroven + 1
                    h = self.manhaton_LC(novy_stav)
                    f = novy_uzel.uroven + h
                    
                    count += 1 # Zvýšíme pořadové číslo
                    heapq.heappush(priority_queue, (f, h, count, novy_uzel))
        return None
    
    def informovany_algortimus_a_star(self):
        if not self.resitelnost(self.root.data):
            print("--- Neresitelne ---")
            return None
        
        start_time = time.time()
        prozkoumano_stavu = 0
        count = 0 # 1. OPRAVA: Počítadlo pro řešení shod v haldě
        priority_queue = []
        
        heapq.heappush(priority_queue, (0, count, self.root))
        
        visited = set()
        visited.add(tuple(map(tuple, self.root.data)))
        
        while priority_queue: # Dokud není zásobník prázdný
            f, c, node = heapq.heappop(priority_queue) #nejnizsi f
            prozkoumano_stavu += 1
            
            if self.srovnani_matic(node.data):
                end_time = time.time()
                print("--- Vyreseno (a*) ---")
                print(f"Cas: {end_time - start_time:.4f} s")
                print(f"Delka cesty: {len(self.zpateční_cesta(node))}")
                print(f"Prozkoumano stavu: {prozkoumano_stavu}")
                print(f"Celkem v pameti (visited): {len(visited)}")
                return node
            
            if node.uroven >= 200: continue
            
            r0, s0 = self.najdi_nulu(node.data)
            pohyby = self.pripustne_pohyby(r0, s0)
            
            for r, s, smer in pohyby:
                #vytvoreni kopie
                novy_stav = [row[:] for row in node.data]
                
                cislo = novy_stav[r][s]
                novy_stav[r0][s0] = cislo
                novy_stav[r][s] = 0
                
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                
                if stav_jako_tuple not in visited:
                    visited.add(stav_jako_tuple)
                    
                    novy_uzel = Node(novy_stav)
                    novy_uzel.set_pohyb(smer)
                    novy_uzel.set_rodic(node)
                    
                    novy_uzel.uroven = node.uroven + 1
                    h = self.manhaton(novy_stav)
                    f = novy_uzel.uroven + h
                    
                    count += 1 # Zvýšíme pořadové číslo
                    heapq.heappush(priority_queue, (f, count, novy_uzel))
        return None
    
    def informovany_algortimus_a_star_LC(self):
        if not self.resitelnost(self.root.data):
            print("--- Neresitelne ---")
            return None
        
        start_time = time.time()
        prozkoumano_stavu = 0
        count = 0 # 1. OPRAVA: Počítadlo pro řešení shod v haldě
        priority_queue = []
        
        heapq.heappush(priority_queue, (0, count, self.root))
        
        visited = set()
        visited.add(tuple(map(tuple, self.root.data)))
        
        while priority_queue: # Dokud není zásobník prázdný
            f, c, node = heapq.heappop(priority_queue) #nejnizsi f
            prozkoumano_stavu += 1
            
            if self.srovnani_matic(node.data):
                end_time = time.time()
                print("--- Vyreseno (a*_LC) ---")
                print(f"Cas: {end_time - start_time:.4f} s")
                print(f"Delka cesty: {len(self.zpateční_cesta(node))}")
                print(f"Prozkoumano stavu: {prozkoumano_stavu}")
                print(f"Celkem v pameti (visited): {len(visited)}")
                return node
            
            if node.uroven >= 200: continue
            
            r0, s0 = self.najdi_nulu(node.data)
            pohyby = self.pripustne_pohyby(r0, s0)
            
            for r, s, smer in pohyby:
                #vytvoreni kopie
                novy_stav = [row[:] for row in node.data]
                
                cislo = novy_stav[r][s]
                novy_stav[r0][s0] = cislo
                novy_stav[r][s] = 0
                
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                
                if stav_jako_tuple not in visited:
                    visited.add(stav_jako_tuple)
                    
                    novy_uzel = Node(novy_stav)
                    novy_uzel.set_pohyb(smer)
                    novy_uzel.set_rodic(node)
                    
                    novy_uzel.uroven = node.uroven + 1
                    h = self.manhaton_LC(novy_stav)
                    f = novy_uzel.uroven + h
                    
                    count += 1 # Zvýšíme pořadové číslo
                    heapq.heappush(priority_queue, (f, count, novy_uzel))
        return None
    
    def informovany_algortimus_a_star_weighted(self):
        if not self.resitelnost(self.root.data):
            print("--- Neresitelne ---")
            return None
        
        start_time = time.time()
        prozkoumano_stavu = 0
        count = 0 # 1. OPRAVA: Počítadlo pro řešení shod v haldě
        priority_queue = []
        
        heapq.heappush(priority_queue, (0, 0, count, self.root))
        
        visited = set()
        visited.add(tuple(map(tuple, self.root.data)))
        
        while priority_queue: # Dokud není zásobník prázdný
            f, h, c, node = heapq.heappop(priority_queue) #nejnizsi f
            prozkoumano_stavu += 1
            
            if self.srovnani_matic(node.data):
                end_time = time.time()
                print("--- Vyreseno (a*weighted) ---")
                print(f"Cas: {end_time - start_time:.4f} s")
                print(f"Delka cesty: {len(self.zpateční_cesta(node))}")
                print(f"Prozkoumano stavu: {prozkoumano_stavu}")
                print(f"Celkem v pameti (visited): {len(visited)}")
                return node
            
            if prozkoumano_stavu % 1000000 == 0:
                print(f"Hledám... prozkoumáno {prozkoumano_stavu} stavů, ve frontě je {len(priority_queue)}")
            
            if node.uroven >= 200: continue
            
            r0, s0 = self.najdi_nulu(node.data)
            pohyby = self.pripustne_pohyby(r0, s0)
            
            for r, s, smer in pohyby:
                #vytvoreni kopie
                novy_stav = [row[:] for row in node.data]
                
                cislo = novy_stav[r][s]
                novy_stav[r0][s0] = cislo
                novy_stav[r][s] = 0
                
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                
                # 2. Oprava: Navštívíme stav jen pokud jsme v menší nebo stejné hloubce než minule
                if stav_jako_tuple not in visited:
                    visited.add(stav_jako_tuple)
                    
                    novy_uzel = Node(novy_stav)
                    novy_uzel.set_pohyb(smer)
                    novy_uzel.set_rodic(node)
                    
                    novy_uzel.uroven = node.uroven + 1
                    h = self.manhaton_LC(novy_stav)
                    
                    # Pokud je Manhattan (h) velký, dej mu větší váhu (chovej se jako Greedy)
                    if h > 10:
                        f = novy_uzel.uroven + (5 * h)  # Váha 2 - agresivnější hledání
                    else:
                        f = novy_uzel.uroven + h        # Klasické A* pro přesné dojetí do cíle
                    
                    count += 1 # Zvýšíme pořadové číslo
                    #vlozime h, takze kdyz je stejne f, budeme se rozhodovat podle h
                    # mensi h znamena, ze jsme blize k cily - mensi manhaton
                    heapq.heappush(priority_queue, (f, h, count, novy_uzel))
        return None             
    
    def manhaton(self, matrix):
        
        total_h = 0
        
        # 1. ZÁKLADNÍ MANHATTAN
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                value = matrix[i][j]

                if value != 0:
                    targetI, targetJ = TARGET_POSITIONS[value]
                    total_h += abs(i - targetI) + abs(j - targetJ)
                        
        return total_h
    
    def manhaton_LC(self, matrix):
        
        total_h = 0
        
        # 1. ZÁKLADNÍ MANHATTAN
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                value = matrix[i][j]

                if value != 0:
                    targetI, targetJ = TARGET_POSITIONS[value]
                    total_h += abs(i - targetI) + abs(j - targetJ)
        
        # 2. HORIZONTÁLNÍ KONFLIKT (Řádky)         
        for i in range(len(matrix)):
            v_radku = []
            for j in range(len(matrix[i])):
                
                value = matrix[i][j]
                if value != 0:
                    if i == TARGET_POSITIONS[value][0]:
                        v_radku.append((value, j))
            
            for k in range(len(v_radku)):
                for l in range(k + 1, len(v_radku)):
                    h1, j1 = v_radku[k]
                    h2, j2 = v_radku[l]
                    
                    if TARGET_POSITIONS[h1][1] > TARGET_POSITIONS[h2][1]:
                        total_h += 2
        
        # 3. VERTIKÁLNÍ KONFLIKT (Sloupce)
        for j in range(len(matrix)):
            v_sloupci = []
            for i in range(len(matrix[j])):
                value = matrix[i][j]
                if value != 0 and TARGET_POSITIONS[value][1] == j:
                    v_sloupci.append((value, i))
        
        for k in range(len(v_sloupci)):
            for l in range(k + 1, len(v_sloupci)):
                val1, curr_i1 = v_sloupci[k]
                val2, curr_i2 = v_sloupci[l]
                # val1 je nad val2 (curr_i1 < curr_i2)
                # Pokud má být val1 v cíli pod val2, je to konflikt
                if TARGET_POSITIONS[val1][0] > TARGET_POSITIONS[val2][0]:
                    total_h += 2
                        
        return total_h

    def zpateční_cesta(self, node):
        
        cesta = []
        
        while node.get_rodic() != None:
            cesta.append(node.get_pohyb())
            node = node.get_rodic()
        
        cesta.reverse()
        
        return cesta      
    
    def resitelnost(self, data):
        n = len(data)
        seznam = [c for radek in data for c in radek if c != 0]
        inverze = sum(seznam[i] > seznam[j] for i in range(len(seznam)) for j in range(i + 1, len(seznam)))
        
        if n % 2 != 0: # Pro 3x3, 5x5...
            return inverze % 2 == 0
        else: # Pro 4x4
            r0, _ = self.najdi_nulu(data)
            radek_odspodu = n - r0
            # Pravidlo: (inverze + radek_nuly_odspodu) musí mít specifickou paritu
            return (inverze + radek_odspodu) % 2 != 0
                
                
puzzle = PuzzleSolver([
    [0, 12, 9, 13],
    [15, 11, 10, 14],
    [3, 7, 2, 5],
    [4, 8, 6, 1]
])

#vysledek = puzzle.informovany_algortimus_a_star()
#vysledek = puzzle.informovany_algortimus_a_star_LC()
#vysledek = puzzle.informovany_algortimus_a_star_tiebreaking_LC()
vysledek = puzzle.informovany_algortimus_a_star_weighted()

#fungoval jenom weighted bud s LC nebo klasik manhaton. Vaha byla rovna 5.

#cesta = puzzle.zpateční_cesta(vysledek)
#print(cesta)
#print(len(cesta))