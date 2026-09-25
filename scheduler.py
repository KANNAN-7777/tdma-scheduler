def create_schedule(coloring):
    schedule = {}

    for node, color in coloring.items():
        schedule[node] = color + 1

    return schedule


def create_slot_matrix(schedule):
    nodes = list(schedule.keys())
    number_of_slots = max(schedule.values())

    matrix = {}

    for slot in range(1, number_of_slots + 1):
        matrix[slot] = {}

        for node in nodes:
            if schedule[node] == slot:
                matrix[slot][node] = 1
            else:
                matrix[slot][node] = 0

    return matrix


def print_schedule(schedule):
    print("\nNode → Slot Mapping")

    for node in sorted(schedule):
        print(f"{node} → Slot {schedule[node]}")


def print_matrix(matrix):
    nodes = list(next(iter(matrix.values())).keys())

    print("\nSlot × Node Matrix")

    print(f"{'Slot':<8}", end="")

    for node in nodes:
        print(f"{node:<10}", end="")

    print()

    for slot, values in matrix.items():
        print(f"{slot:<8}", end="")

        for node in nodes:
            print(f"{values[node]:<10}", end="")

        print()


def print_spatial_reuse(schedule):
    slots = {}

    for node, slot in schedule.items():
        if slot not in slots:
            slots[slot] = []

        slots[slot].append(node)

    print("\nSpatial Reuse")

    reused_slots = 0

    for slot in sorted(slots):
        nodes = slots[slot]

        if len(nodes) > 1:
            reused_slots += 1
            print(
                f"Slot {slot}: "
                f"{', '.join(sorted(nodes))}"
            )

    print(
        f"\nSlots reused by multiple nodes: "
        f"{reused_slots}"
    )


def print_summary(
    nodes,
    communication_graph,
    conflict_graph,
    schedule,
    matrix,
    valid,
    communication_range
):
    total_nodes = len(nodes)
    communication_links = communication_graph.number_of_edges()
    conflict_links = conflict_graph.number_of_edges()
    total_slots = max(schedule.values())

    reused_slots = 0
    max_nodes_per_slot = 0

    for slot, values in matrix.items():
        node_count = sum(values.values())

        if node_count > 1:
            reused_slots += 1

        if node_count > max_nodes_per_slot:
            max_nodes_per_slot = node_count

    print("\n========== SCHEDULE SUMMARY ==========")
    print(f"Nodes                  : {total_nodes}")
    print(f"Communication Range    : {communication_range} m")
    print(f"1-Hop Communication   : {communication_links}")
    print(f"1-Hop / 2-Hop Conflicts: {conflict_links}")
    print(f"Total TDMA Slots      : {total_slots}")
    print(f"Reused Slots           : {reused_slots}")
    print(f"Maximum Nodes / Slot   : {max_nodes_per_slot}")

    if valid:
        print("Verification            : PASS")
    else:
        print("Verification            : FAIL")

    print("=======================================")