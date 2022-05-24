import argparse
import os

from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.utils import align_utils as utils
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.algo.evaluation.replay_fitness import algorithm as evaluator
from timeit import default_timer as timer
import pickle

SEQUENCE_DELIMITER = " >> "


def init_alignment_params(log, model, threads=1):
    """
    Sets common parameters for alignment computation using unit cost function.
    """
    alignment_params = {}

    utils.STD_MODEL_LOG_MOVE_COST = 1
    utils.STD_TAU_COST = 0
    utils.STD_SYNC_COST = 0

    alignment_params[alignments.Parameters.CORES] = threads
    return alignment_params


def construct_alignments(log, net, im, fm, threads=1):
    alignment_params = init_alignment_params(log, net, threads)
    if alignment_params[alignments.Parameters.CORES] == 1:
        return alignments.apply_log(log, net, im, fm, parameters=alignment_params)
    else:
        return alignments.apply_multiprocessing(log, net, im, fm,
                                                parameters=alignment_params)


def serialize_alignments(log_file, net_files, threads=1):
    """
    Constructs the alignments for log_file w.r.t model_file. The resulting alignment are written into file maintining
    the same order as the traces in the original log file
    """
    log = xes_importer.apply(log_file)
    for i in (range(len(net_files))):
        print()
        net_file = net_files[i]
        print(net_file)
        net, im, fm = pnml_importer.apply(net_file)
        alignment_params = init_alignment_params(log, net, threads)

        start = timer()
        aligned_traces = construct_alignments(log, net, im, fm, threads)
        end = timer()

        print(evaluator.evaluate(aligned_traces, variant=evaluator.Variants.ALIGNMENT_BASED))
        print("Elapsed time: " + str(end - start))

        pickle.dump(aligned_traces,
                    open(os.path.splitext(log_file)[0] + "_" + os.path.splitext(net_file)[0] + ".align", "wb"))


def deserialize_alignments(file_name):
    """
    Loads and returns alignments from a serialized file
    """
    aligned_traces = pickle.load(open(file_name, "rb"))
    return aligned_traces


def get_event_sequence(trace):
    """
    Returns a String representation of the event sequence of a trace
    """
    event_representation = ""
    for event in trace:
        event_representation = event_representation + SEQUENCE_DELIMITER + event["concept:name"]
    return event_representation


def zip_log_and_alignments(log, alignments):
    """
    Returns a dict, consisting of string representations of the log traces as keys, and their alignments as values.
    """
    trace_keys = []
    for trace in log:
        trace_keys.append(get_event_sequence(trace))

    assert (len(trace_keys) == len(log))
    return dict(zip(trace_keys, alignments))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", help="the name of the .xes-log")
    parser.add_argument("-nets", help="the names of the .pnml-models for which to construct alignments", nargs='+',
                        required=True)
    parser.add_argument("--threads", help="number of threads to use", type=int)
    args = parser.parse_args()

    serialize_alignments(args.logs, args.nets, args.threads)
