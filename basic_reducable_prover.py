import itertools

import networkx as nx

colours = ['r', 'g', 'y', 'b']

log_count = 0


class Configuration:
    def __init__(self, graph, edge_of_infinite_region, gamma):
        self.graph = graph
        self.edge_of_infinite_region = edge_of_infinite_region
        self.gamma = gamma
        self.free_completion = self.create_free_completion()
        print("contructed free completion")
        self.ring_colourings = list(self.create_ring_colourings())
        print("contructed ring colourings of size", len(self.ring_colourings))
        self.graph_colourings = list(self.create_graph_colourings())
        print("contructed graph colourings", len(self.graph_colourings))

    def ring_size(self):
        nodes = [v for v in self.graph.nodes() if v in self.edge_of_infinite_region]
        ring_size = sum(self.gamma(v) - self.graph.degree(v) - 1 for v in nodes)
        print("ring size was", ring_size)
        return ring_size

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
        ring_size = self.ring_size()
        colourings = [[c] for c in colours]
        new_colourings = []
        for i in range(0, ring_size - 1):
            for colouring in colourings:
                for colour in colours:
                    if colour != colouring[-1]:
                        new_colouring = colouring.copy()
                        new_colouring.append(colour)
                        new_colourings.append(new_colouring)
            colourings = new_colourings
            new_colourings = []
        return [c for c in colourings if self.is_valid_as_ring_colouring(c)]

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
        global log_count
        log_count += 1
        if log_count % 1000000 == 0:
            print("checking", colouring, log_count)
        for i, colour in enumerate(colouring):
            if colouring[i - 1] == colour:
                return False
        return True

    def is_completable_after_single_recolour(self, colouring):
        graph_colourings = list(self.create_graph_colourings())
        for i, colour in enumerate(colouring):
            possible_chains = (chain for chain in self.powerset(range(0, len(colouring)))
                               if i in chain and len(set(colouring[k] for k in chain)) <= 2)

            if all(self.exists_a_completable_recolouring_for_chain(chain, colour, colouring, graph_colourings)
                    for chain in possible_chains):
                return True
        return False

    def exists_a_completable_recolouring_for_chain(self, chain, colour, colouring, graph_colourings):
        other_colours_in_chain = list(set(colouring[k] for k in chain if colouring[k] != colour))
        if not other_colours_in_chain:
            other_colours_in_chain = [c for c in colours if c != colour]
        recolourings = ([self.swap(c, colour, other_colour) for c in colouring]
                        for other_colour in other_colours_in_chain)
        valid_as_ring_colourings = (r for r in recolourings if self.is_valid_as_ring_colouring(r))
        any(self.ring_colouring_has_completion(r, graph_colourings) for r in valid_as_ring_colourings)

    @staticmethod
    def powerset(indexes):
        return itertools.chain.from_iterable(itertools.combinations(indexes, r) for r in range(len(indexes) + 1))

    @staticmethod
    def swap(c, from_colour, to_colour):
        if c == from_colour:
            return to_colour
        if c == to_colour:
            return from_colour
        return c

    def is_reducible(self):
        un_completables = self.ring_colourings_not_having_a_completion_using(
            self.ring_colourings, self.graph_colourings
        )
        return not all(self.is_completable_after_single_recolour(un_completable) for un_completable in un_completables)
