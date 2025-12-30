import mimetypes
import flet as ft
import asyncio
import time
import random
from Muj8PuzzleWEB import PuzzleSolver

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