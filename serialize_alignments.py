import argparse
import os

from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.utils import align_utils as utils
from pm4py.objects.petri_net.importer import importer as pnml_importer
import pickle
import pm4py

SEQUENCE_DELIMITER = " >> "


class ConstantList:
    """
    Implements a list that returns the same value for each index (e.g., value)
    """

    def __init__(self, value):
        self.value = value

    def __getitem__(self, item):
        return self.value


def init_alignment_params(log, model, threads):
    """
    Sets common parameters for alignment computation using unit cost function.
    """
    alignment_params = {}
    model_cost_function = dict()
    sync_cost_function = dict()
    for t in model.transitions:
        if t.label is not None:
            model_cost_function[t] = 1
            sync_cost_function[t] = 0
        else:
            model_cost_function[t] = 0

    # dirty dirty hack to set a global cost for log-moces
    utils.STD_MODEL_LOG_MOVE_COST = 1
    # Set cost for each log-only-move to 1, does not work with current normalization any more
    # trace_cost_function = ConstantList(1)

    alignment_params[alignments.Parameters.PARAM_MODEL_COST_FUNCTION] = model_cost_function
    alignment_params[alignments.Parameters.PARAM_SYNC_COST_FUNCTION] = sync_cost_function
    # alignment_params[alignments.Parameters.PARAM_TRACE_COST_FUNCTION] = trace_cost_function
    alignment_params[alignments.Parameters.CORES] = threads

    return alignment_params


def get_event_sequence(trace):
    """
    Returns a String representation of the event sequence of a trace
    """
    event_representation = ""
    for event in trace:
        event_representation = event_representation + SEQUENCE_DELIMITER + event["concept:name"]
    return event_representation


def serialize_alignments(log_file, net_files, threads=1):
    """
    Constructs the alignments for log_file w.r.t model_file. The resulting alignment are written into file maintining
    the same order as the traces in the original log file
    """
    log = xes_importer.apply(log_file)

    for i in (range(len(net_files))):
        net_file = net_files[i]
        print(net_file)
        net, im, fm = pnml_importer.apply(net_file)
        alignment_params = init_alignment_params(log, net, threads)

        if alignment_params[alignments.Parameters.CORES] == 1:
            aligned_traces = alignments.apply_log(log, net, im, fm, parameters=alignment_params)
        else:
            # simply iterate over all traces, this is a bit convoluted though
            aligned_traces = alignments.apply_multiprocessing(log, net, im, fm,
                                                              parameters=alignment_params)
        pickle.dump(aligned_traces,
                    open(os.path.splitext(log_file)[0] + "_" + os.path.splitext(net_file)[0] + ".align", "wb"))
        # pickle.dump(trace_indices, open(os.path.splitext(log_file)[0] + "_" + os.path.splitext(net_file)[0] + ".indices", "wb"))


def zip_log_and_alignments(log, aligned_traces_file, index_file):
    """
    Returns a dict, consisting of string representations of the log traces as keys, and their alignments as values.
    """
    aligned_traces = pickle.load(open(aligned_traces_file, "rb"))
    trace_keys = []
    for trace in log:
        trace_keys.append(get_event_sequence(trace))

    assert (len(trace_keys) == len(log))
    return dict(zip(trace_keys, aligned_traces))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", help="the name of the .xes-log")
    parser.add_argument("-nets", help="the names of the .pnml-models for which to construct alignments", nargs='+',
                        required=True)
    parser.add_argument("--threads", help="number of threads to use", type=int)
    args = parser.parse_args()

    serialize_alignments(args.logs, args.nets, args.threads)
