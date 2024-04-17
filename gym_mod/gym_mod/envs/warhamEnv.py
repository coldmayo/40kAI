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
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(7,), dtype=np.float32)  # 7-dimensional observation space

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
            self.enemy_health.append(10)
            self.enemyInAttack.append([0,0])   # in attack, index of enemy attacking

        for i in range(len(model)):
            self.unit_weapon.append(model[i].showWeapon())
            self.unit_data.append(model[i].showUnitData())
            self.unit_coords.append([model[i].showCoords()[0], model[i].showCoords()[1]])
            self.unit_health.append(10)
            self.unitInAttack.append([0,0])   # in attack, index of enemy attacking

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
            self.enemy_health.append(10)
            self.enemyInAttack.append([0,0])   # in attack, index of enemy attacking

        for i in range(len(self.unit_data)):
            self.unit_coords.append([np.random.randint(0,self.b_len), np.random.randint(0,self.b_hei)])
            self.unit_health.append(10)
            self.unitInAttack.append([0,0])   # in attack, index of enemy attacking
        
        self.game_over = False
        self.current_action_index = 0
        info = self.get_info()
        return self._get_observation(), info

    def enemyTurn(self):
        for i in range(len(self.enemy_health)):
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

                for j in range(len(self.unit_health)):
                    if self.distance(self.enemy_coords[i], self.unit_coords[j]) <= self.enemy_weapon[i]["Range"] and self.unitInAttack[j][0] == 0:
                        self.unit_health[j] -= self.enemy_weapon[i]["Damage"]
                        self.unitInAttack[j][0] = 1
                        self.unitInAttack[j][1] = i

                        self.enemyInAttack[i][0] = 1
                        self.enemyInAttack[i][1] = j
                        break

            elif self.enemyInAttack[i][0] == 1 and self.enemy_health[i] > 0:
                decide = np.random.randint(0,30)
                idOfM = self.enemyInAttack[i][1]
                if decide == 5:
                    self.enemy_coords[i][0] -= 7
                    self.enemy_coords[i] = self.bounds(self.enemy_coords[i])
                    self.unitInAttack[idOfM][0] = 0
                    self.unitInAttack[idOfM][1] = 0

                    self.enemyInAttack[i][0] = 0
                    self.enemyInAttack[i][1] = 0
                else:
                    # hit rolls
                    rolls = self.dice(num=self.enemy_data[i]["#OfModels"])
                    hits = 0
                    for k in range(len(rolls)):
                        if rolls[k] <= self.enemy_weapon[i]["BS"]:
                            hits+=1
                    # wound rolls
                    dmg = np.array([])
                    for k in range(hits):
                        if self.enemy_weapon[i]["S"] >= self.unit_data[idOfM]["T"]*2:
                            if self.dice() <= 2:
                                dmg = np.append(dmg, self.enemy_weapon[i]["Damage"])
                        elif self.enemy_weapon[i]["S"] > self.unit_data[idOfM]["T"]:
                            if self.dice() <= 3:
                                dmg = np.append(dmg, self.enemy_weapon[i]["Damage"])
                        elif self.enemy_weapon[i]["S"] == self.unit_data[idOfM]["T"]:
                            if self.dice() <= 4:
                                dmg = np.append(dmg, self.enemy_weapon[i]["Damage"])
                        elif self.enemy_weapon[i]["S"]/2 <= self.unit_data[idOfM]["T"]:
                            if self.dice() <= 5:
                                dmg = np.append(dmg, self.enemy_weapon[idOfM]["Damage"])
                        elif self.enemy_weapon[i]["S"] < self.unit_data[idOfM]["T"]:
                            if self.dice() == 6:
                                dmg = np.append(dmg, self.enemy_weapon[i]["Damage"])
                    # saving throws
                    for k in range(len(dmg)):
                        if self.dice()-self.enemy_weapon[i]["AP"] > self.unit_data[idOfM]["Sv"]:
                            dmg[k] = 0
                    # allocating damage
                    for k in dmg:
                        self.unit_health[idOfM] -= k
                        if self.unit_health[idOfM] < 0:
                            self.unit_health[idOfM] = 0
    
    def step(self, action):
        reward = 0
        for i in range(len(self.unit_health)):
            if self.unitInAttack[i][1] == 0 and self.unit_health[i] > 0:
                movement = self.dice()+self.unit_data[i]["Movement"]
                reward = 0.1
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

                if action["attack"] == 1:
                    for j in range(len(self.enemy_health)):
                        if self.distance(self.enemy_coords[j], self.unit_coords[i]) <= self.unit_weapon[i]["Range"] and self.enemyInAttack[j][0] == 0:
                            self.enemy_health[j] -= self.unit_weapon[i]["Damage"]
                            self.unitInAttack[i][0] = 1
                            self.unitInAttack[i][1] = j

                            self.enemyInAttack[j][0] = 1
                            self.enemyInAttack[j][1] = i

                            reward = 0.1
                            break
                        else:
                            reward = -0.1
            
            elif self.unitInAttack[i][0] == 1 and self.unit_health[i] > 0:
                reward = 0.1
                idOfE = self.unitInAttack[i][1]
                if action["attack"] == 1:
                    # hit rolls
                    rolls = self.dice(num=self.unit_data[i]["#OfModels"])
                    hits = 0
                    for k in range(len(rolls)):
                        if rolls[k] <= self.unit_weapon[i]["BS"]:
                            hits+=1
                # wound rolls
                    dmg = np.array([])
                    for k in range(hits):
                        if self.unit_weapon[i]["S"] >= self.enemy_data[idOfE]["T"]*2:
                            if self.dice() <= 2:
                                dmg = np.append(dmg, self.unit_weapon[i]["Damage"])
                        elif self.unit_weapon[i]["S"] > self.enemy_data[idOfE]["T"]:
                            if self.dice() <= 3:
                                dmg = np.append(dmg, self.unit_weapon[i]["Damage"])
                        elif self.unit_weapon[i]["S"] == self.enemy_data[idOfE]["T"]:
                            if self.dice() <= 4:
                                dmg = np.append(dmg, self.unit_weapon[i]["Damage"])
                        elif self.unit_weapon[i]["S"]/2 <= self.enemy_data[idOfE]["T"]:
                            if self.dice() <= 5:
                                dmg = np.append(dmg, self.unit_weapon[i]["Damage"])
                        elif self.unit_weapon[i]["S"] < self.enemy_data[idOfE]["T"]:
                            if self.dice() == 6:
                                dmg = np.append(dmg, self.unit_weapon[i]["Damage"])
                    # saving throws
                    for k in range(len(dmg)):
                        if self.dice()-self.unit_weapon[i]["AP"] > self.enemy_data[idOfE]["Sv"]:
                            dmg[k] = 0
                    # allocating damage
                    for k in dmg:
                        self.enemy_health[idOfE] -= k
                        if self.enemy_health[idOfE] < 0:
                            self.enemy_health[idOfE] = 0
                else:
                    self.unit_coords[i][0] += 7
                    self.unitInAttack[i][0] = 0
                    self.unitInAttack[i][1] = 0

                    self.enemyInAttack[idOfE][0] = 0
                    self.enemyInAttack[idOfE][1] = 0
                    if self.enemy_health[idOfE] <= self.unit_health[i]:
                        reward = -0.1

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
                message += "Unit model "+str(i)+" is Dead"
            elif self.unitInAttack[i][0] == 0:
                message += "Unit model "+str(i)+" is Moving"
            elif self.unitInAttack[i][0] == 1:
                message += "Unit model "+str(i)+" is in Combat"
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

        for i in range(len(self.enemy_health)):
            obs.append(self.enemy_health[i])

        obs.append(int(self.game_over))

        return obs

    def _calculate_reward(self):
        if sum(self.unit_health) > 0:
            return 1.0
        else:
            return -1.0