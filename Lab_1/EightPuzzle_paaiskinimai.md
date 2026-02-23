# Eight Puzzle – Paieškos algoritmų paaiškinimas

## 1. Uždavinio aprašymas

**Eight Puzzle** (8 dėlionė) – tai 3×3 lenta su 8 sunumeruotomis plytelėmis ir vienu tuščiu langeliu. Tikslas – stumdant plyteles pasiekti galutinę būseną.

```
Pradinė būsena:        Galutinė būsena:
 2 | 4 | 3              1 | 2 | 3
 1 | 5 | 6              4 | 5 | 6
 7 | 8 | ·              7 | 8 | ·
```

### Kintamieji būsenų aprašymui

| Kintamasis | Aprašymas |
|---|---|
| `state` | Kortežas iš 9 elementų `(t₀, t₁, t₂, t₃, t₄, t₅, t₆, t₇, t₈)` |
| `tᵢ` | Plytelės numeris pozicijoje `i`, kur `tᵢ ∈ {0,1,2,3,4,5,6,7,8}` |
| `0` | Žymi tuščią langelį |
| Veiksmai | `UP`, `DOWN`, `LEFT`, `RIGHT` – tuščio langelio judėjimo kryptis |

Indeksai lentoje:
```
 0 | 1 | 2
 3 | 4 | 5
 6 | 7 | 8
```

---

## 2. Kaip veikia eilė (Queue) ir stekas (Stack)

### FIFO eilė (Queue) – naudojama BFS

```
Principas: Pirmas įėjo → Pirmas išėjo (First In, First Out)

  Įdedame →  [A] [B] [C] [D]  → Išimame
  (gale)                         (priekyje)

  append(E):  [A] [B] [C] [D] [E]
  popleft():  [B] [C] [D] [E]        ← grąžina A
```

Python realizacija: `collections.deque` su `append()` ir `popleft()`.

### LIFO stekas (Stack) – naudojamas DFS

```
Principas: Paskutinis įėjo → Pirmas išėjo (Last In, First Out)

  [D]  ← viršus (pop/push čia)
  [C]
  [B]
  [A]

  append(E):  [E] [D] [C] [B] [A]
  pop():      [D] [C] [B] [A]        ← grąžina E
```

Python realizacija: paprastas `list` su `append()` ir `pop()`.

### Prioritetinė eilė – naudojama A* ir Best-First

```
Principas: Elementas su mažiausia f(n) reikšme išimamas pirmas

  Įdedame bet kur → [f=7] [f=2] [f=5] [f=1] → Išimamas f=1
                                                 (mažiausias)
```

Python realizacija: `PriorityQueue` klasė su `heapq` moduliu.

---

## 3. Paieška į plotį (BFS – Breadth-First Search)

### Principas

BFS tiria **visas** vieno gylio būsenas prieš pereidamas prie kito gylio. Naudoja **FIFO eilę**.

### Veikimo žingsniai (Eight Puzzle pavyzdys)

```
Gylis 0:  Pradinė būsena eilėje
          Eilė: [(2,4,3,1,5,6,7,8,0)]

Gylis 1:  Išimame pradinę, generuojame vaikus (UP, LEFT)
          Eilė: [(2,4,3,1,5,0,7,8,6), (2,4,3,1,5,6,7,0,8)]

Gylis 2:  Išimame pirmą iš eilės, generuojame JO vaikus,
          tada išimame antrą, generuojame JO vaikus
          Eilė: [...4 naujos būsenos...]

Gylis 3:  ...ir t.t., kol randame galutinę būseną
```

### Kaip BFS naudoja eilę – detalus pavyzdys

```
Žingsnis 1: Eilė = [S0]
            Išimame S0, tikriname – ne tikslas
            S0 vaikai: S1(UP), B0(LEFT)
            Eilė = [S1, B0]

Žingsnis 2: Eilė = [S1, B0]
            Išimame S1, tikriname – ne tikslas
            S1 vaikai: B1(UP), S0(DOWN)→jau tirtas, S2(LEFT)
            Eilė = [B0, B1, S2]

Žingsnis 3: Eilė = [B0, B1, S2]
            Išimame B0, tikriname – ne tikslas
            B0 vaikai: generuojame ir dedame į eilės galą
            Eilė = [B1, S2, ...]

...tęsiama kol randamas tikslas
```

### Kodo realizacija (`search.py`, 273–297 eil.)

```python
def breadth_first_graph_search(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
    frontier = deque([node])         # FIFO eilė
    explored = set()                 # Jau aplankytos būsenos
    while frontier:
        node = frontier.popleft()    # Imame iš PRIEKIO (seniausią)
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                if problem.goal_test(child.state):
                    return child     # Radome tikslą!
                frontier.append(child)  # Dedame į GALĄ
    return None
```

**Svarbiausi aspektai:**
- `deque` + `popleft()` = FIFO eilė
- `explored` rinkinys neleidžia grįžti į jau aplankytas būsenas
- Tikrina tikslą **kai generuoja** vaiką (ne kai išima iš eilės) – taip greičiau

