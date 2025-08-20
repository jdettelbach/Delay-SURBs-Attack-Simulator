import math
import random
import numpy
import pandas as pd

from classes.Node import Node
from classes.Client import Client
from classes.Utilities import log_dropped_packet
import experiments.Settings
import os


class Network(object):

    def __init__(self, env, type, conf, loggers):
        self.env = env
        self.conf = conf
        self.topology = {}
        self.type = type
        self.loggers = loggers

        data = pd.read_csv('pingProbabilityDistribution.csv')
        data.amount = data.amount / sum(data.amount)
        self.delayDist = data

        self.clients = [Client(env, conf, self, loggers = loggers, label=0) for i in range(int(conf["clients"]["number"]))]

        if type == "p2p":
            self.peers = [Node(env, conf, self, id="Peer%s" % i, loggers = loggers) for i in range(int(conf["clients"]["number"]))]
            self.topology["Type"] = "p2p"
            self.init_p2p()
        else:
            if type == "cascade":
                self.topology["Type"] = "cascade"
                self.mixnodes = [Node(env, conf, self, id="M%s" % i, loggers = loggers) for i in range(self.conf["network"]["cascade"]["cascade_len"])]
                self.init_cascade()
            elif type == "stratified":
                self.topology["Type"] = "stratified"
                num_mixnodes = int(self.conf["network"]["stratified"]["layers"]) * int(self.conf["network"]["stratified"]["layer_size"])
                self.mixnodes = [Node(env, conf, self, id="M%s" % i, loggers = loggers) for i in range(num_mixnodes)]
                self.init_stratified()
            elif type == "multi_cascade":
                self.topology["Type"] = "multi_cascade"
                num_mixnodes = int(self.conf["network"]["multi_cascade"]["cascade_len"]) * int(self.conf["network"]["multi_cascade"]["num_cascades"])
                self.mixnodes = [Node(env, conf, self, id="M%s" % i, loggers = loggers) for i in range(num_mixnodes)]
                self.init_multi_cascade()
            else:
                raise Exception("Didn't recognize the network type")
        print("Current topology: ", self.topology["Type"])
        # print("Batching yes/no: ", self.conf["mixnodes"]["batch"])

    def init_p2p(self):
        self.topology["peers"] = self.peers.copy()

    def init_cascade(self):
        self.topology["cascade"] = self.mixnodes.copy()

    def init_multi_cascade(self):
        num_cascades = int(self.conf["network"]["multi_cascade"]["num_cascades"])
        cascade_len = int(self.conf["network"]["multi_cascade"]["cascade_len"])
        ind_cascades = [self.mixnodes[x:x+cascade_len] for x in range(0, len(self.mixnodes), cascade_len)]
        self.topology["cascades"] = ind_cascades

    def init_stratified(self):
        num_layers = int(self.conf["network"]["stratified"]["layers"])
        mixes_per_layer = int(self.conf["network"]["stratified"]["layer_size"])

        layers = [self.mixnodes[i * mixes_per_layer:(i + 1) * mixes_per_layer] for i in range(0, num_layers)]
        self.topology["Layers"] =  layers

        for i in range(0, num_layers - 1):
            for j in range(0, mixes_per_layer):
                self.topology[self.mixnodes[i * mixes_per_layer + j]] = layers[i + 1]

    def select_random_route(self):
        tmp_route = []

        if self.topology["Type"] == "stratified":
            tmp_route = [random.choice(L) for L in self.topology["Layers"]]
        elif self.topology["Type"] == "cascade":
            tmp_route = self.topology["cascade"].copy()
        elif self.topology["Type"] == "multi_cascade":
            tmp_route = random.choice(self.topology["cascades"])
        elif self.topology["Type"] == "p2p":
            length = self.conf["network"]["p2p"]["path_length"]
            tmp_route = random.sample(self.peers, length)

        return tmp_route


    def forward_packet(self, packet, packet_logger):
        ''' Function responsible for forwarding the packet, i.e.,
            checking what is the next hop of the packet and triggering the
            process_packet function by a particular node.

            Keyword arguments:
            packet - the packet to be forwarded.
        '''
        # If needed, some network delay can be added.
        if self.conf["network"]["delay"]:
            netDelay = random.choices(self.delayDist.delay, self.delayDist.amount)[0]
            if netDelay < 0:
                log_dropped_packet(packet, packet_logger, self.env.now)
                yield self.env.timeout(0)
            else:
                yield self.env.timeout(netDelay)
                next_node = packet.route[packet.current_node + 1]
                packet.current_node += 1
                self.env.process(next_node.process_packet(packet))
        else:
            yield self.env.timeout(0)
            next_node = packet.route[packet.current_node + 1]
            packet.current_node += 1
            self.env.process(next_node.process_packet(packet))

        packet.time_m_rec.append(self.env.now)




    def __repr__(self):
        return "topology: " + str(self.topology)
