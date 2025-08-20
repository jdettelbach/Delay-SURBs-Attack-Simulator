from classes.Node import Node
from classes.Utilities import StructuredMessage, packetLog


class Attacker(Node):
    def __init__(self, env, conf, net=None, label=0, loggers=None, id=None):
        self.capturedSURBs = []
        self.victim = None
        super().__init__(env=env, conf=conf, net=net, loggers=loggers, id="attacker")


    def process_received_packet(self, packet):
        ''' 1. Processes the received packets and logs informatiomn about them.
            2. If enabled, it stores ACK packets to send in bulk to the sender.
            3. Checks whether all the packets of particular message were received and logs the information about the reconstructed message.
            Keyword arguments:
            packet - the received packet.

            Attacker only works if ACK is enabled.
        '''

        packet.time_delivered = self.env.now
        self.env.total_messages_received += 1
        total_execution_time = self.conf["phases"]["execution"]+self.conf["phases"]["burnin"]+ self.conf["phases"]["attack"]
        match packet.type:
            case "REAL":
                if self.conf["clients"]["SURB"] and (self.victim is None or packet.real_sender == self.victim) and self.env.now<=total_execution_time:
                    self.capturedSURBs.extend(packet.SURBs)
                self.env.total_messages_sent += 1
                self.num_received_packets += 1
                msg = packet.message

                if not msg.complete_receiving:
                    msg.register_received_pkt(packet)
                    self.msg_buffer_in[msg.id] = msg
                    if self.conf["logging"]["enabled"] and self.packet_logger is not None and self.start_logs:
                        packet_type = "RCV_PKT_REAL"
                        if packet.retransmit:
                            packet_type = "RTM_PKT"
                        packetLog(self.env, packet, packet_type, self.packet_logger, recipient=self)

                if msg.complete_receiving:
                    msg_transit_time = (msg.time_delivered - msg.time_sent)
                    if self.conf["logging"]["enabled"] and self.message_logger is not None and self.start_logs:
                        self.message_logger.info(StructuredMessage(metadata=(
                            "RCV_MSG", self.env.now, self.id, msg.id, len(msg.pkts), msg.time_queued, msg.time_sent,
                            msg.time_delivered, msg_transit_time, len(msg.payload), msg.real_sender.label)))
                    self.env.message_ctr -= 1

            case "DUMMY":
                if self.conf["clients"]["dummies_acks"]:
                    packet.SURBs.time_queued = self.env.now
                    self.send_packet(packet.SURBs)
                if self.conf["logging"]["enabled"] and self.packet_logger is not None and self.start_logs and \
                        self.conf["phases"]["burnin"] <= packet.time_queued <= (
                        self.conf["phases"]["burnin"] + self.conf["phases"]["execution"] + self.conf["phases"]["attack"]):
                    packetLog(self.env, packet, packet.type, self.packet_logger, recipient=self)
                else:
                    pass
            case "ACK" | "DUMMY_ACK":
                self.process_received_ACK(packet)

            case _:
                raise Exception("Packet type not recognised")

        yield self.env.timeout(0.0)

    def set_victim(self, victim):
        self.victim = victim
        return

    def start_attack(self):
        current_time = self.env.now
        print(str(current_time) + ": Starting Attack with " + str(len(self.capturedSURBs)) + " captured packets.")
        for pkt in self.capturedSURBs:
            pkt.time_queued = current_time
            #pkt.probability_mass[i] = 1.0
        self.add_to_buffer(self.capturedSURBs)
        while len(self.pkt_buffer_out) > 0:
                tmp_pkt = self.pkt_buffer_out.pop(0)
                self.env.process(self.send_packet(tmp_pkt))

        yield(self.env.timeout(20.0))