import itertools

import networkx as nx


colours = ['r', 'g', 'y', 'b']


class Configuration:
    def __init__(self, graph, edge_of_infinite_region, gamma):
        self.graph = graph
        self.edge_of_infinite_region = edge_of_infinite_region
        self.gamma = gamma

    def ring_size(self):
        nodes = [v for v in self.graph.nodes() if v in self.edge_of_infinite_region]
        return sum(self.gamma(v) - self.graph.degree(v) - 1 for v in nodes)

    def create_ring(self):
        ring_size = self.ring_size()
        max_node = max(self.graph.nodes())
        ring = nx.Graph()
        edges = ((x, x + 1) for x in range(max_node + 1, max_node + ring_size))
        ring.add_edges_from(edges)
        ring.add_edge(max_node + 1, max_node + ring_size)
        return ring

    def create_free_completion(self):
        free_completion = nx.Graph()
        ring = self.create_ring()

        free_completion.add_edges_from(self.graph.edges())
        free_completion.add_edges_from(ring.edges())

        current_position = 0
        for node in self.edge_of_infinite_region:
            number_of_edges_to_add = self.gamma(node) - free_completion.degree(node)
            rotated = self.rotate(ring.nodes(), current_position)
            for ring_node in rotated[:number_of_edges_to_add]:
                free_completion.add_edge(node, ring_node)
            current_position = current_position + number_of_edges_to_add - 1

        return free_completion

    @staticmethod
    def rotate(nodes, n):
        lst = list(nodes)
        return lst[n:] + lst[:n]

    def create_ring_colourings(self):
        colourings = itertools.product(colours, repeat=self.ring_size())

        def is_valid(colouring):
            for i, colour in enumerate(colouring):
                if colouring[i - 1] == colour:
                    return False
            for i in range(1, int(len(colouring)/2)):
                if colouring[i] == colouring[-i]:
                    return False  # this puts in some extra edges meaning there are less combinations
            return True

        return (list(c) for c in colourings if is_valid(c))

    def create_graph_colourings(self):
        graph_colourings = itertools.product(colours, repeat=len(self.graph.nodes()))
        return (list(colouring) for colouring in graph_colourings if self.is_valid(colouring, self.graph))

    @staticmethod
    def is_valid(colouring, graph):
        for i, colour in enumerate(colouring):
            for neighbor in graph.neighbors(i+1):
                if colouring[neighbor] == colour:
                    return False
        return True

    def all_ring_colourings_have_a_completion(self):
        free_completion = self.create_free_completion()

        ring_colourings = list(self.create_ring_colourings())
        graph_colourings = list(self.create_graph_colourings())

        return all(
                any(
                    self.is_valid(graph_colouring + ring_colouring, free_completion)
                    for graph_colouring in graph_colourings)
                for ring_colouring in ring_colourings
        )

    def is_reducible(self):
        return self.all_ring_colourings_have_a_completion()