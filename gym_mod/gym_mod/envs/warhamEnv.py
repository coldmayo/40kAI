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
        self.observation_space = spaces.Box(low=0, high=1, shape=(7,), dtype=np.float32)  # 7-dimensional observation space

        # Initialize game state + board
        self.iter = 0
        self.restarts = 0
        self.b_len = b_len
        self.b_hei = b_hei
        self.board = np.zeros((self.b_len,self.b_hei))
        self.unit_weapon = model.showWeapon()
        self.enemy_weapon = enemy.showWeapon()
        self.unit_data = model.showUnitData()
        self.enemy_data = enemy.showUnitData()
        self.unit_coords = [model.showCoords()[0], model.showCoords()[1]]
        self.enemy_coords = [enemy.showCoords()[0], enemy.showCoords()[1]]
        self.unit_health = 10.0
        self.enemy_health = 10.0
        self.game_over = False

        self.inAttack = 0

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
        self.unit_health = 10.0
        self.enemy_health = 10.0
        self.unit_coords = [np.random.randint(0,self.b_len), np.random.randint(0,self.b_hei)]
        self.enemy_coords = [np.random.randint(0,self.b_len), np.random.randint(0,self.b_hei)]
        self.game_over = False
        self.current_action_index = 0
        return self._get_observation()

    def enemyTurn(self):
        if self.inAttack == 0:
            movement = self.dice()+self.enemy_data["Movement"]
            dire = np.random.randint(0,3)
            if dire == 0:
                self.enemy_coords[1] -= movement
            elif dire == 1:
                self.enemy_coords[1] += movement
            elif dire == 2:
                self.enemy_coords[0] -= movement
            elif dire == 3:
                self.enemy_coords[0] += movement

            # staying in bounds

            self.enemy_coords = self.bounds(self.enemy_coords)
            if self.enemy_coords == self.enemy_coords:
                self.enemy_coords[0] -= 1

            if self.distance(self.enemy_coords, self.unit_coords) <= self.enemy_weapon["Range"]:
                self.unit_health -= self.enemy_weapon["Damage"]
                self.inAttack = 1

        else:
            decide = np.random.randint(0,30)
            if decide == 5:
                self.enemy_coords[0] -= 7
                self.enemy_coords = self.bounds(self.enemy_coords)
                self.inAttack = 0
            else:
                # hit rolls
                rolls = self.dice(num=self.enemy_data["#OfModels"])
                hits = 0
                for i in range(len(rolls)):
                    if rolls[i] <= self.enemy_weapon["BS"]:
                        hits+=1
                # wound rolls
                dmg = np.array([])
                for i in range(hits):
                    if self.enemy_weapon["S"] >= self.unit_data["T"]*2:
                        if self.dice() <= 2:
                            dmg = np.append(dmg, self.enemy_weapon["Damage"])
                    elif self.enemy_weapon["S"] > self.unit_data["T"]:
                        if self.dice() <= 3:
                            dmg = np.append(dmg, self.enemy_weapon["Damage"])
                    elif self.enemy_weapon["S"] == self.unit_data["T"]:
                        if self.dice() <= 4:
                            dmg = np.append(dmg, self.enemy_weapon["Damage"])
                    elif self.enemy_weapon["S"]/2 <= self.unit_data["T"]:
                        if self.dice() <= 5:
                            dmg = np.append(dmg, self.enemy_weapon["Damage"])
                    elif self.enemy_weapon["S"] < self.unit_data["T"]:
                        if self.dice() == 6:
                            dmg = np.append(dmg, self.enemy_weapon["Damage"])
                # saving throws
                for i in range(len(dmg)):
                    if self.dice()-self.enemy_weapon["AP"] > self.unit_data["Sv"]:
                        dmg[i] = 0
                # allocating damage
                for i in dmg:
                    self.unit_health -= i
    
    def step(self, action):
        if self.inAttack == 0:
            movement = self.dice()+self.unit_data["Movement"]
            dist_before = self.distance(self.enemy_coords, self.unit_coords)
            reward = 0.1
            if action["move"] == 0:
                self.unit_coords[1] -= movement
            elif action["move"] == 1:
                self.unit_coords[1] += movement
            elif action["move"] == 2:
                self.unit_coords[0] -= movement
            elif action["move"] == 3:
                self.unit_coords[0] += movement

            if dist_before > self.distance(self.enemy_coords, self.unit_coords):
                reward = -0.1

            # staying in bounds

            self.unit_coords = self.bounds(self.unit_coords)
            if self.unit_coords == self.enemy_coords:
                self.unit_coords[0] -= 1

            if action["attack"] == 1:
                if self.distance(self.enemy_coords, self.unit_coords) <= self.unit_weapon["Range"]:
                    self.enemy_health -= self.unit_weapon["Damage"]
                    self.inAttack = 1
                    reward = 0.1
                else:
                    reward = -0.1
            
        elif self.inAttack == 1:
            reward = 0.1
            if action["attack"] == 1:
                # hit rolls
                rolls = self.dice(num=self.unit_data["#OfModels"])
                hits = 0
                for i in range(len(rolls)):
                    if rolls[i] <= self.unit_weapon["BS"]:
                        hits+=1
                # wound rolls
                dmg = np.array([])
                for i in range(hits):
                    if self.unit_weapon["S"] >= self.enemy_data["T"]*2:
                        if self.dice() <= 2:
                            dmg = np.append(dmg, self.unit_weapon["Damage"])
                    elif self.unit_weapon["S"] > self.enemy_data["T"]:
                        if self.dice() <= 3:
                            dmg = np.append(dmg, self.unit_weapon["Damage"])
                    elif self.unit_weapon["S"] == self.enemy_data["T"]:
                        if self.dice() <= 4:
                            dmg = np.append(dmg, self.unit_weapon["Damage"])
                    elif self.unit_weapon["S"]/2 <= self.enemy_data["T"]:
                        if self.dice() <= 5:
                            dmg = np.append(dmg, self.unit_weapon["Damage"])
                    elif self.unit_weapon["S"] < self.enemy_data["T"]:
                        if self.dice() == 6:
                            dmg = np.append(dmg, self.unit_weapon["Damage"])
                # saving throws
                for i in range(len(dmg)):
                    if self.dice()-self.unit_weapon["AP"] > self.enemy_data["Sv"]:
                        dmg[i] = 0
                # allocating damage
                for i in dmg:
                    self.enemy_health -= i
            else:
                self.unit_coords[0] += 7
                self.inAttack = 0
                if self.enemy_health <= self.unit_health:
                    reward = -0.1
        
        if self.unit_health <= 0 or self.enemy_health <= 0:
            self.game_over = True

        if self.game_over:
            reward += self._calculate_reward()

        self.iter += 1

        info = {"unit health":self.unit_health, "enemy health": self.enemy_health, "in attack": self.inAttack}
        place_holder = {"pleeb": "pleeb"}
        return self._get_observation(), reward, self.game_over, info, place_holder

    def updateBoard(self):
        self.board = np.zeros((self.b_len,self.b_hei))
        self.unit_coords = self.bounds(self.unit_coords)
        self.enemy_coords = self.bounds(self.enemy_coords)

        self.board[self.unit_coords[0]][self.unit_coords[1]] = 1
        self.board[self.enemy_coords[0]][self.enemy_coords[1]] = 2

    def render(self, mode='human'):
        self.updateBoard()
        
        title = "Iteration "+str(self.iter)+" Lifetime "+str(self.restarts)
        plt.title(title)
        
        if self.inAttack == 0:
            plt.xlabel("Moving")
        elif self.inAttack == 1:
            plt.xlabel("In Combat") 

        plt.xlim(-1,self.b_len+1)
        plt.ylim(-1,self.b_hei+1)
        x1 = np.linspace(0,self.b_len,10)
        y1 = np.zeros(10)
        x2 = np.zeros(10)
        y2 = np.linspace(0, self.b_hei,10)
        plt.plot(x1,y1,color="black")
        plt.plot(x2,y2,color="black")
        plt.plot(x1,y1+self.b_hei,color="black")
        plt.plot(x2+self.b_len,y2,color="black")
        plt.plot(self.unit_coords[0],self.unit_coords[1], 'bo')
        plt.plot(self.enemy_coords[0],self.enemy_coords[1], 'ro')

        fileName = "display/"+str(self.restarts)+"_"+str(self.iter)+".png"
        plt.savefig(fileName)
        plt.cla()

        return self.board

    def close(self):
        pass

    def _get_observation(self):
        return np.array([self.unit_health, self.enemy_health, int(self.game_over), self.unit_coords[0], self.unit_coords[1], self.enemy_coords[0], self.enemy_coords[1]], dtype=np.float32)

    def _calculate_reward(self):
        if self.unit_health > 0:
            return 1.0
        else:
            return -1.0