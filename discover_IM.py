import argparse
import os

import pm4py
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer

from tqdm import tqdm


def discover_inductive(log_file, noise_thresholds):
    """
    Discovers a petri net model from log using the Inductive Miner with specified noise threshold. The resulting model
    is written into file
    """
    log = xes_importer.apply(log_file)
    for i in tqdm(range(len(noise_thresholds)), desc=" > Discovering Models", disable=False):
        current = noise_thresholds[i]
        model, im, fm = pm4py.discover_petri_net_inductive(log, current)
        pnml_exporter.apply(model,
                            im,
                            str(os.path.splitext(log_file)[0])+"_n" + str(current) + ".pnml",
                            final_marking=fm)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file", help="the name of the xes-log from which to discover")
    parser.add_argument("-noise", help="list of noise values to use", nargs='+', type=float, required=True)

    args = parser.parse_args()

    discover_inductive(args.log_file, args.noise)