import argparse
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter


def discover_IM(log_file, noise_threshold=0.2, verbose=False):

    log = xes_importer.apply(log_file)
    model, im, fm = pm4py.discover_petri_net_inductive(log, noise_threshold)

    pnml_exporter.apply(model, im, str(log_file)+"_" + str(noise_threshold) + "_" + ".pnml", final_marking=fm)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file", help="the name of the xes-log from which to discover")
    parser.add_argument("noise_threshold", help="the noise threshold to use for discovery", type=float)
    parser.add_argument("--verbose", help="increase verbosity of output", action="store_true")
    args = parser.parse_args()

    discover_IM(args.log_file, args.noise_threshold, args.verbose)
