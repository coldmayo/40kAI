import matplotlib.pyplot as plt
import numpy as np

class metrics(object):
    def __init__(self):
        self.avgRew = []
        self.loss = []
        self.episodeLen = []
    
    def updateRew(self, add):
        self.avgRew.append(add)

    def updateLoss(self, add):
        self.loss.append(add)

    def updateEpLen(self, add):
        self.episodeLen.append(add)

    def lossCurve(self):
        plt.title("Loss Curve")
        plt.xlabel("Counts")
        plt.ylabel("Loss")
        plt.plot(self.loss)

        plt.savefig("metrics/loss.png")
        plt.savefig("gui/img/loss.png")
        plt.close()

    def showRew(self):
        plt.title("Avg. Reward per Episode")
        plt.xlabel("Episodes")
        plt.ylabel("Reward")
        plt.plot(self.avgRew)

        plt.savefig("metrics/reward.png")
        plt.savefig("gui/img/reward.png")
        plt.close()

    def showEpLen(self):
        plt.title("Episode Length")
        plt.xlabel("Episodes")
        plt.ylabel("Episode Len")
        plt.plot(self.episodeLen)

        plt.savefig("metrics/epLen.png")
        plt.savefig("gui/img/epLen.png")
        plt.close()