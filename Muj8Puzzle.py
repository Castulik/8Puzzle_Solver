import queue1
import copy
import time
import stack1

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
        self.prozkoumano = 0
        self.navstiveno = 0
    
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
        self.prozkoumano = 0 
        fifo = queue1.Queue()
        fifo.push(self.root)
        
        visited = set()
        visited.add(tuple(map(tuple, self.root.data)))
        
        while not fifo.is_empty():
            node = fifo.pop()
            self.prozkoumano += 1 #beru z fifo
            
            if self.srovnani_matic(node.data):
                self.navstiveno = len(visited)
                return node
            
            r0, s0 = self.najdi_nulu(node.data)
            
            for r, s, smer in self.pripustne_pohyby(r0, s0):
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
        return None
                    
    def solve_puzzle_dfs(self):
        self.prozkoumano = 0
        
        stack = stack1.Stack()
        stack.push(self.root)
        
        visited = set()
        visited.add(tuple(map(tuple, self.root.data)))
        
        while not stack.is_empty(): # Dokud není zásobník prázdný
            node = stack.pop() #bere POSLEDNÍ přidaný prvek
            self.prozkoumano += 1
            
            if self.srovnani_matic(node.data):
                self.navstiveno = len(visited)
                return node
            
            r0, s0 = self.najdi_nulu(node.data)
            
            for r, s, smer in self.pripustne_pohyby(r0, s0):
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
        return None
    
    def solve_puzzle_dfs_limit(self):
        self.prozkoumano = 0
        
        stack = stack1.Stack()
        stack.push(self.root)
        
        visited = {tuple(map(tuple, self.root.data)): 0} # Změna na slovník: stav -> hloubka
        
        while not stack.is_empty(): # Dokud není zásobník prázdný
            node = stack.pop() #bere POSLEDNÍ přidaný prvek
            self.prozkoumano += 1
            
            if self.srovnani_matic(node.data):
                self.navstiveno = len(visited)
                return node
            
            if node.uroven >= 31:
                continue
            
            r0, s0 = self.najdi_nulu(node.data)
            
            for r, s, smer in self.pripustne_pohyby(r0, s0):
                #vytvoreni kopie
                novy_stav = copy.deepcopy(node.data)
                
                cislo = novy_stav[r][s]
                novy_stav[r0][s0] = cislo
                novy_stav[r][s] = 0
                
                stav_jako_tuple = tuple(map(tuple, novy_stav))
                nova_hloubka = node.uroven + 1
                
                #Navštívíme stav jen pokud jsme v menší nebo stejné hloubce než minule
                if stav_jako_tuple not in visited or nova_hloubka < visited[stav_jako_tuple]:
                    visited[stav_jako_tuple] = nova_hloubka
                    
                    novy_uzel = Node(novy_stav)
                    novy_uzel.set_pohyb(smer)
                    novy_uzel.set_rodic(node)
                    novy_uzel.uroven = nova_hloubka 
                    
                    stack.push(novy_uzel)
        return None
    
    def zpateční_cesta(self, node):
        
        cesta = []
        aktualni = node
        while aktualni != None:
            cesta.append(aktualni.get_data())
            aktualni = aktualni.get_rodic()
        
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