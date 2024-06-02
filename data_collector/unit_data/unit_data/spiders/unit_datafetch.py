import scrapy

class DataSpider(scrapy.Spider):
    name = "data"

    f = open('links.json', 'r+')
    f.truncate(0)

    def start_requests(self):
        urls = ["https://www.wahapedia.ru/wh40k10ed/factions/adepta-sororitas/datasheets.html", "https://wahapedia.ru/wh40k10ed/factions/orks/datasheets.html"]

        for i in urls:
            yield scrapy.Request(url = i, callback = self.parse)

    def toint(self, string):
        toapp = ""
        for j in string:
            if j.isnumeric() == True:
                toapp += j
        if string == "D3" or string == "D6" or string == "Melee":
            return string
        elif toapp == "":
            return 0
        else:
            return int(toapp)

    def def_url(self, url):
        if url == "https://www.wahapedia.ru/wh40k10ed/factions/adepta-sororitas/datasheets.html":
            return 0
        elif url == "https://wahapedia.ru/wh40k10ed/factions/orks/datasheets.html":
            return 1
        

    def parse(self, response):
        name = response.css('.dsH2Header').xpath("string()").extract()    
        data = response.css('.dsCharValue').xpath("string()").extract()
        unitComp = response.css('.dsUl').xpath('string()').extract()
        splitNames = response.css(".dsModelName").xpath('string()').extract() 
        invVals = response.css(".dsCharInvulValue").xpath('string()').extract()
        weapons = response.css(".wTable2_short").xpath('string()').extract()
        weapRan = response.css(".ct").xpath('string()').extract()
        info = response.css(".dsAbility").xpath('string()').extract()

        curr_url = self.def_url(response.url)

        M = []
        T = []
        Sv = []
        W = []
        Ld = []
        OC = []
        
        Range = []
        A = []
        BS = []
        S = []
        AP = []
        D = []

        numOfModels = []
        names = []
        IVSave = []
        all_data = {"UnitData": [], "WeaponData": []}
        
        ind = 0
        for i in name:
            if i[-1] != ")":
                names.append(splitNames[ind])
                ind += 1
                names.append(splitNames[ind])
                ind += 1
            else:
                # get rid of measurements
                unitName = ""
                app = True
                ind1 = 0
                while app == True:
                    if i[ind1] == "(":
                        app = False
                    else:
                        unitName += i[ind1]
                    ind1 += 1
                names.append(unitName)
        ind = 0
        bossNobInd = 0
        for i in unitComp:
            if curr_url == 0:
                if i[-len("Superior"):] != "Superior":
                    numOfModels.append(int(i[0]))
                elif i[-len("Repentia Superior"):] == "Repentia Superior" or i[-len("Novitiate Superior"):] == "Novitiate Superior":
                    numOfModels.append(int(i[0]))
                if i[-len("EPIC HERO"):] == "EPIC HERO":
                    IVSave.append(self.toint(invVals[ind]))
                    ind += 1
                else:
                    IVSave.append(0)
            elif curr_url == 1:
                numBossNob = 0
                if i[-len("Spanners"):] != "Spanners" and i[-len("Kaptin"):] != "Kaptin" and i[-len("Big Mek with Kustom Force Field"):] != "Big Mek with Kustom Force Field": 
                    numOfModels.append(int(i[0]))
                if i[-len("EPIC HERO"):] == "EPIC HERO":
                    IVSave.append(self.toint(invVals[ind]))
                    ind += 1
                else:
                    IVSave.append(0)

        
        ind = 0
        for i in data:
            if ind == 0:
                M.append(self.toint(i))
                ind = 1

            elif ind == 1:
                T.append(self.toint(i))
                ind = 2

            elif ind == 2:
                Sv.append(self.toint(i))
                ind = 3

            elif ind == 3:
                W.append(self.toint(i))
                ind = 4
            
            elif ind == 4:
                Ld.append(self.toint(i))
                ind = 5

            elif ind == 5:
                OC.append(self.toint(i))
                ind = 0
        
        ind = 0
        for i in weapRan:
            if i != "RANGE" and i != "A" and i != "BS" and i != "WS" and i != "S" and i != "AP" and i != "D":
                if ind == 0:
                    Range.append(self.toint(i))
                    ind += 1
                elif ind == 1:
                    A.append(self.toint(i))
                    ind += 1
                elif ind == 2:
                    BS.append(self.toint(i))
                    ind += 1
                elif ind == 3:
                    S.append(self.toint(i))
                    ind += 1
                elif ind == 4:
                    AP.append(self.toint(i))
                    ind += 1
                elif ind == 5:
                    D.append(self.toint(i))
                    ind = 0
        equ = []
        num = 0
        for entry in info:
            for ind in range(len(entry)):
                if entry[ind:ind+len("is equipped with:")] == "is equipped with:":
                    app = True
                    appInd = ind+len("is equipped with:")+1
                    weap = []
                    weapName = ""
                    while app == True:
                        if appInd == len(entry)-1:
                            weap.append(weapName)
                            app == False
                            break
                        if entry[appInd] == ".":
                            weap.append(weapName)
                            app = False
                        else:
                            if entry[appInd] == ";":
                                appInd += 1
                                weap.append(weapName)
                                weapName = ""
                            else:
                                weapName += entry[appInd]
                        appInd += 1
                    if weap[0] != "nothing":
                        equ.append(weap)
                        num += 1
        equ.append(["slugga", "choppa"])

        for i in range(len(M)):
            if curr_url == 0:
                all_data["UnitData"].append({"Army": "Sisters_of_Battle", "Name": names[i], "Movement": M[i], "#OfModels": numOfModels[i],"T": T[i], "Sv": Sv[i], "W": W[i], "Ld": Ld[i], "OC": OC[i], "IVSave": IVSave[i], "Weapons": equ[i]})
            elif curr_url == 1:
                all_data["UnitData"].append({"Army": "Orks", "Name": names[i], "Movement": M[i], "#OfModels": numOfModels[i],"T": T[i], "Sv": Sv[i], "W": W[i], "Ld": Ld[i], "OC": OC[i], "IVSave": IVSave[i], "Weapons": equ[i]})
        for i in range(len(weapons)):
            if curr_url == 0:
                if Range[i] == "Melee":
                    all_data["WeaponData"].append({"Army": "Sisters_of_Battle", "Name": weapons[i], "Type": Range[i], "WS": BS[i], "S": S[i], "AP": AP[i], "Range": 2, "Damage": D[i]})
                else:
                    all_data["WeaponData"].append({"Army": "Sisters_of_Battle", "Name": weapons[i], "Type": "Ranged", "BS": BS[i], "S": S[i], "AP": AP[i], "Range": Range[i], "Damage": D[i]})
            elif curr_url == 1:
                if Range[i] == "Melee":
                    all_data["WeaponData"].append({"Army": "Orks", "Name": weapons[i], "Type": Range[i], "WS": BS[i], "S": S[i], "AP": AP[i], "Range": 2, "Damage": D[i]})
                else:
                    all_data["WeaponData"].append({"Army": "Orks", "Name": weapons[i], "Type": "Ranged", "BS": BS[i], "S": S[i], "AP": AP[i], "Range": Range[i], "Damage": D[i]})
        return all_data