import networkx as nx
from nose.tools import assert_equals, assert_true, assert_false
from basic_reducable_prover import Configuration

gk = nx.Graph()
gk.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)])
edge_of_inifinte_region = [1, 2, 3, 4]


def gamma(node):
    return 5


diamond = Configuration(gk, edge_of_inifinte_region, gamma)


def test_birkhoff_diamond_has_ring_size_6():
    assert_equals(diamond.ring_size(), 6)


def test_birkhoff_diamond_generates_ring():
    assert_equals(
        set(diamond.create_ring().edges()),
        {(5, 10), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10)}
    )


def test_birkhoff_diamond_generates_free_completion():
    completion = diamond.create_free_completion()
    assert_equals(set(completion.nodes()), set(range(1, 11)))
    
    for node in diamond.graph.nodes():
        assert_equals(completion.degree[node], diamond.gamma(node))
        
    for node in diamond.create_ring().nodes():
        assert_true(completion.degree[node] in [3, 4])
        

def test_birkhoff_diamond_generates_ring_colourings():
    colourings = list(diamond.create_ring_colourings())

    assert_true(['b', 'y', 'g', 'y', 'g', 'y'] in colourings)
    assert_true(['r', 'y', 'r', 'y', 'b', 'r'] not in colourings)
    assert_equals(len(colourings), 108)


def test_some_colouring_do_not_complete_for_the_birkhoff_diamond():
    assert_true(list(diamond.ring_colourings_not_having_a_completion()))


def test_kemp_chain_alteration_of_non_extendable_ring_colouring_swaps_colours_or_reverses_one():
    recolourings = diamond.recolour_using_one_kemp_chain_step(colouring=['r', 'y', 'g', 'b', 'y', 'b'], start=0)

    assert_equals(
        [['g', 'y', 'r', 'b', 'y', 'b'], ['g', 'y', 'g', 'b', 'y', 'b']],
        recolourings
    )


def test_kemp_chain_alteration_of_non_extendable_ring_colouring_does_not_generate_invalid_ring_colourings():
    recolourings = diamond.recolour_using_one_kemp_chain_step(colouring=['r', 'y', 'b', 'g', 'y', 'b'], start=0)

    assert_equals(
        [],
        recolourings
    )


def test_birkhoff_is_reducable():
    assert_true(diamond.is_reducible())
