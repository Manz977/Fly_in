*This project has been created as part of the 42 curriculum by mamonzer.*

# Fly-in — Drone Network Routing Simulator

## Description

**Fly-in** is a drone routing simulation project.  Given a network of interconnected airspace hubs (zones) and a fleet of drones, the program computes the optimal path from a start zone to an end zone and simulates all drones traversing that path simultaneously, turn by turn, while respecting per-zone and per-link capacity constraints.

The goal is to route every drone from the designated start hub to the end hub in the minimum number of turns without violating any capacity rules.  The full simulation history is then replayed in an interactive fullscreen visualiser that lets the user step through each turn and inspect drone movements across the network.

### Feature overview

| Feature | Description |
|---|---|
| Map parsing | Reads a custom `.txt` format describing zones, types, capacities, and connections |
| Pathfinding | Dijkstra's algorithm with zone-type-based traversal costs |
| Simulation | Turn-based movement with per-zone and per-link capacity enforcement |
| Visualiser | Interactive pygame fullscreen display with turn-by-turn playback |

---

## Instructions

### Prerequisites

- Python **3.10+**
- [`pygame`](https://www.pygame.org/) library

Install dependencies:

```bash
pip install pygame
```

### Running the program

```bash
# Default map (maps/hard/03_ultimate_challenge.txt)
python main.py

# Custom map file
python main.py path/to/your_map.txt
```

### Map file format

Map files are plain text with the following directives (one per line):

```
nb_drones: <count>

start_hub: <name> <x> <y> [zone=<type> max_drones=<n> color=<c>]
end_hub:   <name> <x> <y> [zone=<type> max_drones=<n> color=<c>]
hub:       <name> <x> <y> [zone=<type> max_drones=<n> color=<c>]

connection: <name1>-<name2> [max_link_capacity=<n>]
```

**Zone types** and their traversal costs:

| Type | Cost | Effect |
|---|---|---|
| `normal` | 1 | Standard zone |
| `priority` | 1 | Same cost as normal, visually distinguished |
| `restricted` | 2 | Higher traversal cost (Dijkstra penalises this zone) |
| `blocked` | ∞ | Impassable; Dijkstra routes around it |

Lines beginning with `#` are comments.  The special prefix `#start_hub:` is treated as a `start_hub:` directive (used in some map files).

Sample map files are provided under `maps/easy/`, `maps/medium/`, `maps/hard/`, and `maps/challenger/`.

### Visualiser controls

| Key | Action |
|---|---|
| **→** Right Arrow | Advance to the next turn |
| **←** Left Arrow | Go back to the previous turn |
| **ESC** | Exit the visualiser |

---

## Algorithm choices and implementation strategy

### Pathfinding — Dijkstra's algorithm

The pathfinding module ([algorithm/algorithm.py](algorithm/algorithm.py)) implements **Dijkstra's shortest-path algorithm** using Python's `heapq` min-heap as the priority queue.

**Why Dijkstra?**
The network graph has non-negative, heterogeneous edge weights derived from zone types.  Dijkstra's algorithm is optimal for this class of problem: it guarantees the shortest (lowest-cost) path and runs in *O((V + E) log V)* time, which is well within budget for the network sizes used in this project.

**Cost model:**
Edge cost is applied to the *destination* zone, not the link itself.  This means:
- Routing through a `restricted` zone costs 2 instead of 1.
- `blocked` zones receive a cost of `∞`, so they are effectively never chosen.
- `normal` and `priority` zones cost 1, keeping direct routes as short as possible.

All drones share one path computed once at initialisation time.

### Simulation — turn-based capacity-constrained movement

The simulator ([simulator/simulation.py](simulator/simulation.py)) advances the fleet one turn at a time.

**Capacity constraints (per turn):**
1. **Zone capacity** (`max_drones`): at most N drones may occupy a zone simultaneously.
2. **Link capacity** (`max_link_capacity`): at most M drones may traverse a connection in one turn.

Each turn, every drone that has not yet reached the end is evaluated in `id` order.  A move is only executed when *both* the destination zone and the connecting link have remaining capacity.  Drones that are blocked wait and retry in the next turn, creating natural queuing behaviour.

A hard cap of `MAX_TURNS = 100` prevents infinite loops in the event of a deadlock (e.g. a network configuration where drones permanently block each other).

**State recording:**
After each turn, a snapshot dict is appended to `turn_history`.  The snapshot captures drone positions, zone occupancy, and movement events — this is the data consumed by the visualiser.

### Data model — adjacency list graph

The `Network` class ([parser/models.py](parser/models.py)) stores the graph as both a flat zone/connection registry and an `adj_list` dict mapping each zone to its list of neighbouring zones.  The adjacency list provides O(1) neighbour access by zone name without requiring a full scan of the connections list.

---

## Visual representation

The visualiser ([visual/visualizer.py](visual/visualizer.py)) is built with **pygame** and runs in fullscreen at 60 fps.

### Layout

Zone positions are derived from the `x`/`y` coordinates in the map file.  The algorithm:
1. Finds the bounding box of all zone coordinates.
2. Scales the map uniformly so it fills the available drawing area while preserving aspect ratio.
3. Applies a vertical stretch for dense networks (> 30 zones) to reduce node overlap.
4. Centres the result within the padded screen area.

### Visual encoding

| Element | Representation |
|---|---|
| Zone (normal) | Blue filled circle |
| Zone (blocked) | Red filled circle |
| Zone (restricted) | Yellow filled circle |
| Zone (priority) | Green filled circle |
| Connection | Grey line between zone circles |
| Drone | Small red circle with `D<id>` label, rendered at the drone's current zone |
| Turn counter | White text in the top-left corner |

Zone radii and padding are scaled automatically: smaller networks (≤ 10 zones) use larger circles for readability; denser networks use smaller circles to avoid overlap.

### Interaction

The visualiser is a **replay player**: the entire simulation runs first (populating `turn_history`), and the user then navigates the pre-computed frames with the arrow keys.  This design allows the user to move freely forward and backward without re-running any simulation logic.  An instructions overlay is shown before the main loop begins.

---

## Project structure

```
Fly-in/
├── main.py                  Entry point
├── algorithm/
│   ├── __init__.py
│   └── algorithm.py         Dijkstra pathfinder
├── parser/
│   ├── __init__.py
│   ├── models.py            Zone, Connection, Network data model
│   └── parser.py            Map file parser
├── simulator/
│   ├── __init__.py
│   └── simulation.py        Turn-based simulator
├── visual/
│   ├── __init__.py
│   └── visualizer.py        pygame visualiser
└── maps/
    ├── easy/
    ├── medium/
    ├── hard/
    └── challenger/
```

---

## Resources

### Documentation and references

- [Python `heapq` module](https://docs.python.org/3/library/heapq.html) — standard-library min-heap used for the priority queue in Dijkstra's algorithm.
- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) — algorithm description and complexity analysis.
- [pygame documentation](https://www.pygame.org/docs/) — reference for the display, drawing, and event APIs used in the visualiser.
- [pygame.gfxdraw](https://www.pygame.org/docs/ref/gfxdraw.html) — anti-aliased drawing primitives used for smooth zone circles.
- [Python `re` module](https://docs.python.org/3/library/re.html) — regular expressions used in the map file parser.

### AI usage

**Claude (Anthropic)** was used in this project for the following tasks:

- **Docstring generation**: All Google-style docstrings across the four modules (`algorithm`, `parser`, `simulator`, `visual`) were written with AI assistance, ensuring consistent argument documentation, return-type descriptions, and exception notes.
- **README authoring**: This README was drafted with AI assistance based on a full analysis of the source code, covering algorithm rationale, visual design decisions, and usage instructions.
- **Code review / clarification**: AI was consulted to explain Python standard-library behaviour (e.g. `heapq` tie-breaking, `re` group indexing) during development.

AI was *not* used to write the core simulation or pathfinding logic; those were implemented and debugged by the project authors.
