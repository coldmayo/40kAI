# play warhammer!

import pickle
import os
from gym_mod.envs.warhamEnv import *
from gym_mod.engine import genDisplay

savePath = "models"

files = os.listdir(savePath)
files = [os.path.join(savePath, f) for f in files]
files.sort(key=lambda x: os.path.getmtime(x))

with open(files[-1], 'rb') as f:
    env = pickle.load(f)

isdone = False
i = 0

env.reset(Type="big")

while isdone == False:
    action = env.action_space.sample()
    print(env.get_info())
    info_p = env.player()
    next_observation, reward, done, _, info = env.step(action)

    unit_health = info["unit health"]
    enemy_health = info["enemy health"]
    inAttack = info["in attack"]

    if inAttack == 1:
        print("The units are fighting")

    board = env.render()
    message = "Iteration {} ended with reward {}, Player health {}, Model health {}".format(i, reward, enemy_health, unit_health)
    print(message)
    if done == True:
        if reward > 0:
            print("model won!")
        else:
            print("enemy won!")
        print("Restarting...")
        isdone = True
    i+=1