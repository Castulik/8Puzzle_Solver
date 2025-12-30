import mimetypes
import flet as ft
import asyncio
import time
import random
from Muj8Puzzle import PuzzleSolver

# Fix pro MIME typy na Windows
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/javascript', '.mjs')

async def main(page: ft.Page):
    page.title = "8-Puzzle: Solver"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    # Rozšíříme okno, aby se vešla i historie
    page.window_width = 1100
    page.window_height = 800

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
    
    # Historie - ListView pro záznamy
    history_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    
    loader = ft.ProgressBar(width=400, color="blue", visible=False)
    mrizka = ft.GridView(expand=False, runs_count=3, max_extent=110, spacing=8, width=350)

    # --- POMOCNÉ FUNKCE ---
    def je_vyreseno():
        return stav_seznam == CILOVY_STAV

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
        vykresli_ui()

    async def spust_vypocet(e):
        nonlocal stav_seznam, is_animating
        if je_vyreseno(): return
        
        # Zapamatujeme si startovní stav pro historii (ve formátu řetězce)
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
        await asyncio.sleep(0.1)

        start_t = time.time()
        vybrany_text = dropdown_algo.value
        algo_name = mapovani_funkci.get(vybrany_text)

        if not algo_name:
            txt_status.value = "CHYBA: Algoritmus nenalezen!"
            set_ui_busy(False)
            return

        uzol = await asyncio.to_thread(getattr(solver, algo_name))
        trvani = time.time() - start_t

        if uzol:
            cesta_matic = solver.zpateční_cesta(uzol)
            tahy_pocet = len(cesta_matic) - 1
            
            # Aktualizace aktuálních hodnot
            txt_status.value, txt_status.color = "Nalezeno! Animuji...", "green"
            txt_cas.value = f"Čas výpočtu: {trvani:.4f} s"
            txt_kroky_cpu.value = f"Kroky (CPU): {tahy_pocet}"
            txt_prozkoumano.value = f"Prozkoumáno: {solver.prozkoumano}"
            txt_visited.value = f"Navštíveno: {solver.navstiveno}"
            
            # --- PŘIDÁNÍ DO HISTORIE ---
            history_item = ft.Container(
                content=ft.Column([
                    ft.Text(f"{vybrany_text}", weight="bold", color="blue200", size=14),
                    ft.Text(f"Start: {pocatecni_stav_pro_historii}", size=10, color="grey400", font_family="monospace"),
                    ft.Row([
                        ft.Text(f"Tahy: {tahy_pocet}", size=11),
                        ft.Text(f"Čas: {trvani:.3f}s", size=11),
                    ], spacing=15),
                    ft.Text(f"P/V: {solver.prozkoumano} / {solver.navstiveno}", size=11, color="grey500"),
                ], spacing=2),
                padding=10,
                border=ft.border.all(1, "grey700"),
                border_radius=8,
                bgcolor=ft.Colors.with_opacity(0.1, "white")
            )
            
            # Vložit na začátek (nejnovější nahoře)
            history_column.controls.insert(0, history_item)
            # Udržovat max 8 záznamů
            if len(history_column.controls) > 8:
                history_column.controls.pop()
            
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
        vykresli_ui()

    # --- KOMPONENTY ---
    dropdown_algo = ft.Dropdown(
        label="Algoritmus", 
        value="A* Weighted",
        width=200,
        options=[
            ft.dropdown.Option("BFS"),
            ft.dropdown.Option("DFS"),
            ft.dropdown.Option("DFS Limit"),
            ft.dropdown.Option("A*"),
            ft.dropdown.Option("A* LC"),
            ft.dropdown.Option("A* Weighted"),
            ft.dropdown.Option("Greedy"),
        ],
    )
    # --- KOMPONENTY S UPRAVENÝMI BARVAMI ---

    # Tlačítko VYŘEŠIT - modrá (akční barva)
    btn_vyresit = ft.FilledButton(
        "VYŘEŠIT", 
        on_click=spust_vypocet, 
        icon=ft.Icons.AUTO_FIX_HIGH,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE
    )

    # Tlačítko ZAMÍCHAT - jantarová/oranžová (příprava)
    btn_zamichat = ft.FilledButton(
        "ZAMÍCHAT", 
        on_click=zamichej, 
        icon=ft.Icons.SHUFFLE, 
        bgcolor=ft.Colors.AMBER_800,
        color=ft.Colors.WHITE
    )

    # Tlačítko ZPĚT NA START - šedá nebo tmavě modrá (neutrální)
    # U OutlinedButton mění parametr 'color' barvu textu i čáry
    btn_reset = ft.OutlinedButton(
        "ZPĚT NA START", 
        on_click=reset_na_start, 
        icon=ft.Icons.RESTART_ALT,
        style=ft.ButtonStyle(color=ft.Colors.BLUE_GREY_200)
    )

    # Tlačítko STOP - výrazná červená
    btn_stop = ft.FilledTonalButton(
        "STOP", 
        on_click=stop_animace, 
        icon=ft.Icons.STOP, 
        visible=False, 
        bgcolor=ft.Colors.RED_700,
        color=ft.Colors.WHITE
    )

    # Hlavní rozložení: Levý panel (Board) | Střední (Stats) | Pravý (History)
    page.add(
        ft.Column([
            ft.Text("8-Puzzle: Solver", size=32, weight="bold"),
            loader,
            ft.Row([dropdown_algo, btn_vyresit, btn_reset, btn_zamichat,  btn_stop], alignment="center"),
            ft.Divider(),
            ft.Row([
                # 1. Hrací pole
                ft.Container(mrizka, padding=10, border=ft.Border.all(1, "grey300"), border_radius=10),
                
                # 2. Aktuální statistiky
                ft.Column([
                    ft.Text("AKTUÁLNÍ VÝSLEDEK", weight="bold", color="blue"),
                    txt_status,
                    ft.Divider(height=10),
                    txt_kroky_cpu,
                    txt_cas,
                    txt_prozkoumano,
                    txt_visited,
                    ft.Text("\nCíl:", weight="bold"),
                    ft.Text("1 2 3\n4 5 6\n7 8 0", font_family="monospace", size=14)
                ], width=200),
                
                # 3. Historie
                ft.VerticalDivider(width=20),
                ft.Column([
                    ft.Text("HISTORIE (POSLEDNÍCH 8)", weight="bold", color="orange"),
                    ft.Container(
                        content=history_column,
                        width=300,
                        height=450,
                        bgcolor=ft.Colors.with_opacity(0.05, "white"),
                        border_radius=10,
                        padding=10
                    )
                ])

            ], alignment="center", vertical_alignment="start")
        ], horizontal_alignment="center")
    )
    vykresli_ui()

if __name__ == "__main__":
    ft.app(target=main)