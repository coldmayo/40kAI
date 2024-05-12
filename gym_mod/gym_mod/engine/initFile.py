import json
import os
import sys

def makeFile(numIters, modelFaction, enemyFaction, boardx = 60, boardy = 44):

    data = {
        "Army1":modelFaction,
        "Army2":enemyFaction,
        "numLife": int(numIters),
        "x": int(boardx),
        "y": int(boardy)
    }

    with open('gui/data.json', 'w') as f:
        json.dump(data, f)
    
def getNumLife():

    with open(os.path.abspath("gui/data.json")) as j:
        data = json.loads(j.read())

    return data["numLife"]

def getModelFaction():
    with open(os.path.abspath("gui/data.json")) as j:
        data = json.loads(j.read())

    return data["Army1"]

def getEnemyFaction():
    with open(os.path.abspath("gui/data.json")) as j:
        data = json.loads(j.read())

    return data["Army2"]

def getBoardX():
    with open(os.path.abspath("gui/data.json")) as j:
        data = json.loads(j.read())

    return data["x"]

def getBoardY():
    with open(os.path.abspath("gui/data.json")) as j:
        data = json.loads(j.read())

    return data["y"]

def delFile():
    os.system("rm gui/data.json")

if __name__ == "__main__":
    makeFile(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])