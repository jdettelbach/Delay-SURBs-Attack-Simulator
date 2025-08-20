import pathlib

import simpy
import sys
import os
import numpy
from collections import defaultdict
import logging
import argparse

from simulation_modes import test_mode, attacker_mode
import experiments.Settings


def main(args):
    if args.exp_dir:
        experiment_dir = args.exp_dir
    else:
        print("Please provide filename to load the experiment settings from.")
        return

    if args.config_file:
        config_file = args.config_file
    else:
        print("Please provide the name of the config file")
        return

    if not os.path.exists(experiment_dir + '/logs'):
        os.makedirs(experiment_dir + '/logs')
    else:
        try:
            os.remove(experiment_dir + '/logs/packet_log.csv')
            os.remove(experiment_dir + '/logs/message_log.csv')
            os.remove(experiment_dir + '/logs/last_mix_entropy.csv')
        except:
            pass

    mode = args.mode
    if mode == "transcript":
        print("Running simulator in a transcript mode")
        print("Experimental configuration uploaded from path: %s" % config_file)

        email_data_file = "Data/data_email/slices/slice_1.csv" #"Data/data_email/data_riseup_email.csv"
        transcript_mode.run(data_file=email_data_file, conf_file = config_file, exp_dir=experiment_dir)

    elif mode == "synthetic":
        print("Running simulator with syntetic traffic")
        print("Experimental configuration uploaded from path: %s" % config_file)

        # pass This needs an update

    elif mode == "anon":
        print("Running simulator in a anonymous stats mode")
        print("Experimental configuration uploaded from path: %s" % config_file)

        # pass This needs update

    elif mode == "test":
        print("Running simulator in a test mode")
        print("Experimental configuration uploaded from path: %s" % config_file)
        test_mode.run(exp_dir=experiment_dir, conf_file=config_file)

    elif mode == "diff_test":
        print("Running simulator in a diff test mode")
        print("Experimental configuration uploaded from path: %s" % config_file)

        diff_config_test.run(log_dir= os.path.join(experiment_dir,conf["logging"]["dir"]), number_of_clients=conf["clients"]["number"], ticks=conf["phases"]["execution"],
            layers=conf["network"]["layers"],
            MixNodes_per_layer=conf["network"]["layer_size"], num_in=conf["network"]["prov_in"],
            num_out=conf["network"]["prov_out"], num_runs=conf["runs"],
            startup=conf["phases"]["burnin"], cooldown=conf["phases"]["cooldown"],
            perc_corrupt=conf["mixnodes"]["perc_corrupt"], verbose=conf["debug"]["mixnodes_verbose"])

    elif mode == "attacker":
        print("Running simulator in attacker mode")
        print("Experimental configuration uploaded from path: %s" % config_file)
        attacker_mode.run(exp_dir=experiment_dir, conf_file=config_file)

    else:
        print("Mode is not recognised")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-mode", default="test", help="The mode in which we want to run the simulator: transcript, synthetic traces, anon or test")
    parser.add_argument("-exp_dir", default="measurements", help="The directory of the experiment directory")
    parser.add_argument("-config_file", default="test_config.json", help="The file of the experiment configuration", type=pathlib.Path)
    parser.add_argument("-test", help="Test flag")
    parser.add_argument("-datadir", help="The directory to the database file")
    parser.add_argument("-hour", help="Take only one hour slice of dataset")
    parser.add_argument("-12hour", help="Take only the 12hour slice of dataset")
    parser.add_argument("-minute", help="Take a minute slice of dataset")
    parser.add_argument("-day", help="Take a day slice of dataset")

    main(parser.parse_args())
