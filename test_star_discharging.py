from star_discharging import *
from nose.tools import assert_equals, assert_true, assert_false
import intervals as i


def test_creating_rule():
    rule = generate_random_triangular_rule(7)
    ranges = [node[interval] for node in rule.node.values()]

    assert_equals(len(ranges), 3)
    assert_true(all(r.lower <= 7 for r in ranges))
    assert_true(all(r.lower >= 5 for r in ranges))
    assert_true(all(r.upper >= 5 for r in ranges))


def test_generate_trivial_part():
    part = generate_trivial_part(5)

    assert_equals(part.node[0][interval].lower, 5)
    assert_equals(part.node[0][interval].upper, 5)

    for node_index in range(1, 6):
        assert_equals(part.node[node_index][interval].lower, 5)
        assert_equals(part.node[node_index][interval].upper, i.inf)

    assert_equals(part.node[0][gamma], 10)  # calculated as (6 - 5) * 10


def test_check_rules_where_complete_match():
    part = generate_trivial_part(5)
    rule = nx.complete_graph(3)
    for node_index in range(0, 3):
        rule.node[node_index][interval] = i.closed(5, i.inf)

    assert_true(check_apply_unambiguously(part, rule))


def test_check_rules_where_incomplete_match():
    part = generate_trivial_part(5)
    rule = nx.complete_graph(3)
    for node_index in range(0, 3):
        rule.node[node_index][interval] = i.closed(5, i.inf)

    rule.node[2][interval] = i.closed(6, 7)

    assert_false(check_apply_unambiguously(part, rule))


def test_apply_rule():
    part = generate_trivial_part(5)
    rule = nx.complete_graph(3)
    for node_index in range(0, 3):
        rule.node[node_index][interval] = i.closed(5, i.inf)

    assert_equals(calculate_gamma_change(part, rule), 5)
    assert_equals(apply_rule(part, rule).node[0][gamma], 10)  # this is because all the in and out should cancel
