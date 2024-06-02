import json
import os

def inFile(f, info):
    if "Range" in info:
        weapons = f["WeaponData"]
        for j in weapons:
            if j["Name"] == info["Name"]:
                return True

    elif "#OfModels" in info:
        weapons = f["UnitData"]
        for j in weapons:
            if j["Name"] == info["Name"]:
                return True
    return False


with open(os.path.abspath("links.json")) as j:
    data = json.loads(j.read())

with open(os.path.abspath("../../gym_mod/gym_mod/engine/unitDataInit.json")) as j:
    dataFile = json.loads(j.read())

for i in range(len(data)):
    for j in range(len(data[i]["UnitData"])):
        if inFile(dataFile, data[i]["UnitData"][j]) == False:
            dataFile["UnitData"].append(data[i]["UnitData"][j])

    for j in range(len(data[i]["WeaponData"])):
        if inFile(dataFile, data[i]["WeaponData"][j]) == False:
            dataFile["WeaponData"].append(data[i]["WeaponData"][j])

with open('../../gym_mod/gym_mod/engine/unitData.json', 'w') as f:
    json.dump(dataFile, f)