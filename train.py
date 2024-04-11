from unit import *

import numpy as np
import gym
from gym_mod.envs.warhamEnv import *

b_len = 15
b_hei = 15

enemy = Unit({"Army": "Space Marine","Name": "Eliminator Squad", "Movement": 6, "#OfModels": 4, "T": 4, "Sv": 3}, {"Name":"Bolt Pistol","BS":3,"S":4,"AP":0,"Range": 6, "Damage": 1}, np.random.randint(0,b_len), np.random.randint(0,b_hei))
model = Unit({"Army": "Space Marine","Name": "Eliminator Squad", "Movement": 6, "#OfModels": 4, "T": 4, "Sv": 3}, {"Name":"Bolt Pistol","BS":3,"S":4,"AP":0,"Range": 6, "Damage": 1}, np.random.randint(0,b_len), np.random.randint(0,b_hei))

env = Warhammer40kEnv(enemy, model, b_len, b_hei)

observation = env.reset()

for i in range(200):
    action = env.action_space.sample()
    
    env.enemyTurn()

    next_observation, reward, done, unit_health, enemy_health, inAttack = env.step(action)

    if inAttack == 1:
        print("The units are fighting")

    board = env.render()

    print("Iteration {} ended with reward {}, enemy health {}, model health {}".format(i, reward, enemy_health, unit_health))
    if done == True:
        print("Restarting...")
        env.reset()

env.close()