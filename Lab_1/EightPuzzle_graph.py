"""
Eight Puzzle – PILNA būsenų erdvės schema (BFS medis iki gylio 4).
Rodomos VISOS pasiekiamos būsenos ir VISI galimi perėjimai,
įskaitant „blogas" šakas, kurios neveda prie sprendimo.

Kintamieji būsenų aprašymui:
  state = (t0, t1, t2, t3, t4, t5, t6, t7, t8)
    - kiekvienas ti ∈ {0, 1, 2, 3, 4, 5, 6, 7, 8}
    - 0 žymi tuščią langelį
    - indeksai atitinka pozicijas 3×3 lentoje:
        0 | 1 | 2
        3 | 4 | 5
        6 | 7 | 8
  Galimi veiksmai: UP, DOWN, LEFT, RIGHT

Pradinė būsena:  (2, 4, 3, 1, 5, 6, 7, 8, 0)
Galutinė būsena: (1, 2, 3, 4, 5, 6, 7, 8, 0)
"""

import os
import subprocess
from collections import deque
from search import EightPuzzle

MAX_DEPTH = 5


def make_html_label(name, state):
    s = [f"<B>{x}</B>" if x != 0 else " " for x in state]
    return (
        f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="5">'
        f'<TR><TD COLSPAN="3"><B>{name}</B></TD></TR>'
        f'<TR><TD>{s[0]}</TD><TD>{s[1]}</TD><TD>{s[2]}</TD></TR>'
        f'<TR><TD>{s[3]}</TD><TD>{s[4]}</TD><TD>{s[5]}</TD></TR>'
        f'<TR><TD>{s[6]}</TD><TD>{s[7]}</TD><TD>{s[8]}</TD></TR>'
        f'</TABLE>>'
    )


