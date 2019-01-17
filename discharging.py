# generate rules
# generate parts = (K, a, b)
# write branching that separates part into two parts
# apply rules to get bound on Np(W) for all W that match part
# output resulting list of graphs that may or may not reduce, output as a set?

# optionally might need to use symmetry, might need to hash the graph or something?
# They did something for symmetry in the robertson paper

import networkx as nx
from collections import namedtuple

Part = namedtuple('Part', ['K', 'a', 'b'])

inf = float('Inf')


def generate_trivial_part(degree_of_w):
    trivial_part_graph = nx.Graph()
    spokes = list(range(2, degree_of_w + 2))
    hats = list(range(degree_of_w + 2, (2 * degree_of_w) + 2))
    trivial_part_graph.add_edges_from([(1, s) for s in spokes])
    trivial_part_graph.add_edges_from([(s, s + 1) for s in spokes[:-1]])
    trivial_part_graph.add_edges_from([(spokes[0], spokes[-1])])
    trivial_part_graph.add_edges_from([(s, hats[i]) for i, s in enumerate(spokes)])
    trivial_part_graph.add_edges_from([(s, hats[i-1]) for i, s in enumerate(spokes)])

    a = {1: degree_of_w}
    a.update({s: inf for s in spokes})
    a.update({h: inf for h in hats})

    b = {1: degree_of_w}
    b.update({s: 5 for s in spokes})
    b.update({h: 2 for h in hats})

    return Part(K=trivial_part_graph, a=a, b=b)

