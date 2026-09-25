import math
import networkx as nx


def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def build_communication_graph(nodes, communication_range=500):
    graph = nx.Graph()

    for node in nodes:
        graph.add_node(node)

    node_names = list(nodes.keys())

    for i in range(len(node_names)):
        for j in range(i + 1, len(node_names)):
            node1 = node_names[i]
            node2 = node_names[j]

            distance = calculate_distance(
                nodes[node1],
                nodes[node2]
            )

            if distance <= communication_range:
                graph.add_edge(
                    node1,
                    node2,
                    distance=distance
                )

    return graph