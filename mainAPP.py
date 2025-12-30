import mimetypes
import flet as ft
import asyncio
import time
import random
from Muj8PuzzleAPP import PuzzleSolver

# MIME type fix for Windows
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/javascript', '.mjs')

async def main(page: ft.Page):
    page.title = "8-Puzzle: Solver"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.window_width = 1150
    page.window_height = 900 

    # --- STATE VARIABLES ---
    CILOVY_STAV = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    stav_seznam = [8, 6, 7, 2, 5, 4, 3, 0, 1]
    stav_shuffled_start = list(stav_seznam) 
    is_animating = False 

    # --- UI COMPONENTS ---
    txt_status = ft.Text("Ready", size=18, weight=ft.FontWeight.BOLD)
    txt_kroky_cpu = ft.Text("Steps (CPU): 0", color="blue", weight="bold")
    txt_cas = ft.Text("Calc Time: 0s")
    txt_prozkoumano = ft.Text("Nodes Explored: 0")
    txt_visited = ft.Text("Visited (in memory): 0")
    
    txt_cesta_pismena = ft.Text("", color="amber", weight="bold", size=16, selectable=True)
    
    history_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    loader = ft.ProgressBar(width=400, color="blue", visible=False)
    mrizka = ft.GridView(expand=False, runs_count=3, max_extent=110, spacing=8, width=350)

    # --- TARGET GOAL VIEW ---
    def create_mini_tile(num):
        return ft.Container(
            content=ft.Text(str(num) if num != 0 else "", size=12, weight="bold"),
            alignment=ft.Alignment.CENTER,
            width=30, height=30,
            bgcolor="green900" if num != 0 else "grey900",
            border_radius=3
        )

    target_display = ft.Column([
        ft.Text("TARGET GOAL", size=14, weight="bold", color="green"),
        ft.Row([create_mini_tile(1), create_mini_tile(2), create_mini_tile(3)], spacing=5),
        ft.Row([create_mini_tile(4), create_mini_tile(5), create_mini_tile(6)], spacing=5),
        ft.Row([create_mini_tile(7), create_mini_tile(8), create_mini_tile(0)], spacing=5),
    ], horizontal_alignment="center", spacing=5)

    # --- HELPER FUNCTIONS ---
    def je_vyreseno():
        return stav_seznam == CILOVY_STAV

    def ziskej_path_string(cesta_matic):
        path_str = ""
        for i in range(len(cesta_matic) - 1):
            m1, m2 = cesta_matic[i], cesta_matic[i+1]
            r1, c1, r2, c2 = 0, 0, 0, 0
            for r in range(3):
                for c in range(3):
                    if m1[r][c] == 0: r1, c1 = r, c
                    if m2[r][c] == 0: r2, c2 = r, c
            if r2 < r1: path_str += "U"
            elif r2 > r1: path_str += "D"
            elif c2 < c1: path_str += "L"
            elif c2 > c1: path_str += "R"
        return path_str

    def vytvor_dlazdici(cislo, index):
        vyreseno = je_vyreseno()
        barva = "green700" if vyreseno and cislo != 0 else ("blue700" if cislo != 0 else "grey800")
        return ft.Container(
            content=ft.Text(str(cislo) if cislo != 0 else "", size=25, weight="bold"),
            alignment=ft.Alignment.CENTER,
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
            txt_status.value = "GOAL REACHED!"
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
        txt_status.value = "Animation stopped"
        page.update()

    async def reset_na_start(e):
        nonlocal stav_seznam
        stav_seznam = list(stav_shuffled_start)
        txt_status.value = "Reset to starting configuration"
        txt_status.color = "white"
        txt_cesta_pismena.value = "" 
        vykresli_ui()

    async def spust_vypocet(e):
        nonlocal stav_seznam, is_animating
        if je_vyreseno(): return
        pocatecni_stav_pro_historii = str(list(stav_seznam))
        mapovani_funkci = {
            "BFS": "solve_puzzle_bfs", "DFS": "solve_puzzle_dfs",
            "DFS Limit": "solve_puzzle_dfs_limit", "A*": "informovany_algortimus_a_star",
            "A* LC": "informovany_algortimus_a_star_LC",
            "A* Weighted": "informovany_algortimus_a_star_weighted",
            "Greedy": "informovany_algortimus_greedy"
        }
        matice_start = [stav_seznam[i:i+3] for i in range(0, 9, 3)]
        solver = PuzzleSolver(matice_start)
        if not solver.resitelnost(matice_start):
            txt_status.value, txt_status.color = "UNSOLVABLE!", "red"
            page.update()
            return
        set_ui_busy(True)
        txt_status.value, txt_status.color = "CPU is calculating...", "blue"
        txt_cesta_pismena.value = ""
        await asyncio.sleep(0.1)
        start_t = time.time()
        algo_name = mapovani_funkci.get(dropdown_algo.value)
        uzol = await asyncio.to_thread(getattr(solver, algo_name))
        trvani = time.time() - start_t
        if uzol:
            cesta_matic = solver.zpateční_cesta(uzol)
            tahy_pocet = len(cesta_matic) - 1
            pismena_cesty = ziskej_path_string(cesta_matic)
            txt_cesta_pismena.value = f"Path ({tahy_pocet}): {pismena_cesty}"
            txt_status.value, txt_status.color = "Solved! Animating...", "green"
            txt_cas.value = f"Calc Time: {trvani:.4f} s"
            txt_kroky_cpu.value = f"Steps (CPU): {tahy_pocet}"
            txt_prozkoumano.value = f"Explored: {solver.prozkoumano}"
            txt_visited.value = f"Visited: {solver.navstiveno}"
            
            history_item = ft.Container(
                content=ft.Column([
                    ft.Text(f"{dropdown_algo.value}", weight="bold", color="blue200", size=14),
                    ft.Text(f"Start: {pocatecni_stav_pro_historii}", size=9, color="grey400", font_family="monospace"),
                    ft.Text(f"Path: {pismena_cesty}", size=9, color="amber", italic=True),
                    ft.Row([ft.Text(f"Steps: {tahy_pocet}", size=11), ft.Text(f"Time: {trvani:.3f}s", size=11)], spacing=15),
                    ft.Text(f"E/V: {solver.prozkoumano} / {solver.navstiveno}", size=11, color="grey500"),
                ], spacing=2),
                padding=10, border=ft.border.all(1, "grey700"), border_radius=8, bgcolor=ft.Colors.with_opacity(0.1, "white")
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
            txt_status.value, txt_status.color = "Path not found.", "orange"
            set_ui_busy(False)

    def zamichej(e):
        nonlocal stav_seznam, stav_shuffled_start
        temp_solver = PuzzleSolver([[0]*3]*3)
        while True:
            random.shuffle(stav_seznam)
            if temp_solver.resitelnost([stav_seznam[i:i+3] for i in range(0, 9, 3)]) and not je_vyreseno():
                break
        stav_shuffled_start = list(stav_seznam)
        txt_kroky_cpu.value = "Steps (CPU): 0"
        txt_status.value = "New puzzle generated"
        txt_status.color = "white"
        txt_cesta_pismena.value = ""
        vykresli_ui()

    dropdown_algo = ft.Dropdown(
        label="Algorithm", value="A* Weighted", width=200,
        options=[ft.dropdown.Option(k) for k in ["BFS", "DFS", "DFS Limit", "A*", "A* LC", "A* Weighted", "Greedy"]],
    )

    btn_vyresit = ft.FilledButton("SOLVE", on_click=spust_vypocet, icon=ft.Icons.AUTO_FIX_HIGH, bgcolor=ft.Colors.BLUE_700)
    btn_zamichat = ft.FilledButton("SHUFFLE", on_click=zamichej, icon=ft.Icons.SHUFFLE, bgcolor=ft.Colors.AMBER_800)
    btn_reset = ft.OutlinedButton("RESET TO START", on_click=reset_na_start, icon=ft.Icons.RESTART_ALT)
    btn_stop = ft.FilledTonalButton("STOP", on_click=stop_animace, icon=ft.Icons.STOP, visible=False, bgcolor=ft.Colors.RED_700)

    page.add(
        ft.Column([
            ft.Text("8-Puzzle: Solver", size=32, weight="bold"),
            loader,
            ft.Row([dropdown_algo, btn_vyresit, btn_reset, btn_zamichat, btn_stop], alignment="center"),
            ft.Divider(),
            ft.Row([
                ft.Column([
                    ft.Container(target_display, padding=5),
                ], horizontal_alignment="center"),
                ft.Column([
                    ft.Container(mrizka, padding=10, border=ft.Border.all(1, "grey300"), border_radius=10),
                ], horizontal_alignment="center"),
                ft.Column([
                    ft.Text("CURRENT RESULT", weight="bold", color="blue"),
                    txt_status, ft.Divider(height=10),
                    txt_kroky_cpu, txt_cas,
                    ft.Text("Directions (Empty tile):", size=12, color="grey"),
                    txt_cesta_pismena, ft.Divider(height=10),
                    txt_prozkoumano, txt_visited,
                ], width=250),
                ft.VerticalDivider(width=20),
                ft.Column([
                    ft.Text("HISTORY", weight="bold", color="orange"),
                    ft.Container(content=history_column, width=300, height=500, padding=10)
                ])
            ], alignment="center", vertical_alignment="start")
        ], horizontal_alignment="center")
    )
    vykresli_ui()

if __name__ == "__main__":
    ft.app(target=main)