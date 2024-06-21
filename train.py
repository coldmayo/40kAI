import sys
import os
import numpy as np
import gymnasium as gym
import pickle
import datetime
import json
from tqdm import tqdm
from gym_mod.envs.warhamEnv import *
from gym_mod.engine import genDisplay, Unit, unitData, weaponData, initFile, metrics

from model.DQN import *
from model.memory import *
from model.utils import *

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

import warnings
warnings.filterwarnings("ignore") 

with open(os.path.abspath("hyperparams.json")) as j:
    data = json.loads(j.read())

TAU = data["tau"]
LR = data["lr"]

b_len = 60
b_hei = 40

print("\nTraining...\n")

enemy1 = Unit(unitData("Space_Marine", "Eliminator Squad"), weaponData("Bolt Pistol"), weaponData("Close combat weapon"), b_len, b_hei)
model1 = Unit(unitData("Space_Marine", "Eliminator Squad"), weaponData("Bolt Pistol"), weaponData("Close combat weapon"), b_len, b_hei)

enemy2 = Unit(unitData("Space_Marine", "Apothecary"), weaponData("Absolver Bolt Pistol"), weaponData("Close combat weapon"), b_len, b_hei)
model2 = Unit(unitData("Space_Marine", "Apothecary"), weaponData("Absolver Bolt Pistol"), weaponData("Close combat weapon"), b_len, b_hei)

enemy = [enemy1, enemy2]
model = [model1, model2]

end = False
trunc = True
totLifeT = 10
steps_done = 0

if os.path.isfile("gui/data.json"):

    totLifeT = initFile.getNumLife()
    b_len = initFile.getBoardX()
    b_hei = initFile.getBoardY()
    print("Model Units:\n")
    if len(initFile.getEnemyUnits()) > 0:
        enemy = []
        for i in range(len(initFile.getEnemyUnits())):
            enemy.append(Unit(unitData(initFile.getEnemyFaction(), initFile.getEnemyUnits()[i]), weaponData(initFile.getEnemyW()[i][0]), weaponData(initFile.getEnemyW()[i][1]), b_len, b_hei))
            print("Name:", initFile.getEnemyUnits()[i], "Weapons: ", initFile.getEnemyW()[i][0], initFile.getEnemyW()[i][1])
    print("Enemy Units:\n")
    if len(initFile.getModelUnits()) > 0:
        model = []
        for i in range(len(initFile.getModelUnits())):
            model.append(Unit(unitData(initFile.getModelFaction(), initFile.getModelUnits()[i]), weaponData(initFile.getModelW()[i][0]), weaponData(initFile.getModelW()[i][1]), b_len, b_hei))
            print("Name:", initFile.getModelUnits()[i], "Weapons: ", initFile.getModelW()[i][0], initFile.getModelW()[i][1])

numLifeT = 0

deployType = ["Search and Destroy", "Hammer and Anvil", "Dawn of War"]
deployChang = np.random.choice(deployType)
for m in model:
    m.deployUnit(deployChang, "model")
for e in enemy:
    e.deployUnit(deployChang, "player")

env = gym.make("40kAI-v0", disable_env_checker=True, enemy = enemy, model = model, b_len = b_len, b_hei = b_hei)

n_actions = [5,2,len(enemy), len(enemy), 4, len(model)]
state, info = env.reset(m=model, e=enemy)
n_observations = len(state)

policy_net = DQN(n_observations, n_actions).to(device)
target_net = DQN(n_observations, n_actions).to(device)
target_net.load_state_dict(policy_net.state_dict())

optimizer = optim.AdamW(policy_net.parameters(), lr=LR, amsgrad=True)
memory = ReplayMemory(10000)

inText = []

inText.append("Model units:")
for i in model:
    inText.append("Name: {}, Army Type: {}".format(i.showUnitData()["Name"], i.showUnitData()["Army"]))
inText.append("Enemy units:")
for i in enemy:
    inText.append("Name: {}, Army Type: {}".format(i.showUnitData()["Name"], i.showUnitData()["Army"]))
