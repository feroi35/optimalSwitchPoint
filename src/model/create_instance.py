from pathlib import Path
import numpy as np
import json


def create_instance(specific_part_count: int, seed: int = 42) -> dict:
    """
    Create an instance of the optimization model.

    Robot B is cheaper to produce than Robot A.
    But there are specific parts for robot A that are still in the inventory
    and that would be wasted if we don't produce robot A.
    So, the optimization model should consider this trade-off.
    """
    rng = np.random.default_rng(seed=seed)

    instance = {}

    # Unit production cost of each robot
    instance["robot_a_unit_cost"] = round(float(rng.uniform(600, 700)), 2)
    instance["robot_b_unit_cost"] = round(float(rng.uniform(500, 550)), 2)

    # Number of parts specific to robot A
    instance["specific_part_count"] = int(specific_part_count)

    # Parts required to build one robot A, and their unit costs
    instance["robot_a_part_quantities"] = [int(x) for x in rng.integers(5, 10, size=specific_part_count)]
    instance["part_unit_costs"] = [round(float(x), 2) for x in rng.uniform(1, 20, size=specific_part_count)]

    # Purchase lot size for each part
    instance["part_purchase_lot_sizes"] = [int(x) for x in rng.integers(100, 500, size=specific_part_count)]

    # Initial inventory of each part
    instance["initial_part_inventory"] = [int(x) for x in rng.integers(500, 2000, size=specific_part_count)]

    return instance


def save_instance(instance: dict, filename: str) -> None:
    """
    Save the instance data to a file as a .json

    Parameters:
    instance (dict): A dictionary containing the instance data for the optimization model.
    filename (str): The name of the file to save the instance data to.
    """
    with open(filename, 'w') as f:
        json.dump(instance, f, indent=4)


def read_instance(filename: Path) -> dict:
    """
    Read the instance data from a .json file.

    Parameters:
    filename (str): The name of the file to read the instance data from.

    Returns:
    dict: A dictionary containing the instance data for the optimization model.
    """
    with open(filename, 'r') as f:
        instance = json.load(f)
    return instance


def get_instance(
    create_new: bool,
    read_from_file: bool,
    save_to_file: bool,
    filename: Path,
    specific_part_count: int,
    seed: int,
) -> dict:
    """Create or read the configured instance, optionally saving it."""
    if create_new == read_from_file:
        raise ValueError("Enable exactly one of create_new or read_from_file.")

    if create_new:
        instance = create_instance(
            specific_part_count=specific_part_count,
            seed=seed,
        )
    else:
        instance = read_instance(filename)

    if save_to_file:
        filename.parent.mkdir(parents=True, exist_ok=True)
        save_instance(instance, str(filename))
        print(f"Instance saved to {filename}")

    return instance


def display_instance(instance: dict) -> None:
    """Print the instance data and the cost of robot A's specific parts."""
    print("\nInstance")
    print(f"Number of robot A-specific parts: {instance['specific_part_count']}")
    print(f"Robot A production cost: {instance['robot_a_unit_cost']:.2f}")
    print(f"Robot B production cost: {instance['robot_b_unit_cost']:.2f}")
    print("\nRobot A-specific parts:")
    print("Part | Required per A | Unit price | Initial stock | Purchase lot")

    specific_parts_cost = 0.0
    for part_index in range(instance["specific_part_count"]):
        required_quantity = instance["robot_a_part_quantities"][part_index]
        unit_price = instance["part_unit_costs"][part_index]
        specific_parts_cost += required_quantity * unit_price
        print(
            f"{part_index + 1:>4} | "
            f"{required_quantity:>14} | "
            f"{unit_price:>10.2f} | "
            f"{instance['initial_part_inventory'][part_index]:>13} | "
            f"{instance['part_purchase_lot_sizes'][part_index]:>12}"
        )

    print(f"\nSpecific parts cost per robot A: {specific_parts_cost:.2f}")
    print(f"Robot A production cost including ONLY specific parts: {specific_parts_cost:.2f}")
    print()
