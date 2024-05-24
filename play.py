# play warhammer!

import pickle
import os
import sys
from gym_mod.envs.warhamEnv import *
import warnings
warnings.filterwarnings("ignore")

from model.DQN import *
from model.utils import *

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if sys.argv[1] == "None":
    savePath = "models/"

    folders = os.listdir(savePath)

    envs = []
    model = []

    for i in folders:
        fs = os.listdir(savePath+i+"/")
        for j in fs:
            if j[-len(".pickle"):] == ".pickle":
                envs.append(savePath+i+"/"+j)
            elif j[-len(".pth"):] == ".pth":
                model.append(savePath+i+"/"+j)

    envs.sort(key=lambda x: os.path.getmtime(x))
    model.sort()

    checkpoint = torch.load(model[-1])

    print("Playing with environment saved here: ", envs[-1])
    with open(envs[-1], 'rb') as f:
        env = pickle.load(f)
else: 
    print("Playing with model saved here: ", sys.argv[1])
    with open(sys.argv[1], 'rb') as f:
        env = pickle.load(f)
    f = str(sys.argv[1])
    modelpth = f[:-len("pickle")]+"pth"
    checkpoint = torch.load(modelpth)


state, info = env.reset()
n_actions = [4,2,len(info["player health"]), len(info["player health"]), 4, len(info["model health"])]
n_observations = len(state)

policy_net = DQN(n_observations, n_actions).to(device)
target_net = DQN(n_observations, n_actions).to(device)
optimizer = torch.optim.Adam(policy_net.parameters())

policy_net.load_state_dict(checkpoint['policy_net'])
target_net.load_state_dict(checkpoint['target_net'])
optimizer.load_state_dict(checkpoint['optimizer'])

policy_net.eval()
target_net.eval()

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
    done, info = env.player()
    state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
    action = select_action(env, state, i, policy_net)
    action_dict = convertToDict(action)
    if done != True:
        next_observation, reward, done, _, info = env.step(action_dict)
        reward = torch.tensor([reward], device=device)
        unit_health = info["model health"]
        enemy_health = info["player health"]
        inAttack = info["in attack"]

        if inAttack == 1:
            print("The units are fighting")

        board = env.render()
        message = "Iteration {} ended with reward {}, Player health {}, Model health {}".format(i, reward, enemy_health, unit_health)
        print(message)
        next_state = torch.tensor(next_observation, dtype=torch.float32, device=device).unsqueeze(0)
        state = next_state
    if done == True:
        if reward > 0:
            print("model won!")
        else:
            print("you won!")
        isdone = True
    i+=1