import gym
from gym import spaces
import numpy as np
import matplotlib.pyplot as plt
import os

class Warhammer40kEnv(gym.Env):
    def __init__(self, enemy, model, b_len, b_hei):
        
        savePath = "display/"
        for fil in os.listdir(savePath):
            os.remove(os.path.join(savePath, fil))

        self.action_space = spaces.Dict({
            'move': spaces.Discrete(4),  # Four directions: Up, Down, Left, Right
            'attack': spaces.Discrete(2),  # Two attack options: Engage Attack, Leave Attack/move
        })

        # Initialize game state + board
        self.iter = 0
        self.restarts = 0
        self.b_len = b_len
        self.b_hei = b_hei
        self.board = np.zeros((self.b_len,self.b_hei))
        self.unit_weapon = []
        self.enemy_weapon = []
        self.unit_data = []
        self.enemy_data = []
        self.unit_coords = []
        self.enemy_coords = []
        self.unit_health = []
        self.enemy_health = []
        self.game_over = False
        self.unitInAttack = []
        self.enemyInAttack = []

        for i in range(len(enemy)):
            self.enemy_weapon.append(enemy[i].showWeapon())
            self.enemy_data.append(enemy[i].showUnitData())
            self.enemy_coords.append([enemy[i].showCoords()[0], enemy[i].showCoords()[1]])
            self.enemy_health.append(enemy[i].showUnitData()["W"]*enemy[i].showUnitData()["#OfModels"])
            self.enemyInAttack.append([0,0])   # in attack, index of enemy attacking

        for i in range(len(model)):
            self.unit_weapon.append(model[i].showWeapon())
            self.unit_data.append(model[i].showUnitData())
            self.unit_coords.append([model[i].showCoords()[0], model[i].showCoords()[1]])
            self.unit_health.append(model[i].showUnitData()["W"]*model[i].showUnitData()["#OfModels"])
            self.unitInAttack.append([0,0])   # in attack, index of enemy attacking

        obsSpace = (len(model)*3)+(len(enemy)*3)+1

        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obsSpace,), dtype=np.float32)  # 7-dimensional observation space

    def get_info(self):
        return {"unit health":self.unit_health, "enemy health": self.enemy_health, "in attack": self.unitInAttack}
    
    def distance(self, p1, p2):
        return np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

    def dice(self, min = 1, max = 6, num=1):
        rolls = np.array([])
        if num == 1:
            return np.random.randint(min, max)
        else:
            for i in range(num):
                rolls = np.append(rolls,np.random.randint(min, max))
            return rolls

    def bounds(self, coords):
        if coords[0] <= 0:
            coords[0] = 0
        if coords[1] <= 0:
            coords[1] = 0
        if coords[0] >= self.b_len:
            coords[0] = self.b_len-1
        if coords[1] >= self.b_hei:
            coords[1] = self.b_hei-1
        return coords

    def attack(self, attackerHealth, attackerWeapon, attackerData, attackeeHealth, attackeeData, rangeOfComb="Ranged"):
        rolls = self.dice(num=attackerData["#OfModels"])
        hits = 0
        if type(rolls) != type(1):
            for k in range(len(rolls)):
                if rolls[k] <= attackerWeapon["BS"]:
                    hits+=1
        else:
            if rolls <= attackerWeapon["BS"]:
                hits+=1
        # wound rolls
        dmg = np.array([])
        for k in range(hits):
            if attackerWeapon["S"] >= attackeeData["T"]*2:
                if self.dice() <= 2:
                    dmg = np.append(dmg, attackerWeapon["Damage"])
            elif attackerWeapon["S"] > attackeeData["T"]:
                if self.dice() <= 3:
                    dmg = np.append(dmg, attackerWeapon["Damage"])
            elif attackerWeapon["S"] == attackeeData["T"]:
                if self.dice() <= 4:
                    dmg = np.append(dmg, attackerWeapon["Damage"])
            elif attackerWeapon["S"]/2 <= attackeeData["T"]:
                if self.dice() <= 5:
                    dmg = np.append(dmg, attackerWeapon["Damage"])
            elif attackerWeapon["S"] < attackeeData["T"]:
                if self.dice() == 6:
                    dmg = np.append(dmg, attackerWeapon["Damage"])
        # saving throws
        for k in range(len(dmg)):
            if self.dice()-attackerWeapon["AP"] > attackeeData["Sv"]:
                dmg[k] = 0
        # allocating damage
        for k in dmg:
            attackeeHealth -= k
            if attackeeHealth < 0:
                attackeeHealth = 0
        return dmg, attackeeHealth

    def reset(self):
        self.iter = 0
        self.restarts += 1
        self.board = np.zeros((self.b_len,self.b_hei))
        self.enemy_coords = []
        self.unit_coords = []
        self.enemy_health = []
        self.unit_health = []
        self.enemyInAttack = []
        self.unitInAttack = []
        for i in range(len(self.enemy_data)):
            self.enemy_coords.append([np.random.randint(0,self.b_len), np.random.randint(0,self.b_hei)])
            self.enemy_health.append(self.enemy_data[i]["W"]*self.enemy_data[i]["#OfModels"])
            self.enemyInAttack.append([0,0])   # in attack, index of enemy attacking

        for i in range(len(self.unit_data)):
            self.unit_coords.append([np.random.randint(0,self.b_len), np.random.randint(0,self.b_hei)])
            self.unit_health.append(self.unit_data[i]["W"]*self.unit_data[i]["#OfModels"])
            self.unitInAttack.append([0,0])   # in attack, index of enemy attacking
        
        self.game_over = False
        self.current_action_index = 0
        info = self.get_info()
        return self._get_observation(), info

    def enemyTurn(self):
        for i in range(len(self.enemy_health)):
            #print(i)
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

                movement = self.dice()+self.enemy_data[i]["Movement"]
                if self.distance(self.unit_coords[idOfM], [self.enemy_coords[i][0], self.enemy_coords[i][1] - movement]) < self.distance(self.unit_coords[idOfM], self.enemy_coords[i]):
                    self.enemy_coords[i][1] -= movement
                elif self.distance(self.unit_coords[idOfM], [self.enemy_coords[i][0], self.enemy_coords[i][1] + movement]) < self.distance(self.unit_coords[idOfM], self.enemy_coords[i]):
                    self.enemy_coords[i][1] += movement
                elif self.distance(self.unit_coords[idOfM], [self.enemy_coords[i][0] - movement, self.enemy_coords[i][1]]) < self.distance(self.unit_coords[idOfM], self.enemy_coords[i]):
                    self.enemy_coords[i][0] -= movement
                elif self.distance(self.unit_coords[idOfM], [self.enemy_coords[i][0] + movement, self.enemy_coords[i][1]]) < self.distance(self.unit_coords[idOfM], self.enemy_coords[i]):
                    self.enemy_coords[i][0] += movement

                # staying in bounds

                self.enemy_coords[i] = self.bounds(self.enemy_coords[i])
                for j in range(len(self.unit_health)):
                    if self.enemy_coords[i] == self.unit_coords[j]:
                        self.enemy_coords[i][0] -= 1

                # Shooting phase (if applicable)
                for j in range(len(self.unit_health)):
                    if self.distance(self.enemy_coords[i], self.unit_coords[j]) <= self.enemy_weapon[i]["Range"]:
                        idOfM = j
                        dmg, modHealth = self.attack(self.enemy_health[i], self.enemy_weapon[i], self.enemy_data[i], self.unit_health[idOfM], self.unit_data[idOfM])
                        self.unit_health[idOfM] = modHealth
                        print("Enemy Unit",i,"shoots Model Unit",idOfM,sum(dmg),"times")
                # Charging (if applicable)
                for j in range(len(self.unit_health)):
                    if self.distance(self.enemy_coords[i], self.unit_coords[j]) <= 12 and self.unitInAttack[j][0] == 0:
                        if self.distance(self.enemy_coords[j], self.unit_coords[i]) - sum(self.dice(num=2)) <= 5:
                            print("Enemy unit", i,"started attack with Model unit", j)
                            self.unit_health[j] -= self.enemy_weapon[i]["Damage"]

                            self.enemy_coords[i][0] = self.unit_coords[j][0] + 1
                            self.enemy_coords[i][1] = self.unit_coords[j][1] + 1
                            self.enemy_coords[i] = self.bounds(self.enemy_coords[i])

                            self.unitInAttack[j][0] = 1
                            self.unitInAttack[j][1] = i

                            self.enemyInAttack[i][0] = 1
                            self.enemyInAttack[i][1] = j
                        break

            elif self.enemyInAttack[i][0] == 1 and self.enemy_health[i] > 0:
                decide = np.random.randint(0,10)
                idOfM = self.enemyInAttack[i][1]
                if decide == 5:
                    print("Enemy unit", i,"pulled out of fight with Model unit", idOfM)
                    self.enemy_coords[i][0] -= 7
                    self.enemy_coords[i] = self.bounds(self.enemy_coords[i])
                    self.unitInAttack[idOfM][0] = 0
                    self.unitInAttack[idOfM][1] = 0

                    self.enemyInAttack[i][0] = 0
                    self.enemyInAttack[i][1] = 0
                else:
                    dmg, modHealth = self.attack(self.enemy_health[i], self.enemy_weapon[i], self.enemy_data[i], self.unit_health[idOfM], self.unit_data[idOfM])
                    self.unit_health[idOfM] = modHealth
    
    def step(self, action):
        reward = 0
        for i in range(len(self.unit_health)):
            if self.unitInAttack[i][0] == 0 and self.unit_health[i] > 0:
                movement = self.dice()+self.unit_data[i]["Movement"]
                if action["move"] == 0:
                    self.unit_coords[i][1] -= movement
                elif action["move"] == 1:
                    self.unit_coords[i][1] += movement
                elif action["move"] == 2:
                    self.unit_coords[i][0] -= movement
                elif action["move"] == 3:
                    self.unit_coords[i][0] += movement

            # staying in bounds

                self.unit_coords[i] = self.bounds(self.unit_coords[i])
                for j in range(len(self.enemy_health)):
                    if self.unit_coords[i] == self.enemy_coords[j]:
                        self.unit_coords[i][0] -= 1

                # shooting phase (if eligible)

                for j in range(len(self.enemy_health)):
                    if self.distance(self.unit_coords[i], self.enemy_coords[j]) <= self.unit_weapon[i]["Range"]:
                        # hit rolls
                        idOfE = j
                        dmg, modHealth = self.attack(self.unit_health[i], self.unit_weapon[i], self.unit_data[i], self.enemy_health[idOfE], self.enemy_data[idOfE])
                        self.enemy_health[idOfE] = modHealth
                        print("Model Unit",i,"shoots Enemy Unit",idOfE,sum(dmg),"times")

                # Charge (if applicable)

                if action["attack"] == 1:
                    for j in range(len(self.enemy_health)):
                        if self.distance(self.enemy_coords[j], self.unit_coords[i]) <= 12 and self.enemyInAttack[j][0] == 0:
                            if self.distance(self.enemy_coords[j], self.unit_coords[i]) - sum(self.dice(num=2)) <= 5:
                                print("Model unit", i,"started attack with Enemy unit", j)
                                self.enemy_health[j] -= self.unit_weapon[i]["Damage"]
                                self.unitInAttack[i][0] = 1
                                self.unitInAttack[i][1] = j

                                self.unit_coords[i][0] = self.enemy_coords[j][0] + 1
                                self.unit_coords[i][1] = self.enemy_coords[j][1] + 1
                                self.unit_coords[i] = self.bounds(self.unit_coords[i])

                                self.enemyInAttack[j][0] = 1
                                self.enemyInAttack[j][1] = i

                                reward = 0.5
                            break
                        else:
                            reward = -0.5
            
            elif self.unitInAttack[i][0] == 1 and self.unit_health[i] > 0:
                reward = 0.1
                idOfE = self.unitInAttack[i][1]
                if action["attack"] == 1:
                    dmg, modHealth = self.attack(self.unit_health[i], self.unit_weapon[i], self.unit_data[i], self.enemy_health[idOfE], self.enemy_data[idOfE])
                    self.enemy_health[idOfE] = modHealth
                elif action["attack"] == 0:
                    print("Model unit", i,"pulled out of fight with Enemy unit", idOfE)
                    self.unit_coords[i][0] += self.unit_weapon[i]["Range"]+6
                    self.unitInAttack[i][0] = 0
                    self.unitInAttack[i][1] = 0

                    self.enemyInAttack[idOfE][0] = 0
                    self.enemyInAttack[idOfE][1] = 0

        for i in self.unit_health:
            if i < 0:
                i = 0
        
        for i in self.enemy_health:
            if i < 0:
                i = 0

        if sum(self.unit_health) <= 0 or sum(self.enemy_health) <= 0:
            self.game_over = True

        if self.game_over:
            reward += self._calculate_reward()

        self.iter += 1

        info = self.get_info()
        return self._get_observation(), reward, self.game_over, 0, info

    def updateBoard(self):
        self.board = np.zeros((self.b_len,self.b_hei))

        for i in range(len(self.unit_health)):
            self.unit_coords[i] = self.bounds(self.unit_coords[i])
            self.board[self.unit_coords[i][0]][self.unit_coords[i][1]] = 1

        for i in range(len(self.enemy_health)):
            self.enemy_coords[i] = self.bounds(self.enemy_coords[i])
            self.board[self.enemy_coords[i][0]][self.enemy_coords[i][1]] = 2

    def render(self, mode='human'):
        self.updateBoard()
        
        title = "Iteration "+str(self.iter)+" Lifetime "+str(self.restarts)
        plt.title(title)
        

        message = ""

        for i in range(len(self.unit_health)):
            if self.unit_health[i] <= 0:
                message += "Unit model "+str(i)+" is Dead "
            elif self.unitInAttack[i][0] == 0:
                message += "Unit model "+str(i)+" is Moving "
            elif self.unitInAttack[i][0] == 1:
                message += "Unit model "+str(i)+" is in Combat "
        plt.xlabel(message)
        x1 = np.linspace(0,self.b_len,10)
        y1 = np.zeros(10)
        x2 = np.zeros(10)
        y2 = np.linspace(0, self.b_hei,10)
        plt.plot(x1,y1,color="black")
        plt.plot(x2,y2,color="black")
        plt.plot(x1,y1+self.b_hei,color="black")
        plt.plot(x2+self.b_len,y2,color="black")
        for i in range(len(self.unit_health)):
            if i == 0:
                plt.plot(self.unit_coords[i][0],self.unit_coords[i][1], 'bo', label="Model Unit")
            else:
                plt.plot(self.unit_coords[i][0],self.unit_coords[i][1], 'bo')
        for i in range(len(self.enemy_health)):
            if i == 0:
                plt.plot(self.enemy_coords[i][0],self.enemy_coords[i][1], 'ro', label="Enemy Unit")
            else:
                plt.plot(self.enemy_coords[i][0],self.enemy_coords[i][1], 'ro')
        plt.legend()
        fileName = "display/"+str(self.restarts)+"_"+str(self.iter)+".png"
        plt.savefig(fileName)
        plt.cla()

        return self.board

    def close(self):
        pass

    def _get_observation(self):
        obs = []
        
        for i in range(len(self.unit_health)):
            obs.append(self.unit_health[i])
            obs.append(self.unit_coords[i][0])
            obs.append(self.unit_coords[i][1])

        for i in range(len(self.enemy_health)):
            obs.append(self.enemy_health[i])
            obs.append(self.enemy_coords[i][0])
            obs.append(self.enemy_coords[i][1])

        obs.append(int(self.game_over))

        return np.array(obs, dtype=np.float32)

    def _calculate_reward(self):
        if sum(self.unit_health) > 0:
            return 1.0
        else:
            return -1.0