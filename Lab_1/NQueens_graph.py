"""
N Queens – PILNA būsenų erdvės schema (BFS medis iki MAX_DEPTH).
Rodomos VISOS pasiekiamos būsenos ir VISI galimi perėjimai,
įskaitant „blogas" šakas (aklavietes), kurios neveda prie sprendimo.

Kintamieji būsenų aprašymui:
  state = (q₀, q₁, ..., qₙ₋₁)  — N elementų kortežas
    - qᵢ ∈ {0, 1, ..., N-1} — karalienės eilutė i-ajame stulpelyje
    - qᵢ = -1 — stulpelis dar neužpildytas
    - Stulpeliai pildomi iš kairės į dešinę
  Veiksmas: skaičius r (eilutė), kurioje statoma karalienė
    kitame laisvame stulpelyje, jei nekonfliktuoja
  Apribojimai: jokios dvi karalienės negali būti toje pačioje
    eilutėje, stulpelyje ar įstrižainėje

N = 4 pavyzdys:
  Pradinė būsena:  (-1, -1, -1, -1)  — tuščia lenta
  Galutinės būsenos: (1, 3, 0, 2) ir (2, 0, 3, 1)
"""

import os
import subprocess
from collections import deque
from search import NQueensProblem, best_first_graph_search

N_QUEENS = 4
MAX_DEPTH = 4   # Keiskite šią reikšmę, kad matytumėte daugiau/mažiau gylių


def make_html_label(name, state, n):
    """Graphviz HTML etiketė su NxN šachmatų lenta."""
    rows = []
    rows.append(f'<TR><TD COLSPAN="{n}"><B>{name}</B></TD></TR>')
    # Būsenos kortežas po lentos paveiksliuku
    state_str = "(" + ", ".join(str(x) for x in state) + ")"
    for r in range(n):
        cells = []
        for c in range(n):
            is_dark = (r + c) % 2 == 1
            bg = "#D2B48C" if is_dark else "#FFF8DC"
            if c < len(state) and state[c] == r:
                cells.append(f'<TD BGCOLOR="{bg}" WIDTH="28" HEIGHT="28">'
                             f'<FONT COLOR="#CC0000" POINT-SIZE="16"><B>♛</B></FONT></TD>')
            elif state[c] == -1 and c == state.index(-1) if -1 in state else False:
                cells.append(f'<TD BGCOLOR="{bg}" WIDTH="28" HEIGHT="28"> </TD>')
            else:
                cells.append(f'<TD BGCOLOR="{bg}" WIDTH="28" HEIGHT="28"> </TD>')
        rows.append("<TR>" + "".join(cells) + "</TR>")
    rows.append(f'<TR><TD COLSPAN="{n}"><FONT POINT-SIZE="8">{state_str}</FONT></TD></TR>')
    return "<<TABLE BORDER=\"1\" CELLBORDER=\"0\" CELLSPACING=\"0\" CELLPADDING=\"2\">" + \
           "".join(rows) + "</TABLE>>"


