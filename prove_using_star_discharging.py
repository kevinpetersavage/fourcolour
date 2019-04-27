from star_discharging import *
from basic_reducable_prover import *
import intervals as i
from itertools import product


def generate_proof_randomly():
    rules = []
    last_counted_avoidable = 0
    last_counted_reduced = 0

    while True:
        print('not proved with', len(rules), 'rules')
        print('last_counted is', last_counted_avoidable, last_counted_reduced)
        if len(rules) == 0:
            rules = [generate_random_triangular_rule(9) for i in range(0, 10)]
        else:
            rules.append(generate_random_triangular_rule(9))
        maximum_part_degree = find_maximum_part_degree(rules)
        print('maximum degree was', maximum_part_degree)
        count_avoidable, count_reduced = check_rules_prove_theorem(rules, maximum_part_degree)
        if maximum_part_degree > 20 or count_avoidable + count_reduced < last_counted_avoidable + last_counted_reduced:
            rules = rules[:int(len(rules)/5)]

        last_counted_avoidable = max(count_avoidable, last_counted_avoidable)
        last_counted_reduced = max(count_reduced, last_counted_reduced)


def check_rules_prove_theorem(rules, maximum_part_degree):
    parts_to_check = generate_parts_to_check(maximum_part_degree, rules)
    count_reduced = 0
    count_avoidable = 0
    for part in parts_to_check:
        if np_w(part, rules) > 0:
            if not check_part_reduces(part):
                return count_avoidable, count_reduced
            count_reduced += 1
        else:
            count_avoidable += 1

    print('proved with', rules)
    exit(0)


def generate_parts_to_check(maximum_part_degree, rules):
    for d in range(5, maximum_part_degree + 1):
        part = generate_trivial_part(d)
        for part_to_check in generate_parts_to_check_from(part, rules):
            yield part_to_check


def generate_parts_to_check_from(part, rules):
    rules_that_require_branch = [rule for rule in rules if not check_apply_unambiguously(part, rule)]
    if rules_that_require_branch:
        first = rules_that_require_branch[0]
        for branched in branch(part, first):
            for unambiguous in generate_parts_to_check_from(branched, rules):
                yield unambiguous
    else:
        yield part


def create_gammas(part):
    for degree_list in product(*(interval_to_list(part.node[node_index][interval]) for node_index in sorted(part.node))):
        yield lambda x: degree_list[x]


def interval_to_list(inter):
    # presuming not infinite and closed
    return list(range(inter.lower, inter.upper + 1))


def check_part_reduces(part):
    if any(part.node[node][interval].upper == i.inf for node in part.nodes()):
        return False  # can only reduce finite things I think, is that true?

    # one part may describe many Configuration because of multiple gammas
    gammas = list(create_gammas(part))
    print('checking part reduces with', len(gammas), 'gammas')

    nodes = [v for v in part.nodes() if v in list(range(1, part.degree(0) + 1))]
    sum_of_ring_size = sum(sum(gamma(v) - part.degree(v) - 1 for v in nodes) for gamma in gammas)
    print('sum of ring size **********', sum_of_ring_size)
    if sum_of_ring_size > 15:
        return False

    result = all(Configuration(part, list(range(1, part.degree(0) + 1)), gamma).is_reducible() for gamma in gammas)
    print('checked reduction', result)
    return result


if __name__ == "__main__":
    generate_proof_randomly()
