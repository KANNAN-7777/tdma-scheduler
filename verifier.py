def verify_schedule(conflict_graph, schedule):
    conflicts = []

    for node1, node2 in conflict_graph.edges:
        if schedule[node1] == schedule[node2]:
            conflicts.append((node1, node2))

    if conflicts:
        return False, conflicts

    return True, []