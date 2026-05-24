INF = 10**9


GRAPH = {
    0: {1: 1, 2: 3, 3: 7},
    1: {0: 1, 2: 1},
    2: {0: 3, 1: 1, 3: 2},
    3: {0: 7, 2: 2},
}


UPDATED_GRAPH = {
    0: {1: 1, 2: 3, 3: 7},
    1: {0: 1, 2: 1},
    2: {0: 3, 1: 1, 3: 10},
    3: {0: 7, 2: 10},
}


class Node:
    def __init__(self, name, neighbors, all_nodes):
        self.name = name
        self.neighbors = neighbors
        self.distance = {node: INF for node in all_nodes}
        self.next_hop = {node: None for node in all_nodes}

        self.distance[name] = 0
        self.next_hop[name] = name

        for neighbor, cost in neighbors.items():
            self.distance[neighbor] = cost
            self.next_hop[neighbor] = neighbor

    def update(self, neighbor_name, neighbor_distance):
        return bellmanFordCalcDistance(self, neighbor_name, neighbor_distance)

    def print_table(self):
        print(f"Node {self.name}")
        print("dest  cost  next")

        for destination in sorted(self.distance):
            cost = self.distance[destination]
            next_hop = self.next_hop[destination]
            print(f"{destination:>4}  {cost:>4}  {next_hop}")

        print()


def bellmanFordCalcDistance(node, neighbor_name, neighbor_distance):
    changed = False
    cost_to_neighbor = node.neighbors[neighbor_name]

    for destination, neighbor_cost in neighbor_distance.items():
        new_cost = cost_to_neighbor + neighbor_cost

        if new_cost < node.distance[destination]:
            node.distance[destination] = new_cost
            node.next_hop[destination] = neighbor_name
            changed = True

    return changed


def run_distance_vector(graph):
    nodes = {
        name: Node(name, neighbors, graph.keys())
        for name, neighbors in graph.items()
    }

    round_number = 1

    while True:
        changed = False
        print(f"Round {round_number}")

        for node in nodes.values():
            for neighbor_name in node.neighbors:
                neighbor = nodes[neighbor_name]
                changed |= node.update(neighbor_name, neighbor.distance)

        for node in nodes.values():
            node.print_table()

        if not changed:
            break

        round_number += 1


print("Initial network")
run_distance_vector(GRAPH)

print("After changing link cost 2-3 from 2 to 10")
run_distance_vector(UPDATED_GRAPH)
