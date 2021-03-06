import networkx as nx
from nose.tools import assert_equals, assert_true

from basic_reducable_prover import Configuration

gk = nx.Graph()
gk.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)])
edge_of_inifinte_region = [0, 1, 2, 3]


def gamma(node):
    return 5


diamond = Configuration(gk, edge_of_inifinte_region, gamma)


def test_birkhoff_diamond_has_ring_size_6():
    assert_equals(diamond.ring_size(), 6)


def test_birkhoff_diamond_generates_ring():
    assert_equals(
        set(diamond.create_ring().edges()),
        {(4, 9), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)}
    )


def test_birkhoff_diamond_generates_free_completion():
    completion = diamond.create_free_completion()
    assert_equals(set(completion.nodes()), set(range(0, 10)))

    for node in diamond.graph.nodes():
        assert_equals(completion.degree[node], diamond.gamma(node))

    for node in diamond.create_ring().nodes():
        assert_true(completion.degree[node] in [3, 4])


def test_birkhoff_diamond_generates_ring_colourings():
    colourings = list(diamond.create_ring_colourings())

    assert_true(['b', 'g', 'y', 'r', 'g', 'y'] in colourings)
    assert_true(['r', 'y', 'r', 'y', 'b', 'r'] not in colourings)
    assert_equals(len(colourings), 183)


def test_some_colouring_do_not_complete_for_the_birkhoff_diamond():
    assert_true(list(diamond.ring_colourings_not_having_a_completion()))


def test_birkhoff_is_reducable():
    assert_true(diamond.is_reducible())
