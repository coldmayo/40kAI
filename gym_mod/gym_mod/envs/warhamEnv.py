import gymnasium as gym
from gym import spaces
import numpy as np
import matplotlib.pyplot as plt
import os
from gym_mod.engine.utils import *
from gym_mod.engine.GUIinteract import *

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
            'use_cp': spaces.Discrete(5),   # choose to use cp, 0 = no stratagems, 1 = insane bravery, 2 = overwatch, 3 = smokescreen, 4 = heroic intervention 
            'cp_on': spaces.Discrete(len(model))   # choose which model unit cp is used on
        })

        for i in range(len(model)):
            label = "move_num_"+str(i)
            self.action_space[label] = spaces.Discrete(12)
        # Initialize game state + board
        self.iter = 0
        self.restarts = 0
        self.playType = False
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
        self.modelOC = []
        self.enemyOC = []
        self.relic = 3
        self.vicCond = dice(max = 3)   # roll for victory condition: Slay and Secure, Ancient Relic, Domination
        self.modelUpdates = ""
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
            self.enemyOC.append(enemy[i].showUnitData()["OC"])

        for i in range(len(model)):
            self.unit_weapon.append(model[i].showWeapon())
            self.unit_melee.append(model[i].showMelee())
            self.unit_data.append(model[i].showUnitData())
            self.unit_coords.append([model[i].showCoords()[0], model[i].showCoords()[1]])
            self.unit_health.append(model[i].showUnitData()["W"]*model[i].showUnitData()["#OfModels"])
            self.unitInAttack.append([0,0])   # in attack, index of enemy attacking
            self.modelOC.append(model[i].showUnitData()["OC"])

        obsSpace = (len(model)*3)+(len(enemy)*3)+len(self.coordsOfOM*2)+2

        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obsSpace,), dtype=np.float32)  # 7-dimensional observation space


    def get_info(self):
        return {"model health":self.unit_health, "player health": self.enemy_health, "modelCP": self.modelCP, "playerCP": self.enemyCP, "in attack": self.unitInAttack, "model VP": self.modelVP, "player VP": self.enemyVP, "victory condition": self.vicCond}

    # small reset = used in training
    # big reset reset env completely for testing/validation

    def reset(self, m, e, playType=False, Type = "small", trunc = False):
        self.iter = 0
        self.trunc = trunc
        self.playType=playType

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
        self.modelUpdates = ""
        
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
        use_cp = np.random.randint(0, 5)
        for i in range(len(self.enemy_health)):

            # command phase

            enemyName = i+21
            battleSh = False
            if isBelowHalfStr(self.enemy_data[i],self.enemy_health[i]) == True and self.unit_health[i] > 0:
                if trunc == False:
                    print("This unit is Below Half Strength, starting test...")
                    print("Rolling 2D6...")
                diceRoll = dice(num=2)
                if trunc == False:
                    print("Player rolled", diceRoll[0], diceRoll[1])
                if sum(diceRoll) >= self.enemy_data[i]["Ld"]:
                    if trunc == False:
                        print("Battle-shock test passed!")
                        self.enemyOC[i] = self.enemy_data[i]["OC"]
                else:
                    battleSh = True
                    self.enemyOC[i] = 0
                    if trunc == False:
                        print("Battle-shock test failed")
                    if use_cp == 1 and cp_on == i and self.enemyCP -1 >= 0:
                        battleSh = False
                        self.enemyCP -= 1
                        self.enemyOC[i] = self.enemy_data[i]["OC"]

            if use_cp == 4 and cp_on == i:
                if self.enemyCP - 2 >= 0 and self.enemyInAttack[i][0] == 0: # make sure current model is not in combat
                    for j in range(len(self.unitInAttack)):
                        if self.unitInAttack[j][0] == 1 and distance(self.enemy_coords[i], self.unit_coords[j]) >= 6:
                            self.enemyInAttack[i][0] = 1
                            self.enemyInAttack[i][1] = j

                            self.enemyInAttack[self.enemyInAttack[j][1]][0] = 0
                            self.enemyInAttack[self.enemyInAttack[j][1]][1] = 0

                            self.enemy_coords[i][0] = self.enemy_coords[j][0] + 1
                            self.enemy_coords[i][1] = self.enemy_coords[j][1] + 1
                            self.enemy_coords[i] = bounds(self.unit_coords[i], self.b_len, self.b_hei)

                            self.unitInAttack[j][1] = i
                            self.enemyCP -= 2
                            break
                            
                    

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
                if use_cp == 2 and cp_on == i and self.enemyCP - 1 >= 0 and battleSh == False:
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

                if use_cp == 3 and cp_on == i and self.enemyCP - 1 >= 0 and battleSh == False:
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
                if self.enemyOC[self.enemyOnOM[i]] > self.modelOC[self.modelOnOM[i]]:
                    self.enemyVP += 1
            elif self.enemyOnOM[i] != -1:
                self.enemyVP += 1
    
    def step(self, action):
        reward = 0
        self.enemyCP += 1
        self.modelCP += 1
        effect = None
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
                    self.modelOC[i] = self.unit_data[i]["OC"]
                    if self.trunc == False:
                        print("Battle-shock test passed!")
                else:
                    battleSh = True
                    if self.trunc == False:
                        print("Battle-shock test failed")
                    self.modelOC[i] = 0
                    if action["use_cp"] == 1 and action["cp_on"] == i:
                        if self.modelCP - 1 >= 0:
                            battleSh = False
                            reward += 0.5
                            self.modelCP -= 1
                            if self.trunc == False:
                                self.model[i] = self.unit_data[i]["OC"]
                                print("Used Insane Bravery Stratagem to pass Battle Shock test")
                        else:
                            reward -= 0.5
            ## Heroic Intervention
            if action["use_cp"] == 4 and action["cp_on"] == i:
                if self.modelCP - 2 >= 0 and self.unitInAttack[i][0] == 0: # make sure current model is not in combat
                    for j in range(len(self.enemyInAttack)):
                        if self.enemyInAttack[j][0] == 1 and distance(self.unit_coords[i], self.enemy_coords[j]) >= 6:
                            self.unitInAttack[i][0] = 1
                            self.unitInAttack[i][1] = j

                            self.unitInAttack[self.enemyInAttack[j][1]][0] = 0
                            self.unitInAttack[self.enemyInAttack[j][1]][1] = 0

                            self.unit_coords[i][0] = self.enemy_coords[j][0] + 1
                            self.unit_coords[i][1] = self.enemy_coords[j][1] + 1
                            self.unit_coords[i] = bounds(self.unit_coords[i], self.b_len, self.b_hei)

                            self.enemyInAttack[j][1] = i
                            self.modelCP -= 2
                            break
                            reward += 0.5
                            
                    reward += 0.5
                else:
                    reward -= 0.5

            if self.unitInAttack[i][0] == 0 and self.unit_health[i] > 0:
                max_move = dice()+self.unit_data[i]["Movement"]
                # set specific movement length
                label = "move_num_"+str(i)
                if action[label] >= max_move:
                    movement = max_move
                elif action[label] < max_move:
                    movement = action[label]

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
                if self.trunc == False:
                    if action["move"] == 0:
                        print("Model unit", modelName, "moved", movement, "inches downward")
                    elif action["move"] == 1:
                        print("Model unit", modelName, "moved", movement, "inches upward")
                    elif action["move"] == 2:
                        print("Model unit", modelName, "moved", movement, "inches left")
                    elif action["move"] == 3:
                        print("Model unit", modelName, "moved", movement, "inches right")
                    elif action["move"] == 4:
                        print("Model unit", modelName, "did not move")
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
                    elif battleSh != False:
                        if self.trunc == False:
                            print("This unit is BattleShocked, no stratagems can be used on it")
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
                                
                            dmg, modHealth = attack(self.unit_health[i], self.unit_weapon[i], self.unit_data[i], self.enemy_health[idOfE], self.enemy_data[idOfE], effects = effect)
                            self.enemy_health[idOfE] = modHealth
                            reward += 0.2
                            if self.trunc == False:
                                print("Model Unit",modelName,"shoots Enemy Unit",idOfE+11,sum(dmg),"times")
                            else:
                                self.modelUpdates+="Model Unit {} shoots Enemy Unit {} {} times\n".format(modelName, idOfE+11, sum(dmg))
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
                        else:
                            self.modelUpdates+="Model unit {} started attack with Enemy Unit {}\n".format(modelName, j+11)
                        self.unitInAttack[i][0] = 1
                        self.unitInAttack[i][1] = j

                        self.unit_coords[i][0] = self.enemy_coords[j][0] + 1
                        self.unit_coords[i][1] = self.enemy_coords[j][1] + 1
                        self.unit_coords[i] = bounds(self.unit_coords[i], self.b_len, self.b_hei)

                        dmg, modHealth = attack(self.unit_health[i], self.unit_melee[i], self.unit_data[i], self.enemy_health[idOfE], self.enemy_data[idOfE], rangeOfComb="Melee", effects=effect)
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
                    elif battleSh != False:
                        if self.trunc == False:
                            print("This unit is Battle shocked, stratagems can not be used")
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
                    dmg, modHealth = attack(self.unit_health[i], self.unit_melee[i], self.unit_data[i], self.enemy_health[idOfE], self.enemy_data[idOfE], rangeOfComb="Melee", effects=effect)
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
                    else:
                        self.modelUpdates+="Model Unit {} pulled out of fight with Enemy unit {}\n".format(modelName, idOfE+11)
                    
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


        self.enemyStrat["overwatch"] = -1
        self.enemyStrat["smokescreen"] = -1

        for i in range(len(self.modelOnOM)):
            if self.enemyOnOM[i] != -1 and self.modelOnOM[i] != -1:
                if self.enemyOC[self.enemyOnOM[i]] < self.modelOC[self.modelOnOM[i]]:
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
                        if self.enemyOC[self.enemyOnOM[i]] > self.modelOC[self.modelOnOM[i]]:
                            self.enemyVP += 1
                        elif self.enemyOC[self.enemyOnOM[i]] < self.modelOC[self.modelOnOM[i]]:
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
                    if self.enemyOC[self.enemyOnOM[self.relic]] > self.modelOC[self.modelOnOM[self.relic]]:
                        self.enemyVP += 6
                    elif self.enemyOC[self.enemyOnOM[self.relic]] < self.modelOC[self.modelOnOM[self.relic]]:
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
            if self.playType == False:
                if self.vicCond == 1:
                    print("Victory Condition rolled: Slay and Secure")
                elif self.vicCond == 2:
                    print("Victory Condition rolled: Ancient Relic")
                elif self.vicCond == 3:
                    print("Victory Condition rolled: Domination")
            else:
                if self.vicCond == 1:
                    sendToGUI("Victory Condition rolled: Slay and Secure")
                elif self.vicCond == 2:
                    sendToGUI("Victory Condition rolled: Ancient Relic")
                elif self.vicCond == 3:
                    sendToGUI("Victory Condition rolled: Domination")
        if self.playType == False:
            print(self.get_info())
        else:
            info = self.get_info()
            moreInfo = "Model Unit Health: {}, Player Unit Health: {}\nModel CP: {}, Player CP: {}\nModel VP: {}, Player VP: {}\n".format(info["model health"], info["player health"], info["modelCP"], info["playerCP"], info["model VP"], info["player VP"])

        if self.playType != False:
            if self.modelUpdates != "":
                sendToGUI(moreInfo+self.modelUpdates+"\nWould you like to continue: ")
            else:
                sendToGUI(moreInfo+"\nWould you like to continue: ")
            ans = recieveGUI()
            response = False
            while response == False:
                if ans.lower() == "y" or ans.lower() == "yes":
                    response = True
                    self.modelUpdates = ""
                elif ans.lower() == "n" or ans.lower() == "no":
                    self.game_over = True
                    info = self.get_info
                    return self.game_over, info
                else:
                    sendToGUI("Its a yes or no question dude...: ")
                    ans = recieveGUI()

        for i in range(len(self.enemy_health)):
            
            playerName = i+11
            if self.playType == False:
                print("For unit", playerName)
            else:
                sendToGUI("For unit {}".format(playerName))
            battleSh = False
            if isBelowHalfStr(self.enemy_data[i],self.enemy_health[i]) == True and self.unit_health[i] > 0:
                if self.playType == False:
                    print("This unit is Battle-shocked, starting test...")
                    print("Rolling 2D6...")
                    diceRoll = dice(num=2)
                    print("You rolled", diceRoll[0], diceRoll[1])
                else:
                    diceRoll = dice(num=2)
                    sendToGUI("This unit is Battle-shocked, starting test...\nRolling 2D6...\nYou rolled: {} and {}".format(diceRoll[0], diceRoll[1]))
                if sum(diceRoll) >= self.enemy_data[i]["Ld"]:
                    if self.playType == False:
                        print("Battle-shock test passed!")
                    else:
                        sendToGUI("Battle-shock test passed!")
                    self.enemyOC[i] = self.enemy_data[i]["OC"]
                else:
                    battleSh = True
                    if self.playType == False:
                        print("Battle-shock test failed")
                    else:
                        sendToGUI("Battle-shock test failed")
                    response = False
                    self.enemyOC[i] = 0
                    if self.enemyCP -1 >= 0:
                        if self.playType == False:
                            strat = input("Would you like to use the Insane Bravery Strategem? (y/n): ")
                        else:
                            sendToGUI("Would you like to use the Insane Bravery Strategem for Unit {}? (y/n): ".format(playerName))
                            strat = recieveGUI()
                        while response == False:
                            if strat.lower() == "y" or strat.lower() == "yes":
                                response = True
                                battleSh = False
                                self.enemyCP -= 1
                                self.enemyOC[i] = self.enemy_data[i]["OC"]
                            elif strat.lower() == "n" or strat.lower() == "no":
                                response = True
                            elif strat.lower() == "quit":
                                self.game_over = True
                                info = self.get_info()
                                return self.game_over, info
                            elif strat.lower() == "?" or strat.lower() == "help":
                                if self.playType == False:
                                    print("The Insane Bravery Stratagem costs 1 Command Point and is used when a unit fails a Battle-Shock Test. If used it treats the unit as if it passed.")
                                    strat = input("Would you like to use the Insane Bravery Stratagem? (y/n): ")
                                else:
                                    sendToGUI("The Insane Bravery Stratagem costs 1 Command Point and is used when a unit fails a Battle-Shock Test. If used it treats the unit as if it passed.\nWould you like to use the Insane Bravery Stratagem? (y/n): ")
                                    strat = recieveGUI()
                            else:
                                if self.playType == False:
                                    strat = input("Valid answers are: y, yes, n, and no: ")
                                else:
                                    sendToGUI("Valid answers are: y, yes, n, and no: ")
                                    strat = recieveGUI()
            if self.enemyCP - 2 >= 0 and self.enemyInAttack[i][0] == 0: 
                response = False
                if self.playType == False:
                    strat = input("Would you like to use the Heroic Intervention Stratagem? (y/n): ")
                else:
                    sendToGUI("Would you like to use the Heroic Intervention Stratagem for Unit {}? (y/n): ".format(playerName))
                    strat = recieveGUI()
                while response == False:
                    if strat.lower() == "y" or strat.lower() == "yes":
                        response = True
                        for j in range(len(self.unitInAttack)):
                            if self.unitInAttack[j][0] == 1 and distance(self.enemy_coords[i], self.unit_coords[j]) >= 6:
                                self.enemyInAttack[i][0] = 1
                                self.enemyInAttack[i][1] = j

                                self.enemyInAttack[self.enemyInAttack[j][1]][0] = 0
                                self.enemyInAttack[self.enemyInAttack[j][1]][1] = 0

                                self.enemy_coords[i][0] = self.enemy_coords[j][0] + 1
                                self.enemy_coords[i][1] = self.enemy_coords[j][1] + 1
                                self.enemy_coords[i] = bounds(self.unit_coords[i], self.b_len, self.b_hei)

                                self.unitInAttack[j][1] = i
                                self.enemyCP -= 2

                                if self.playType == False:
                                    print("Heroic Intervention Successfully used!")
                                else:
                                    sendToGUI("Heroic Intervention Successfully used!")
                                break
                    elif strat.lower() == "n" or strat.lower() == "no":
                        response = True
                    elif strat.lower() == "quit":
                        self.game_over = True
                        info = self.get_info
                        return self.game_over, info
                    elif strat.lower() == "?" or strat.lower() == "help":
                        if self.playType == False:
                            print("The Heroic Intervention strategem allows the player to choose an enemy unit within 6 inches and charge them")
                            strat = input("Would you like to use the Heroic Intervention Stratagem? (y/n): ")
                        else:
                            sendToGUI("The Heroic Intervention strategem allows the player to choose an enemy unit within 6 inches and charge them\nWould you like to use the Heroic Intervention Stratagem? (y/n): ")
                            strat = recieveGUI()
                    else:
                        if self.playType == False:
                            strat = input("Valid answers are: y, yes, n, and no: ")
                if self.enemyInAttack[i][0] != 1:
                    if self.playType == False:
                        print("Heroic Intervention failed")
                    else:
                        sendToGUI("Heroic Intervention failed")

            if self.enemyInAttack[i][0] == 0 and self.enemy_health[i] > 0:

                self.enemy_coords[i] = bounds(self.enemy_coords[i], self.b_len, self.b_hei)
                for j in range(len(self.enemy_health)):
                    if self.enemy_coords[i] == self.unit_coords[j]:
                        self.enemy_coords[i][0] -= 1

                self.updateBoard()
                self.showBoard()
                if self.playType == False:
                    print("Take a look at board.txt or click the Show Board button in the GUI to view the current board")
                    print("If you would like to end the game type 'quit' into the prompt")
                    dire = input("Enter the direction of movement (up, down, left, right, none (no move)): ")
                else:
                    sendToGUI("Take a look at board.txt or click the Show Board button in the GUI to view the current board\nIf you would like to end the game type 'quit' into the prompt\nEnter the direction of movement for Unit {} (up, down, left, right, none (no move)): ".format(playerName))
                    dire = recieveGUI()
                if dire.lower() == "quit":
                    self.game_over = True
                    info = self.get_info()
                    return self.game_over, info
                if dire.lower() != "none":
                    if self.playType == False:
                        print("Rolling 1 D6...")
                        roll = dice()
                        print("You rolled a", roll)
                    else:
                        roll = dice()
                        sendToGUI("Rolling 1 D6...\nYou rolled a {}".format(dice))
                    movement = roll+self.unit_data[i]["Movement"]
                    if self.playType == False:
                        move_len = input("What how many inches would you like to move your unit: ")
                    else:
                        inp = "How many inches would you like to move your unit (Max: " + str(movement) + "): "
                        sendToGUI(inp)
                        move_len = recieveGUI()
                    response = False
                    while response == False:
                        if is_num(move_len) == True:
                            if int(move_len) <= movement:
                                move_num = int(move_len)
                                response = True
                            else:
                                if self.playType == False:
                                    move_len = input("Not in range, try again: ")
                                else:
                                    sendToGUI("Not in range, try again: ")
                                    move_len = recieveGUI()
                        elif move_len.lower() == "quit" or move_len.lower() == "q":
                            self.game_over = True
                            info = self.get_info()
                            return self.game_over, info
                        else:
                            if self.playType == False:
                                move_len = input("Not a number, try again: ")
                            else:
                                sendToGUI("Not a number, try again: ")
                                move_len = recieveGUI()
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
                        if self.playType == False:
                            dire = input("Not a valid response (up, down, left, right):")
                        else:
                            sendToGUI("Not a valid response (up, down, left, right):")
                            dire = recieveGUI()
                        response = False
                    

            # staying in bounds

                self.enemy_coords[i] = bounds(self.enemy_coords[i], self.b_len, self.b_hei)
                for j in range(len(self.enemy_health)):
                    if self.enemy_coords[i] == self.unit_coords[j]:
                        self.enemy_coords[i][0] -= 1

                self.updateBoard()
                self.showBoard()

                if self.enemyCP - 1 >= 0 and battleSh == False:
                    response = False
                    if self.playType == False:
                        strat = input("Would you like to use the Fire Overwatch Stratagem? (y/n): ")
                    else:
                        sendToGUI("Would you like to use the Fire Overwatch Stratagem? (y/n): ")
                        strat = recieveGUI()
                    while response == False:
                        if strat.lower() == "y" or strat.lower() == "yes":
                            response = True
                            self.enemyStrat["overwatch"] = i
                            self.enemyCP -= 1
                        elif strat.lower() == "n" or strat.lower() == "no":
                            response = True
                        elif strat.lower() == "?" or strat.lower() == "help":
                            if self.playType == False:
                                print("The Fire Overwatch Stratagem costs 1 Command Point and if your unit and the opposing unit are 21 inches from each other during their Movement/Charge Phase then your unit can shoot that enemy unit as if it were your Shooting phase")
                                strat = input("Would you like to use the Fire Overwatch Stratagem? (y/n): ")
                            else:
                                sendToGUI("The Fire Overwatch Stratagem costs 1 Command Point and if your unit and the opposing unit are 21 inches from each other during their Movement/Charge Phase then your unit can shoot that enemy unit as if it were your Shooting phase\nWould you like to use the Fire Overwatch Stratagem? (y/n): ")
                                strat = recieveGUI()
                        elif strat.lower() == "quit":
                            self.game_over = True
                            info = self.get_info()
                            return self.game_over, info
                        else:
                            if self.playType == False:
                                strat = input("Valid answers are: y, yes, n, and no: ")
                            else:
                                sendToGUI("Valid answers are: y, yes, n, and no: ")
                                strat = recieveGUI()

                if self.modelStrat["overwatch"] != -1 and self.unit_weapon[self.modelStrat["overwatch"]] != "None":
                    if distance(self.enemy_coords[i], self.unit_coords[self.modelStrat["overwatch"]]) <= self.unit_weapon[self.modelStrat["overwatch"]]["Range"]:
                        dmg, modHealth = attack(self.unit_health[self.modelStrat["overwatch"]], self.unit_weapon[self.modelStrat["overwatch"]], self.unit_data[self.modelStrat["overwatch"]], self.enemy_health[i], self.enemy_data[i])
                        self.enemy_health[i] = modHealth
                        if self.playType == False:
                            print("Model unit", self.modelStrat["overwatch"]+21, "successfully hit player unit", i+11, "for", sum(dmg), "damage using the overwatch strategem")
                        else:
                            sendToGUI("Model unit {} successfully hit player unit {} for {} damage using the overwatch stratagem".format(self.modelStrat["overwatch"]+21, i+11, sum(dmg)))
                        self.modelStrat["overwatch"] = -1

                self.updateBoard()
                self.showBoard()
                
                # shooting phase (if eligible)
                if self.enemy_weapon[i] != "None":
                    if self.playType == False:
                        print("Beginning shooting phase!")
                    else:
                        sendToGUI("Beginning shooting phase!")
                    shootAble = np.array([])
                    for j in range(len(self.unit_health)):
                        if distance(self.enemy_coords[i], self.unit_coords[j]) <= self.enemy_weapon[i]["Range"] and self.unit_health[j] > 0 and self.unitInAttack[j][0] == 0:
                        # save index of available units to shoot
                            shootAble = np.append(shootAble, j)

                    if len(shootAble) > 0 and self.enemy_weapon[i] != "None":
                        response = False
                        while response == False:
                            if self.playType == False:
                                shoot = input("Select which enemy unit you would like to shoot ({}): ".format(shootAble+21))
                            else:
                                sendToGUI("Select which enemy unit you would like to shoot ({}) with Unit {}: ".format(shootAble+21, playerName))
                                shoot = recieveGUI()
                            if is_num(shoot) == True and int(shoot)-21 in shootAble:
                                idOfE = int(shoot)-21
                                if self.modelStrat["smokescreen"] != -1 and self.modelStrat["smokescreen"] == idOfE:
                                    if self.playType == False:
                                        print("Model unit", self.modelStrat["smokescreen"]+21, "used the Smokescreen Strategem")
                                    else:
                                        sendToGUI("Model unit {} used the Smokescreen Stratagem".format(self.modelStrat["smokescreen"]+21))
                                    self.modelStrat["smokescreen"] = -1
                                    effect = "benefit of cover"
                                else:
                                    effect = None
                                dmg, modHealth = attack(self.enemy_health[i], self.enemy_weapon[i], self.enemy_data[i], self.unit_health[idOfE], self.unit_data[idOfE], effects = effect)
                                self.unit_health[idOfE] = modHealth
                                if self.playType == False:
                                    print("Player Unit",playerName,"shoots Model Unit",idOfE+21,sum(dmg),"times")
                                else:
                                    sendToGUI("Player Unit {} shoots Model Unit {} {} times".format(playerName, idOfE+21, sum(dmg)))
                                response = True
                            elif shoot == "quit":
                                self.game_over = True
                                info = self.get_info()
                                return self.game_over, info
                            else:
                                if self.playType == False:
                                    print("Not an available unit")
                                else:
                                    sendToGUI("Not an available unit")
                    
                else:
                    if self.playType == False:
                        print("No available units to attack")
                    else:
                        sendToGUI("No available units to attack")


                # Charge (if applicable)
                if self.playType == False:
                    print("Beginning Charge phase!")
                else:
                    sendToGUI("Beginning Charge phase!")
                charg = np.array([])
                for j in range(len(self.unit_health)):
                    if distance(self.unit_coords[j], self.enemy_coords[i]) <= 12 and self.unitInAttack[j][0] == 0 and self.unit_health[j] > 0:
                        charg = np.append(charg, j)

                if len(charg) > 0:
                    response = False
                    while response == False:
                        if self.playType == False:
                            attk = input("Select while enemy you would like to charge ({}): ".format(charg+21))
                        else:
                            sendToGUI("Select while enemy you would like to charge ({}) with Unit {}: ".format(charg+21, playerName))
                            attk = recieveGUI()
                            
                        if is_num(attk) == True and int(attk)-21 in charg:
                            response = True
                            j = int(attk)-21
                            if self.playType == False:
                                print("Rolling 2 D6...")
                                roll = dice(num=2)
                                print("You rolled a", roll[0], "and", roll[1])
                            else:
                                sendToGUI("Rolling 2 D6...")
                                roll = dice(num=2)
                                sendToGUI("You rolled a {} and {}".format(roll[0], roll[1]))
                                
                            if distance(self.enemy_coords[i], self.unit_coords[j]) - sum(roll) <= 5:
                                if self.playType == False:
                                    print("Player Unit", playerName, "Successfully charged Model Unit", j+21)
                                else:
                                    sendToGUI("Player Unit {} Successfully charged Model Unit {}".format(playerName, j+21))
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
                                if self.playType == False:
                                    print("Player Unit {} Failed to charge Model Unit {}".format(playerName, j+21))
                                else:
                                    sendToGUI("Player Unit {} Failed to charge Model Unit {}".format(playerName, j+21))
                        
                        elif attack == "quit":
                            self.game_over = True
                            info = self.get_info()
                            return self.game_over, info
                        else:
                            if self.playType == False:
                                print("Not an available unit")
                            else:
                                sendToGUI("Not an available unit")
                else:
                    if self.playType == False:
                        print("No available units to attack")
                    else:
                        sendToGUI("No available units to attack")
                if self.enemyCP - 1 >= 0 and battleSh == False:    
                    response = False
                    if self.playType == False:
                        strat = input("Would you like to use the Smokescreen Stratagem for this unit? (y/n): ")
                    else:
                        sendToGUI("Would you like to use the Smokescreen Stratagem for this unit? (y/n): ")
                        strat = recieveGUI()
                    while response == False:
                        if strat.lower() == "y" or strat.lower() == "yes":
                            self.enemyStrat["smokescreen"] = i 
                            response = True
                        elif strat.lower() == "n" or strat.lower() == "no":
                       	    response = True
                        elif strat.lower() == "?" or strat.lower() == "help":
                            if self.playType == False:
                                print("The Smokescreen Stratagem costs 1 Command Point and when used all models in the unit have the Benefit of Cover and the Stealth ability")
                                strat = input("Would you like to use the Smokescreen Stratagem? (y/n): ")
                            else:
                                sendToGUI("The Smokescreen Stratagem costs 1 Command Point and when used all models in the unit have the Benefit of Cover and the Stealth ability\nWould you like to use the Smokescreen Stratagem? (y/n): ")
                                strat = recieveGUI()
                        else:
                            if self.playType == False:
                                strat = input("It's a yes or no question dude")
                            else:
                                sendToGUI("It's a yes or no question dude")
                                strat = recieveGUI()
            
                for j in range(len(self.coordsOfOM)):
                    if distance(self.coordsOfOM[j], self.enemy_coords[i]) <= 5:
                        self.enemyOnOM[j] = i

            elif self.enemyInAttack[i][0] == 1 and self.enemy_health[i] > 0:
                idOfE = self.enemyInAttack[i][1]
                response = False
                while response == False:
                    if self.playType == False:
                        fallB = input("Would you like Unit {} to fallback? (y/n): ".format(playerName))
                    else:
                        sendToGUI("Would you like Unit {} to fallback? (y/n): ".format(playerName))
                        fallB = recieveGUI()
                    if fallB.lower() == "n" or fallB.lower() == "no":
                        response = True
                        if self.playType == False:
                            print("Player Unit", playerName, "Is attacking Model Unit", idOfE+21)
                        else:
                            sendToGUI("Player Unit {} Is attacking Model Unit {}".format(playerName, idOfE+21))
                        dmg, modHealth = attack(self.enemy_health[i], self.enemy_melee[i], self.enemy_data[i], self.unit_health[idOfE], self.unit_data[idOfE], rangeOfComb="Melee")
                        self.unit_health[idOfE] = modHealth
                        if self.unit_health[idOfE] <= 0:
                            if self.playType == False:
                                print("Model Unit", idOfE+21, "has been killed")
                            else:
                                sendToGUI("Model Unit {} has been killed".format(idOfE+21))
                            self.enemyInAttack[i][0] = 0
                            self.enemyInAttack[i][1] = 0

                            self.unitInAttack[idOfE][0] = 0
                            self.unitInAttack[idOfE][1] = 0
                    elif fallB.lower() == "y" or fallB.lower() == "yes":
                        response = True
                        if self.playType == False:
                            print("Player Unit", playerName,"fell back from Enemy unit", idOfE+21)
                        else:
                            sendToGUI("Player Unit {} fell back from Enemy unit {}".format(playerName, idOfE+21))
                        
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
                        if self.playType == False:
                            fallB = input("It's a yes or no question dude")
                        else:
                            sendToGUI("It's a yes or no question dude")
                            fallB = recieveGUI()
            
            elif self.enemy_health[i] == 0:
                if self.playType == False:
                    print("Unit", playerName, "is dead")
                else:
                    sendToGUI("Unit {} is dead".format(playerName))

        if self.modelStrat["overwatch"] != -1:
            self.modelStrat["overwatch"] = -1
        if self.modelStrat["smokescreen"] != -1:
            self.modelStrat["smokescreen"] = -1

        for i in range(len(self.enemyOnOM)):
            if self.enemyOnOM[i] != -1 and self.modelOnOM[i] != -1:
                if self.enemyOC[self.enemyOnOM[i]] > self.modelOC[self.modelOnOM[i]]:
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
        self.render(mode = "test")
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

    def render(self, mode='train'):
        
        fig = plt.figure()
        ax = fig.add_subplot()
        fig.subplots_adjust(top=0.85)
        if mode == 'train':
            title = "Turn "+str(self.iter)+" Lifetime "+str(self.restarts)
        else:
            title = "Turn "+str(self.iter) 
        fig.suptitle(title)

        health = "Model Unit health: {}, CP: {}; Enemy Unit health: {}, CP {}\nVP {}".format(self.unit_health, self.modelCP, self.enemy_health, self.enemyCP, [self.modelVP, self.enemyVP])
        ax.set_title(health)
        
        x1 = np.linspace(0,self.b_len,10)
        y1 = np.zeros(10)
        x2 = np.zeros(10)
        y2 = np.linspace(0, self.b_hei,10)
        ax.set_ylim(-5,self.b_len+5)
        ax.set_xlim(-3,self.b_hei*1.65)
        ax.plot(y1,x1,color="black")
        ax.plot(y2,x2,color="black")
        ax.plot(y1+self.b_hei,x1,color="black")
        ax.plot(y2,x2+self.b_len,color="black")

        for i in range(len(self.unit_health)):
            if i == 0:
                ax.plot(self.unit_coords[i][1],self.unit_coords[i][0], 'bo', label="Model Unit")
            else:
                ax.plot(self.unit_coords[i][1],self.unit_coords[i][0], 'bo')
        for i in range(len(self.enemy_coords)):
            if i == 0:
                ax.plot(self.enemy_coords[i][1],self.enemy_coords[i][0], 'go', label="Player Unit")
            else:
                ax.plot(self.enemy_coords[i][1],self.enemy_coords[i][0], 'go')
        
        for i in range(len(self.coordsOfOM)):
            if i == 0:
                ax.plot(self.coordsOfOM[i][1], self.coordsOfOM[i][0], 'o', color="black", label="Objective Marker(s)")
            elif i == self.relic and self.vicCond == 2:
                ax.plot(self.coordsOfOM[i][1], self.coordsOfOM[i][0], 'o', color="gold", label="Relic") 
            else:
                ax.plot(self.coordsOfOM[i][1], self.coordsOfOM[i][0], 'o', color="black")

        ax.legend(loc = "right")
        if mode == "train":
            fileName = "display/"+str(self.restarts)+"_"+str(self.iter)+".png"
        else:
            fileName = "gui/build/img/board.png"
            fig.savefig("gui/img/board.png")
        fig.savefig(fileName)
        ax.cla()
        plt.close()

        return self.board

    def showBoard(self):
        board = self.returnBoard()
        np.savetxt("board.txt", board.astype(int), fmt="%i", delimiter=",")
        self.render(mode="play")

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
