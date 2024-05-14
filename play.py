# play warhammer!

import pickle
import os
import sys
from gym_mod.envs.warhamEnv import *
from gym_mod.engine import genDisplay

if sys.argv[1] == "None":
    savePath = "models/"

    folders = os.listdir(savePath)

    files = []

    for i in folders:
        fs = os.listdir(savePath+i+"/")
        for j in fs:
            files.append(savePath+i+"/"+j)

    files.sort(key=lambda x: os.path.getmtime(x))

    print("Playing with model saved here: ", files[-1])
    with open(files[-1], 'rb') as f:
        env = pickle.load(f)
else: 
    print("Playing with model saved here: ", sys.argv[1])
    with open(sys.argv[1], 'rb') as f:
        env = pickle.load(f)


isdone = False
i = 0

env.reset(Type="big")

reward = 0

print("\nInstructions:\n")
print("Observe board at board.txt or click the 'Show Board' button")
print("The popup from the button automatically updates, so you won't need to keep pressing it")
print("The player (you) controls units starting with 1 (i.e. 11, 12, etc)")
print("The model controls units starting with 2 (i.e. 21, 22, etc)\n")

while isdone == False:
    action = env.action_space.sample()
    print(env.get_info())
    done, info = env.player()
    if done != True:
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
            print("you won!")
        isdone = True
    i+=1