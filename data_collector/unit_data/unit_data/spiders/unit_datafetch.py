import scrapy

class DataSpider(scrapy.Spider):
    name = "data"

    f = open('links.json', 'r+')
    f.truncate(0)

    def start_requests(self):
        urls = ["https://www.wahapedia.ru/wh40k10ed/factions/adepta-sororitas/datasheets.html"]

        for i in urls:
            yield scrapy.Request(url = i, callback = self.parse)
    def toint(self, string):
        toapp = ""
        for j in string:
            if j.isnumeric() == True:
                toapp += j
        if toapp == "":
            return 0
        else:
            return int(toapp)
    def parse(self, response):
        name = response.css('.dsH2Header').xpath("string()").extract()    
        data = response.css('.dsCharValue').xpath("string()").extract()
        unitComp = response.css('.dsUl').xpath('string()').extract()
        splitNames = response.css(".dsModelName").xpath('string()').extract() 
        invVals = response.css(".dsCharInvulValue").xpath('string()').extract()
        M = []
        T = []
        Sv = []
        W = []
        Ld = []
        OC = []
        numOfModels = []
        names = []
        IVSave = []
        all_data = {"UnitData": []}
        
        ind = 0
        for i in name:
            if i == "Aestred Thurga And Agathae Dolan" or i == "Daemonifuge" or i == "Saint Celestine" or i == "Repentia Squad" or i == "Sisters Novitiate Squad":
                names.append(splitNames[ind])
                ind += 1
                names.append(splitNames[ind])
                ind += 1
            else:
                names.append(i)
        ind = 0
        for i in unitComp:
            if i[-len("Superior"):] != "Superior":
                numOfModels.append(int(i[0]))
            elif i[-len("Repentia Superior"):] == "Repentia Superior" or i[-len("Novitiate Superior"):] == "Novitiate Superior":
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

        for i in range(len(M)):
            all_data["UnitData"].append({"Army": "Sisters_of_Battle", "Name": names[i], "Movement": M[i], "#OfModels": numOfModels[i],"T": T[i], "Sv": Sv[i], "W": W[i], "Ld": Ld[i], "OC": OC[i], "IVSave": IVSave[i]})                
        return all_data