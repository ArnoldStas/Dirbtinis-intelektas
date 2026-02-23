"""
Eight Puzzle sprendimas naudojant AIMA (Artificial Intelligence: A Modern Approach) architektūrą.

AIMA architektūros komponentai (visi realizuoti šiame faile):
  1. Problem  – abstrakti uždavinio klasė
  2. Node     – paieškos medžio mazgas
  3. Paieškos algoritmai: BFS, DFS, Best-First, A*
  4. Pagalbinės struktūros: PriorityQueue, memoize
  5. EightPuzzle – konkreti Problem subklasė
"""

import heapq
import functools
from collections import deque


# ============================================================================
# 1. AIMA bazinė klasė: Problem
# ============================================================================

class Problem:
    """Abstrakti uždavinio klasė (AIMA Fig. 3.1).
    Subklasė privalo realizuoti: actions(), result().
    Gali perrašyti: goal_test(), path_cost(), h()."""

    def __init__(self, initial, goal=None):
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        """Grąžina galimų veiksmų sąrašą duotoje būsenoje."""
        raise NotImplementedError

    def result(self, state, action):
        """Grąžina būseną, gautą atlikus veiksmą."""
        raise NotImplementedError

    def goal_test(self, state):
        """Ar būsena yra tikslinė?"""
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Kelio kaina. Numatytoji: kiekvienas žingsnis kainuoja 1."""
        return c + 1

    def h(self, node):
        """Euristinė funkcija (numatytoji: 0)."""
        return 0


# ============================================================================
# 2. AIMA paieškos medžio mazgas: Node
# ============================================================================

class Node:
    """Paieškos medžio mazgas (AIMA Fig. 3.10).
    Saugo: būseną, tėvą, veiksmą, kelio kainą, gylį."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return f"<Node {self.state}>"

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        """Išplėsti mazgą – grąžinti visus vaikinius mazgus."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """Sukurti vaikinį mazgą pagal veiksmą."""
        next_state = problem.result(self.state, action)
        return Node(next_state, self, action,
                    problem.path_cost(self.path_cost, self.state, action, next_state))

    def solution(self):
        """Grąžina veiksmų seką nuo šaknies iki šio mazgo."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Grąžina mazgų sąrašą nuo šaknies iki šio mazgo."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)


# ============================================================================
# 3. Pagalbinės struktūros
# ============================================================================

class PriorityQueue:
    """Prioritetinė eilė (min-heap), naudojama Best-First ir A* paieškose."""

    def __init__(self, f=lambda x: x):
        self.heap = []
        self.f = f

    def append(self, item):
        heapq.heappush(self.heap, (self.f(item), item))

    def pop(self):
        return heapq.heappop(self.heap)[1]

    def __len__(self):
        return len(self.heap)

    def __contains__(self, key):
        return any(item == key for _, item in self.heap)

    def __getitem__(self, key):
        for value, item in self.heap:
            if item == key:
                return value
        raise KeyError(str(key))

    def __delitem__(self, key):
        try:
            del self.heap[[item == key for _, item in self.heap].index(True)]
        except ValueError:
            raise KeyError(str(key))
        heapq.heapify(self.heap)


def memoize(fn, slot=None):
    """Įsimena funkcijos rezultatus (kešavimas).
    Jei slot nurodyta – saugo kaip mazgo atributą."""
    if slot:
        def memoized_fn(obj, *args):
            if hasattr(obj, slot):
                return getattr(obj, slot)
            val = fn(obj, *args)
            setattr(obj, slot, val)
            return val
    else:
        @functools.lru_cache(maxsize=128)
        def memoized_fn(*args):
            return fn(*args)
    return memoized_fn


# ============================================================================
# 4. Paieškos algoritmai
# ============================================================================

def breadth_first_graph_search(problem):
    """Paieška į plotį (BFS) – FIFO eilė (AIMA Fig. 3.11).
    Randa optimalų (trumpiausią) sprendimą."""
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
    frontier = deque([node])       # FIFO eilė
    explored = set()
    while frontier:
        node = frontier.popleft()  # Imame seniausią (iš priekio)
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                if problem.goal_test(child.state):
                    return child
                frontier.append(child)  # Dedame į galą
    return None


def depth_first_graph_search(problem, max_depth=50):
    """Paieška į gylį (DFS) – stekas/LIFO (AIMA Fig. 3.7).
    Naudoja mažiau atminties, bet neranda optimalaus sprendimo.
    max_depth riboja gylį, kad neklaidžiotų per ilgai."""
    frontier = [Node(problem.initial)]  # Stekas
    explored = set()
    while frontier:
        node = frontier.pop()           # Imame naujausią (iš viršaus)
        if problem.goal_test(node.state):
            return node
        if node.depth >= max_depth:
            continue
        explored.add(node.state)
        frontier.extend(child for child in node.expand(problem)
                        if child.state not in explored and child not in frontier)
    return None


