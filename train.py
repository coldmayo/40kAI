import sys
import os
import numpy as np
import gym
import pickle
import datetime
from tqdm import tqdm
from gym_mod.envs.warhamEnv import *
from gym_mod.engine import genDisplay, Unit, unitData, weaponData, initFile

b_len = 60
b_hei = 44

enemy1 = Unit(unitData("Space_Marine", "Eliminator Squad"), weaponData("Bolt Pistol"), weaponData("Close combat weapon"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
model1 = Unit(unitData("Space_Marine", "Eliminator Squad"), weaponData("Bolt Pistol"), weaponData("Close combat weapon"), np.random.randint(0,b_len), np.random.randint(0,b_hei))

enemy2 = Unit(unitData("Space_Marine", "Apothecary"), weaponData("Absolver Bolt Pistol"), weaponData("Close combat weapon"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
model2 = Unit(unitData("Space_Marine", "Apothecary"), weaponData("Absolver Bolt Pistol"), weaponData("Close combat weapon"), np.random.randint(0,b_len), np.random.randint(0,b_hei))

enemy = [enemy1, enemy2]
model = [model1, model2]

end = False
trunc = True
totLifeT = 600
if os.path.isfile("gui/data.json"):
    totLifeT = initFile.getNumLife()
    b_len = initFile.getBoardX()
    b_hei = initFile.getBoardY()
    if initFile.getModelFaction() == "Space_Marine":
        model1 = Unit(unitData("Space_Marine", "Eliminator Squad"), weaponData("Bolt Pistol"), weaponData("Close combat weapon"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
        model2 = Unit(unitData("Space_Marine", "Apothecary"), weaponData("Absolver Bolt Pistol"), weaponData("Close combat weapon"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
    elif initFile.getModelFaction() == "Orks":
        model1 = Unit(unitData("Orks", "Snagga Boyz"), weaponData("Slugga"), weaponData("Choppa"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
        model2 = Unit(unitData("Orks", "Beastboss"), weaponData("Shoota"), weaponData("Beastchoppa"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
    if initFile.getEnemyFaction() == "Space_Marine":
        enemy1 = Unit(unitData("Space_Marine", "Eliminator Squad"), weaponData("Bolt Pistol"), weaponData("Close combat weapon"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
        enemy2 = Unit(unitData("Space_Marine", "Apothecary"), weaponData("Absolver Bolt Pistol"), weaponData("Close combat weapon"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
    elif initFile.getEnemyFaction() == "Orks":
        enemy1 = Unit(unitData("Orks", "Snagga Boyz"), weaponData("Slugga"), weaponData("Choppa"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
        enemy2 = Unit(unitData("Orks", "Beastboss"), weaponData("Shoota"), weaponData("Beastchoppa"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
    enemy = [enemy1, enemy2]
    model = [model1, model2]
numLifeT = 0

env = gym.make("40kAI-v0", enemy = enemy, model = model, b_len = b_len, b_hei = b_hei)

observation = env.reset()

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

while end == False:
    action = env.action_space.sample()
    if trunc == False:
        print(env.get_info())

    env.enemyTurn(trunc=trunc)
    next_observation, reward, done, _, info = env.step(action)

    unit_health = info["model health"]
    enemy_health = info["player health"]
    inAttack = info["in attack"]

    if inAttack == 1:
        if trunc == False:
            print("The units are fighting")

    board = env.render()
    message = "Iteration {} ended with reward {}, enemy health {}, model health {}".format(i, reward, enemy_health, unit_health)
    if trunc == False:
        print(message)
    inText.append(message)
    if done == True:
        pbar.update(1)
        if reward > 0:
            if trunc == False:
                print("model won!")
        else:
            if trunc == False:
                print("enemy won!")
        if trunc == False:
            print("Restarting...")
        numLifeT+=1
        env.reset()
    if numLifeT == totLifeT:
        end = True
        pbar.close()
    i+=1

env.close()

with open('trainRes.txt', 'w') as f:
    for i in range(len(inText)):
        f.write(inText[i])
        f.write('\n')

if totLifeT > 20:
    genDisplay.makeGif(numOfLife=totLifeT, trunc = True)
else:
    genDisplay.makeGif(numOfLife=totLifeT)

current_time = datetime.datetime.now()
date = str(current_time.second)+"-"+str(current_time.microsecond)
name = "M:"+model[0].showUnitData()["Army"]+"_vs_"+"P:"+enemy[0].showUnitData()["Army"]
if (os.path.exists("models/{}".format(name)) == False):
    os.system("mkdir models/{}".format(name))

with open("models/{}/model-{}.pickle".format(name, date), "wb") as file:
    pickle.dump(env, file)

if os.path.isfile("gui/data.json"):
    initFile.delFile()