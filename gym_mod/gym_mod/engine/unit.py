import numpy as np 

class Unit:
    def __init__(self, data, weapon, melee = None, b_len=0, b_hei=0):
        self.unit_data = data
        self.unit_weapon = weapon
        self.unit_melee = melee
        self.b_len = b_len
        self.b_hei = b_hei
        self.unit_coords = np.array([0,0])
    def updateUnitData(self, dicto):
        self.unit_weapon.update(dicto)
    def updateWeapon(self, dicto):
        self.unit_weapon.update(dicto)
    def updateMelee(self, dicto):
        self.unit_melee.update(dicto)
    def selectUnitPos(self, xmin, xmax, ymin, ymax):
        coords = input("Enter the coordinates (example: 10,10): ")
        run = True
        while run:
            if coords[0].isnumeric() != True:
                coords = input("Use the format: x,y: ")
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
                if int(x) >= self.b_hei/2 and int(x) <= self.b_hei and int(y) >= self.b_len/2 and int(y) <= self.b_len:
                    run = False
                    self.unit_coords[0] = int(x)
                    self.unit_coords[1] = int(y)
                else:
                    coords = input("Not in bounds, try again: ")
                        
    def deployUnit(self, deployment, unitType, choose=False):
        if choose == True:
            run = True
            contChoose = input("Would you like to choose where to deploy this unit? (y/n): ")
            while run:
                if contChoose.lower() == "y" or contChoose.lower() == "yes":
                    choose = True
                    run = False
                elif contChoose.lower() == "n" or contChoose.lower() == "no":
                    choose = False
                    run = False
                else:
                    contChoose = input("Valid answers are: y, yes, n, and no: ")
        
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
    def showUnitData(self):
        return self.unit_data
    def showWeapon(self):
        return self.unit_weapon
    def showMelee(self):
        return self.unit_melee
    def showCoords(self):
        return self.unit_coords
