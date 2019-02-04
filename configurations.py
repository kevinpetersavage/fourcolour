import networkx as nx
import itertools

colours = ['r','g','y','b']


class Configuration:
    def __init__(self, graph, edge_of_inifinte_region, gamma):
        self.graph = graph
        self.edge_of_inifinte_region = edge_of_inifinte_region
        self.gamma = gamma
        
    def verify_gamma(self):
        for v in self.graph.nodes():
            number_of_components = self.components_without_v(v)
            gamma = self.gamma(v)
            degree = self.graph.degree[v]
            
            if number_of_components > 2: 
                return False
            if number_of_components == 2 and gamma != degree + 2:
                return False
            if v not in self.edge_of_inifinte_region:
                if gamma != degree:
                    return False
            elif gamma <= degree:
                return False                
            if gamma < 5:
                return False
        return self.ring_size() >= 2

    def ring_size(self):
        nodes = [v for v in self.graph.nodes() 
            if self.components_without_v(v) == 1 and v in self.edge_of_inifinte_region]
        return sum(self.gamma(v) - self.graph.degree[v] -1 for v in nodes)
        
    def components_without_v(self, v):
        nodes = self.graph.nodes()
        nodes_without_v = [n for n in nodes if n != v]
        subgraph = self.graph.subgraph(nodes_without_v)
        return len(list(nx.connected_components(subgraph)))
        
    def create_ring(self):
        ring_size = self.ring_size()
        max_node = max(self.graph.nodes())
        ring = nx.Graph()
        edges = ((x, x+1) for x in range(max_node+1, max_node + ring_size))
        ring.add_edges_from(edges)
        ring.add_edge(max_node+1, max_node + ring_size)
        return ring
        
    def create_free_completion(self):
        free_completion = nx.Graph()
        ring = self.create_ring()
        
        free_completion.add_edges_from(self.graph.edges())
        free_completion.add_edges_from(ring.edges())
        
        current_position = 0
        for node in self.edge_of_inifinte_region:
            number_of_edges_to_add = self.gamma(node) - free_completion.degree[node]
            rotated = self.rotate(ring.nodes(), current_position)
            for ring_node in rotated[:number_of_edges_to_add]:
                free_completion.add_edge(node, ring_node)
            current_position = current_position + number_of_edges_to_add - 1
        
        return free_completion

    def rotate(self, nodes, n):
        l = list(nodes)
        return l[n:] + l[:n]
        
    def create_ring_colourings(self):
        ring = self.create_ring()                    
        colourings = itertools.product(colours, repeat=self.ring_size())
        def is_valid(colouring):
            for i, colour in enumerate(colouring):
                if colouring[i-1] == colour:
                    return False
            return True
        return (c for c in colourings if is_valid(c))

    def create_ring_colourings_that_extend(self):
        ring_colourings = list(self.create_ring_colourings())
        free_completion = self.create_free_completion()
        
        graph_colourings = itertools.product(colours, repeat=len(self.graph.nodes()))
        def is_valid(colouring, graph):
            for i, colour in enumerate(colouring):
                for adj in graph.adj[i+1]:
                    if colouring[adj-1] == colour:
                        return False
            return True
        
        valid_graph_colourings = [c for c in graph_colourings if is_valid(c, self.graph)]
        completion_colourings = itertools.product(valid_graph_colourings, ring_colourings)
        return set(d for c, d in completion_colourings if is_valid(c+d, free_completion))
        
    def create_all_signed_paths(self):
        graph_nodes = max(self.graph.nodes())
        ring = self.create_ring()
        ring_nodes = range(graph_nodes + 1, graph_nodes + self.ring_size() + 1)
        partition_lists = self.partition(list(ring_nodes))
        partitions = [[tuple(p) for p in l] for l in partition_lists if self.connected(l, ring)]
        for p in partitions:
            s_functions = self.create_s_functions(p)
            for s_function in s_functions:
                yield (p, s_function)
        
    def connected(self, partition, ring):
        for p in partition:
            if not nx.is_connected(ring.subgraph(p)):
                return False
        return True
        
    def create_s_functions(self, partition):
        outputs = itertools.product([0,1], repeat=len(partition))
        for output in outputs:
            d = dict(zip(partition, output))
            yield lambda p: d[p]
        
    def partition(self, collection):
        if len(collection) == 1:
            yield [ collection ]
            return
    
        first = collection[0]
        for smaller in self.partition(collection[1:]):
            # insert `first` in each of the subpartition's subsets
            for n, subset in enumerate(smaller):
                yield smaller[:n] + [[ first ] + subset]  + smaller[n+1:]
            # put `first` in its own subset 
            yield [ [ first ] ] + smaller

    def create_signed_paths_for_non_extending(self):
        extending = set(self.create_ring_colourings_that_extend())
        non_extending = set(self.create_ring_colourings()) - set(self.create_ring_colourings_that_extend())
        signed_paths = self.create_all_signed_paths()
        
        fitted = [signed_path for signed_path in signed_paths 
            if self.fits_at_least_one(signed_path, non_extending)]
        return (signed_path for signed_path in fitted 
            if not self.fits_at_least_one(signed_path, extending))
        
        
    def fits_at_least_one(self, signed_path, colourings):
        for colouring in colourings:
            if self.fits(colouring, signed_path):
                return True
        return False
        
    def fits(self, colouring, signed_path):
        partition, s = signed_path
        possible_colour_partitions = set([tuple(sorted(list(set(p)))) for p in partition])
        colour_partitions = [p for p in possible_colour_partitions if len(p) > 1]

        if not colour_partitions:
            return True
        if len(colour_partitions) > 2:
            return False
        if any(len(c)>2 for c in colour_partitions):
            return False
        return True
        
    def is_d_reducable(self):
        if not list(self.create_signed_paths_for_non_extending()):
            return True
        else:
            raise Exception("We don't yet look at s when checking signed paths so this might not be correct")