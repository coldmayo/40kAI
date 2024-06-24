import gymnasium as gym
from gym import spaces
import numpy as np
import matplotlib.pyplot as plt
import os
from gym_mod.engine.utils import *

class Warhammer40kEnv(gym.Env):
    def __init__(self, enemy, model, b_len, b_hei):
        
        savePath = "display/"
        for fil in os.listdir(savePath):
            os.remove(os.path.join(savePath, fil))

        self.action_space = spaces.Dict({
            'move': spaces.Discrete(5),  # Four directions: Up, Down, Left, Right
            'attack': spaces.Discrete(2),  # Two attack options: Engage Attack, Leave Attack/move
            'shoot': spaces.Discrete(len(enemy)),   # choose which model to attack in the shooting phase
            'charge': spaces.Discrete(len(enemy)),   # choose which model to attack in the charge phase
            'use_cp': spaces.Discrete(4),   # choose to use cp, 0 = no stratagems, 1 = insane bravery, 2 = overwatch, 3 = smokescreen
            'cp_on': spaces.Discrete(len(model))   # choose which model unit cp is used on
        })

        # Initialize game state + board
        self.iter = 0
        self.restarts = 0
        self.b_len = b_len
        self.b_hei = b_hei
        self.board = np.zeros((self.b_len,self.b_hei))
        self.unit_weapon = []
        self.unit_melee = []
        self.enemy_weapon = []
        self.enemy_melee = []
        self.unit_data = []
        self.enemy_data = []
        self.unit_coords = []
        self.enemy_coords = []
        self.unit_health = []
        self.enemy_health = []
        self.game_over = False
        self.unitInAttack = []
        self.enemyInAttack = []
        self.trunc = False
        self.enemyCP = 0
        self.modelCP = 0
        self.enemyOverwatch = -1
        self.modelStrat = {"overwatch": -1, "smokescreen": -1}
        self.enemyStrat = {"overwatch": -1, "smokescreen": -1}
        self.modelVP = 0
        self.enemyVP = 0
        self.numTurns = 0
        self.coordsOfOM = np.array([[self.b_len/2 + 8, self.b_hei/2 + 12],[self.b_len/2 - 8, self.b_hei/2 + 12],[self.b_len/2 + 8, self.b_hei/2 - 12],[self.b_len/2 - 8, self.b_hei/2 - 12]])
        self.modelOnOM = np.array([-1,-1,-1,-1])
        self.enemyOnOM = np.array([-1,-1,-1,-1])
        self.relic = 3
        self.vicCond = dice(max = 3)   # roll for victory condition: Slay and Secure, Ancient Relic, Domination
        if self.trunc == True:
            if self.vicCond == 1:
                print("Victory Condition rolled: Slay and Secure")
            elif self.vicCond == 2:
                print("Victory Condition rolled: Ancient Relic")
            elif self.vicCond == 3:
                print("Victory Condition rolled: Domination")

        for i in range(len(enemy)):
            self.enemy_weapon.append(enemy[i].showWeapon())
            self.enemy_melee.append(enemy[i].showMelee())
            self.enemy_data.append(enemy[i].showUnitData())
            self.enemy_coords.append([enemy[i].showCoords()[0], enemy[i].showCoords()[1]])
            self.enemy_health.append(enemy[i].showUnitData()["W"]*enemy[i].showUnitData()["#OfModels"])
            self.enemyInAttack.append([0,0])   # in attack, index of enemy attacking

        for i in range(len(model)):
            self.unit_weapon.append(model[i].showWeapon())
            self.unit_melee.append(model[i].showMelee())
            self.unit_data.append(model[i].showUnitData())
            self.unit_coords.append([model[i].showCoords()[0], model[i].showCoords()[1]])
            self.unit_health.append(model[i].showUnitData()["W"]*model[i].showUnitData()["#OfModels"])
            self.unitInAttack.append([0,0])   # in attack, index of enemy attacking

        obsSpace = (len(model)*3)+(len(enemy)*3)+len(self.coordsOfOM*2)+2

        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obsSpace,), dtype=np.float32)  # 7-dimensional observation space


    def get_info(self):
        return {"model health":self.unit_health, "player health": self.enemy_health, "modelCP": self.modelCP, "playerCP": self.enemyCP, "in attack": self.unitInAttack, "model VP": self.modelVP, "player VP": self.enemyVP, "victory condition": self.vicCond}

    # small reset = used in training
    # big reset reset env completely for testing/validation

    def reset(self, m, e, Type = "small"):
        self.iter = 0
        self.trunc = False
        if Type == "small":
            self.restarts += 1
        elif Type == "big":
            self.restarts = 0
            savePath = "display/"
            for fil in os.listdir(savePath):
                os.remove(os.path.join(savePath, fil))

        self.board = np.zeros((self.b_len,self.b_hei))
        self.enemy_coords = []
        self.unit_coords = []
        self.enemy_health = []
        self.unit_health = []
        self.enemyInAttack = []
        self.unitInAttack = []
        self.modelCP = 0
        self.enemyCP = 0
        self.modelVP = 0
        self.enemyVP = 0
        self.numTurns = 0
        self.vicCond = dice(max = 3)
        
        for i in range(len(self.enemy_data)):
            self.enemy_coords.append([e[i].showCoords()[0], e[i].showCoords()[1]])
            self.enemy_health.append(self.enemy_data[i]["W"]*self.enemy_data[i]["#OfModels"])
            self.enemyInAttack.append([0,0])   # in attack, index of enemy attacking

        for i in range(len(self.unit_data)):
            self.unit_coords.append([m[i].showCoords()[0], m[i].showCoords()[1]])
            self.unit_health.append(self.unit_data[i]["W"]*self.unit_data[i]["#OfModels"])
            self.unitInAttack.append([0,0])   # in attack, index of enemy attacking
        
        self.game_over = False
        self.current_action_index = 0
        info = self.get_info()

        if Type == "big":
            self.updateBoard()

        return self._get_observation(), info

    def enemyTurn(self, trunc=False):
        if trunc == True:
            self.trunc = True
        self.enemyCP += 1
        self.modelCP += 1
        self.numTurns += 1
        cp_on = np.random.randint(0,len(self.enemy_health))
        use_cp = np.random.randint(0, 4)
        for i in range(len(self.enemy_health)):

            # command phase

            enemyName = i+21
            battleSh = False
            if isBelowHalfStr(self.enemy_data[i],self.enemy_health[i]) == True and self.unit_health[i] > 0:
                if trunc == False:
                    print("This unit is Battle-shocked, starting test...")
                    print("Rolling 2D6...")
                diceRoll = dice(num=2)
                if trunc == False:
                    print("Model rolled", diceRoll[0], diceRoll[1])
                if sum(diceRoll) >= self.enemy_data[i]["Ld"]:
                    if trunc == False:
                        print("Battle-shock test passed!")
                else:
                    battleSh = True
                    if trunc == False:
                        print("Battle-shock test failed")
                    if use_cp == 1 and cp_on == i and self.enemyCP -1 >= 0:
                        battleSh = False
                        self.enemyCP -= 1

            if self.enemyInAttack[i][0] == 0 and self.enemy_health[i] > 0:

                # the enemy used for training will try to get as close to the model units as possible

                # follow random model unit
                aliveUnits = []
                for j in range(len(self.unit_health)):
                    if self.unit_health[j] > 0:
                        aliveUnits.append(j)
                if len(aliveUnits) == 0:
                    break
                idOfM = np.random.choice(aliveUnits)

                movement = dice()+self.enemy_data[i]["Movement"]
                if distance(self.unit_coords[idOfM], [self.enemy_coords[i][0], self.enemy_coords[i][1] - movement]) < distance(self.unit_coords[idOfM], self.enemy_coords[i]):
                    self.enemy_coords[i][1] -= movement
                elif distance(self.unit_coords[idOfM], [self.enemy_coords[i][0], self.enemy_coords[i][1] + movement]) < distance(self.unit_coords[idOfM], self.enemy_coords[i]):
                    self.enemy_coords[i][1] += movement
                elif distance(self.unit_coords[idOfM], [self.enemy_coords[i][0] - movement, self.enemy_coords[i][1]]) < distance(self.unit_coords[idOfM], self.enemy_coords[i]):
                    self.enemy_coords[i][0] -= movement
                elif distance(self.unit_coords[idOfM], [self.enemy_coords[i][0] + movement, self.enemy_coords[i][1]]) < distance(self.unit_coords[idOfM], self.enemy_coords[i]):
                    self.enemy_coords[i][0] += movement

                # staying in bounds

                self.enemy_coords[i] = bounds(self.enemy_coords[i], self.b_len, self.b_hei)
                for j in range(len(self.unit_health)):
                    if self.enemy_coords[i] == self.unit_coords[j]:
                        self.enemy_coords[i][0] -= 1
                        
                if self.modelStrat["overwatch"] != -1:
                    if self.unit_weapon[self.modelStrat["overwatch"]] != "None":
                        if distance(self.enemy_coords[i], self.unit_coords[self.modelStrat["overwatch"]]) <= self.unit_weapon[self.modelStrat["overwatch"]]["Range"]:
                            dmg, modHealth = attack(self.unit_health[self.modelStrat["overwatch"]], self.unit_weapon[self.modelStrat["overwatch"]], self.unit_data[self.modelStrat["overwatch"]], self.enemy_health[i], self.enemy_data[i])
                            self.enemy_health[i] = modHealth
                            self.modelStrat["overwatch"] = -1
                
                # set overwatch
                if use_cp == 2 and cp_on == i and self.enemyCP - 1 >= 0:
                    self.enemyCP -= 1
                    self.enemyStrat["overwatch"] = i

                # Shooting phase (if applicable)
                if self.enemy_weapon[i] != "None":
                    shootAbleUnits = []
                    for j in range(len(self.unit_health)):
                        if distance(self.enemy_coords[i], self.unit_coords[j]) <= self.enemy_weapon[i]["Range"] and self.unit_health[j] > 0 and self.unitInAttack[j][0] == 0:
                            shootAbleUnits.append(j)
                    if (len(shootAbleUnits) > 0):
                        idOfM = np.random.choice(shootAbleUnits)
                        if self.modelStrat["smokescreen"] != -1 and self.modelStrat["smokescreen"] == idOfM:
                            self.modelStrat["smokescreen"] = -1
                            effect = "benefit of cover"
                        else:
                            effect = None
                        dmg, modHealth = attack(self.enemy_health[i], self.enemy_weapon[i], self.enemy_data[i], self.unit_health[idOfM], self.unit_data[idOfM], effects=effect)
                        self.unit_health[idOfM] = modHealth
                        if trunc == False:
                            print("Enemy Unit",enemyName,"shoots Model Unit",idOfM+11,sum(dmg),"times")

                # Charging (if applicable)
                
                chargeAble = []
                diceRoll = sum(dice(num=2))

                for j in range(len(self.unit_health)):
                    if distance(self.enemy_coords[i], self.unit_coords[j]) <= 12 and self.unitInAttack[j][0] == 0:
                        if distance(self.enemy_coords[i], self.unit_coords[j]) - diceRoll <= 5:
                            chargeAble.append(j)

                if (len(chargeAble) > 0):  
                    if trunc == False:          
                        print("Enemy unit", enemyName,"started attack with Model unit", j+11)

                    self.enemy_coords[i][0] = self.unit_coords[j][0] + 1
                    self.enemy_coords[i][1] = self.unit_coords[j][1] + 1
                    self.enemy_coords[i] = bounds(self.enemy_coords[i], self.b_len, self.b_hei)

                    idOfM = np.random.choice(chargeAble)
                    dmg, modHealth = attack(self.enemy_health[i], self.enemy_melee[i], self.enemy_data[i], self.unit_health[idOfM], self.unit_data[idOfM], rangeOfComb="Melee")
                    self.unit_health[idOfM] = modHealth

                    self.unitInAttack[j][0] = 1
                    self.unitInAttack[j][1] = i

                    self.enemyInAttack[i][0] = 1
                    self.enemyInAttack[i][1] = idOfM

                if use_cp == 3 and cp_on == i and self.enemyCP - 1 >= 0:
                    self.enemyCP -= 1
                    self.enemyStrat["smokescreen"] = i

                for j in range(len(self.coordsOfOM)):
                    if distance(self.coordsOfOM[j], self.enemy_coords[i]) <= 5:
                        self.enemyOnOM[j] = i


            elif self.enemyInAttack[i][0] == 1 and self.enemy_health[i] > 0:
                decide = np.random.randint(0,10)
                idOfM = self.enemyInAttack[i][1]
                if decide == 5:
                    if trunc == False:
                        print("Enemy unit", enemyName,"pulled out of fight with Model unit", idOfM+11)
                    
                    if battleSh == True:
                            diceRoll = dice()
                            if diceRoll < 3:
                                self.enemy_health[i] -= self.enemy_data[i]["W"]
                    
                    self.enemy_coords[i][0] -= self.enemy_data[i]["Movement"]
                    self.enemy_coords[i] = bounds(self.enemy_coords[i], self.b_len, self.b_hei)
                    self.unitInAttack[idOfM][0] = 0
                    self.unitInAttack[idOfM][1] = 0

                    self.enemyInAttack[i][0] = 0
                    self.enemyInAttack[i][1] = 0
                else:
                    if self.unit_health[idOfM] > 0:
                        dmg, modHealth = attack(self.enemy_health[i], self.enemy_melee[i], self.enemy_data[i], self.unit_health[idOfM], self.unit_data[idOfM], rangeOfComb="Melee")
                        self.unit_health[idOfM] = modHealth
                    else:
                        self.unitInAttack[idOfM][0] = 0
                        self.unitInAttack[idOfM][1] = 0

                        self.enemyInAttack[i][0] = 0
                        self.enemyInAttack[i][1] = 0
        
        if self.modelStrat["overwatch"] != -1:
            self.modelStrat["overwatch"] = -1
        if self.modelStrat["smokescreen"] != -1:
            self.modelStrat["smokescreen"] = -1
        
        for i in range(len(self.enemyOnOM)):
            if self.enemyOnOM[i] != -1 and self.modelOnOM[i] != -1:
                if self.enemy_data[self.enemyOnOM[i]]["OC"] > self.unit_data[self.modelOnOM[i]]["OC"]:
                    self.enemyVP += 1
            elif self.enemyOnOM[i] != -1:
                self.enemyVP += 1
    
    def step(self, action):
        reward = 0
        self.enemyCP += 1
        self.modelCP += 1
        res = 0
        for i in range(len(self.unit_health)):
            modelName = i+21
            battleSh = False
            if isBelowHalfStr(self.unit_data[i],self.unit_health[i]) == True and self.unit_health[i] > 0:
                if self.trunc == False:
                    print("This unit is Battle-shocked, starting test...")
                    print("Rolling 2D6...")
                diceRoll = dice(num=2)
                if self.trunc == False:
                    print("Model rolled", diceRoll[0], diceRoll[1])
                if sum(diceRoll) >= self.unit_data[i]["Ld"]:
                    if self.trunc == False:
                        print("Battle-shock test passed!")
                else:
                    battleSh = True
                    if self.trunc == False:
                        print("Battle-shock test failed")
                    if action["use_cp"] == 1 and action["cp_on"] == i:
                        if self.modelCP - 1 >= 0:
                            battleSh = False
                            reward += 0.5
                            self.modelCP -= 1
                            if self.trunc == False:
                                print("Used Insane Bravery Stratagem to pass Battle Shock test")
                        else:
                            reward -= 1

            if self.unitInAttack[i][0] == 0 and self.unit_health[i] > 0:
                movement = dice()+self.unit_data[i]["Movement"]
                if action["move"] == 0:   # down
                    self.unit_coords[i][0] += movement
                elif action["move"] == 1:   # up
                    self.unit_coords[i][0] -= movement
                elif action["move"] == 2:   # left
                    self.unit_coords[i][1] -= movement
                elif action["move"] == 3:   # right
                    self.unit_coords[i][1] += movement
                elif action["move"] == 4:   # no move
                    for j in range(len(self.coordsOfOM)):
                        if distance(self.unit_coords[i], self.coordsOfOM[i]) <= 5:
                            reward += 0.5
                        else:
                            reward -= 0.5

            # staying in bounds

                self.unit_coords[i] = bounds(self.unit_coords[i], self.b_len, self.b_hei)
                for j in range(len(self.enemy_health)):
                    if self.unit_coords[i] == self.enemy_coords[j]:
                        self.unit_coords[i][0] -= 1

                if self.enemyStrat["overwatch"] != -1 and self.enemy_weapon[self.modelStrat["overwatch"]] != "None":
                    if distance(self.unit_coords[i], self.enemy_coords[self.enemyStrat["overwatch"]]) <= self.enemy_weapon[self.enemyStrat["overwatch"]]["Range"]:
                        dmg, modHealth = attack(self.enemy_health[self.enemyStrat["overwatch"]], self.enemy_weapon[self.enemyStrat["overwatch"]], self.enemy_data[self.enemyStrat["overwatch"]], self.unit_health[i], self.unit_data[i])
                        self.unit_health[i] = modHealth
                        if self.trunc == False:
                            print("Player unit", self.enemyStrat["overwatch"]+11, "successfully hit model unit", i+11, "for", sum(dmg), "damage using the overwatch strategem")
                        self.enemyStrat["overwatch"] = -1

                if action["use_cp"] == 2 and action["cp_on"] == i:
                    if self.modelCP - 1 >= 0 and self.enemy_weapon[i] != "None":
                        self.modelCP -= 1
                        self.modelStrat["overwatch"] = i
                        reward += 0.5
                    else:
                        reward -= 1

                # shooting phase (if eligible)
                if self.unit_weapon[i] != "None":
                    shootAbleUnits = []
                    for j in range(len(self.enemy_health)):
                        if distance(self.unit_coords[i], self.enemy_coords[j]) <= self.unit_weapon[i]["Range"] and self.enemy_health[j] > 0 and self.enemyInAttack[j][0] == 0:
                            # hit rolls
                            shootAbleUnits.append(j)

                    if (len(shootAbleUnits) > 0):        
                        idOfE = action["shoot"]
                        if (idOfE in shootAbleUnits):
                            if idOfE == self.enemyStrat["smokescreen"]:
                                effect = "benefit of cover"
                            else:
                                effect = None
                            dmg, modHealth = attack(self.unit_health[i], self.unit_weapon[i], self.unit_data[i], self.enemy_health[idOfE], self.enemy_data[idOfE], effects = effect)
                            self.enemy_health[idOfE] = modHealth
                            reward += 0.2
                            if self.trunc == False:
                                print("Model Unit",modelName,"shoots Enemy Unit",idOfE+11,sum(dmg),"times")
                        else:
                            reward -= 0.5
                            if self.trunc == False:
                                print("Model Unit", modelName, "fails to shoot an Enemy Unit")

                # Charge (if applicable)
                chargeAble = []
                diceRoll = sum(dice(num=2))

                if action["attack"] == 1:
                    for j in range(len(self.enemy_health)):
                        if distance(self.enemy_coords[j], self.unit_coords[i]) <= 12 and self.enemyInAttack[j][0] == 0 and self.enemy_health[j] > 0:
                            if distance(self.enemy_coords[j], self.unit_coords[i]) - diceRoll <= 5:
                                chargeAble.append(j)
                if (len(chargeAble) > 0):
                    idOfE = action["charge"]
                    if idOfE in chargeAble:
                        if self.trunc == False:
                            print("Model unit", modelName,"started attack with Enemy unit", j+11)
                        self.unitInAttack[i][0] = 1
                        self.unitInAttack[i][1] = j

                        self.unit_coords[i][0] = self.enemy_coords[j][0] + 1
                        self.unit_coords[i][1] = self.enemy_coords[j][1] + 1
                        self.unit_coords[i] = bounds(self.unit_coords[i], self.b_len, self.b_hei)

                        dmg, modHealth = attack(self.unit_health[i], self.unit_melee[i], self.unit_data[i], self.enemy_health[idOfE], self.enemy_data[idOfE], rangeOfComb="Melee")
                        self.enemy_health[idOfE] = modHealth

                        self.enemyInAttack[j][0] = 1
                        self.enemyInAttack[j][1] = i

                        reward += 0.5
                    else:
                        if self.trunc == False:
                            print("Model unit", modelName, "failed to attack Enemy")
                        reward -= 0.5
                # use smokescreen strategem
                if action["use_cp"] == 3 and action["cp_on"] == i:
                    if self.modelCP - 1 >= 0:
                        self.modelCP -= 1
                        self.modelStrat["smokescreen"] = i
                        reward += 0.5
                    else:
                        reward -= 0.5

                for j in range(len(self.coordsOfOM)):
                    if distance(self.coordsOfOM[j], self.unit_coords[i]) <= 5:
                        reward += 0.5
                        self.modelOnOM[j] = i
            
            elif self.unitInAttack[i][0] == 1 and self.unit_health[i] > 0:
                reward = 0
                idOfE = self.unitInAttack[i][1]
                if action["attack"] == 1:
                    dmg, modHealth = attack(self.unit_health[i], self.unit_melee[i], self.unit_data[i], self.enemy_health[idOfE], self.enemy_data[idOfE], rangeOfComb="Melee")
                    self.enemy_health[idOfE] = modHealth
                    reward += 0.2
                    if self.enemy_health[idOfE] <= 0:
                        reward += 0.3
                        self.unitInAttack[i][0] = 0
                        self.unitInAttack[i][1] = 0

                        self.enemyInAttack[idOfE][0] = 0
                        self.enemyInAttack[idOfE][1] = 0

                    reward += 0.5

                elif action["attack"] == 0:
                    if self.unit_health[i]*2 >= self.enemy_health[idOfE]:
                        reward -= 0.5
                    if self.trunc == False:
                        print("Model unit", modelName,"pulled out of fight with Enemy unit", idOfE+11)
                    
                    if battleSh == True:
                            diceRoll = dice()
                            if diceRoll < 3:
                                self.unit_health[i] -= self.unit_data[i]["W"]

                    self.unit_coords[i][0] += self.unit_data[i]["Movement"]
                    self.unitInAttack[i][0] = 0
                    self.unitInAttack[i][1] = 0

                    self.enemyInAttack[idOfE][0] = 0
                    self.enemyInAttack[idOfE][1] = 0
            
            elif self.unit_health[i] == 0:
                reward -= 1
                if self.trunc == False:
                    print("Model unit", modelName ,"is destroyed")


        if self.enemyStrat["overwatch"] != -1:
            self.enemyStrat["overwatch"] = -1
        if self.enemyStrat["smokescreen"] != -1:
            self.enemyStrat["smokescreen"] = -1

        for i in range(len(self.modelOnOM)):
            if self.enemyOnOM[i] != -1 and self.modelOnOM[i] != -1:
                if self.enemy_data[self.enemyOnOM[i]]["OC"] < self.unit_data[self.modelOnOM[i]]["OC"]:
                    self.modelVP += 1
            elif self.modelOnOM[i] != -1:
                self.modelVP += 1

        for i in range(len(self.unit_health)):
            if self.unit_health[i] < 0:
                self.unit_health[i] = 0
        
        for i in range(len(self.enemy_health)):
            if self.enemy_health[i] < 0:
                self.enemy_health[i] = 0

        # Determine winning team

        # Major victory

        if sum(self.unit_health) <= 0:
            self.game_over = True
            reward -= 2
            res = 4
        elif sum(self.enemy_health) <= 0:
            self.game_over = True
            reward += 2
            res = 4
        # Other victory conditions: Slay and Secure, Ancient Relic, Domination
        if self.numTurns == 5 and self.game_over != True:
            self.game_over = True
            res = self.vicCond   # Roll dice to see which victory condition is used
            if res == 1:
                self.modelVP = 0
                self.enemyVP = 0
                for i in range(len(self.enemyOnOM)):
                    if self.enemyOnOM[i] != -1 and self.modelOnOM[i] != -1:
                        if self.enemy_data[self.enemyOnOM[i]]["OC"] > self.unit_data[self.modelOnOM[i]]["OC"]:
                            self.enemyVP += 1
                        elif self.enemy_data[self.enemyOnOM[i]]["OC"] < self.unit_data[self.modelOnOM[i]]["OC"]:
                            self.modelVP += 1
                    elif self.enemyOnOM[i] != -1:
                        self.enemyVP += 1
                    elif self.modelOnOM[i] != -1:
                        self.modelVP += 1
                if self.modelVP > self.enemyVP:
                    reward += 2
                else: 
                    reward -= 2
            elif res == 2:
                if self.enemyOnOM[self.relic] != -1 and self.modelOnOM[self.relic] != -1:
                    if self.enemy_data[self.enemyOnOM[self.relic]]["OC"] > self.unit_data[self.modelOnOM[self.relic]]["OC"]:
                        self.enemyVP += 6
                    elif self.enemy_data[self.enemyOnOM[self.relic]]["OC"] < self.unit_data[self.modelOnOM[self.relic]]["OC"]:
                        self.modelVP += 6
                if self.modelVP > self.enemyVP:
                    reward += 2
                else: 
                    reward -= 2
            elif res == 3:
                if self.modelVP > self.enemyVP:
                    reward += 2
                else: 
                    reward -= 2

        self.iter += 1

        info = self.get_info()
        return self._get_observation(), reward, self.game_over, res, info

    # for a real person playing
    def player(self):
        self.enemyCP += 1
        self.modelCP += 1

        if self.numTurns == 0:
            if self.vicCond == 1:
                print("Victory Condition rolled: Slay and Secure")
            elif self.vicCond == 2:
                print("Victory Condition rolled: Ancient Relic")
            elif self.vicCond == 3:
                print("Victory Condition rolled: Domination")

        print(self.get_info())

        for i in range(len(self.enemy_health)):
            playerName = i+11
            print("For unit", playerName)
            battleSh = False
            if isBelowHalfStr(self.enemy_data[i],self.enemy_health[i]) == True and self.unit_health[i] > 0:
                print("This unit is Battle-shocked, starting test...")
                print("Rolling 2D6...")
                diceRoll = dice(num=2)
                print("You rolled", diceRoll[0], diceRoll[1])
                if sum(diceRoll) >= self.enemy_data[i]["Ld"]:
                    print("Battle-shock test passed!")
                else:
                    battleSh = True
                    print("Battle-shock test failed")
                    response = False
                    if self.enemyCP -1 >= 0:
                        strat = input("Would you like to use the Insane Bravery Strategem? (y/n): ")
                        while response == False:
                            if strat.lower() == "y" or strat.lower() == "yes":
                                response = True
                                battleSh = False
                                self.enemyCP -= 1
                            elif strat.lower() == "n" or strat.lower() == "no":
                                response = True
                            elif strat.lower() == "quit":
                                self.game_over = True
                                info = self.get_info()
                                return self.game_over, info
                            elif strat.lower() == "?" or strat.lower() == "help":
                                print("The Insane Bravery Stratagem costs 1 Command Point and is used when a unit fails a Battle-Shock Test. If used it treats the unit as if it passed.")
                                strat = input("Would you like to use the Insane Bravery Stratagem? (y/n): ")
                            else: 
                                strat = input("Valid answers are: y, yes, n, and no: ")


            if self.enemyInAttack[i][0] == 0 and self.enemy_health[i] > 0:
                self.updateBoard()
                self.showBoard()
                print("Take a look at board.txt or click the Show Board button to view the current board")
                print("If you would like to end the game type 'quit' into the prompt")
                dire = input("Enter the direction of movement (up, down, left, right, none (no move)): ")
                
                if dire.lower() == "quit":
                    self.game_over = True
                    info = self.get_info()
                    return self.game_over, info
                if dire.lower() != "none":
                	print("Rolling 1 D6...")
                	roll = dice()
                	print("You rolled a", roll)
                	movement = roll+self.unit_data[i]["Movement"]
                response = False
                while response == False:
                    if dire.lower() == "down":
                        self.enemy_coords[i][0] += movement
                        response = True
                    elif dire.lower() == "up":
                        self.enemy_coords[i][0] -= movement
                        response = True
                    elif dire.lower() == "left":
                        self.enemy_coords[i][1] -= movement
                        response = True
                    elif dire.lower() == "right":
                        self.enemy_coords[i][1] += movement
                        response = True
                    elif dire.lower() == "none":
                        response = True
                    elif dire.lower() == "quit":
                        self.game_over = True
                        info = self.get_info()
                        return self.game_over, info
                    else:
                        dire = input("Not a valid response (up, down, left, right):")
                        response = False

            # staying in bounds

                self.enemy_coords[i] = bounds(self.enemy_coords[i], self.b_len, self.b_hei)
                for j in range(len(self.enemy_health)):
                    if self.enemy_coords[i] == self.unit_coords[j]:
                        self.enemy_coords[i][0] -= 1
                
                if self.enemyCP - 1 >= 0:
                    response = False
                    strat = input("Would you like to use the Fire Overwatch Stratagem? (y/n)")
                    while response == False:
                        if strat.lower() == "y" or strat.lower() == "yes":
                            response = True
                            self.enemyStrat["overwatch"] = i
                            self.enemyCP -= 1
                        elif strat.lower() == "n" or strat.lower() == "no":
                            response = True
                        elif strat.lower() == "?" or strat.lower() == "help":
                                print("The Fire Overwatch Stratagem costs 1 Command Point and if your unit and the opposing unit are 21 inches from each other during their Movement/Charge Phase then your unit can shoot that enemy unit as if it were your Shooting phase")
                                strat = input("Would you like to use the Fire Overwatch Stratagem? (y/n): ")
                        elif strat.lower() == "quit":
                            self.game_over = True
                            info = self.get_info()
                            return self.game_over, info
                        else: 
                            strat = input("Valid answers are: y, yes, n, and no: ")

                if self.modelStrat["overwatch"] != -1 and self.unit_weapon[self.modelStrat["overwatch"]] != "None":
                    if distance(self.enemy_coords[i], self.unit_coords[self.modelStrat["overwatch"]]) <= self.unit_weapon[self.modelStrat["overwatch"]]["Range"]:
                        dmg, modHealth = attack(self.unit_health[self.modelStrat["overwatch"]], self.unit_weapon[self.modelStrat["overwatch"]], self.unit_data[self.modelStrat["overwatch"]], self.enemy_health[i], self.enemy_data[i])
                        self.enemy_health[i] = modHealth
                        print("Model unit", self.modelStrat["overwatch"]+21, "successfully hit player unit", i+11, "for", sum(dmg), "damage using the overwatch strategem")
                        self.modelStrat["overwatch"] = -1
                self.updateBoard()
                self.showBoard()
                print("Take a look at board.txt to view the updated board")
                
                # shooting phase (if eligible)
                if self.enemy_weapon[i] != "None":
                    print("Beginning shooting phase!")
                    shootAble = np.array([])
                    for j in range(len(self.unit_health)):
                        if distance(self.enemy_coords[i], self.unit_coords[j]) <= self.enemy_weapon[i]["Range"] and self.unit_health[j] > 0 and self.unitInAttack[j][0] == 0:
                        # save index of available units to shoot
                            shootAble = np.append(shootAble, j)

                    if len(shootAble) > 0 and self.enemy_weapon[i] != "None":
                        response = False
                        while response == False:
                            shoot = input("Select which enemy unit you would like to shoot ({}): ".format(shootAble+21))
                            if is_num(shoot) == True and int(shoot)-21 in shootAble:
                                idOfE = int(shoot)-21
                                if self.modelStrat["smokescreen"] != -1 and self.modelStrat["smokescreen"] == idOfE:
                                    print("Model unit", self.modelStrat["smokescreen"]+21, "used the Smokescreen Strategem")
                                    self.modelStrat["smokescreen"] = -1
                                    effect = "benefit of cover"
                                else:
                                    effect = None
                                dmg, modHealth = attack(self.enemy_health[i], self.enemy_weapon[i], self.enemy_data[i], self.unit_health[idOfE], self.unit_data[idOfE], effects = effect)
                                self.unit_health[idOfE] = modHealth
                                print("Player Unit",playerName,"shoots Model Unit",idOfE+21,sum(dmg),"times")
                                response = True
                            elif shoot == "quit":
                                self.game_over = True
                                info = self.get_info()
                                return self.game_over, info
                            else:
                                print("Not an available unit")
                    
                else:
                    print("No available units to attack")


                # Charge (if applicable)
                print("Beginning Charge phase!")
                charg = np.array([])
                for j in range(len(self.unit_health)):
                    if distance(self.unit_coords[j], self.enemy_coords[i]) <= 12 and self.unitInAttack[j][0] == 0 and self.unit_health[j] > 0:
                        charg = np.append(charg, j)

                if len(charg) > 0:
                    response = False
                    while response == False:
                        attk = input("Select while enemy you would like to charge ({}): ".format(charg+21))
                        if is_num(attk) == True and int(attk)-21 in charg:
                            response = True
                            j = int(attk)-21
                            print("Rolling 2 D6...")
                            roll = dice(num=2)
                            print("You rolled a", roll[0], "and", roll[1])
                            if distance(self.enemy_coords[i], self.unit_coords[j]) - sum(roll) <= 5:
                                print("Player Unit", playerName, "Successfully charged Model Unit", j+21)
                                self.enemyInAttack[i][0] = 1
                                self.enemyInAttack[i][1] = j

                                self.enemy_coords[i][0] = self.unit_coords[j][0] + 1
                                self.enemy_coords[i][1] = self.unit_coords[j][1] + 1
                                self.enemy_coords[i] = bounds(self.enemy_coords[i], self.b_len, self.b_hei)

                                idOfE = j
                                dmg, modHealth = attack(self.enemy_health[i], self.enemy_melee[i], self.enemy_data[i], self.unit_health[idOfE], self.unit_data[idOfE], rangeOfComb="Melee")
                                self.unit_health[idOfE] = modHealth

                                self.unitInAttack[j][0] = 1
                                self.unitInAttack[j][1] = i
                            else:
                                print("Player Unit", playerName, "Failed to charge Model Unit", j+21)
                        
                        elif attack == "quit":
                            self.game_over = True
                            info = self.get_info()
                            return self.game_over, info
                        else:
                            print("Not an available unit")
                else:
                    print("No available units to attack")  

                response = False
                strat = input("Would you like to use the Smokescreen Stratagem for this unit? (y/n): ")
                while response == False:
                    if strat.lower() == "y" or strat.lower() == "yes":
                        self.enemyStrat["smokescreen"] = i 
                        response = True
                    elif strat.lower() == "n" or strat.lower() == "no":
                        response = True
                    elif strat.lower() == "?" or strat.lower() == "help":
                                print("The Smokescreen Stratagem costs 1 Command Point and when used all models in the unit have the Benefit of Cover and the Stealth ability")
                                strat = input("Would you like to use the Smokescreen Stratagem? (y/n): ")
                    else:
                        strat = input("It's a yes or no question dude")
            
                for j in range(len(self.coordsOfOM)):
                    if distance(self.coordsOfOM[j], self.enemy_coords[i]) <= 5:
                        self.enemyOnOM[j] = i

            elif self.enemyInAttack[i][0] == 1 and self.enemy_health[i] > 0:
                idOfE = self.enemyInAttack[i][1]
                response = False
                while response == False:
                    fallB = input("Would you like to fallback? (y/n): ")
                    if fallB.lower() == "n" or fallB.lower() == "no":
                        response = True
                        print("Player Unit", playerName, "Is attacking Model Unit", idOfE+21)
                        dmg, modHealth = attack(self.enemy_health[i], self.enemy_melee[i], self.enemy_data[i], self.unit_health[idOfE], self.unit_data[idOfE], rangeOfComb="Melee")
                        self.unit_health[idOfE] = modHealth
                        if self.unit_health[idOfE] <= 0:
                            print("Model Unit", idOfE+21, "has been killed")
                            self.enemyInAttack[i][0] = 0
                            self.enemyInAttack[i][1] = 0

                            self.unitInAttack[idOfE][0] = 0
                            self.unitInAttack[idOfE][1] = 0
                    elif fallB.lower() == "y" or fallB.lower() == "yes":
                        response = True
                        print("Player Unit", playerName,"fell back from Enemy unit", idOfE+21)
                        
                        if battleSh == True:
                            diceRoll = dice()
                            if diceRoll < 3:
                                self.enemy_health[i] -= self.enemy_data[i]["W"]

                        self.enemy_coords[i][0] += self.enemy_data[i]["Movement"]
                        self.enemyInAttack[i][0] = 0
                        self.enemyInAttack[i][1] = 0

                        self.unitInAttack[idOfE][0] = 0
                        self.unitInAttack[idOfE][1] = 0
                    elif fallB.lower() == "quit":
                        self.game_over = True
                        info = self.get_info()
                        return self.game_over, info
                    else:
                        print("It's a yes or no question dude")
            
            elif self.enemy_health[i] == 0:
                print("Unit", playerName, "is dead")

        if self.modelStrat["overwatch"] != -1:
            self.modelStrat["overwatch"] = -1
        if self.modelStrat["smokescreen"] != -1:
            self.modelStrat["smokescreen"] = -1

        for i in range(len(self.enemyOnOM)):
            if self.enemyOnOM[i] != -1 and self.modelOnOM[i] != -1:
                if self.enemy_data[self.enemyOnOM[i]]["OC"] > self.unit_data[self.modelOnOM[i]]["OC"]:
                    self.enemyVP += 1
            elif self.enemyOnOM[i] != -1:
                self.enemyVP += 1

        for i in self.enemy_health:
            if i < 0:
                i = 0
        
        for i in self.enemy_health:
            if i < 0:
                i = 0

        self.iter += 1

        info = self.get_info()
        return self.game_over, info

    def updateBoard(self):
        self.board = np.zeros((self.b_len,self.b_hei))

        for i in range(len(self.unit_health)):
            self.unit_coords[i] = bounds(self.unit_coords[i], self.b_len, self.b_hei)
            self.board[self.unit_coords[i][0]][self.unit_coords[i][1]] = 20+i+1

        for i in range(len(self.enemy_health)):
            self.enemy_coords[i] = bounds(self.enemy_coords[i], self.b_len, self.b_hei)
            self.board[self.enemy_coords[i][0]][self.enemy_coords[i][1]] = 10+i+1

        for i in range(len(self.coordsOfOM)):
            self.board[int(self.coordsOfOM[i][0])][int(self.coordsOfOM[i][1])] = 3

    def returnBoard(self):
        return self.board

    def render(self, mode='human'):
        self.updateBoard()
        
        fig = plt.figure()
        ax = fig.add_subplot()
        fig.subplots_adjust(top=0.85)

        title = "Turn "+str(self.iter)+" Lifetime "+str(self.restarts)
        fig.suptitle(title)

        health = "Model Unit health: {}, CP: {}; Enemy Unit health: {}, CP {}\nVP {}".format(self.unit_health, self.modelCP, self.enemy_health, self.enemyCP, [self.modelVP, self.enemyVP])
        ax.set_title(health)
        
        x1 = np.linspace(0,self.b_len,10)
        y1 = np.zeros(10)
        x2 = np.zeros(10)
        y2 = np.linspace(0, self.b_hei,10)
        ax.set_xlim(-5,self.b_len*1.43333)
        ax.set_ylim(-3,self.b_hei + 4)
        ax.plot(x1,y1,color="black")
        ax.plot(x2,y2,color="black")
        ax.plot(x1,y1+self.b_hei,color="black")
        ax.plot(x2+self.b_len,y2,color="black")

        for i in range(len(self.unit_health)):
            if i == 0:
                ax.plot(self.unit_coords[i][0],self.unit_coords[i][1], 'bo', label="Model Unit")
            else:
                ax.plot(self.unit_coords[i][0],self.unit_coords[i][1], 'bo')
        for i in range(len(self.enemy_health)):
            if i == 0:
                ax.plot(self.enemy_coords[i][0],self.enemy_coords[i][1], 'ro', label="Enemy Unit")
            else:
                ax.plot(self.enemy_coords[i][0],self.enemy_coords[i][1], 'ro')
        
        for i in range(len(self.coordsOfOM)):
            ax.plot(self.coordsOfOM[i][0], self.coordsOfOM[i][1], 'o', color="black")

        ax.legend(loc = "right")
        fileName = "display/"+str(self.restarts)+"_"+str(self.iter)+".png"
        fig.savefig(fileName)
        ax.cla()
        plt.close()

        return self.board

    def showBoard(self):
        board = self.returnBoard()
        np.savetxt("board.txt", board.astype(int), fmt="%i", delimiter=",")

    def close(self):
        pass

    def _get_observation(self):
        obs = []
        
        for i in range(len(self.unit_health)):
            obs.append(self.unit_health[i])
            obs.append(self.unit_coords[i][0])
            obs.append(self.unit_coords[i][1])

        obs.append(self.modelCP)

        for i in range(len(self.enemy_health)):
            obs.append(self.enemy_health[i])
            obs.append(self.enemy_coords[i][0])
            obs.append(self.enemy_coords[i][1])
        
        obs.append(self.enemyCP)

        for OM in self.coordsOfOM:
            obs.append(OM[0])
            obs.append(OM[1])

        obs.append(int(self.game_over))

        obs.append(self.vicCond)

        return np.array(obs, dtype=np.float32)
