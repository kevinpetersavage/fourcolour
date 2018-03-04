import networkx as nx


VERTS = 27	# max number of vertices in a free completion + 1
DEG = 13	# max degree of a vertex in a free completion + 1
EDGES = 62	# max number of edges in a free completion + 1    
MAXRING = 14  # max ring size


def main():
    
    # what is this? it is something to do with signed matches
    simatchnumber = [0, 0, 1, 3, 10, 30, 95, 301, 980, 3228, 10797, 36487, 124542, 428506, 1485003]

    power = [3**i for i in range(-1,16)]
    ncodes = (power[MAXRING] + 1) / 2	# max number of codes. What are codes?
    nchar = simatchnumber[MAXRING] / 8 + 2;
    
    with open("unavoidable.conf") as fp:
        lines = [l.strip() for l in fp.readlines()]
        graphs = []
        while lines:
            graph, lines = readSingleConf(lines)
            graphs.append(graph)
        print("read {} graphs from config".format(len(graphs)))
        
        for graph in graphs:
            number_edges(graph)
        
        example = graphs[0].free_completion[1][2]
        print("numbered the graphs, the first looks like this {}".format(example))
        
    

class ConfigGraph:
    def __init__(self, name, num_vertices, ring_size, cardinality_C, cardinality_Cprime, X, free_completion, coordinates):
        self.name = name
        self.num_vertices = num_vertices
        self.ring_size = ring_size
        self.cardinality_C = cardinality_C
        self.cardinality_Cprime = cardinality_Cprime
        self.X = X
        self.free_completion = free_completion
        self.coordinates = coordinates

    def __str__(self):
        return str([self.name, self.num_vertices, self.ring_size, self.X, list(self.free_completion.edges), self.coordinates])


def number_edges(graph: ConfigGraph):
    """ Numbers edges from 1 up, so that each edge has as many later edges in
     * triangles as possible; the ring edges are first.  """
    
    h = nx.Graph()
    h.add_edges_from(graph.free_completion.edges)
        
    edge_number = 1
    while h.edges():
        max_edge = max(h.edges(), key = lambda edge: len(set(h[edge[0]]).intersection(h[edge[1]])))
        graph.free_completion[max_edge[0]][max_edge[1]]["edge_number"] = edge_number
        h.remove_edge(max_edge[0], max_edge[1])
        edge_number += 1


def readSingleConf(lines):
    name = lines[0]
    num_vertices, ring_size, cardinality_C, cardinality_Cprime = map(int, lines[1].split())
    x_data = lines[2].split()[1:]
    X = [map(int, x_data[i:i+2]) for i in range(0, len(x_data), 2)]
    
    G = nx.Graph()
    adjacency_lines = lines[3:3 + num_vertices]
    split_lines = [line.split() for line in adjacency_lines]
    edges = [(int(line[0]),int(y)) for line in split_lines for y in line[2:]]
    G.add_edges_from(edges)
    
    i = 0
    coordinates = []
    while 3 + num_vertices + i < len(lines) and lines[3 + num_vertices + i]:
        line = lines[3 + num_vertices + i]
        coordinates.extend([int(l) for l in line.split()])
        i += 1
    
    return ConfigGraph(
        name, 
        num_vertices, 
        ring_size, 
        cardinality_C, 
        cardinality_Cprime,
        X, 
        G,
        coordinates), lines[4 + num_vertices + i:]

if __name__ == "__main__":
    main()