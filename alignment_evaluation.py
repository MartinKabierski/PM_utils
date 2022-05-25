import argparse
from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
from pm4py.algo.evaluation.replay_fitness import algorithm as evaluator

from construct_alignments import deserialize_alignments


def plot_fitness_distribution(alignments):
    x = [x["fitness"] for x in alignments]
    plt.hist(x, 100, weights=np.zeros_like(x) + 1. / len(x))
    plt.show()


def get_log_conformance(alignments):
    return evaluator.evaluate(alignments, variant=evaluator.Variants.ALIGNMENT_BASED)


def get_variance(alignments):
    mean = get_log_conformance(alignments)["log_fitness"]
    values = [x["fitness"] for x in alignments]
    return 1/len(alignments) * sum([pow(mean - x, 2) for x in values])


def get_standard_error(alignments, n, finite_population=False):
    var = get_variance(alignments)
    return sqrt(var / n) * (1- ((n-1)/(len(alignments)-1))) if finite_population else sqrt(var / n)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("alignments", help="the name of the .xes-log")
    args = parser.parse_args()

    alignments = deserialize_alignments(args.alignments)

    log_data = get_log_conformance(alignments)
    var = get_variance(alignments)
    print(f"Evaluation:     {log_data}")
    print(f"Variance:       {var}")
    print(f"Std deviation:  {sqrt(var)}")
    print()

    print("Sample Size\tStandard Error\t\tw finite population correction")
    for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500]:
        std_err = get_standard_error(alignments, n)
        std_err_cor = get_standard_error(alignments, n, True)
        print(f"{n}:\t\t{std_err}\t{std_err_cor}")

    plot_fitness_distribution(alignments)
