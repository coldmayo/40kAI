import numpy as np
import gym
from gym_mod.envs.warhamEnv import *

env = Warhammer40kEnv()

observation = env.reset()

for i in range(200):
    action = env.action_space.sample()
    
    env.enemyTurn()

    next_observation, reward, done, unit_health, enemy_health, inAttack = env.step(action)
    
    if inAttack == 1:
        print("The units are fighting")
    print("Iteration {} ended with reward {}, enemy health {}, model health {}".format(i, reward, enemy_health, unit_health))
    if done == True:
        print("Restarting...")
        env.reset()

env.close()