def main():
    puzzle = EightPuzzle((2, 4, 3, 1, 5, 6, 7, 8, 0))

    # Rasti sprendimo kelią
    solution_actions = ["UP", "LEFT", "UP", "LEFT", "DOWN", "RIGHT", "RIGHT", "DOWN"]
    st = puzzle.initial
    solution_states = {st}
    solution_edges = set()
    for a in solution_actions:
        ns = puzzle.result(st, a)
        solution_edges.add((st, ns))
        solution_states.add(ns)
        st = ns

    # BFS – surinkti VISAS būsenas iki MAX_DEPTH
    state_name = {}   # state -> name
    state_depth = {}  # state -> depth
    edges = []        # (src_state, dst_state, action)
    counter = [0]

    def get_name(state):
        if state not in state_name:
            state_name[state] = f"N{counter[0]}"
            counter[0] += 1
        return state_name[state]

    get_name(puzzle.initial)
    state_depth[puzzle.initial] = 0
    frontier = deque([(puzzle.initial, 0)])
    visited = {puzzle.initial}

    while frontier:
        s, d = frontier.popleft()
        for a in puzzle.actions(s):
            ns = puzzle.result(s, a)
            edges.append((s, ns, a))
            if ns not in visited:
                visited.add(ns)
                get_name(ns)
                state_depth[ns] = d + 1
                if d + 1 < MAX_DEPTH:
                    frontier.append((ns, d + 1))

    # DOT
    lines = [
        "digraph EightPuzzle {",
        '    rankdir=TB;',
        '    graph [fontname="Arial", fontsize=14, label=<'
        '<B>Eight Puzzle – Pilna būsenų erdvės schema (BFS, gylis ≤ '
        f'{MAX_DEPTH})</B><BR/>'
        'Kintamieji: state = (t<SUB>0</SUB>…t<SUB>8</SUB>), '
        't<SUB>i</SUB> ∈ {{0…8}}, 0 = tuščias<BR/>'
        'Veiksmai: UP, DOWN, LEFT, RIGHT<BR/>'
        f'Pradinė: {tuple(puzzle.initial)}  |  '
        f'Galutinė: {puzzle.goal}<BR/>'
        f'Būsenų: {len(state_name)} | Briaunų: {len(edges)}'
        '>, labelloc=t, nodesep=0.3, ranksep=0.8];',
        '    node [fontname="Courier", fontsize=9, style=filled];',
        '    edge [fontname="Arial", fontsize=8];',
        '',
    ]

    # Grupuoti pagal gylį
    by_depth = {}
    for s, d in state_depth.items():
        by_depth.setdefault(d, []).append(s)

    for d in sorted(by_depth):
        rank_nodes = " ".join(state_name[s] for s in by_depth[d])
        lines.append(f"    {{ rank=same; {rank_nodes} }}")

    lines.append("")

    # Mazgai
    for s, name in state_name.items():
        label = make_html_label(name, s)
        is_initial = (s == puzzle.initial)
        is_goal = (s == puzzle.goal)
        on_path = (s in solution_states)

        if is_initial:
            attrs = 'fillcolor="#FFFACD" penwidth=3 color="#DAA520"'
        elif is_goal:
            attrs = 'fillcolor="#90EE90" penwidth=3 color="#006400"'
        elif on_path:
            attrs = 'fillcolor="#ADD8E6" penwidth=2 color="#4682B4"'
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

        if is_sol:
            lines.append(
                f'    {src_n} -> {dst_n} [label="  {act}  " '
                f'color="#006400" penwidth=2.5 fontcolor="#006400"];'
            )
        elif dst_s in solution_states and src_s in solution_states:
            lines.append(
                f'    {src_n} -> {dst_n} [label="  {act}  " '
                f'color="#4682B4" penwidth=1.2 fontcolor="#4682B4" style=dashed];'
            )
        else:
            lines.append(
                f'    {src_n} -> {dst_n} [label="  {act}  " '
                f'color="#999999" penwidth=0.8 fontcolor="#777777" style=dashed];'
            )

    lines.append("")

    # Legenda
    lines.append("    subgraph cluster_legend {")
    lines.append('        label="Legenda"; fontname="Arial"; fontsize=11;')
    lines.append("        style=rounded; color=gray70; bgcolor=white;")
    lines.append('        L1 [label="Pradinė būsena" fillcolor="#FFFACD" '
                 'penwidth=2 color="#DAA520" shape=box];')
    lines.append('        L2 [label="Galutinė būsena" fillcolor="#90EE90" '
                 'penwidth=2 color="#006400" shape=box];')
    lines.append('        L3 [label="Sprendimo kelyje" '
                 'fillcolor="#ADD8E6" color="#4682B4" shape=box];')
    lines.append('        L4 [label="Blogoji šaka" '
                 'fillcolor="#FFE4E1" color="#CD5C5C" shape=box];')
    lines.append('        L5 [label="━━ Sprendimo kelias" shape=plaintext '
                 'fillcolor=white fontcolor="#006400"];')
    lines.append('        L6 [label="╌╌ Kita šaka" shape=plaintext '
                 'fillcolor=white fontcolor="#999999"];')
    lines.append("        L1 -> L2 -> L3 -> L4 -> L5 -> L6 [style=invis];")
    lines.append("    }")

    lines.append("}")

    dot_content = "\n".join(lines)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dot_file = os.path.join(script_dir, "EightPuzzle_states.dot")
    png_file = os.path.join(script_dir, "EightPuzzle_states.png")

    with open(dot_file, "w") as f:
        f.write(dot_content)

    subprocess.run(
        ["dot", "-Tpng", "-Gdpi=150", dot_file, "-o", png_file], check=True
    )

    print(f"Schema sugeneruota: {png_file}")
    print(f"Būsenų: {len(state_name)}")
    print(f"Briaunų: {len(seen)}")
    for d in sorted(by_depth):
        print(f"  Gylis {d}: {len(by_depth[d])} būsenos")
    print(f"Sprendimo kelyje: {len(solution_states & set(state_name.keys()))} būsenos")
    print(f"Blogose šakose: {len(set(state_name.keys()) - solution_states)} būsenos")


if __name__ == "__main__":
    main()
