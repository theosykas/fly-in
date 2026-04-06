from visualizeur_sim import Visualizeur
from solver import Solver
from read_map import Reader
import sys


def main() -> None:
    try:
        if len(sys.argv) < 2:
            print('Usage: choose your dir and map <PATH>')
            sys.exit(1)
        map_dir = sys.argv[1]
        reader = Reader(map_dir)
        reader.parse_map()
        solver_dijkstra = Solver(reader=reader)
        find_path = solver_dijkstra.dijkstra()
        if find_path:
            print("path: " + " -> ".join(find_path))
        else:
            print('path not found')
        run_sim = Visualizeur(1200, 600, map_read=reader, path=find_path)
        run_sim.start_sim()
    except Exception as err:
        print(f'Error: {err}')


if __name__ == "__main__":
    main()
