import argparse
import json

from graph_builder import build_communication_graph

from coloring import (
    build_conflict_graph,
    color_graph,
    get_available_slots,
    try_improve_coloring,
    try_reduce_slots
)

from scheduler import (
    create_schedule,
    create_slot_matrix,
    print_schedule,
    print_matrix,
    print_spatial_reuse,
    print_summary
)

from verifier import verify_schedule


def load_nodes(input_file):
    with open(input_file, "r") as file:
        return json.load(file)


def print_communication_graph(graph):
    print("\n1-Hop Communication Links")

    for node1, node2, data in graph.edges(data=True):
        distance = data["distance"]

        print(
            f"{node1} <-> {node2} "
            f"({distance:.2f} m)"
        )


def print_conflict_graph(graph):
    print("\n1-Hop / 2-Hop Conflict Links")

    for node1, node2 in graph.edges:
        print(f"{node1} <-> {node2}")


def main():
    parser = argparse.ArgumentParser(
        description="TDMA Distance-2 Graph Coloring Scheduler"
    )

    parser.add_argument(
        "--input",
        default="sample_input.json",
        help="Path to JSON coordinate file"
    )

    parser.add_argument(
        "--range",
        type=float,
        default=500,
        help="Communication range in meters"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show communication and conflict graph details"
    )

    args = parser.parse_args()

    nodes = load_nodes(args.input)

    print("========================================")
    print(" TDMA SCHEDULE PLANNER AND OPTIMIZER")
    print("========================================")

    print(f"\nNumber of nodes: {len(nodes)}")
    print(f"Communication range: {args.range} meters")

    communication_graph = build_communication_graph(
        nodes,
        args.range
    )

    if args.verbose:
        print_communication_graph(
            communication_graph
        )

    conflict_graph = build_conflict_graph(
        communication_graph
    )

    if args.verbose:
        print_conflict_graph(
            conflict_graph
        )

    coloring = color_graph(
        conflict_graph
    )

    print("\nAvailable Slots Test")

    test_node = next(iter(nodes))

    available_slots = get_available_slots(
        test_node,
        conflict_graph,
        coloring
    )

    print(
        f"{test_node} can use existing slots: "
        f"{[slot + 1 for slot in available_slots]}"
    )

    improved_coloring = try_improve_coloring(
        conflict_graph,
        coloring
    )

    optimized_coloring = try_reduce_slots(
        conflict_graph,
        improved_coloring
    )

    print("\nColoring Improvement Test")

    for node in sorted(improved_coloring):
        print(
            f"{node}: "
            f"Slot {improved_coloring[node] + 1}"
        )

    original_slots = len(
        set(coloring.values())
    )

    improved_slots = len(
        set(improved_coloring.values())
    )

    optimized_slots = len(
        set(optimized_coloring.values())
    )

    print(
        f"\nOriginal Slots: {original_slots}"
    )

    print(
        f"Improved Slots: {improved_slots}"
    )

    print(
        f"Optimized Slots: {optimized_slots}"
    )

    schedule = create_schedule(
        optimized_coloring
    )

    matrix = create_slot_matrix(
        schedule
    )

    print_schedule(
        schedule
    )

    print_matrix(
        matrix
    )

    print_spatial_reuse(
        schedule
    )

    valid, conflicts = verify_schedule(
        conflict_graph,
        schedule
    )

    print("\nSchedule Verification")

    if valid:
        print(
            "PASS: No 1-hop or 2-hop conflicts detected."
        )

    else:
        print(
            "FAIL: Conflicts detected."
        )

        for node1, node2 in conflicts:
            print(
                f"{node1} <-> {node2} "
                f"share Slot {schedule[node1]}"
            )

    print_summary(
        nodes,
        communication_graph,
        conflict_graph,
        schedule,
        matrix,
        valid,
        args.range
    )

    print(
        f"\nTotal TDMA Slots: "
        f"{max(schedule.values())}"
    )


if __name__ == "__main__":
    main()