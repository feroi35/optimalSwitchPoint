import pyomo.environ as pyo


def create_model(instance: dict) -> pyo.ConcreteModel:
    """
    Create a MILP for the robot A production count and part purchase lots.

    Parameters:
    instance (dict): A dictionary containing the instance data for the optimization model.

    Returns:
    pyo.ConcreteModel: A Pyomo ConcreteModel object representing the optimization model.
    """
    model = pyo.ConcreteModel()
    part_count = instance["specific_part_count"]
    model.parts = pyo.Set(initialize=range(part_count), ordered=True)

    model.robot_a_count = pyo.Var(domain=pyo.NonNegativeIntegers)
    model.purchase_lot_counts = pyo.Var(
        model.parts,
        domain=pyo.NonNegativeIntegers,
    )

    model.remaining_part_quantities = pyo.Expression(
        model.parts,
        rule=lambda model, part: (
            instance["initial_part_inventory"][part]
            + model.purchase_lot_counts[part]
            * instance["part_purchase_lot_sizes"][part]
            - model.robot_a_count * instance["robot_a_part_quantities"][part]
        ),
    )
    model.part_availability = pyo.Constraint(
        model.parts,
        rule=lambda model, part: model.remaining_part_quantities[part] >= 0,
    )

    model.production_cost_difference = pyo.Expression(
        expr=model.robot_a_count
        * (instance["robot_a_unit_cost"] - instance["robot_b_unit_cost"])
    )
    model.remaining_parts_cost = pyo.Expression(
        expr=sum(
            model.remaining_part_quantities[part]
            * instance["part_unit_costs"][part]
            for part in model.parts
        )
    )
    model.purchase_lot_cost = pyo.Expression(
        expr=sum(
            model.purchase_lot_counts[part]
            * instance["part_purchase_lot_sizes"][part]
            * instance["part_unit_costs"][part]
            for part in model.parts
        )
    )
    model.total_cost = pyo.Objective(
        expr=pyo.quicksum(
            [
                model.production_cost_difference,
                model.remaining_parts_cost,
                model.purchase_lot_cost,
            ]
        ),
        sense=pyo.minimize,
    )

    return model


def solve_model(model: pyo.ConcreteModel) -> dict:
    """
    Solve the model and return its optimal decision and cost values.

    Parameters:
    model (pyo.ConcreteModel): A Pyomo ConcreteModel object representing the optimization model.

    Returns:
    dict: Optimal robot count, purchase lots, remaining parts, and cost components.
    """
    solver = pyo.SolverFactory("highs")
    results = solver.solve(model, tee=True)
    if not pyo.check_optimal_termination(results):
        raise RuntimeError(
            f"HiGHS did not find an optimal solution: "
            f"{results.solver.termination_condition}"
        )

    solution = {
        "robot_a_count": int(round(pyo.value(model.robot_a_count))),
        "purchase_lot_counts": [
            int(round(pyo.value(model.purchase_lot_counts[part])))
            for part in model.parts
        ],
        "remaining_part_quantities": [
            int(round(pyo.value(model.remaining_part_quantities[part])))
            for part in model.parts
        ],
        "production_cost_difference": pyo.value(model.production_cost_difference),
        "remaining_parts_cost": pyo.value(model.remaining_parts_cost),
        "lot_quantity_term": pyo.value(model.purchase_lot_cost),
        "total_cost": pyo.value(model.total_cost),
    }

    print(f"\nOptimal number of robot A: {solution['robot_a_count']}")
    for part, lot_count in enumerate(solution["purchase_lot_counts"]):
        print(
            f"Part {part + 1}: {lot_count} purchase lot(s), "
            f"{solution['remaining_part_quantities'][part]} part(s) remaining"
        )
    print(f"Production cost difference: {solution['production_cost_difference']:.2f}")
    print(f"Remaining parts cost: {solution['remaining_parts_cost']:.2f}")
    print(f"Purchase lot cost: {solution['lot_quantity_term']:.2f}")
    print(f"Optimal total cost: {solution['total_cost']:.2f}")

    return solution
