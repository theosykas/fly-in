from visualizeur_sim import InitWindow
from read_map import Reader


def main() -> None:
    reader = Reader("maps/hard/02_capacity_hell.txt")
    reader.parse_map()
    run_sim = InitWindow(1200, 600, map_r=reader)
    run_sim.start_sim()


if __name__ == "__main__":
    main()
