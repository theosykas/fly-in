from visualizeur import Visualizeur
from read_map import Reader
import sys


def main() -> None:
    """Initializes and starts the simulation from a map file.

        Retrieves the file path from command-line arguments, uses the Reader
        to extract map data, then initializes the Visualizer to display
        the simulation.

        Raises:
            SystemExit: If no map path argument is provided.
            Exception: For any error occurring during parsing or simulation.
        """
    try:
        if len(sys.argv) < 2:
            print('Usage: uv run python3 main.py /maps/type/XX_xxx')
            sys.exit(0)
        map_dir = sys.argv[1]
        reader = Reader(map_dir)
        reader.parse_map()
        run_sim = Visualizeur(1200, 600, map_read=reader)
        run_sim.start_sim()
    except Exception as err:
        print(f'[Error]: {err}')


if __name__ == "__main__":
    main()
