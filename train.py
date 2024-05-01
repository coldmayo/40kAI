import sys
import numpy as np
import gym
import pickle
import datetime
from gym_mod.envs.warhamEnv import *
from gym_mod.engine import genDisplay, Unit, unitData, weaponData

b_len = 60
b_hei = 44

enemy1 = Unit(unitData("Space Marine", "Eliminator Squad"), weaponData("Bolt Pistol"), weaponData("Close combat weapon"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
model1 = Unit(unitData("Space Marine", "Eliminator Squad"), weaponData("Bolt Pistol"), weaponData("Close combat weapon"), np.random.randint(0,b_len), np.random.randint(0,b_hei))

enemy2 = Unit(unitData("Space Marine", "Apothecary"), weaponData("Absolver Bolt Pistol"), weaponData("Close combat weapon"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
model2 = Unit(unitData("Space Marine", "Apothecary"), weaponData("Absolver Bolt Pistol"), weaponData("Close combat weapon"), np.random.randint(0,b_len), np.random.randint(0,b_hei))

enemy = [enemy1, enemy2]
model = [model1, model2]

env = gym.make("40kAI-v0", enemy = enemy, model = model, b_len = b_len, b_hei = b_hei)

observation = env.reset()

inText = []

end = False
totLifeT = 600
numLifeT = 0

inText.append("Model units:")
for i in model:
    inText.append("Name: {}, Army Type: {}".format(i.showUnitData()["Name"], i.showUnitData()["Army"]))
inText.append("Enemy units:")
for i in enemy:
    inText.append("Name: {}, Army Type: {}".format(i.showUnitData()["Name"], i.showUnitData()["Army"]))
inText.append("Number of Lifetimes ran: {}\n".format(totLifeT))

i = 0

while end == False:
    action = env.action_space.sample()
    print(env.get_info())

    env.enemyTurn()
    next_observation, reward, done, _, info = env.step(action)

    unit_health = info["unit health"]
    enemy_health = info["enemy health"]
    inAttack = info["in attack"]

    if inAttack == 1:
        print("The units are fighting")

    board = env.render()
    message = "Iteration {} ended with reward {}, enemy health {}, model health {}".format(i, reward, enemy_health, unit_health)
    print(message)
    inText.append(message)
    if done == True:
        if reward > 0:
            print("model won!")
        else:
            print("enemy won!")
        print("Restarting...")
        numLifeT+=1
        env.reset()
    if numLifeT == totLifeT:
        end = True
    i+=1

env.close()

with open('trainRes.txt', 'w') as f:
    for i in range(len(inText)):
        f.write(inText[i])
        f.write('\n')

genDisplay.makeGif(numOfLife=totLifeT, trunc = True)

current_time = datetime.datetime.now()
date = str(current_time.year)+"-"+str(current_time.month)+"-"+str(current_time.day)+"-"+str(current_time.hour)+"-"+str(current_time.minute)+"-"+str(current_time.second)+"-"+str(current_time.microsecond)
with open("models/model-{}.pickle".format(date), "wb") as file:
    pickle.dump(env, file)