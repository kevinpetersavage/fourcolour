# Done: generate rules
# Done: generate trivial part = (K, a, b)
# write branching that separates part into multiple parts
# Done: apply rules to get bound on Np(W) for all W that match part
# write function to apply rules to prove > N case and determine N
# output resulting list of graphs that may or may not reduce, output as a set? Count rejected?

# optionally might need to use symmetry, might need to hash the graph or something?
# They did something for symmetry in the robertson paper
import networkx as nx
import intervals as i
from random import randint, choice

interval = 'interval'


def generate_random_triangular_rule(max_term_in_rule: int):
    rule = nx.complete_graph(3)
    for node_index in range(0, 3):
        rule.node[node_index][interval] = generate_random_interval(max_term_in_rule)
    return rule


def generate_random_interval(max_term_in_rule: int):
    start = randint(5, max_term_in_rule)
    possible_ends = list(range(start, max_term_in_rule)) + [i.inf]
    end = choice(possible_ends)
    return i.closed(start, end)


def generate_trivial_part(degree: int):
    part = nx.star_graph(degree)
    part.node[0][interval] = i.closed(degree, degree)
    for node_index in range(1, degree + 1):
        part.node[node_index][interval] = i.closed(5, i.inf)
    return part


def check_apply_unambiguously(part: nx.Graph, rule: nx.Graph):
    return all(check_apply_unambiguously_at_rotation(part, rule, rotation) for rotation in range(0, part.degree(0)))


def check_apply_unambiguously_at_rotation(part: nx.Graph, rule: nx.Graph, rotation: int):
    return (not rule_applies_some_of_the_time(part, rule, rotation)) or \
           (not rule_does_not_apply_some_of_the_time(part, rule, rotation))


def rotate_index(part: nx.Graph, rotation: int, index: int):
    if index == 0:
        return 0
    else:
        return ((index - 1 + rotation) % part.degree(0)) + 1


def rule_applies_some_of_the_time(part: nx.Graph, rule: nx.Graph, rotation: int):
    return all(part.node[rotate_index(part, rotation, index)][interval].intersection(rule.node[index][interval])
               for index in range(0, 3))


def rule_does_not_apply_some_of_the_time(part: nx.Graph, rule: nx.Graph, rotation: int):
    return any(not rule.node[index][interval].contains(part.node[rotate_index(part, rotation, index)][interval])
               for index in range(0, 3))


def rule_applies_all_of_the_time(part: nx.Graph, rule: nx.Graph, rotation: int):
    return any(rule.node[index][interval].contains(part.node[rotate_index(part, rotation, index)][interval])
               for index in range(0, 3))


def rule_np_w_contribution(part: nx.Graph, rule: nx.Graph):
    gamma_out = calculate_gamma_change(part, rule)
    rotated_rule = rotate_rule(rule)
    gamma_in = calculate_gamma_change(part, rotated_rule)
    return gamma_in - gamma_out


def rotate_rule(rule):
    rotated_rule = nx.relabel_nodes(rule, {i: (i + 1) % 3 for i in rule.nodes}, copy=True)
    return rotated_rule


def calculate_gamma_change(part: nx.Graph, rule: nx.Graph):
    return sum(rule_applies_all_of_the_time(part, rule, rotation) for rotation in range(0, part.degree(0)))


def np_w(part: nx.Graph, rules: [nx.Graph]):
    return 10 * (6 - part.degree(0)) + sum(rule_np_w_contribution(part, rule) for rule in rules)


def branch(part, rule):
    so_far = [part]
    for rotation in range(0, part.degree(0)):
        for b in branch_for_rotation(part, rule, rotation):
            if not graph_in(so_far, b):
                so_far.append(b)
                yield b

    rotated_rule = rotate_rule(rule)
    for rotation in range(0, part.degree(0)):
        for b in branch_for_rotation(part, rotated_rule, rotation):
            if not graph_in(so_far, b):
                so_far.append(b)
                yield b


def branch_for_rotation(part, rule, rotation):
    first_part_interval = part.node[rotate_index(part, rotation, 1)][interval]
    second_part_interval = part.node[rotate_index(part, rotation, 2)][interval]
    first_rule_interval = rule.node[1][interval]
    second_rule_interval = rule.node[2][interval]

    first_split = (
        convert_integer_open_to_closed(first_rule_interval.intersection(first_part_interval)),
        convert_integer_open_to_closed(first_rule_interval.complement().intersection(first_part_interval))
    )
    second_split = (
        convert_integer_open_to_closed(second_rule_interval.intersection(second_part_interval)),
        convert_integer_open_to_closed(second_rule_interval.complement().intersection(second_part_interval))
    )

    all_splits_possible = [(a, b) for a in first_split for b in second_split if not a.is_empty() and not b.is_empty()]

    for a, b in all_splits_possible:
        copy_of_part = part.copy()
        copy_of_part.node[rotate_index(part, rotation, 1)][interval] = a
        copy_of_part.node[rotate_index(part, rotation, 2)][interval] = b
        yield copy_of_part


def convert_integer_open_to_closed(possibly_open: i.Interval):
    if possibly_open.left == i.OPEN:
        possibly_open = possibly_open.replace(left=i.CLOSED, lower=lambda x: x + 1)
    if possibly_open.right == i.OPEN and possibly_open.upper != i.inf:
        possibly_open = possibly_open.replace(right=i.CLOSED, upper=lambda x: x - 1)
    return possibly_open


def graph_in(branched, expected_part):
    return any(graph_equals(expected_part, b) for b in branched)


def graph_equals(g1, g2):
    return nx.is_isomorphic(g1, g2, node_match=lambda x, y: x == y)

