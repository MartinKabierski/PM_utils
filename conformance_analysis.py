import argparse
from math import sqrt

import matplotlib.pyplot as plt
from pm4py.algo.evaluation.replay_fitness import algorithm as evaluator

from construct_alignments import deserialize_alignments


def get_log_conformance(alignments):
    return evaluator.evaluate(alignments, variant=evaluator.Variants.ALIGNMENT_BASED)


def plot_fitness_distribution(traces):
    fitness_values = [x["fitness"] for x in traces]
    #print(fitness_values)
    plt.hist(fitness_values, 100)
    plt.show()


def estimate_standard_error(alignments):
    sample_sizes = [100, 200, 300, 400, 500]
    #get log fitness
    fitness = get_log_conformance(alignments)
    #get standard deviation
    trace_fitness = [x["log_fitness"] for x in alignments]
    stddev = sqrt(1/len(alignments) * sum([pow(fitness - x, 2) for x in trace_fitness]))

    for n in sample_sizes:
        std_err = stddev / sqrt(n)
        print (f"Standard Error for sample size {n}: {std_err}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("alignments", help="the name of the .xes-log")
    args = parser.parse_args()

    alignments = deserialize_alignments(args.alignments)

    print(get_log_conformance(alignments)+"\n")
    plot_fitness_distribution(alignments)
    estimate_standard_error(alignments)