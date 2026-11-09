from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import seaborn as sns

from .evaluate import evaluate_sol


def generate_graphics(
    instance: dict,
    graphic_path: Path,
    max_robot_a_count: int,
    robot_a_count_step: int,
    optimal_solution: Optional[dict] = None,
) -> None:
    """Plot evaluation costs over a configured range of robot A counts."""
    if robot_a_count_step <= 0:
        raise ValueError("robot_a_count_step must be a positive integer.")
    if max_robot_a_count < 0:
        raise ValueError("max_robot_a_count must be non-negative.")

    max_count = max_robot_a_count
    if optimal_solution is not None:
        max_count = max(max_count, optimal_solution["robot_a_count"])

    robot_a_counts = list(range(0, max_count + 1, robot_a_count_step))
    if optimal_solution is not None:
        optimal_robot_a_count = optimal_solution["robot_a_count"]
        if optimal_robot_a_count not in robot_a_counts:
            robot_a_counts.append(optimal_robot_a_count)
            robot_a_counts.sort()

    evaluations = [
        evaluate_sol(instance, robot_a_count)
        for robot_a_count in robot_a_counts
    ]
    production_cost_differences = [
        result["production_cost_difference"] for result in evaluations
    ]
    remaining_parts_costs = [
        result["remaining_parts_cost"] for result in evaluations
    ]
    purchase_lot_costs = [result["lot_quantity_term"] for result in evaluations]
    total_costs = [result["total_cost"] for result in evaluations]

    if optimal_solution is None:
        minimum_index = min(
            range(len(total_costs)),
            key=total_costs.__getitem__,
        )
        optimal_robot_a_count = robot_a_counts[minimum_index]
        minimum_total_cost = total_costs[minimum_index]
    else:
        optimal_robot_a_count = optimal_solution["robot_a_count"]
        minimum_total_cost = optimal_solution["total_cost"]

    sns.set_theme(style="whitegrid")
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.plot(
        robot_a_counts,
        production_cost_differences,
        label="Production cost difference",
    )
    axis.plot(robot_a_counts, remaining_parts_costs, label="Remaining parts cost")
    axis.plot(robot_a_counts, purchase_lot_costs, label="Purchase lot cost")
    axis.plot(robot_a_counts, total_costs, label="Total cost", linewidth=2.5)
    axis.scatter(
        optimal_robot_a_count,
        minimum_total_cost,
        color="red",
        marker="*",
        s=180,
        zorder=3,
        label="Minimum total cost",
    )
    axis.annotate(
        f"Minimum: {optimal_robot_a_count} robot(s) A\n"
        f"Cost: {minimum_total_cost:.2f}",
        xy=(optimal_robot_a_count, minimum_total_cost),
        xytext=(12, -30),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "red"},
    )
    axis.set(
        title="Evaluation cost by number of robot A units",
        xlabel="Number of robot A units",
        ylabel="Cost",
    )
    axis.legend()
    figure.tight_layout()

    graphic_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(graphic_path)
    print(f"Graphic saved to {graphic_path}")
    plt.show()
