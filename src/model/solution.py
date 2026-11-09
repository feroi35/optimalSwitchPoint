import json
from math import isclose
from pathlib import Path

from .evaluate import evaluate_sol


def verify_solution(instance: dict, optimal_solution: dict) -> None:
    """Compare a MILP solution with direct evaluation at its robot count."""
    evaluated_solution = evaluate_sol(
        instance,
        optimal_solution["robot_a_count"],
        verbose=True,
    )

    exact_keys = ("purchase_lot_counts", "remaining_part_quantities")
    for key in exact_keys:
        if optimal_solution[key] != evaluated_solution[key]:
            raise RuntimeError(
                f"Solution mismatch for {key}: MILP={optimal_solution[key]}, "
                f"evaluation={evaluated_solution[key]}"
            )

    numeric_keys = (
        "production_cost_difference",
        "remaining_parts_cost",
        "lot_quantity_term",
        "total_cost",
    )
    for key in numeric_keys:
        if not isclose(
            optimal_solution[key],
            evaluated_solution[key],
            rel_tol=1e-9,
            abs_tol=1e-6,
        ):
            raise RuntimeError(
                f"Solution mismatch for {key}: MILP={optimal_solution[key]}, "
                f"evaluation={evaluated_solution[key]}"
            )

    print("MILP solution matches evaluate_sol.")


def save_solution(solution: dict, filename: Path) -> None:
    """Save a solution as JSON, rounding floating-point values to two decimals."""
    output_solution = {
        key: round(value, 2) if isinstance(value, float) else value
        for key, value in solution.items()
    }
    filename.parent.mkdir(parents=True, exist_ok=True)
    with filename.open("w", encoding="utf-8") as solution_file:
        json.dump(output_solution, solution_file, indent=4)
        solution_file.write("\n")
    print(f"Solution saved to {filename}")
