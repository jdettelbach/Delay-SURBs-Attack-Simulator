from binascii import hexlify
from os import urandom
import logging
import logging.handlers
import numpy 


def random_string(size):
    return hexlify(urandom(size)).decode('utf8')
    # return ''.join(random.choice(chars) for x in range(size))

def get_exponential_delay(avg_delay, cache=[]):
    if cache == []:
        cache.extend(list(numpy.random.exponential(avg_delay, 10000)))

    return cache.pop()

class StructuredMessage(object):
    def __init__(self, metadata):
        self.metadata = metadata

    def __str__(self):
        return ';'.join(str(x) for x in self.metadata)  # json.dumps(self.metadata)



def float_equlity(tested, correct=1.0):
    return correct * 0.99 < tested < correct * 1.01


def stlm_to_file(filename, stream):
    with open(filename, 'a') as outfile:
        outfile.write(stream.getvalue())


def setup_logger(logger_name, filehandler_name, capacity=50000000):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    filehandler = logging.FileHandler(filehandler_name)
    memoryhandler = logging.handlers.MemoryHandler(
                    capacity=capacity,
                    flushLevel=logging.ERROR,
                    target=filehandler
                    )

    logger.addHandler(memoryhandler)
    return logger

def packetLog(env, packet, packet_type, logger, recipient):
    match packet.conf['mode']:
        case "attack":
            logger.info(StructuredMessage(metadata=(
                packet.packet_id, packet_type, packet.type, env.now, recipient.id, packet.real_sender.label, packet.time_queued,
                packet.time_sent, packet.time_delivered, packet.time_gateway, packet.time_m_rec[0], packet.time_m_send[0],
                packet.time_m_rec[1], packet.time_m_send[1], packet.time_m_rec[2], packet.time_m_send[2], packet.route)))
        case "test":
            logger.info(StructuredMessage(metadata=(
                packet_type, env.now, recipient.id, packet.packet_id, packet.type, packet.msg_id,
                packet.time_queued, packet.time_sent, packet.time_delivered, packet.fragments,
                packet.sender_estimates[0], packet.sender_estimates[1], packet.sender_estimates[2],
                packet.real_sender.label, packet.route, packet.pool_logs)))

def log_dropped_packet(packet, logger, cur_time):
    if len(packet.time_m_rec) < 3:
        packet.time_m_rec.append(None)
        packet.time_m_rec.append(None)
        packet.time_m_rec.append(None)
    if len(packet.time_m_send) < 3:
        packet.time_m_send.append(None)
        packet.time_m_send.append(None)
        packet.time_m_send.append(None)
    logger.info(StructuredMessage(metadata=(
        packet.packet_id, "DRP_PKT", packet.type, cur_time, packet.dest.id, packet.real_sender.label, packet.time_queued,
        packet.time_sent, packet.time_delivered, packet.time_gateway, packet.time_m_rec[0],
        packet.time_m_send[0], packet.time_m_rec[1], packet.time_m_send[1], packet.time_m_rec[2],
        packet.time_m_send[2], packet.route)))