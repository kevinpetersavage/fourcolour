import copy
import itertools
from math import floor

import networkx as nx

colours = ['r', 'g', 'y', 'b']


class Configuration:
    def __init__(self, graph, edge_of_infinite_region, gamma):
        self.graph = graph
        self.edge_of_infinite_region = edge_of_infinite_region
        self.gamma = gamma
        self.free_completion = self.create_free_completion()

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
        #  assumes that the ring is flattened
        ring_size = self.ring_size()
        colourings = itertools.product(colours, repeat=ring_size)
        colouring_lists = (list(colouring) for colouring in colourings)
        return (c for c in colouring_lists if self.is_valid_as_ring_colouring(c))

    def create_graph_colourings(self):
        graph_colourings = itertools.product(colours, repeat=len(self.graph.nodes()))
        return (list(colouring) for colouring in graph_colourings if self.colouring_is_valid(colouring, self.graph))

    @staticmethod
    def colouring_is_valid(colouring, graph):
        for i, colour in enumerate(colouring):
            for neighbor in graph.neighbors(i + 1):
                if colouring[neighbor - 1] == colour:
                    return False
        return True

    def ring_colourings_not_having_a_completion(self):
        ring_colourings = list(self.create_ring_colourings())
        graph_colourings = list(self.create_graph_colourings())
        return self.ring_colourings_not_having_a_completion_using(ring_colourings, graph_colourings)

    def ring_colouring_has_completion(self, ring_colouring, graph_colourings):
        return any(self.colouring_is_valid(graph_colouring + ring_colouring, self.free_completion)
                   for graph_colouring in graph_colourings)

    def ring_colourings_not_having_a_completion_using(self, ring_colourings, graph_colourings):
        for ring_colouring in ring_colourings:
            if not self.ring_colouring_has_completion(ring_colouring, graph_colourings):
                yield ring_colouring

    @staticmethod
    def is_valid_as_ring_colouring(colouring):
        for i, colour in enumerate(colouring):
            if colouring[i - 1] == colour:
                return False
        return True

    def recolour(self, colouring):
        colour_pairings = set([tuple(sorted([a, b])) for a in colours for b in colours if a != b])
        for colour_pairing in colour_pairings:
            indexes = [i for i, c in enumerate(colouring) if c in colour_pairing]
            power_set_of_indexes = self.powerset(indexes)
            for set_of_indexes in power_set_of_indexes:
                if set_of_indexes:
                    yield [self.map_colour(colour, colour_pairing, set_of_indexes, i) for i, colour in
                           enumerate(colouring)]

    @staticmethod
    def powerset(indexes):
        return itertools.chain.from_iterable(itertools.combinations(indexes, r) for r in range(len(indexes) + 1))

    @staticmethod
    def map_colour(colour, pairing, indexes, i):
        if i in indexes and colour in pairing:
            index = pairing.index(colour)
            return pairing[index - 1]
        else:
            return colour

    def is_reducible(self):
        ring_colourings = list(self.create_ring_colourings())
        graph_colourings = list(self.create_graph_colourings())
        un_completable = list(self.ring_colourings_not_having_a_completion_using(ring_colourings, graph_colourings))
        recolourings = [recoloured for colouring in un_completable for recoloured in self.recolour(colouring)]

        still_uncompleteable = list(self.ring_colourings_not_having_a_completion_using(recolourings, graph_colourings))

        print(still_uncompleteable)
        return not still_uncompleteable
