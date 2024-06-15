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
    def deployUnit(self, deployment, unitType, choose=False):
        if deployment == "Search and Destroy":
            if unitType == "model":
                self.unit_coords[0] = np.random.randint(0, self.b_hei/2)
                self.unit_coords[1] = np.random.randint(0, self.b_len/2)
            elif unitType == "player":
                self.unit_coords[0] = np.random.randint(self.b_hei/2, self.b_hei)
                self.unit_coords[1] = np.random.randint(self.b_len/2, self.b_len)
        if deployment == "Hammer and Anvil":
            if unitType == "model":
                self.unit_coords[0] = np.random.randint(0, self.b_hei)
                self.unit_coords[1] = np.random.randint(0, self.b_len/4)
            elif unitType == "player":
                self.unit_coords[0] = np.random.randint(0, self.b_hei)
                self.unit_coords[1] = np.random.randint(self.b_len*3/4, self.b_len)
    def showUnitData(self):
        return self.unit_data
    def showWeapon(self):
        return self.unit_weapon
    def showMelee(self):
        return self.unit_melee
    def showCoords(self):
        return self.unit_coords