### BFS savybės

| Savybė | Reikšmė |
|---|---|
| Pilnumas | Taip – visada randa sprendinį, jei jis egzistuoja |
| Optimalumas | Taip – randa trumpiausią kelią (mažiausiai žingsnių) |
| Laiko sudėtingumas | O(b^d), kur b = šakojimosi faktorius, d = gylis |
| Atminties sudėtingumas | O(b^d) – saugo visas gylio būsenas atmintyje |

---

## 4. Paieška į gylį (DFS – Depth-First Search)

### Principas

DFS tiria **vieną šaką iki galo** prieš grįždamas ir bandydamas kitą. Naudoja **steką (LIFO)**.

### Veikimo žingsniai (Eight Puzzle pavyzdys)

```
Žingsnis 1: Stekas = [S0]
            pop() → S0, vaikai: S1(UP), B0(LEFT)
            Stekas = [S1, B0]

Žingsnis 2: Stekas = [S1, B0]
            pop() → B0 (paskutinis įdėtas!)   ← SKIRTUMAS nuo BFS!
            B0 vaikai: ...
            Stekas = [S1, B0_vaikas1, B0_vaikas2]

Žingsnis 3: pop() → B0_vaikas2 (vėl paskutinis)
            Eina GILYN į B0 šaką...
            ...kol šaka baigiasi

Žingsnis N: Grįžta prie S1, pradeda tirti JO šaką
```

### Kodo realizacija (`search.py`, 222–241 eil.)

```python
def depth_first_graph_search(problem):
    frontier = [Node(problem.initial)]  # Stekas (paprastas list)
    explored = set()
    while frontier:
        node = frontier.pop()           # Imame iš GALO (naujausią)
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)
        frontier.extend(child for child in node.expand(problem)
                        if child.state not in explored
                        and child not in frontier)
    return None
```

**Svarbiausi aspektai:**
- `list` + `pop()` = stekas (LIFO)
- Tikrina tikslą **kai išima** iš steko (ne kai generuoja)
- `explored` rinkinys apsaugo nuo ciklų

### DFS savybės

| Savybė | Reikšmė |
|---|---|
| Pilnumas | Taip (su `explored` rinkiniu baigtinėje erdvėje) |
| Optimalumas | **Ne** – gali rasti ilgesnį kelią |
| Laiko sudėtingumas | O(b^m), kur m = maksimalus gylis |
| Atminties sudėtingumas | O(b·m) – daug mažiau nei BFS |

---

## 5. BFS vs DFS – palyginimas su Eight Puzzle pavyzdžiu

```
                         S0 (pradinė)
                        /            \
                      S1(UP)       B0(LEFT)
                    / | \           |   \
                 B1  S0* S2      ...    ...
                     ↑(jau tirta)
```

### BFS eiga (plotis):
```
Eilė: [S0]
Eilė: [S1, B0]           ← tiriame gylį 1: S1, paskui B0
Eilė: [B0, B1, S2]       ← tiriame gylį 2: B0 vaikus, tada...
...kiekviename gylyje tiriamos VISOS būsenos
```
**Rezultatas:** randa optimalų 8 žingsnių sprendimą.

### DFS eiga (gylis):
```
Stekas: [S0]
Stekas: [S1, B0]
pop → B0 (eina į LEFT šaką pirma!)
Stekas: [S1, B0_vaikas1, B0_vaikas2]
pop → B0_vaikas2 (giliau ir giliau į blogą šaką...)
...gali ilgai klaidžioti blogose šakose
```
**Rezultatas:** gali rasti sprendimą, bet nebūtinai trumpiausią.

---

## 6. Euristikos paieškos pagreitinimui

Euristika – tai **spėjimo funkcija h(n)**, kuri įvertina, kiek „kainuos" pasiekti tikslą iš dabartinės būsenos. Ji padeda algoritmu pasirinkti perspektyviausią kelią.

### 6.1 Neteisingai padėtų plytelių skaičius (Misplaced Tiles)

**h₁(n)** = kiek plytelių yra ne savo vietoje.

```python
def h(self, node):
    return sum(s != g for (s, g) in zip(node.state, self.goal))
```

Pavyzdys:
```
Dabartinė:    Galutinė:
 2 | 4 | 3    1 | 2 | 3
 1 | 5 | 6    4 | 5 | 6
 7 | 8 | ·    7 | 8 | ·

Pozicija 0: 2 ≠ 1  ✗
Pozicija 1: 4 ≠ 2  ✗
Pozicija 2: 3 = 3  ✓
Pozicija 3: 1 ≠ 4  ✗
Pozicija 4: 5 = 5  ✓
Pozicija 5: 6 = 6  ✓
Pozicija 6: 7 = 7  ✓
Pozicija 7: 8 = 8  ✓

h₁ = 3 (trys plytelės ne savo vietoje)
```

