from pathlib import Path

from .create_instance import display_instance, get_instance
from .optimize import create_model, solve_model
from .plot_solution import generate_graphics
from .solution import save_solution, verify_solution

# Configs
CREATE_NEW_INSTANCE = False
SAVE_INSTANCE = False
READ_INSTANCE_FROM_FILE = True
DISPLAY_INSTANCE = True
SOLVE_MILP = True
VERIFY_MILP_WITH_EVALUATION = True
SAVE_SOLUTION = True
GENERATE_GRAPHICS = True

SPECIFIC_PART_COUNT = 5
RANDOM_SEED = 42
MAX_ROBOT_A_COUNT = 300
ROBOT_A_COUNT_STEP = 1

SOURCE_DIR = Path(__file__).resolve().parents[1]
INSTANCE_PATH = SOURCE_DIR / "inputs" / "instance.json"
SOLUTION_PATH = SOURCE_DIR / "outputs" / "solution.json"
GRAPHIC_PATH = SOURCE_DIR / "graphics" / "graphic.png"


def main() -> None:
    """Run the enabled instance, optimization, output, and plotting steps."""
    instance = get_instance(
        create_new=CREATE_NEW_INSTANCE,
        read_from_file=READ_INSTANCE_FROM_FILE,
        save_to_file=SAVE_INSTANCE,
        filename=INSTANCE_PATH,
        specific_part_count=SPECIFIC_PART_COUNT,
        seed=RANDOM_SEED,
    )
    if DISPLAY_INSTANCE:
        display_instance(instance)

    optimal_solution = None
    if SOLVE_MILP:
        model = create_model(instance)
        optimal_solution = solve_model(model)
        if VERIFY_MILP_WITH_EVALUATION:
            verify_solution(instance, optimal_solution)

    if SAVE_SOLUTION:
        if optimal_solution is None:
            raise ValueError("SAVE_SOLUTION requires SOLVE_MILP to be enabled.")
        save_solution(optimal_solution, SOLUTION_PATH)

    if GENERATE_GRAPHICS:
        generate_graphics(
            instance,
            graphic_path=GRAPHIC_PATH,
            max_robot_a_count=MAX_ROBOT_A_COUNT,
            robot_a_count_step=ROBOT_A_COUNT_STEP,
            optimal_solution=optimal_solution,
        )


if __name__ == "__main__":
    main()
