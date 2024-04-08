import gym
from gym import spaces
import numpy as np

class Warhammer40kEnv(gym.Env):
    def __init__(self):
        
        self.action_space = spaces.Dict({
            'move': spaces.Discrete(4),  # Four directions: Up, Down, Left, Right
            'attack': spaces.Discrete(2),  # Two attack options: Engage Attack, Leave Attack/move
        })
        self.observation_space = spaces.Box(low=0, high=1, shape=(7,), dtype=np.float32)  # 5-dimensional observation space

        # Initialize game state + board
        self.b_len = 15
        self.b_hei = 15
        self.board = np.zeros((self.b_len,self.b_hei))
        self.unit_weapon = {"Range": 6, "Damage": 2}
        self.enemy_weapon = {"Range": 6, "Damage": 2}
        self.unit_data = {"Army": "Space Marine","Name": "Scout Squad", "Movement": 6}
        self.enemy_data = {"Army": "Space Marine","Name": "Scout Squad", "Movement": 6}
        self.unit_coords = [np.random.randint(0,6), np.random.randint(0,6)]
        self.enemy_coords = [np.random.randint(0,6), np.random.randint(0,6)]
        self.unit_health = 10.0
        self.enemy_health = 10.0
        self.game_over = False

        self.inAttack = 0

    def distance(self, p1, p2):
        return np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

    def dice(self, min = 1, max = 6):
        return np.random.randint(min, max)

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
            decide = np.random.randint(0,15)
            if decide == 5:
                self.enemy_coords[0] -= 7
                self.enemy_coords = self.bounds(self.enemy_coords)
                self.inAttack = 0
            self.unit_health -= self.enemy_weapon["Damage"]
    
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
            reward = 0
            if action["attack"] == 1:
                self.enemy_health -= self.unit_weapon["Damage"]
                reward = 0.1
            else:
                self.unit_coords[0] += 7
                self.inAttack = 0
                if self.enemy_health <= self.unit_health:
                    reward = -0.1
        
        if self.unit_health <= 0 or self.enemy_health <= 0:
            self.game_over = True

        if self.game_over:
            reward += self._calculate_reward()

        return self._get_observation(), reward, self.game_over, self.unit_health, self.enemy_health, self.inAttack

    def updateBoard(self):
        self.board = np.zeros((self.b_len,self.b_hei))
        self.board[self.unit_coords[0]][self.unit_coords[1]] = 1
        self.board[self.enemy_coords[0]][self.enemy_coords[1]] = 2

    def render(self, mode='human'):
        self.updateBoard()
        print(self.board)

    def close(self):
        pass

    def _get_observation(self):
        return np.array([self.unit_health, self.enemy_health, int(self.game_over), 0, 0], dtype=np.float32)

    def _calculate_reward(self):
        if self.unit_health > 0:
            return 1.0
        else:
            return -1.0
