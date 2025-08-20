import math
from typing import Set, Any

import numpy as np
from numpy.matlib import empty
from pandas._libs.internals import defaultdict
from classes.Utilities import StructuredMessage
from scipy import stats

def getEntropy(data, num_target_packets):
	columnsNames = ['Entropy'+str(x) for x in range(num_target_packets)]
	entropies = []
	for column in columnsNames:
		dist = data.iloc[0][column]
		# suma = sum([float(x) for x in dist])
		# print("For column %s the sum is %f" % (column, suma))
		# entropies.append()
		entropies.append(dist)
	return np.mean(entropies)

# def getEntropy(data):
# 	tmp = data[data["Type"] == "ENTROPY"]
# 	entropy = np.mean(tmp["Entropy"].tolist())
# 	return entropy



def getUnlinkability(data):
	epsilon = []
	dlts = 0
	est_senderA = data["PrSenderA"]
	est_senderB = data["PrSenderB"]
	realSenderLabel = data["RealSenderLabel"]

	for (prA, prB, label) in zip(est_senderA, est_senderB, realSenderLabel):
		if label == 1:
			if not float(prB) == 0.0:
				ratio = float(prA) / float(prB)
				if not ratio == 0.0:
					epsilon.append(math.log(ratio))
			else:
				dlts += 1
		elif label == 2:
			if not float(prA) == 0.0:
				ratio = float(prB) / float(prA)
				if not ratio == 0.0:
					epsilon.append(math.log(ratio))
			else:
				dlts += 1
		else:
			pass
	meanEps = None
	if epsilon != []:
		meanEps = np.mean(epsilon)
	delta = float(dlts) / float(len(est_senderA))
	return (meanEps, delta)


def computeE2ELatency(df):
	travelTime = []
	for i, r in df.iterrows():
		timeSent = float(r['PacketTimeSent'])
		timeDelivered = float(r['PacketTimeDelivered'])
		travelTime.append(timeDelivered - timeSent)
	return np.nanmean(travelTime)


def totalArrivalRate(df, total_logger):
	arrivalRates = defaultdict(list)
	for i, r in df.iterrows():
		interval = np.ceil(r['PacketTimeDelivered']/10)
		arrivalRates[interval].append(r['PacketTimeDelivered'])
	for interval in arrivalRates.keys():
		arrivalRates[interval] = len(arrivalRates[interval])/10
		total_logger.info(StructuredMessage(metadata=(str(interval*10), arrivalRates[interval])))
	return


def singleArrivalRate(df, single_logger, time):
	arrivalRates = defaultdict(list)
	entries = defaultdict(list)

	clients = set()

	for i, r in df.iterrows():
		interval = np.ceil(r['PacketTimeDelivered'] / 10)*10
		arrivalRates[interval].append(r['ClientID'])
		clients.add(r['ClientID'])

	for client in clients:
		entries[client].append(client)

		for i in range(10,time+10,10):
			entries[client].append(arrivalRates[i].count(client)/10)

	for client in entries.keys():
		result = entries[client]
		single_logger.info(StructuredMessage(metadata=(result )))
