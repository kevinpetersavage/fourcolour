import itertools
import networkx as nx


colours = ['r', 'g', 'y', 'b']


class Configuration:
    def __init__(self, graph, edge_of_infinite_region, gamma):
        self.graph = graph
        self.edge_of_infinite_region = edge_of_infinite_region
        self.gamma = gamma
        self.free_completion = self.create_free_completion()
        self.completable = set()
        self.stack = list()

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
        colouring_lists = (tuple(colouring) for colouring in colourings)
        return (c for c in colouring_lists if self.is_valid_as_ring_colouring(c))

    def create_graph_colourings(self):
        graph_colourings = itertools.product(colours, repeat=len(self.graph.nodes()))
        return (tuple(colouring) for colouring in graph_colourings if self.colouring_is_valid(colouring, self.graph))

    @staticmethod
    def colouring_is_valid(colouring, graph):
        for i, colour in enumerate(colouring):
            for neighbor in graph.neighbors(i + 1):
                if colouring[neighbor - 1] == colour:
                    return False
        return True

    def ring_colouring_has_direct_completion(self, ring_colouring, graph_colourings):
        if ring_colouring in self.completable:
            return True
        directly_recolours = any(self.colouring_is_valid(graph_colouring + ring_colouring, self.free_completion)
                                 for graph_colouring in graph_colourings)
        if directly_recolours:
            self.completable.add(ring_colouring)
        return directly_recolours

    def all_ring_colourings_are_completable(self, ring_colourings, graph_colourings):
        return all(self.ring_colouring_has_completion_after_possible_recolouring(ring_colouring, graph_colourings)
                   for ring_colouring in ring_colourings)

    def ring_colouring_has_completion_after_possible_recolouring(self, ring_colouring, graph_colourings):
        print(self.stack)
        if ring_colouring in self.stack:
            return False
        self.stack.append(ring_colouring)
        if ring_colouring in self.completable:
            self.stack.pop()
            return True
        if self.ring_colouring_has_direct_completion(ring_colouring, graph_colourings):
            self.stack.pop()
            return True
        else:
            power_set_of_indexes = self.powerset(range(0, len(ring_colouring)))
            possible_chains = (indexes for indexes in power_set_of_indexes
                               if 0 < len({ring_colouring[i] for i in indexes}) < 3)
            chains_recolour = (self.check_possible_chain(possible_chain, ring_colouring, graph_colourings)
                               for possible_chain in possible_chains)
            all_chains_recolour = all(chains_recolour)
            if all_chains_recolour:
                self.completable.add(ring_colouring)
            self.stack.pop()
            return all_chains_recolour

    def check_possible_chain(self, possible_chain, ring_colouring, graph_colourings):
        recolourings = list(self.valid_ring_recolourings(ring_colouring, possible_chain))
        if recolourings:
            for recolouring in recolourings:
                if self.ring_colouring_has_direct_completion(recolouring, graph_colourings):
                    return True
            for recolouring in recolourings:
                if self.ring_colouring_has_completion_after_possible_recolouring(recolouring, graph_colourings):
                    return True
            print('no recolourings were valid for {} with chain {}'.format(ring_colouring, possible_chain))
            return False  # means we didn't manage to recolour
        return False  # means the chain is not actually a valid chain

    def valid_ring_recolourings(self, ring_colouring, possible_chain):
        used_colours = list({ring_colouring[index] for index in possible_chain})
        if len(used_colours) == 1:
            mappings = [{used_colours[0]: colour} for colour in colours if colour != used_colours[0]]
        elif len(used_colours) == 2:
            mappings = [{used_colours[0]: used_colours[1], used_colours[1]: used_colours[0]}]
        else:
            raise RuntimeError("should have already checked this")

        for mapping in mappings:
            recolouring = [self.apply_mapping(colour, i, possible_chain, mapping)
                           for i, colour in enumerate(ring_colouring)]
            if self.is_valid_as_ring_colouring(recolouring):
                yield tuple(recolouring)

    @staticmethod
    def apply_mapping(colour, index, possible_chain, mapping):
        if index in possible_chain:
            return mapping[colour]
        else:
            return colour

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
        all_completable = self.all_ring_colourings_are_completable(ring_colourings, graph_colourings)
        print(self.completable)
        return all_completable
