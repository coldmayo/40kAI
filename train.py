import sys
import numpy as np
import gym
from gym_mod.envs.warhamEnv import *
from gym_mod.engine import genDisplay, Unit, unitData, weaponData

b_len = 60
b_hei = 44

enemy1 = Unit(unitData("Space Marine", "Eliminator Squad"), weaponData("Bolt Pistol"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
model1 = Unit(unitData("Space Marine", "Eliminator Squad"), weaponData("Bolt Pistol"), np.random.randint(0,b_len), np.random.randint(0,b_hei))

enemy2 = Unit(unitData("Space Marine", "Apothecary"), weaponData("Absolver Bolt Pistol"), np.random.randint(0,b_len), np.random.randint(0,b_hei))
model2 = Unit(unitData("Space Marine", "Apothecary"), weaponData("Absolver Bolt Pistol"), np.random.randint(0,b_len), np.random.randint(0,b_hei))

env = gym.make("40kAI-v0", enemy = [enemy1, enemy2], model = [model1, model2], b_len = b_len, b_hei = b_hei)

observation = env.reset()

end = False
numLifeT = 0
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

    print("Iteration {} ended with reward {}, enemy health {}, model health {}".format(i, reward, enemy_health, unit_health))
    if done == True:
        if reward >= 1:
            print("model won!")
        else:
            print("enemy won!")
        print("Restarting...")
        numLifeT+=1
        env.reset()
    if numLifeT == 10:
        end = True
    i+=1

env.close()
genDisplay.makeGif()