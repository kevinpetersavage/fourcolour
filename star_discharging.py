# Done: generate rules
# Done: generate trivial part = (K, a, b)
# write branching that separates part into multiple parts
# apply rules to get bound on Np(W) for all W that match part
# write function to apply rules to prove > N case and determine N
# output resulting list of graphs that may or may not reduce, output as a set?

# optionally might need to use symmetry, might need to hash the graph or something?
# They did something for symmetry in the robertson paper
import networkx as nx
import intervals as i
from random import randint, choice

interval = 'interval'
gamma = 'gamma'


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
    part.node[0][gamma] = 10 * (6 - degree)
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


def apply_rule(part: nx.Graph, rule: nx.Graph):
    gamma_out = calculate_gamma_change(part, rule)
    rotated_rule = nx.relabel_nodes(rule, {i: (i+1) % 3 for i in rule.nodes}, copy=True)
    gamma_in = calculate_gamma_change(part, rotated_rule)
    copy = part.copy()
    copy.node[0][gamma] = part.node[0][gamma] - gamma_out + gamma_in
    return copy


def calculate_gamma_change(part, rule):
    return sum(rule_applies_all_of_the_time(part, rule, rotation) for rotation in range(0, part.degree(0)))
