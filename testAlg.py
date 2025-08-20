import os
from collections import defaultdict

import scipy.stats as stats
import pandas as pd

def myround(x, base=5):
    return base * round(x/base)

def exceedLimit(data, limit):
    if data-limit <= 0:
        return 0
    else: return 1

def test(directory, filename, numClients=1):
    data = pd.read_csv(os.path.join(directory, filename), sep=";", index_col=0)
    data = data[data.index >= 6000]
    data = data[data.index <= 9500]
    attack = data[data.index >= 8200]
    data = data[data.index < 8200]
    if numClients>1: data.drop(columns=["SURBs", "total"], inplace=True)
    comparison = pd.DataFrame()
    comparison["average"] = data.sum(axis=0) / len(data.index)
    comparison["average"] = myround(comparison["average"] - numClients*0.5) + numClients*0.5
    comparison["limit"] = stats.poisson.ppf(0.99, comparison["average"])
    limitTest = attack - comparison["limit"].transpose()
    comparison["limitExceeded"] = 0
    comparison["maxValue"] = 0
    for c in limitTest.columns:
        comparison.at[c, "limitExceeded"] = len(limitTest[limitTest[c]>0])
        comparison.at[c, "maxValue"] = max(attack[c])
    ranking = pd.DataFrame()
    ranking["limitExceeded"] = comparison[comparison["limitExceeded"]>0].limitExceeded
    ranking["maxValue"] = comparison[comparison["limitExceeded"]>0].maxValue
    ranking["rank"] = ranking["limitExceeded"].rank(method="dense", ascending=False)
    return ranking

def precisionRecall(path, filename, numClients=1):
    falsepositives = 0
    truepositives = 0
    for i in range(1, 101):
        ranking = test(os.path.join(path, str(i)), filename, numClients)
        guess = ranking[ranking["rank"]==1]
        guess = guess[guess["maxValue"]==max(guess["maxValue"])]
        for index in guess.index:
            if index == "victim":
                truepositives+=1
            else: falsepositives+=1
    result = defaultdict()
    result["precision"] = truepositives/(truepositives+falsepositives)
    result["recall"] = truepositives/100
    return result


for i in range(1,11):
    print(precisionRecall("data/"+str(10*i)+"SURBs", "even_gateway_arrival_rates_in_100ms.csv", numClients=6))