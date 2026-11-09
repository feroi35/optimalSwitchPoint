from math import ceil


def evaluate_sol(instance: dict, robot_a_count: int, verbose: bool = False) -> dict:
    """Evaluate the objective terms for a proposed number of robot A units."""
    specific_part_count = instance["specific_part_count"]
    purchase_lot_counts = []
    remaining_part_quantities = []

    for part_index in range(specific_part_count):
        required_quantity = (
            instance["robot_a_part_quantities"][part_index] * robot_a_count
        )
        initial_inventory = instance["initial_part_inventory"][part_index]
        purchase_lot_size = instance["part_purchase_lot_sizes"][part_index]

        purchase_lot_count = max(
            0,
            ceil((required_quantity - initial_inventory) / purchase_lot_size)
        )

        remaining_quantity = (
            initial_inventory
            + purchase_lot_count * purchase_lot_size
            - required_quantity
        )
        purchase_lot_counts.append(purchase_lot_count)
        remaining_part_quantities.append(remaining_quantity)

    production_cost_difference = robot_a_count * (
        instance["robot_a_unit_cost"] - instance["robot_b_unit_cost"]
    )
    remaining_parts_cost = sum(
        remaining_part_quantities[part_index] * instance["part_unit_costs"][part_index]
        for part_index in range(specific_part_count)
    )
    lot_quantity_term = sum(
        purchase_lot_counts[part_index]
        * instance["part_unit_costs"][part_index]
        * instance["part_purchase_lot_sizes"][part_index]
        for part_index in range(specific_part_count)
    )
    total_cost = (
        production_cost_difference + remaining_parts_cost + lot_quantity_term
    )

    solution = {
        "purchase_lot_counts": purchase_lot_counts,
        "remaining_part_quantities": remaining_part_quantities,
        "production_cost_difference": production_cost_difference,
        "remaining_parts_cost": remaining_parts_cost,
        "lot_quantity_term": lot_quantity_term,
        "total_cost": total_cost,
    }

    if verbose:
        print(f"Evaluation for {robot_a_count} robot(s) A")
        for part_index in range(specific_part_count):
            print(
                f"Part {part_index + 1}: "
                f"required={instance['robot_a_part_quantities'][part_index] * robot_a_count}, "
                f"initial stock={instance['initial_part_inventory'][part_index]}, "
                f"purchase lots={purchase_lot_counts[part_index]}, "
                f"remaining={remaining_part_quantities[part_index]}"
            )
        print(f"Production cost difference n_robots A * (B - A): {production_cost_difference:.2f}")
        print(f"Remaining parts cost: {remaining_parts_cost:.2f}")
        print(f"Lot-quantity cost: {lot_quantity_term:.2f}")
        print(f"Total cost: {total_cost:.2f}")

    return solution
