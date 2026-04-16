*This project has been created as part of the 42 curriculum by thsykas.*

# Fly-in: Multi-Drone Pathfinding and Routing System


---

## 1. Description

**Fly-in** is an autonomous drone fleet management system designed to route multiple drones from a starting base to a target location through a dynamic network of zones. The primary objective is to move all drones from the start zone to the end zone in the fewest possible simulation turns. The system must strictly adhere to physical constraints such as zone capacities, connection limits, and varying movement costs based on specific zone types. 

The system implements a custom, fully object-oriented graph-based simulation engine that handles simultaneous movements, path conflicts, and strategic waiting, ensuring high throughput and deadlock avoidance.

---

## 2. Instructions

### Prerequisites
* **Environment:** Python 3.10 or later is strictly required.

* **Typing & Linting:** The project uses `mypy` for static type checking and `flake8` for enforcing coding standards.

### Installation
Install the necessary dependencies using the provided `Makefile`:
```bash
make install
```

### Execution
To run the simulation with a specific map file:
```bash
python3 main.py < path/to/map_file
# OR using the Makefile
make run
```

### Development Tools
* **Linting:** Run `make lint` to execute `flake8` and `mypy` with strict validation flags.
* **Debugging:** Run `make debug` to execute the main script using Python's built-in `pdb` debugger.

* **Cleanup:** Run `make clean` to remove temporary files and cache directories like `__pycache__`.

---

## 3. Architecture & Implementation

### Project Structure
* **`main.py`**: The entry point. It coordinates the parser, the simulation engine, and the terminal output formatting.
* **`reade_map.py`**: A robust parser that validates and transforms the input text file into an internal object-oriented graph. It handles syntax validation, unique naming constraints, integer coordinates, and capacity extraction.
* **`visualizeur.py`**: Manages the visual representation of the simulation, providing colored terminal output to display drone movements and zone states turn-by-turn.
* **`solver.py`**: Houses the pathfinding logic. It leverages advanced graph algorithms to distribute drones across multiple paths and avoid bottlenecks.


### Core Logic & Algorithms

#### 1. Graph Representation
The network is modeled as a bidirectional graph where each node (Zone) and edge (Connection) is an object.
* **Normal Zone:** Standard zone with a 1-turn movement cost.
* **Restricted Zone:** A sensitive zone costing 2 turns; drones occupy the incoming connection for the first turn.
* **Priority Zone:** Preferred routing zone with a 1-turn cost, prioritized by the pathfinding algorithm.
* **Blocked Zone:** Inaccessible areas that invalidate any path trying to cross them.

#### 2. Advanced Pathfinding (Dijkstra & Yen's K-Shortest Paths)
Instead of sending all drones down a single shortest path—which would cause massive bottlenecks due to capacity limits—`solver.py` utilizes a sophisticated multi-path flow strategy:
* **Dijkstra's Algorithm:** Used as the baseline to calculate the absolute shortest path from the `start_hub` to the `end_hub` , taking into account the varying weights of Priority (lower weight) and Restricted (higher weight) zones.
* **Yen's Algorithm (K-Shortest Paths):** This algorithm iterates upon Dijkstra to find the $K$ shortest loopless paths in the network. By systematically masking edges and nodes from the best path, Yen's algorithm discovers alternative, disjoint, or slightly overlapping routes.
* **Path Allocation:** The solver distributes the fleet of drones across this pool of K-paths. It calculates whether it is faster for a drone to wait for capacity on the shortest path or to immediately take a slightly longer alternative path, thereby maximizing global throughput.

#### 3. Simulation Mechanics
The simulation follows strict discrete turns:
1. **Release:** Drones moving out of a zone immediately free up capacity for that same turn.
2. **Validation:** Drones can only move into a zone if it does not exceed its `max_drones` capacity. Similarly, connections enforce `max_link_capacity`.
3. **Multi-turn Transit:** Drones entering restricted zones must stay in transit on the connection, arriving exactly after the specified turns without waiting indefinitely.

---

## 4. Output & Visual Representation

The simulation outputs step-by-step drone movements formatted precisely as `D<ID>-<zone>` (e.g., `D1-roof1 D2-corridorA`). Drones that reach the end zone are considered successfully delivered. 

To enhance user experience, `visualizeur.py` parses map metadata (like `[color=red]`) to generate colored terminal logs, providing real-time visual feedback on drone throughput and active routing.

---

## 5. Resources & References
* **Graph Theory Documentation:** References to GeeksForGeeks for Dijkstra's Algorithm and Yen's K-Shortest Path implementations.
* **PEP Documentation:** Adherence to PEP 257 for docstrings and PEP 484 for `mypy` type hinting.
* **AI Usage:** AI was utilized to brainstorm edge cases for parser error handling, refine the English documentation structure for clarity, and conceptualize the weighting system for Priority vs. Restricted zones within Yen's algorithm.

---

## 6. Performance Benchmarks

The implemented `solver.py` logic targets high efficiency across varying map complexities. Expected performance benchmarks include:
* **Easy Maps:** Target $\le 6$ to $8$ turns.
* **Medium Maps:** Target $\le 12$ to $20$ turns.
* **Hard Maps:** Target $\le 35$ to $60$ turns depending on drone count.
* **Challenger Map:** The algorithms have been deeply optimized to attempt the "Impossible Dream" map with an aim to beat the 45-turn reference record.
```