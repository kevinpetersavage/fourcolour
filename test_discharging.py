import networkx as nx
from nose.tools import assert_equals, assert_true, assert_false
from discharging import generate_trivial_part, Part, inf

degree_three_trivial_part = nx.Graph()
degree_three_trivial_part.add_edges_from(
    [(1, 2), (1, 3), (1, 4),  # spokes
     (2, 3), (3, 4), (4, 2),  # rim
     (2, 5), (3, 5), (3, 6), (4, 6), (4, 7), (2, 7)  # hats
     ])
edge_of_inifinte_region = list(range(2, 7+1))


def test_generating_trivial_parts():
    part = generate_trivial_part(3)

    expected = Part(
        K=degree_three_trivial_part,
        a={1: 3, 2: inf, 3: inf, 4: inf,
           5: inf, 6: inf, 7: inf},  # not sure about the last 3 which are hats. Do we need to define this at all?
        b={1: 3, 2: 5, 3: 5, 4: 5, 5: 2, 6: 2, 7: 2}   # again not sure about the last 3
    )

    assert_equals(part.a, expected.a)
    assert_equals(part.b, expected.b)
    assert_true(nx.is_isomorphic(part.K, expected.K))
