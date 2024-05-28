import json
import os

def unitData(army, unitName):
    with open(os.path.abspath("gym_mod/gym_mod/engine/unitData.json")) as j:
        data = json.loads(j.read())
    for i in data["UnitData"]:
        if i["Army"].lower() == army.lower() and i["Name"].lower() == unitName.lower():
            return i
    print("Unit Not Found")
    return {}

def weaponData(name):
    with open(os.path.abspath("gym_mod/gym_mod/engine/unitData.json")) as j:
        data = json.loads(j.read())
    for i in data["WeaponData"]:
        if i["Name"].lower() == name.lower():
            return i
    print(i, "Weapon Not Found")
    return {}