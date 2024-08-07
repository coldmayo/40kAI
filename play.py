# play warhammer!

import pickle
import os
import sys
from gym_mod.envs.warhamEnv import *
import warnings
warnings.filterwarnings("ignore")

from model.DQN import *
from model.utils import *
from gym_mod.engine.GUIinteract import *

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if sys.argv[1] == "None":
    savePath = "models/"

    folders = os.listdir(savePath)

    envs = []
    modelpth = []

    for i in folders:
        
        if os.path.isdir(savePath+i):
            fs = os.listdir(savePath+i)
            for j in fs:
                if j[-len(".pickle"):] == ".pickle":
                    envs.append(savePath+i+"/"+j)
                elif j[-len(".pth"):] == ".pth":
                    modelpth.append(savePath+i+"/"+j)

    envs.sort(key=lambda x: os.path.getmtime(x))
    modelpth.sort()

    checkpoint = torch.load(modelpth[-1])

    #print("Playing with environment saved here: ", envs[-1])
    with open(envs[-1], 'rb') as f:
        env, model, enemy = pickle.load(f)
else: 
    #print("Playing with model saved here: ", sys.argv[1])
    with open(sys.argv[1], 'rb') as f:
        env, model, enemy = pickle.load(f)
    f = str(sys.argv[1])
    modelpth = f[:-len("pickle")]+"pth"
    checkpoint = torch.load(modelpth)

playInGUI = False
if sys.argv[2] == "True":
    playInGUI = True

deployType = ["Search and Destroy", "Hammer and Anvil", "Dawn of War"]
deployChang = np.random.choice(deployType)

if playInGUI == False:
    print("Deployment Type: ", deployChang)
else:
    sendToGUI("Deployment Type: {}".format(deployChang))

for m in model:
    m.deployUnit(deployChang, "model")
i = 0
for e in enemy:
    sendToGUI("Deploying Unit {} or {}".format(i, e.showUnitData()["Name"]))
    e.deployUnit(deployChang, "player", GUI=playInGUI, choose = True)
    i += 1

state, info = env.reset(m=model, e=enemy)
n_actions = [5,2,len(info["player health"]), len(info["player health"]), 5, len(info["model health"])]
for i in range(len(model)):
    n_actions.append(12)
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

if playInGUI == True:
    env.reset(m=model, e=enemy, playType = playInGUI, Type="big", trunc=True)
else:
    env.reset(m=model, e=enemy, playType = playInGUI, Type="big", trunc=False)

reward = 0
if playInGUI == False:
    print("\nInstructions:\n")
    print("Observe board at board.txt or click the 'Show Board' button")
    print("The popup from the button automatically updates, so you won't need to keep pressing it")
    print("The player (you) controls units starting with 1 (i.e. 11, 12, etc)")
    print("The model controls units starting with 2 (i.e. 21, 22, etc)\n")
else:
    sendToGUI("\nInstructions:\nObserve board at board.txt or click the 'Show Board' button\nThe popup from the button automatically updates, so you won't need to keep pressing it\nThe player (you) controls units starting with 1 (i.e. 11, 12, etc)\nThe model controls units starting with 2 (i.e. 21, 22, etc)\n")

while isdone == False:
    done, info = env.player()
    state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
    action = select_action(env, state, i, policy_net, len(model))
    action_dict = convertToDict(action)
    if done != True:
        next_observation, reward, done, _, info = env.step(action_dict)
        reward = torch.tensor([reward], device=device)
        unit_health = info["model health"]
        enemy_health = info["player health"]
        inAttack = info["in attack"]

        board = env.render()
        message = "Iteration {} ended with reward {}, Player health {}, Model health {}".format(i, reward, enemy_health, unit_health)
        if playInGUI == False:
            print(message)
        else:
            sendToGUI(message)
        next_state = torch.tensor(next_observation, dtype=torch.float32, device=device).unsqueeze(0)
        state = next_state
    if done == True:
        if reward > 0:
            if playInGUI == False:
                print("model won!")
            else:
                sendToGUI("model won!")
        else:
            if playInGUI == False:
                print("you won!")
            else:
                sendToGUI("you won!")
        isdone = True
    i+=1
