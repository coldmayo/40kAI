import matplotlib.pyplot as plt
import numpy as np

class metrics(object):
    def __init__(self):
        self.avgRew = []
        self.loss = []
    
    def updateRew(self, add):
        self.avgRew.append(add)

    def updateLoss(self, add):
        self.loss.append(add)

    def lossCurve(self):
        plt.title("Loss Curve")
        plt.xlabel("Counts")
        plt.ylabel("Loss")
        plt.plot(self.loss)

        plt.savefig("loss.png")
        plt.close()

    def showRew(self):
        plt.title("Avg. Reward per Episode")
        plt.xlabel("Episodes")
        plt.ylabel("Reward")
        plt.plot(self.avgRew)

        plt.savefig("reward.png")
        plt.close()