import numpy as np

def is_num(maybeNum):
    return maybeNum.isnumeric()

def isBelowHalfStr(data, health):
    startStr = data["#OfModels"]
        
    if health < (data["W"]*startStr)/2:
        return True
        
    return False

def distance(p1, p2):
    return np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

def dice(min = 1, max = 6, num=1):
    rolls = np.array([])
    if num == 1:
        return np.random.randint(min, max)
    else:
        for i in range(num):
            rolls = np.append(rolls,np.random.randint(min, max))
        return rolls

def bounds(coords, b_len, b_hei):
    if coords[0] <= 0:
        coords[0] = 0
    if coords[1] <= 0:
        coords[1] = 0
    if coords[0] >= b_len:
        coords[0] = b_len-1
    if coords[1] >= b_hei:
        coords[1] = b_hei-1
    return coords

def attack(attackerHealth, attackerWeapon, attackerData, attackeeHealth, attackeeData, rangeOfComb="Ranged", effects=None):
    if effects == "benefit of cover" and rangeOfComb == "Ranged":
        armorSave = attackeeData["Sv"]+1
    else:
        armorSave = attackeeData["Sv"]

    rolls = dice(num=attackerData["#OfModels"])
    hits = 0
    if type(rolls) != type(1):
        for k in range(len(rolls)):
            if rangeOfComb == "Ranged":
                if rolls[k] <= attackerWeapon["BS"]:
                    hits+=1
            elif rangeOfComb == "Melee":
                if rolls[k] <= attackerWeapon["WS"]:
                    hits+=1
    else:
        if rangeOfComb == "Ranged":
            if rolls <= attackerWeapon["BS"]:
                hits+=1
        elif rangeOfComb == "Melee":
            if rolls <= attackerWeapon["WS"]:
                hits+=1
        # wound rolls
    dmg = np.array([])
    for k in range(hits):
        if attackerWeapon["S"] >= attackeeData["T"]*2:
            if dice() <= 2:
                if type(attackerWeapon["Damage"]) == type(8008135):
                    dmg = np.append(dmg, attackerWeapon["Damage"])
                elif attackerWeapon["Damage"] == "D3":
                    dmg = np.append(dmg, dice(min=1,max=3))
        elif attackerWeapon["S"] > attackeeData["T"]:
            if dice() <= 3:
                if type(attackerWeapon["Damage"]) == type(8008135):
                    dmg = np.append(dmg, attackerWeapon["Damage"])
                elif attackerWeapon["Damage"] == "D3":
                    dmg = np.append(dmg, dice(min=1,max=3))
        elif attackerWeapon["S"] == attackeeData["T"]:
            if dice() <= 4:
                if type(attackerWeapon["Damage"]) == type(8008135):
                    dmg = np.append(dmg, attackerWeapon["Damage"])
                elif attackerWeapon["Damage"] == "D3":
                    dmg = np.append(dmg, dice(min=1,max=3))
        elif attackerWeapon["S"]/2 <= attackeeData["T"]:
            if dice() <= 5:
                if type(attackerWeapon["Damage"]) == type(8008135):
                    dmg = np.append(dmg, attackerWeapon["Damage"])
                elif attackerWeapon["Damage"] == "D3":
                    dmg = np.append(dmg, dice(min=1,max=3))
        elif attackerWeapon["S"] < attackeeData["T"]:
            if dice() == 6:
                if type(attackerWeapon["Damage"]) == type(8008135):
                    dmg = np.append(dmg, attackerWeapon["Damage"])
                elif attackerWeapon["Damage"] == "D3":
                    dmg = np.append(dmg, dice(min=1,max=3))
        # saving throws (automatically does invulnerable saves)
    for k in range(len(dmg)):
        diceRoll = dice()
        if diceRoll > 1:
            if attackeeData["IVSave"] == 0 or attackerWeapon["AP"] <= 0:
                if diceRoll+attackerWeapon["AP"] > armorSave:
                    dmg[k] = 0
            elif attackeeData["IVSave"] > 0 and attackerWeapon["AP"] > 0:
                if diceRoll+attackerWeapon["AP"] > attackeeData["IVSave"]:
                    dmg[k] = 0
        else:
            dmg[k] = 0
        # allocating damage
    for k in dmg:
        attackeeHealth -= k
        if attackeeHealth < 0:
            attackeeHealth = 0
    return dmg, attackeeHealth