def iterative_deepening_search(problem):
    """Iteratyvaus gilinimo paieška (IDDFS) – AIMA Fig. 3.18.
    Derina DFS atminties efektyvumą su BFS optimalumu."""
    for depth_limit in range(0, 100):
        result = depth_limited_search(problem, depth_limit)
        if result is not None and result != 'cutoff':
            return result
    return None


def depth_limited_search(problem, limit):
    """DFS su fiksuotu gylio limitu."""
    def recursive_dls(node, limit):
        if problem.goal_test(node.state):
            return node
        if limit == 0:
            return 'cutoff'
        cutoff_occurred = False
        for child in node.expand(problem):
            result = recursive_dls(child, limit - 1)
            if result == 'cutoff':
                cutoff_occurred = True
            elif result is not None:
                return result
        return 'cutoff' if cutoff_occurred else None
    return recursive_dls(Node(problem.initial), limit)


def best_first_graph_search(problem, f):
    """Best-First paieška – prioritetinė eilė (AIMA Fig. 3.14).
    Funkcija f(n) nustato mazgų tyrimo prioritetą."""
    f = memoize(f, 'f')
    node = Node(problem.initial)
    frontier = PriorityQueue(f)
    frontier.append(node)
    explored = set()
    while frontier:
        node = frontier.pop()  # Imame su mažiausiu f(n)
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                if f(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)
    return None


def astar_search(problem, h=None):
    """A* paieška – f(n) = g(n) + h(n) (AIMA Fig. 3.26).
    Optimalus algoritmas su leistina euristika."""
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n))


def greedy_best_first_search(problem, h=None):
    """Godžioji Best-First paieška – f(n) = h(n).
    Greita, bet negarantuoja optimalaus sprendimo."""
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, h)


# ============================================================================
# 5. Eight Puzzle uždavinys – Problem subklasė
# ============================================================================

