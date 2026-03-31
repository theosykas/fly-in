from visualizeur_sim import InitWindow
from read_map import Reader


def main() -> None:
    try:
        reader = Reader("maps/hard/02_capacity_hell.txt")
        reader.parse_map()
        run_sim = InitWindow(1200, 600, map_read=reader)
        run_sim.start_sim()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
