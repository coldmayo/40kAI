import json
import os
import sys

def makeFile(numIters, modelFaction, enemyFaction, modelUnits, enemyUnits, modelW, enemyW, boardx = 60, boardy = 44):

    data = {
        "Army1":modelFaction,
        "Army2":enemyFaction,
        "modelUnits":modelUnits,
        "enemyUnits":enemyUnits,
        "modelWeapons":modelW,
        "enemyWeapons":enemyW,
        "numLife": int(numIters),
        "x": int(boardx),
        "y": int(boardy)
    }

    with open('gui/data.json', 'w') as f:
        json.dump(data, f)
    
def addingUnits():
    model = []
    enemy = []
    file = open("gui/units.txt", "r")
    content = file.readlines()
    flip = 0
    for i in content[1:len(content)]:
        name = i[0:len(i)-1]
        if name == "Model Units":
            flip = 1
        elif flip == 0:
            enemy.append(name)
        elif flip == 1:
            model.append(name)

    return model, enemy

def addingWeapons(m, e):

    with open(os.path.abspath("gym_mod/gym_mod/engine/unitData.json")) as j:
        data = json.loads(j.read())

    model = []
    enemy = []

    for i in data["UnitData"]:
        for j in m:
            if i["Name"] == j:
                model.append(i["Weapons"])
        for j in e:
            if i["Name"] == j:
                enemy.append(i["Weapons"])
    
    return model, enemy

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

def getModelUnits():
    with open(os.path.abspath("gui/data.json")) as j:
        data = json.loads(j.read())

    return data["modelUnits"]

def getEnemyUnits():
    with open(os.path.abspath("gui/data.json")) as j:
        data = json.loads(j.read())

    return data["enemyUnits"]

def getModelW():
    with open(os.path.abspath("gui/data.json")) as j:
        data = json.loads(j.read())

    return data["modelWeapons"]

def getEnemyW():
    with open(os.path.abspath("gui/data.json")) as j:
        data = json.loads(j.read())

    return data["enemyWeapons"]

def delFile():
    os.system("rm gui/data.json")

if __name__ == "__main__":
    model, enemy = addingUnits()
    modelw, enemyw = addingWeapons(model, enemy)
    makeFile(sys.argv[1], sys.argv[2], sys.argv[3],model, enemy, modelw, enemyw, sys.argv[4], sys.argv[5])