class EightPuzzle(Problem):
    """8 dėlionės uždavinys (AIMA).

    Būsena: 9 elementų kortežas (tuple), pvz. (2, 4, 3, 1, 5, 6, 7, 8, 0)
    Veiksmai: UP, DOWN, LEFT, RIGHT (tuščio langelio judėjimo kryptis)
    Lenta:
        indeksai:    reikšmės (pavyzdys):
        0 | 1 | 2    2 | 4 | 3
        3 | 4 | 5    1 | 5 | 6
        6 | 7 | 8    7 | 8 | ·
    """

    def __init__(self, initial, goal=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        super().__init__(initial, goal)

    def find_blank(self, state):
        """Rasti tuščio langelio (0) indeksą."""
        return state.index(0)

    def actions(self, state):
        """Galimi veiksmai pagal tuščio langelio poziciją."""
        possible = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        blank = self.find_blank(state)
        if blank % 3 == 0:
            possible.remove('LEFT')
        if blank < 3:
            possible.remove('UP')
        if blank % 3 == 2:
            possible.remove('RIGHT')
        if blank > 5:
            possible.remove('DOWN')
        return possible

    def result(self, state, action):
        """Atlikti veiksmą – sukeisti tuščią langelį su kaimynu."""
        blank = self.find_blank(state)
        new_state = list(state)
        delta = {'UP': -3, 'DOWN': 3, 'LEFT': -1, 'RIGHT': 1}
        neighbor = blank + delta[action]
        new_state[blank], new_state[neighbor] = new_state[neighbor], new_state[blank]
        return tuple(new_state)

    def goal_test(self, state):
        return state == self.goal

    def h(self, node):
        """Euristika: neteisingai padėtų plytelių skaičius (Misplaced Tiles)."""
        return sum(s != g for (s, g) in zip(node.state, self.goal))

    def manhattan(self, node):
        """Euristika: Manheteno atstumas (Manhattan Distance).
        Tikslesnė euristika – skaičiuoja kiekvienos plytelės atstumą
        iki jos tikslinės pozicijos."""
        distance = 0
        for i, tile in enumerate(node.state):
            if tile == 0:
                continue
            goal_i = self.goal.index(tile)
            # Eilutė ir stulpelis dabartinėje ir tikslinėje pozicijoje
            distance += abs(i // 3 - goal_i // 3) + abs(i % 3 - goal_i % 3)
        return distance


# ============================================================================
# 6. Pagalbinė funkcija: būsenos spausdinimas
# ============================================================================

def print_state(state, label=""):
    """Atspausdinti 3×3 lentą."""
    if label:
        print(label)
    for row in range(3):
        tiles = []
        for col in range(3):
            val = state[row * 3 + col]
            tiles.append(str(val) if val != 0 else "·")
        print(f"  {tiles[0]} | {tiles[1]} | {tiles[2]}")
    print()


def print_solution_path(problem, result_node):
    """Atspausdinti visą sprendimo kelią su būsenomis."""
    if result_node is None:
        print("Sprendimas nerastas!")
        return
    path = result_node.path()
    print(f"Sprendimas rastas! Žingsnių: {len(path) - 1}\n")
    for i, node in enumerate(path):
        if i == 0:
            print_state(node.state, "Pradinė būsena:")
        elif i == len(path) - 1:
            print(f"  ↓ Veiksmas: {node.action}")
            print_state(node.state, f"Galutinė būsena (žingsnis {i}):")
        else:
            print(f"  ↓ Veiksmas: {node.action}")
            print_state(node.state, f"Žingsnis {i}:")


# ============================================================================
# 7. Pagrindinis vykdymas – visų algoritmų palyginimas
# ============================================================================

if __name__ == "__main__":
    initial = (2, 4, 3, 1, 5, 6, 7, 8, 0)
    goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)

    print("=" * 60)
    print("EIGHT PUZZLE – AIMA ARCHITEKTŪRA")
    print("=" * 60)

    print_state(initial, "\nPradinė būsena:")
    print_state(goal, "Galutinė (tikslinė) būsena:")

    puzzle = EightPuzzle(initial, goal)

    # --- BFS ---
    print("-" * 60)
    print("1. PAIEŠKA Į PLOTĮ (BFS)")
    print("   Duomenų struktūra: FIFO eilė (deque)")
    print("-" * 60)
    result_bfs = breadth_first_graph_search(puzzle)
    print(f"   Sprendimas: {result_bfs.solution()}")
    print(f"   Žingsnių:   {len(result_bfs.solution())}")
    print()

    # --- DFS ---
    print("-" * 60)
    print("2. PAIEŠKA Į GYLĮ (DFS, max_depth=50)")
    print("   Duomenų struktūra: Stekas (list)")
    print("-" * 60)
    result_dfs = depth_first_graph_search(puzzle, max_depth=50)
    if result_dfs:
        print(f"   Sprendimas: {result_dfs.solution()}")
        print(f"   Žingsnių:   {len(result_dfs.solution())}")
    else:
        print("   Sprendimas nerastas per nurodytą gylį")
    print()

    # --- IDDFS ---
    print("-" * 60)
    print("3. ITERATYVAUS GILINIMO PAIEŠKA (IDDFS)")
    print("   Duomenų struktūra: Stekas (rekursija)")
    print("-" * 60)
    result_iddfs = iterative_deepening_search(puzzle)
    if result_iddfs:
        print(f"   Sprendimas: {result_iddfs.solution()}")
        print(f"   Žingsnių:   {len(result_iddfs.solution())}")
    else:
        print("   Sprendimas nerastas")
    print()

    # --- Greedy Best-First ---
    print("-" * 60)
    print("4. GODŽIOJI BEST-FIRST PAIEŠKA")
    print("   Duomenų struktūra: Prioritetinė eilė")
    print("   Euristika: Neteisingai padėtos plytelės h₁(n)")
    print("-" * 60)
    result_greedy = greedy_best_first_search(puzzle)
    print(f"   Sprendimas: {result_greedy.solution()}")
    print(f"   Žingsnių:   {len(result_greedy.solution())}")
    print()

    # --- A* su Misplaced Tiles ---
    print("-" * 60)
    print("5. A* PAIEŠKA (euristika: neteisingos plytelės)")
    print("   Duomenų struktūra: Prioritetinė eilė")
    print("   f(n) = g(n) + h₁(n)")
    print("-" * 60)
    result_astar1 = astar_search(puzzle)
    print(f"   Sprendimas: {result_astar1.solution()}")
    print(f"   Žingsnių:   {len(result_astar1.solution())}")
    print()

    # --- A* su Manhattan Distance ---
    print("-" * 60)
    print("6. A* PAIEŠKA (euristika: Manheteno atstumas)")
    print("   Duomenų struktūra: Prioritetinė eilė")
    print("   f(n) = g(n) + h₂(n)")
    print("-" * 60)
    result_astar2 = astar_search(puzzle, h=puzzle.manhattan)
    print(f"   Sprendimas: {result_astar2.solution()}")
    print(f"   Žingsnių:   {len(result_astar2.solution())}")
    print()

    # --- Rezultatų palyginimas ---
    print("=" * 60)
    print("ALGORITMŲ PALYGINIMAS")
    print("=" * 60)
    results = [
        ("BFS (plotis)",            result_bfs),
        ("DFS (gylis)",             result_dfs),
        ("IDDFS (iter. gilinimas)", result_iddfs),
        ("Greedy Best-First",       result_greedy),
        ("A* (neteisingos plyt.)",  result_astar1),
        ("A* (Manheteno atst.)",    result_astar2),
    ]
    print(f"  {'Algoritmas':<28} {'Žingsniai':>10}")
    print(f"  {'-'*28} {'-'*10}")
    for name, res in results:
        steps = len(res.solution()) if res else "N/A"
        print(f"  {name:<28} {steps:>10}")

    # --- Pilnas sprendimo kelias (A* Manhattan) ---
    print()
    print("=" * 60)
    print("PILNAS SPRENDIMO KELIAS (A* su Manheteno atstumu)")
    print("=" * 60)
    print_solution_path(puzzle, result_astar2)
