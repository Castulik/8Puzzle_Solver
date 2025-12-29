# at to ukazuje v UI cestu, ktera se solverem provadi.
# 
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
    page.title = "8-Puzzle: Solver MZI"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 30

    # --- STAVOVÉ PROMĚNNÉ ---
    CILOVY_STAV = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    stav_seznam = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    stav_shuffled_start = list(stav_seznam) 
    is_animating = False 
    pocet_tahu_manual = 0 

    # --- UI KOMPONENTY ---
    txt_status = ft.Text("Připraven", size=18, weight=ft.FontWeight.BOLD)
    txt_manual_tahy = ft.Text("Tvoje tahy: 0", color="amber", weight="bold", size=16)
    txt_kroky_cpu = ft.Text("Kroky (CPU): 0", color="blue")
    txt_cas = ft.Text("Čas výpočtu: 0s")
    txt_prozkoumano = ft.Text("Prozkoumáno uzlů: 0")
    txt_visited = ft.Text("Navštíveno (v paměti): 0")
    
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
        btn_stop.visible = busy # STOP je vidět jen při animaci/výpočtu
        loader.visible = busy
        page.update()

    # --- LOGIKA ---
    def klik_na_dlazdici(idx_klik):
        nonlocal stav_seznam, pocet_tahu_manual
        if is_animating or btn_vyresit.disabled: return
        idx_nula = stav_seznam.index(0)
        r_k, c_k = divmod(idx_klik, 3)
        r_n, c_n = divmod(idx_nula, 3)
        if abs(r_k - r_n) + abs(c_k - c_n) == 1:
            stav_seznam[idx_klik], stav_seznam[idx_nula] = stav_seznam[idx_nula], stav_seznam[idx_klik]
            pocet_tahu_manual += 1
            txt_manual_tahy.value = f"Tvoje tahy: {pocet_tahu_manual}"
            vykresli_ui()

    async def stop_animace(e):
        nonlocal is_animating
        is_animating = False
        txt_status.value = "Animace zastavena"
        page.update()

    async def reset_na_start(e):
        nonlocal stav_seznam, pocet_tahu_manual
        stav_seznam = list(stav_shuffled_start)
        pocet_tahu_manual = 0
        txt_manual_tahy.value = "Tvoje tahy: 0"
        txt_status.value = "Zpět na začátku zadání"
        txt_status.color = "white"
        vykresli_ui()

    async def spust_vypocet(e):
        nonlocal stav_seznam, is_animating
        if je_vyreseno(): return

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
        algo_name = f"solve_puzzle_{dropdown_algo.value.lower().replace(' ', '_')}"
        uzol = await asyncio.to_thread(getattr(solver, algo_name))
        trvani = time.time() - start_t

        if uzol:
            cesta_matic = solver.zpateční_cesta(uzol)
            txt_status.value, txt_status.color = "Nalezeno! Animuji...", "green"
            txt_cas.value = f"Čas výpočtu: {trvani:.4f} s"
            txt_kroky_cpu.value = f"Kroky (CPU): {len(cesta_matic) - 1}"
            txt_prozkoumano.value = f"Prozkoumáno: {solver.prozkoumano}"
            txt_visited.value = f"Navštíveno: {solver.navstiveno}"
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
        nonlocal stav_seznam, stav_shuffled_start, pocet_tahu_manual
        temp_solver = PuzzleSolver([[0]*3]*3)
        while True:
            random.shuffle(stav_seznam)
            if temp_solver.resitelnost([stav_seznam[i:i+3] for i in range(0, 9, 3)]) and not je_vyreseno():
                break
        stav_shuffled_start = list(stav_seznam)
        pocet_tahu_manual = 0
        txt_kroky_cpu.value = "Kroky (CPU): 0"
        txt_manual_tahy.value = "Tvoje tahy: 0"
        txt_status.value = "Nové zadání"
        txt_status.color = "white"
        vykresli_ui()

    # --- KOMPONENTY ---
    dropdown_algo = ft.Dropdown(
        label="Algoritmus", value="BFS", width=140,
        options=[ft.dropdown.Option("BFS"), ft.dropdown.Option("DFS"), ft.dropdown.Option("DFS Limit")],
    )
    btn_vyresit = ft.FilledButton("VYŘEŠIT", on_click=spust_vypocet, icon=ft.Icons.AUTO_FIX_HIGH)
    btn_zamichat = ft.FilledButton("NOVÉ ZADÁNÍ", on_click=zamichej, icon=ft.Icons.SHUFFLE, bgcolor="bluegrey-700")
    btn_reset = ft.OutlinedButton("ZPĚT NA START", on_click=reset_na_start, icon=ft.Icons.RESTART_ALT)
    btn_stop = ft.FilledTonalButton("STOP", on_click=stop_animace, icon=ft.Icons.STOP, visible=False, color="red")

    page.add(
        ft.Column([
            ft.Text("8-Puzzle: MZI Solver", size=32, weight="bold"),
            loader,
            ft.Row([dropdown_algo, btn_vyresit, btn_zamichat, btn_reset, btn_stop], alignment="center"),
            ft.Divider(),
            ft.Row([
                ft.Container(mrizka, padding=10, border=ft.Border.all(1, "grey300"), border_radius=10),
                ft.Column([
                    txt_status,
                    ft.Divider(height=10, color="transparent"),
                    txt_manual_tahy,
                    txt_kroky_cpu,
                    ft.Divider(height=10),
                    txt_cas,
                    txt_prozkoumano,
                    txt_visited,
                    ft.Text("\nCíl:", weight="bold"),
                    ft.Text("1 2 3\n4 5 6\n7 8 0", font_family="monospace", size=14)
                ], width=250)
            ], alignment="center", vertical_alignment="start")
        ], horizontal_alignment="center")
    )
    vykresli_ui()

if __name__ == "__main__":
    ft.app(target=main)