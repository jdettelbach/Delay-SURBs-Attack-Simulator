from classes.Utilities import random_string
import numpy

class Packet():
    ''' This module implements the Packet object, which is the data structure responsible for
        transporting message blocks among clients.
    '''

    __slots__ = ['conf', 'packet_id', 'route', 'payload', 'real_sender', 'dest', 'msg_id', 'message', 'fragments',
                 'type', 'pool_logs', 'dropped', 'current_node', 'times_transmitted', 'SURBs', 'time_queued',
                 'time_sent', 'time_delivered', 'sender_estimates', 'probability_mass', 'retransmit', 'time_gateway',
                 'time_m_rec', 'time_m_send']

    def __init__(self, conf, route, payload, sender, dest, type, packet_id=None, msg_id="DUMMY", order=1, num=1, message=None):
        self.conf = conf
        self.packet_id = packet_id or random_string(32)
        self.retransmit = False

        self.route = route
        self.payload = payload
        self.real_sender = sender
        self.dest = dest

        self.msg_id = msg_id
        self.message = message

        self.fragments = num

        self.SURBs = None

        self.type = type
        self.pool_logs = []

        # State
        self.dropped = False
        self.current_node = -1
        self.times_transmitted = 0
        self.time_queued = None
        self.time_sent = None
        self.time_delivered = None
        self.time_gateway = None
        self.time_m_rec = []
        self.time_m_send = []

        # Measurements
        self.sender_estimates = numpy.array([0.0, 0.0, 0.0]) #Other, A, B
        self.sender_estimates[self.real_sender.label] = 1.0
        self.probability_mass = numpy.zeros(self.conf["misc"]["num_target_packets"])

        if self.type=="REAL":
            self.message.reconstruct.add(self.packet_id)


    @classmethod
    def new(cls, conf, net, dest, payload, sender, type, num, msg_id, order=1, message=None):
        '''Method used for constructing a new Packet where
        the content is defined by the client but the route is generated on the constructor.'''

        rand_route = net.select_random_route()
        rand_route = rand_route + [dest]
        packet = cls(conf=conf, route=rand_route, payload=payload, sender=sender, dest=dest, type=type, num=num, order=order, msg_id=msg_id, message=message)
        if conf["clients"]["SURB"]: #If Surbs activated: Number of SURBs in conf gets added plus 1 additional as ACK
            surbs = []
            for i in range(conf["clients"]["SURB_number"]+1):
                surbs.append(Packet.surb(conf=conf, net=net, dest=sender, sender=dest, packet_id=packet.packet_id, msg_id=msg_id))
            packet.SURBs = surbs
        return packet


    @classmethod
    def surb(cls, conf, net, dest, sender, packet_id, msg_id):
        '''  The class method used for creating an ack Packet. '''


        payload = random_string(conf["packet"]["packet_size"])
        rand_route = net.select_random_route()
        rand_route = rand_route + [dest]
        return cls(conf=conf, route=rand_route, payload=payload, sender=sender, dest=dest, packet_id=packet_id, msg_id=msg_id, type="ACK")

    @classmethod
    def dummy(cls, conf, net, dest, sender):
        '''  The class method used for creating a dummy Packet. '''

        payload = random_string(conf["packet"]["packet_size"])
        rand_route = net.select_random_route()
        rand_route = rand_route + [dest]
        packet = cls(conf=conf, route=rand_route, payload=payload, sender=sender, dest=dest, type="DUMMY", msg_id="-")
        if conf["clients"]["dummies_acks"]:
            ack = Packet.dummy_ack(conf=conf, net=net, dest=sender, sender=dest)
            packet.SURBs = ack
        return packet

    @classmethod
    def dummy_ack(cls, conf, net, dest, sender):

        payload = random_string(conf["packet"]["packet_size"])
        rand_route = net.select_random_route()
        rand_route = rand_route + [dest]
        return cls(conf=conf, route=rand_route, payload=payload, sender=sender, dest=dest, type="DUMMY_ACK", msg_id="DUMMY_ACK")

    @classmethod
    def copy(cls, packet):
        conf = packet.conf
        packet_id = packet.packet_id

        route = packet.route
        payload = packet.payload
        real_sender = packet.real_sender
        dest = packet.dest

        msg_id = packet.msg_id
        message = packet.message

        fragments = packet.fragments
        type = packet.type
        copy = cls(conf=conf, packet_id=packet_id, route=route, payload=payload, sender=real_sender, dest=dest, type=type,
                   num=fragments, msg_id=msg_id, message=message)
        copy.time_queued = packet.time_queued
        copy.times_transmitted = packet.times_transmitted
        copy.SURBs = packet.SURBs
        return copy

    def output(self):
        ''' Function prints the information about the packet'''

        if not self.conf["debug"]["enabled"]:
            return

        print("=====================")
        print("Packet ID              : " + str(self.packet_id))
        print("Packet Type            : " + str(self.type))
        print("Sender                 : " + str(self.real_sender))
        print("Labels                 : " + str(self.sender_estimates))
        print("Time Added to Queue    : " + str(self.time_queued))
        print("Time Sent              : " + str(self.time_sent))
        print("Time Delivered         : " + str(self.time_delivered))
        print("ACK Received           : " + str(self.ACK_Received))
        print("Route                  : " + str(self.route))
        print("Current Hop            : " + str(self.current_node))
        print("Times Transmitted      : " + str(self.times_transmitted))
        print("=====================")
