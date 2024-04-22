import numpy as np 

class Unit:
    def __init__(self, data, weapon, melee = None, x=0, y=0):
        self.unit_data = data
        self.unit_weapon = weapon
        self.unit_melee = melee
        self.unit_coords = np.array([x,y])
    def updateUnitData(self, dicto):
        self.unit_weapon.update(dicto)
    def updateWeapon(self, dicto):
        self.unit_weapon.update(dicto)
    def updateMelee(self, dicto):
        self.unit_melee.update(dicto)
    def updateCoords(self, x = "nan", y = "nan"):
        if x != "nan":
            self.unit_coords[0] = x
        if y != "nan":
            self.unit_coords[1] = y
    def showUnitData(self):
        return self.unit_data
    def showWeapon(self):
        return self.unit_weapon
    def showMelee(self):
        return self.unit_melee
    def showCoords(self):
        return self.unit_coords
