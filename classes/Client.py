import numpy as np
import copy
import sys
import random

from classes.Packet import Packet
from classes.Message import Message
from classes.Node import Node
from classes.Utilities import StructuredMessage, setup_logger, random_string
import experiments.Settings

class Client(Node):
    def __init__(self, env, conf, net, loggers=None, label=0, id=None, p2p=False):
        self.conf = conf

        super().__init__(env=env, conf=conf, net=net, loggers=loggers, id=id)


    def schedule_retransmits(self):
        #current_time = self.env.now
       # if current_time < self.conf["phases"]["burnin"]:
        #    yield self.env.timeout(self.conf["phases"]["burnin"]-current_time)
        print("starting retransmits at " + str(self.env.now))
        while self.env.now <= (self.conf["phases"]["burnin"]+self.conf["phases"]["execution"]+self.conf["phases"]["attack"]):
            current_time = self.env.now
            if not self.pkt_buffer_out_not_ack.empty():
                packet = self.pkt_buffer_out_not_ack.get()
                time_waited = current_time-packet.time_sent
                if time_waited < self.conf["clients"]["retransmit_timeout"]:
                    yield self.env.timeout(self.conf["clients"]["retransmit_timeout"]-time_waited)
                if packet.times_transmitted < self.conf["clients"]["max_retransmissions"] and packet.SURBs.time_delivered is None:
                    ACK = Packet.copy(packet.SURBs)
                    ACK.time_queued = None
                    packet.SURBs = ACK
                    self.add_to_buffer({packet})
            else:
                yield self.env.timeout(5)


    def schedule_message(self, message):
        #  This function is used in the transcript mode
        ''' schedule_message adds given message into the outgoing client's buffer. Before adding the message
            to the buffer the function records the time at which the message was queued.'''

        print("> Scheduled message")
        current_time = self.env.now
        message.time_queued = current_time
        for pkt in message.pkts:
            pkt.time_queued = current_time
        self.add_to_buffer(message.pkts)


    def print_msgs(self):
        ''' Method prints all the messages gathered in the buffer of incoming messages.'''
        for msg in self.msg_buffer_in:
            msg.output()