inText.append("Number of Lifetimes ran: {}\n".format(totLifeT))

i = 0

pbar = tqdm(total=totLifeT)

state, info = env.reset(m = model, e = enemy, Type="big")

metrics = metrics()

rewArr = []

epLen = 0

while end == False:
    epLen += 1
    state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
    
    action = select_action(env, state, i, policy_net)
    action_dict = convertToDict(action)
    if trunc == False:
        print(env.get_info())

    env.enemyTurn(trunc=trunc)
    next_observation, reward, done, res, info = env.step(action_dict)
    rewArr.append(reward)
    reward = torch.tensor([reward], device=device)

    unit_health = info["model health"]
    enemy_health = info["player health"]
    inAttack = info["in attack"]

    if inAttack == 1:
        if trunc == False:
            print("The units are fighting")

    board = env.render()
    message = "Iteration {} ended with reward {}, enemy health {}, model health {}, model VP {}, enemy VP {}, victory condition {}".format(i, reward, enemy_health, unit_health, info["model VP"], info["player VP"], info["victory condition"])
    if trunc == False:
        print(message)
    inText.append(message)

    next_state = torch.tensor(next_observation, dtype=torch.float32, device=device).unsqueeze(0)
    memory.push(state, action, next_state, reward)
    state = next_state
    loss = optimize_model(policy_net, target_net, optimizer, memory, n_observations)
    metrics.updateLoss(loss)
    
    for key in policy_net.state_dict():
        target_net.state_dict()[key] = policy_net.state_dict()[key]*TAU + target_net.state_dict()[key]*(1-TAU)
    target_net.load_state_dict(target_net.state_dict())

    if done == True:
        pbar.update(1)
        metrics.updateRew(sum(rewArr)/len(rewArr))
        metrics.updateEpLen(epLen)
        epLen = 0
        rewArr = []

        if res == 1:
            inText.append("Slay and Secure Victory Condition")
        elif res == 2:
            inText.append("Ancient Relic Victory Condition")
        elif res == 3:
            inText.append("Domination Victory Condition")
        elif res == 4:
            inText.append("Major Victory")

        if reward > 0:
            inText.append("model won!")
            if trunc == False:
                print("model won!")
        else:
            inText.append("enemy won!")
            if trunc == False:
                print("enemy won!")
        if trunc == False:
            print("Restarting...")
        numLifeT+=1

        deployChang = np.random.choice(deployType)
        for m in model:
            m.deployUnit(deployChang, "model")
        for e in enemy:
            e.deployUnit(deployChang, "player")

        state, info = env.reset(m=model, e=enemy, Type="small")

    if numLifeT == totLifeT:
        end = True
        pbar.close()
    i+=1

env.close()

with open('trainRes.txt', 'w') as f:
    for i in range(len(inText)):
        f.write(inText[i])
        f.write('\n')

if totLifeT > 30:
    genDisplay.makeGif(numOfLife=totLifeT, trunc = True)
else:
    genDisplay.makeGif(numOfLife=totLifeT)

metrics.lossCurve()
metrics.showRew()
metrics.showEpLen()
print("Generated metrics")

current_time = datetime.datetime.now()
date = str(current_time.second)+"-"+str(current_time.microsecond)
name = "M:"+model[0].showUnitData()["Army"]+"_vs_"+"P:"+enemy[0].showUnitData()["Army"]
if (os.path.exists("models/{}".format(name)) == False):
    os.system("mkdir models/{}".format(name))

torch.save({
    "policy_net": policy_net.state_dict(),
    "target_net": target_net.state_dict(),
    'optimizer': optimizer.state_dict(),}
    , ("models/{}/model-{}.pth".format(name, date)))

toSave = [env, model, enemy]

with open("models/{}/model-{}.pickle".format(name, date), "wb") as file:
    pickle.dump(toSave, file)

if os.path.isfile("gui/data.json"):
    initFile.delFile()