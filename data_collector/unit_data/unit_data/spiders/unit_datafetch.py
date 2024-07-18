import scrapy

class DataSpider(scrapy.Spider):
    name = "data"

    f = open('links.json', 'r+')
    f.truncate(0)

    def start_requests(self):
        urls = [
            "https://www.wahapedia.ru/wh40k10ed/factions/adepta-sororitas/datasheets.html", 
            "https://wahapedia.ru/wh40k10ed/factions/orks/datasheets.html", 
            "https://wahapedia.ru/wh40k10ed/factions/adeptus-custodes/datasheets.html",
            "https://wahapedia.ru/wh40k10ed/factions/tyranids/datasheets.html",
            "https://wahapedia.ru/wh40k10ed/factions/adeptus-mechanicus/datasheets.html",
            "https://wahapedia.ru/wh40k10ed/factions/astra-militarum/datasheets.html",
            "https://wahapedia.ru/wh40k10ed/factions/t-au-empire/datasheets.html"
        ]

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
        elif url == "https://wahapedia.ru/wh40k10ed/factions/adeptus-custodes/datasheets.html":
            return 2
        elif url == "https://wahapedia.ru/wh40k10ed/factions/tyranids/datasheets.html":
            return 3
        elif url == "https://wahapedia.ru/wh40k10ed/factions/adeptus-mechanicus/datasheets.html":
            return 4
        elif url == "https://wahapedia.ru/wh40k10ed/factions/astra-militarum/datasheets.html":
            return 5
        elif url == "https://wahapedia.ru/wh40k10ed/factions/t-au-empire/datasheets.html":
            return 6

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
        nums = 0
        for i in name:
            if i == "Death Korps Grenadier Squad":
                names.append(i)
            elif i[-1] != ")":
                names.append(splitNames[ind])
                ind += 1
                names.append(splitNames[ind])
                ind += 1
                if splitNames[ind-1] == "VETERAN HEAVY WEAPONS TEAM":
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
            nums += 1
        ind = 0
        bossNobInd = 0
        toDel = []
        nums = 0
        for i in unitComp:
            if curr_url == 0:
                if i[-len("Superior"):] != "Superior":
                    numOfModels.append(self.toint(i[0:2]))
                elif i[-len("Repentia Superior"):] == "Repentia Superior" or i[-len("Novitiate Superior"):] == "Novitiate Superior":
                    numOfModels.append(self.toint(i[0:2]))
                if i[-len("EPIC HERO"):] == "EPIC HERO":
                    IVSave.append(self.toint(invVals[ind]))
                    ind += 1
                else:
                    IVSave.append(0)
            elif curr_url == 1:
                numBossNob = 0
                if i[-len("Spanners"):] != "Spanners" and i[-len("Kaptin"):] != "Kaptin" and i[-len("Big Mek with Kustom Force Field"):] != "Big Mek with Kustom Force Field": 
                    numOfModels.append(self.toint(i[0:2]))
                if i[-len("EPIC HERO"):] == "EPIC HERO":
                    IVSave.append(self.toint(invVals[ind]))
                    ind += 1
                else:
                    IVSave.append(0)
            elif curr_url == 2:
                if i[-len("Superior"):] != "Superior":
                    numOfModels.append(self.toint(i[0:2]))
                if i[-len("EPIC HERO"):] == "EPIC HERO":
                    IVSave.append(self.toint(invVals[ind]))
                    ind += 1
                else:
                    IVSave.append(0)
            elif curr_url == 3:
                if i[-len("Nodebeasts*"):] != "Nodebeasts*" and i[-len("Prime"):] != "Prime":
                    numOfModels.append(self.toint(i[0:2]))
                if i[-len("EPIC HERO"):] == "EPIC HERO":
                    IVSave.append(self.toint(invVals[ind]))
                    ind += 1
                else:
                    IVSave.append(0)
            elif curr_url == 4:
                if i[-len("Alpha"):] != "Alpha" and i[-len("Princeps"):] != "Princeps":
                    numOfModels.append(self.toint(i[0:2]))
                if i[-len("EPIC HERO"):] == "EPIC HERO":
                    IVSave.append(self.toint(invVals[ind]))
                    ind += 1
                else:
                    IVSave.append(0)
            elif curr_url == 5:
                if i[-len("Sergeant"):] != "Sergeant" and i[-len("Watchmasters"):] != "Watchmasters" and i[-len("Bone ‘ead"):] != "Bone ‘ead" and i[-len("Tempestor"):] != "Tempestor" and i[-len("Ridemaster"):] != "Ridemaster":
                    numOfModels.append(self.toint(i[0:2]))
                else:
                    toDel.append(nums)
                if i[-len("EPIC HERO"):] == "EPIC HERO":
                    IVSave.append(self.toint(invVals[ind]))
                    ind += 1
                else:
                    IVSave.append(0)
                nums += 1
            elif curr_url == 6:
                if i[-len("Shas’ui"):] != "Shas’ui" and i[-len("Long-quill"):] != "Long-quill" and i[-len("Kill-broker"):] != "Kill-broker" and i[-len("Strain Leader"):] != "Strain Leader":
                    numOfModels.append(self.toint(i[0:2]))
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
        skip = 0
        for entry in info:
            for ind in range(len(entry)):
                if entry[ind:ind+len("is equipped with:")] == "is equipped with:" and entry[ind-len("Alpha model "):ind] != "Alpha model ":
                    app = True
                    appInd = ind+len("is equipped with:")+1
                    weap = []
                    weapName = ""
                    while app == True:
                        if appInd == len(entry)-1:
                            if weapName == "vaultswords":
                                weap.append("Vaultswords – Behemor [precision]")
                                weap.append("Vaultswords – Hurricanus [sustained hits 1]")
                                weap.append("Vaultswords – Victus [devastating wounds]")
                            else:
                                weap.append(weapName)
                            app == False
                            break
                        elif entry[appInd] == ".":
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
                    if weap[0] != "nothing" and weap[0] != "Fidelity":
                        equ.append(weap)
                        num += 1
                    elif curr_url == 3:
                        equ.append(weap)
                        num += 1
        if curr_url == 1:
            equ.append(["slugga", "choppa"])

        # check lens
        #print(curr_url, len(names), len(numOfModels), len(weapons), len(equ), len(M))

        armies = ["Sisters_of_Battle", "Orks", "Custodes", "Tyranids", "Mechanicus", "Militarum", "Tau"]

        for i in range(len(M)):
            all_data["UnitData"].append({"Army": armies[curr_url], "Name": names[i], "Movement": M[i], "#OfModels": numOfModels[i],"T": T[i], "Sv": Sv[i], "W": W[i], "Ld": Ld[i], "OC": OC[i], "IVSave": IVSave[i], "Weapons": equ[i]})
        for i in range(len(weapons)):
                if Range[i] == "Melee":
                    all_data["WeaponData"].append({"Army": armies[curr_url], "Name": weapons[i], "Type": Range[i], "WS": BS[i], "S": S[i], "AP": AP[i], "Range": 2, "Damage": D[i]})
                else:
                    all_data["WeaponData"].append({"Army": armies[curr_url], "Name": weapons[i], "Type": "Ranged", "BS": BS[i], "S": S[i], "AP": AP[i], "Range": Range[i], "Damage": D[i]})

        return all_data
