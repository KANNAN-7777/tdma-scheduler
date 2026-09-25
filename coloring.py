import networkx as nx


def build_conflict_graph(communication_graph):
    conflict_graph = nx.Graph()

    conflict_graph.add_nodes_from(communication_graph.nodes)

    nodes = list(communication_graph.nodes)

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            node1 = nodes[i]
            node2 = nodes[j]

            try:
                path_length = nx.shortest_path_length(
                    communication_graph,
                    node1,
                    node2
                )

                if path_length <= 2:
                    conflict_graph.add_edge(node1, node2)

            except nx.NetworkXNoPath:
                pass

    return conflict_graph


def color_graph(conflict_graph):
    strategies = [
        "largest_first",
        "smallest_last",
        "saturation_largest_first"
    ]

    best_coloring = None
    best_slot_count = float("inf")

    for strategy in strategies:

        if strategy == "saturation_largest_first":
            coloring = nx.coloring.greedy_color(
                conflict_graph,
                strategy=strategy,
                interchange=False
            )
        else:
            coloring = nx.coloring.greedy_color(
                conflict_graph,
                strategy=strategy,
                interchange=True
            )

        slot_count = len(set(coloring.values()))

        print(
            f"Strategy: {strategy:<25} "
            f"Slots: {slot_count}"
        )

        if slot_count < best_slot_count:
            best_slot_count = slot_count
            best_coloring = coloring

    print(
        f"\nSelected coloring uses "
        f"{best_slot_count} slots."
    )

    return best_coloring


def get_available_slots(node, conflict_graph, coloring):
    used_slots = set()

    for neighbor in conflict_graph.neighbors(node):
        if neighbor in coloring:
            used_slots.add(coloring[neighbor])

    available_slots = []

    total_slots = len(set(coloring.values()))

    for slot in range(total_slots):
        if slot not in used_slots:
            available_slots.append(slot)

    return available_slots

def try_improve_coloring(conflict_graph, coloring):
    improved_coloring = coloring.copy()

    nodes = list(improved_coloring.keys())

    for node in nodes:
        current_slot = improved_coloring[node]

        available_slots = get_available_slots(
            node,
            conflict_graph,
            improved_coloring
        )

        for slot in available_slots:

            if slot < current_slot:
                improved_coloring[node] = slot
                break

    return improved_coloring

def try_reduce_slots(conflict_graph, coloring):
    optimized_coloring = coloring.copy()

    slots = sorted(set(optimized_coloring.values()), reverse=True)

    for slot_to_remove in slots:
        nodes_in_slot = [
            node
            for node, slot in optimized_coloring.items()
            if slot == slot_to_remove
        ]

        temp_coloring = optimized_coloring.copy()

        success = True

        for node in nodes_in_slot:
            available_slots = get_available_slots(
                node,
                conflict_graph,
                temp_coloring
            )

            available_slots = [
                slot
                for slot in available_slots
                if slot != slot_to_remove
            ]

            if not available_slots:
                success = False
                break

            temp_coloring[node] = min(available_slots)

        if success:
            optimized_coloring = temp_coloring

    return optimized_coloring

def try_reduce_slots(conflict_graph, coloring):
    optimized_coloring = coloring.copy()

    slots = sorted(
        set(optimized_coloring.values()),
        reverse=True
    )

    for slot_to_remove in slots:
        nodes_in_slot = [
            node
            for node, slot in optimized_coloring.items()
            if slot == slot_to_remove
        ]

        temp_coloring = optimized_coloring.copy()

        success = True

        for node in nodes_in_slot:
            available_slots = get_available_slots(
                node,
                conflict_graph,
                temp_coloring
            )

            available_slots = [
                slot
                for slot in available_slots
                if slot != slot_to_remove
            ]

            if not available_slots:
                success = False
                break

            temp_coloring[node] = min(available_slots)

        if success:
            optimized_coloring = temp_coloring

    return optimized_coloring