import numpy as np 
from gym_mod.engine.GUIinteract import *
import time

class Unit:
    def __init__(self, data, weapon, melee = None, GUI=False, b_len=0, b_hei=0):
        self.unit_data = data
        self.unit_weapon = weapon
        self.unit_melee = melee
        self.b_len = b_len
        self.b_hei = b_hei
        self.unit_coords = np.array([0,0])
        self.playInGUI = GUI
    def updateUnitData(self, dicto):
        self.unit_weapon.update(dicto)
    def updateWeapon(self, dicto):
        self.unit_weapon.update(dicto)
    def updateMelee(self, dicto):
        self.unit_melee.update(dicto)
    def selectUnitPos(self, xmin, xmax, ymin, ymax):
        if self.playInGUI == False:
            coords = input("Enter the coordinates (example: 10,10): ")
        else:
            sendToGUI("Enter the coordinates (example: 10,10): ")
            coords = recieveGUI()
        run = True
        while run:
            if coords[0].isnumeric() != True:
                if self.playInGUI == False:
                    coords = input("Use the format: x,y: ")
                else:
                    sendToGUI("Use the format: x,y: ")
                    coords = recieveGUI()
            else:
                x = ""
                y = ""
                switch = 0
                for i in range(len(coords)):
                    if coords[i].isnumeric() != True:
                        switch = 1
                    elif switch == 0:
                        x += coords[i]
                    elif switch == 1:
                        y += coords[i]
                if int(x) >= xmin and int(x) <= xmax and int(y) >= ymin and int(y) <= ymax:
                    run = False
                    self.unit_coords[0] = int(x)
                    self.unit_coords[1] = int(y)
                else:
                    if self.playInGUI == False:
                        coords = input("Not in bounds, try again: ")
                    else:
                        sendToGUI("Not in bounds, try again:")
                        coords = recieveGUI()
                        
    def deployUnit(self, deployment, unitType, GUI = False, choose=False):
        self.playInGUI = GUI
        if choose == True:
            run = True
            if self.playInGUI == False:
                contChoose = input("Would you like to choose where to deploy this unit? (y/n): ")
            else:
                sendToGUI("Would you like to choose where to deploy this unit? (y/n): ")
                contChoose = recieveGUI()
            while run:
                print(contChoose)
                if contChoose.lower() == "y" or contChoose.lower() == "yes":
                    choose = True
                    run = False
                elif contChoose.lower() == "n" or contChoose.lower() == "no":
                    choose = False
                    run = False
                else:
                    if self.playInGUI == False:
                        contChoose = input("Valid answers are: y, yes, n, and no: ")
                    else:
                        sendToGUI("Valid answers are: y, yes, n, and no: ")
                        contChoose = recieveGUI()
        
        if deployment == "Search and Destroy":
            if choose == False:
                if unitType == "model":
                    self.unit_coords[0] = np.random.randint(0, self.b_hei/2)
                    self.unit_coords[1] = np.random.randint(0, self.b_len/2)
                elif unitType == "player":
                    self.unit_coords[0] = np.random.randint(self.b_hei/2, self.b_hei)
                    self.unit_coords[1] = np.random.randint(self.b_len/2, self.b_len)
            elif choose == True:
                if unitType == "player":
                    print("The bounds for x axis: {} to {}\nThe bounds for y axis: {} to {}".format(self.b_hei/2, self.b_hei, self.b_len/2, self.b_len))
                    self.selectUnitPos(self.b_hei/2, self.b_hei, self.b_len/2, self.b_len)
        elif deployment == "Hammer and Anvil":
            if choose == False:
                if unitType == "model":
                    self.unit_coords[0] = np.random.randint(0, self.b_hei)
                    self.unit_coords[1] = np.random.randint(0, self.b_len/4)
                elif unitType == "player":
                    self.unit_coords[0] = np.random.randint(0, self.b_hei)
                    self.unit_coords[1] = np.random.randint(self.b_len*3/4, self.b_len)
            elif choose == True:
                if unitType == "player":
                    print("The bounds for x axis: {} to {}\nThe bounds for y axis: {} to {}".format(0, self.b_hei, self.b_len*3/4, self.b_len))
                    self.selectUnitPos(0, self.b_hei, self.b_len*3/4, self.b_len)

        elif deployment == "Dawn of War":
            if choose == False:
                if unitType == "model":
                    self.unit_coords[0] = np.random.randint(0, self.b_hei/4)
                    self.unit_coords[1] = np.random.randint(0, self.b_len)
                elif unitType == "player":
                    self.unit_coords[0] = np.random.randint(self.b_hei*3/4, self.b_hei)
                    self.unit_coords[1] = np.random.randint(0, self.b_len)
            elif choose == True:
                if unitType == "player":
                    print("The bounds for x axis: {} to {}\nThe bounds for y axis: {} to {}".format(0, self.b_hei, self.b_len*3/4, self.b_len))
                    self.selectUnitPos(self.b_hei*3/4, self.b_hei, 0, self.b_len)

    def showUnitData(self):
        return self.unit_data
    def showWeapon(self):
        return self.unit_weapon
    def showMelee(self):
        return self.unit_melee
    def showCoords(self):
        return self.unit_coords