def main():
    problem = NQueensProblem(N_QUEENS)

    # Rasti sprendimo kelią (Best-First)
    result_node = best_first_graph_search(problem, lambda n: problem.h(n))
    sol_path = result_node.path()
    solution_states = {node.state for node in sol_path}
    solution_edges = set()
    for i in range(len(sol_path) - 1):
        solution_edges.add((sol_path[i].state, sol_path[i + 1].state))

    # Surasti VISAS galutines būsenas (gali būti keli sprendimai)
    goal_states = set()

    # BFS – surinkti VISAS būsenas iki MAX_DEPTH
    state_name = {}
    state_depth = {}
    edges = []
    counter = [0]

    def get_name(state):
        if state not in state_name:
            state_name[state] = f"N{counter[0]}"
            counter[0] += 1
        return state_name[state]

    get_name(problem.initial)
    state_depth[problem.initial] = 0
    frontier = deque([(problem.initial, 0)])
    visited = {problem.initial}

    while frontier:
        s, d = frontier.popleft()
        actions = problem.actions(s)
        for a in actions:
            ns = problem.result(s, a)
            edges.append((s, ns, a))
            if ns not in visited:
                visited.add(ns)
                get_name(ns)
                state_depth[ns] = d + 1
                if problem.goal_test(ns):
                    goal_states.add(ns)
                if d + 1 < MAX_DEPTH:
                    frontier.append((ns, d + 1))

    # Identifikuoti aklavietes (būsenos be vaikų, kurios nėra tikslai)
    states_with_children = {src for src, _, _ in edges}
    dead_ends = {s for s in state_name if s not in states_with_children
                 and s not in goal_states and s != problem.initial}

    # DOT generavimas
    lines = [
        "digraph NQueens {",
        "    rankdir=TB;",
        f'    graph [fontname="Arial", fontsize=14, label=<'
        f'<B>N Queens (N={N_QUEENS}) – Pilna būsenų erdvės schema '
        f'(BFS, gylis ≤ {MAX_DEPTH})</B><BR/>'
        f'Kintamieji: state = (q<SUB>0</SUB>…q<SUB>{N_QUEENS-1}</SUB>), '
        f'q<SUB>i</SUB> ∈ {{-1, 0…{N_QUEENS-1}}}, -1 = neužpildytas<BR/>'
        f'Veiksmas: eilutės numeris r, kurioje statoma karalienė<BR/>'
        f'Pradinė: {problem.initial}  |  '
        f'Galutinės: {", ".join(str(g) for g in sorted(goal_states))}<BR/>'
        f'Būsenų: {len(state_name)} | Briaunų: {len(edges)}'
        '>, labelloc=t, nodesep=0.4, ranksep=1.0];',
        '    node [fontname="Courier", fontsize=9, style=filled];',
        '    edge [fontname="Arial", fontsize=9];',
        "",
    ]

    # Grupuoti pagal gylį (rank)
    by_depth = {}
    for s, d in state_depth.items():
        by_depth.setdefault(d, []).append(s)

    for d in sorted(by_depth):
        rank_nodes = " ".join(state_name[s] for s in by_depth[d])
        lines.append(f"    {{ rank=same; {rank_nodes} }}")

    lines.append("")

    # Mazgai
    for s, name in state_name.items():
        label = make_html_label(name, s, N_QUEENS)
        is_initial = (s == problem.initial)
        is_goal = s in goal_states
        on_path = s in solution_states
        is_dead = s in dead_ends

        if is_initial:
            attrs = 'fillcolor="#FFFACD" penwidth=3 color="#DAA520"'
        elif is_goal and on_path:
            attrs = 'fillcolor="#90EE90" penwidth=3 color="#006400"'
        elif is_goal:
            attrs = 'fillcolor="#B0FFB0" penwidth=2 color="#228B22"'
        elif on_path:
            attrs = 'fillcolor="#ADD8E6" penwidth=2 color="#4682B4"'
        elif is_dead:
            attrs = 'fillcolor="#FFCCCC" penwidth=2 color="#CC0000" style="filled,bold"'
        else:
            attrs = 'fillcolor="#FFE4E1" penwidth=1 color="#CD5C5C"'
        lines.append(f"    {name} [{attrs} label={label}];")

    lines.append("")

    # Briaunos
    seen = set()
    for src_s, dst_s, act in edges:
        src_n = state_name[src_s]
        dst_n = state_name.get(dst_s)
        if dst_n is None:
            continue
        key = (src_n, dst_n, act)
        if key in seen:
            continue
        seen.add(key)

        is_sol = (src_s, dst_s) in solution_edges
        col = src_s.index(-1) if -1 in src_s else "?"
        edge_label = f"stulp.{col}←eil.{act}"

        if is_sol:
            lines.append(
                f'    {src_n} -> {dst_n} [label="  {edge_label}  " '
                f'color="#006400" penwidth=2.5 fontcolor="#006400"];'
            )
        else:
            lines.append(
                f'    {src_n} -> {dst_n} [label="  {edge_label}  " '
                f'color="#999999" penwidth=0.8 fontcolor="#777777" style=dashed];'
            )

    lines.append("")

    # Legenda
    lines.append("    subgraph cluster_legend {")
    lines.append('        label="Legenda"; fontname="Arial"; fontsize=11;')
    lines.append("        style=rounded; color=gray70; bgcolor=white;")
    lines.append('        L1 [label="Pradinė (tuščia lenta)" fillcolor="#FFFACD" '
                 'penwidth=2 color="#DAA520" shape=box];')
    lines.append('        L2 [label="Galutinė (sprendimas)" fillcolor="#90EE90" '
                 'penwidth=2 color="#006400" shape=box];')
    lines.append('        L3 [label="Sprendimo kelyje" '
                 'fillcolor="#ADD8E6" color="#4682B4" shape=box];')
    lines.append('        L4 [label="Kita šaka" '
                 'fillcolor="#FFE4E1" color="#CD5C5C" shape=box];')
    lines.append('        L5 [label="Aklavietė (nėra galimų veiksmų)" '
                 'fillcolor="#FFCCCC" penwidth=2 color="#CC0000" shape=box '
                 'style="filled,bold"];')
    lines.append('        L6 [label="━━ Sprendimo kelias" shape=plaintext '
                 'fillcolor=white fontcolor="#006400"];')
    lines.append('        L7 [label="╌╌ Kita šaka" shape=plaintext '
                 'fillcolor=white fontcolor="#999999"];')
    lines.append("        L1 -> L2 -> L3 -> L4 -> L5 -> L6 -> L7 [style=invis];")
    lines.append("    }")

    lines.append("}")

    dot_content = "\n".join(lines)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dot_file = os.path.join(script_dir, "NQueens_states.dot")
    png_file = os.path.join(script_dir, "NQueens_states.png")

    with open(dot_file, "w") as f:
        f.write(dot_content)

    subprocess.run(
        ["dot", "-Tpng", "-Gdpi=150", dot_file, "-o", png_file], check=True
    )

    print(f"Schema sugeneruota: {png_file}")
    print(f"N = {N_QUEENS}")
    print(f"MAX_DEPTH = {MAX_DEPTH}")
    print(f"Būsenų: {len(state_name)}")
    print(f"Briaunų: {len(seen)}")
    for d in sorted(by_depth):
        print(f"  Gylis {d}: {len(by_depth[d])} būsenos")
    print(f"Sprendimo kelyje: {len(solution_states & set(state_name.keys()))} būsenos")
    print(f"Galutinės (tikslai): {len(goal_states)} — {sorted(goal_states)}")
    print(f"Aklavietės: {len(dead_ends)}")


if __name__ == "__main__":
    main()
