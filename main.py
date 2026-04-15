from visualizeur_sim import Visualizeur
# from solver import Solver
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
        run_sim = Visualizeur(1200, 600, map_read=reader)
        run_sim.start_sim()
    except Exception as err:
        import traceback
        traceback.print_exc()
        print(f'Error: {err}')


if __name__ == "__main__":
    main()
