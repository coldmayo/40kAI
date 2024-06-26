import matplotlib.pyplot as plt
import numpy as np
import json
from scipy.optimize import curve_fit

class metrics(object):
    def __init__(self, folder, randNum, modelName):
        self.avgRew = []
        self.loss = []
        self.episodeLen = {"labels": [], "vals": []}
        self.folder = folder
        self.randNum = randNum
        self.modelName = modelName

    def updateRew(self, add):
        self.avgRew.append(add)

    def updateLoss(self, add):
        self.loss.append(add)

    def updateEpLen(self, add):
        self.episodeLen["vals"].append(add)
        self.episodeLen["labels"].append(str(add))

    def lossCurve(self):
        plt.title("Loss Curve")
        plt.xlabel("Counts")
        plt.ylabel("Loss")
        plt.plot(self.loss)

        plt.savefig("metrics/loss_{}.png".format(self.randNum))
        plt.savefig("gui/img/loss.png")
        plt.savefig("gui/img/loss_{}.png".format(self.randNum))
        plt.close()

    def showRew(self):
        y = lambda x,a,b: a * x + b
        x = np.arange(len(self.avgRew))
        popt, _ = curve_fit(y, x, self.avgRew)
        a, b = popt

        plt.title("Avg. Reward per Episode")
        plt.xlabel("Episodes")
        plt.ylabel("Reward")
        plt.plot(self.avgRew)
        plt.plot(x, y(x, a, b))

        plt.savefig("metrics/reward_{}.png".format(self.randNum))
        plt.savefig("gui/img/reward.png")
        plt.savefig("gui/img/reward_{}.png".format(self.randNum))
        plt.close()

    def showEpLen(self):
        plt.title("Episode Length")
        plt.xlabel("Episodes")
        plt.ylabel("Episode Len")
        plt.bar(self.episodeLen["labels"], self.episodeLen["vals"])

        plt.savefig("metrics/epLen_{}.png".format(self.randNum))
        plt.savefig("gui/img/epLen.png")
        plt.savefig("gui/img/epLen_{}.png".format(self.randNum))
        plt.close()

    def createJson(self):
        data = {"loss":"img/loss_{}.png".format(self.randNum), "reward":"img/reward_{}.png".format(self.randNum), "epLen":"img/epLen_{}.png".format(self.randNum)}
        with open("models/data_{}.json".format(self.modelName), "w") as f:
            json.dump(data, f)