### 6.2 Manheteno atstumas (Manhattan Distance)

**h₂(n)** = kiekvienos plytelės atstumų iki tikslinės pozicijos suma (horizontaliai + vertikaliai).

```
Dabartinė:          Galutinė:
 2 | 4 | 3          1 | 2 | 3
 1 | 5 | 6          4 | 5 | 6
 7 | 8 | ·          7 | 8 | ·

Plytelė 2: pozicija (0,0) → tikslas (0,1) = |0-0|+|0-1| = 1
Plytelė 4: pozicija (0,1) → tikslas (1,0) = |0-1|+|1-0| = 2
Plytelė 1: pozicija (1,0) → tikslas (0,0) = |1-0|+|0-0| = 1
(kitos plytelės jau savo vietose = 0)

h₂ = 1 + 2 + 1 = 4
```

**Manheteno atstumas yra tikslesnė euristika** nei neteisingai padėtų plytelių skaičius (h₂ ≥ h₁), todėl A* su ja tiria mažiau būsenų.

### 6.3 Euristikų palyginimas

| Euristika | h(pradinė) | Tikslumas | Greitis |
|---|---|---|---|
| h₁ – Neteisingos plytelės | 3 | Žemas | Lėtesnis |
| h₂ – Manheteno atstumas | 4 | Aukštas | Greitesnis |
| h = 0 (be euristikos) | 0 | Jokio | Lėčiausias (= BFS) |

---

## 7. Best-First ir A* paieška

### Best-First paieška

Naudoja **prioritetinę eilę** – visada išima būseną su **mažiausia f(n) reikšme**.

```python
def best_first_graph_search(problem, f):
    node = Node(problem.initial)
    frontier = PriorityQueue('min', f)   # Prioritetinė eilė
    frontier.append(node)
    explored = set()
    while frontier:
        node = frontier.pop()            # Išimame su mažiausiu f(n)
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                if f(child) < frontier[child]:  # Radome geresnį kelią
                    del frontier[child]
                    frontier.append(child)
    return None
```

### A* paieška

A* naudoja formulę: **f(n) = g(n) + h(n)**

| Komponentas | Reikšmė |
|---|---|
| g(n) | Faktinė kelio kaina nuo pradžios iki n |
| h(n) | Euristinis įvertis nuo n iki tikslo |
| f(n) | Bendras įvertis – kuo mažesnis, tuo perspektyvesnis mazgas |

```python
def astar_search(problem, h=None):
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n))
```

### A* veikimo pavyzdys su Eight Puzzle

```
Prioritetinė eilė (mažiausias f pirmas):

Žingsnis 1: [(S0, f=0+3=3)]
            Išimame S0 (f=3)
            Vaikai: S1(g=1,h=2,f=3), B0(g=1,h=4,f=5)
            Eilė: [(S1,f=3), (B0,f=5)]

Žingsnis 2: Išimame S1 (f=3, mažesnis už B0 f=5)
            A* „žino", kad S1 perspektyvesnis!
            Vaikai: S2(g=2,h=2,f=4), B1(g=2,h=4,f=6)
            Eilė: [(S2,f=4), (B0,f=5), (B1,f=6)]

Žingsnis 3: Išimame S2 (f=4)
            Tęsiame perspektyviausiu keliu...

→ A* randa optimalų sprendimą tirdamas DAUG MAŽIAU būsenų nei BFS
```

---

## 8. Algoritmų palyginimo lentelė

| Savybė | BFS | DFS | A* |
|---|---|---|---|
| Duomenų struktūra | FIFO eilė (`deque`) | Stekas (`list`) | Prioritetinė eilė |
| Išėmimo tvarka | Seniausias | Naujausias | Mažiausias f(n) |
| Randa optimalų? | Taip | Ne | Taip (su leistina h) |
| Atminties naudojimas | Didelis O(b^d) | Mažas O(b·m) | Vidutinis |
| Greitis | Lėtas (tiria viską) | Greitas, bet neoptimalus | Greičiausias su gera h |
| Kada naudoti? | Kai reikia trumpiausio kelio | Kai atmintis ribota | Kai yra gera euristika |

---

## 9. Vizualizacija

Failas `EightPuzzle_states.png` rodo pilną būsenų erdvės schemą (BFS medis iki gylio 5):

- **Geltona** – pradinė būsena S0
- **Žalia** – galutinė būsena (tikslas)
- **Mėlyna** – būsenos sprendimo kelyje
- **Rausva** – „blogos" šakos (alternatyvūs keliai, kurie šiame gylyje neveda prie tikslo)
- **Žalios linijos** – sprendimo kelias (BFS rastas optimalus)
- **Pilkos brūkšninės** – visi kiti galimi perėjimai

Schemoje matosi, kaip paieškos medis **eksponentiškai auga** su kiekvienu gyliu (1→2→4→8→16→20 būsenų), ir kodėl euristikos yra svarbios – jos leidžia „apkarpyti" blogas šakas ir surasti sprendimą greičiau.
