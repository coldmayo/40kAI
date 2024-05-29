import scrapy

class DataSpider(scrapy.Spider):
    name = "data"

    f = open('links.json', 'r+')
    f.truncate(0)

    def start_requests(self):
        urls = ["https://www.wahapedia.ru/wh40k10ed/factions/adepta-sororitas/datasheets.html"]

        for i in urls:
            yield scrapy.Request(url = i, callback = self.parse)
    
    def parse(self, response):
        names = response.css('.dsH2Header').xpath("string()").extract()    
        data = response.css('.dsProfileBaseWrap').xpath("string()").extract()
        M = []
        T = []
        Sv = []
        W = []
        Ld = []
        OC = []

        for i in data:
            ind = -1
            for j in range(len(i)):
                char = i[j]
                if char == "M":
                    ind = 0
                elif char == "T":
                    ind = 1
                elif char == "S" and i[j+1] == "v":
                    ind = 2
                elif char == "W":
                    ind = 3
                elif char == "L" and i[j+1] == "d":
                    ind = 4
                elif char == "O" and i[j+1] == "C":
                    ind = 5

                if ind == 0 and char.isnumeric() == True:
                    ind = -1
                    if i[j+1].isnumeric() == True:
                        val = int(str(char)+str(i[j+1]))
                        if val <= 12:
                            M.append(val)
                        else:
                            M.append(int(char))
                    else:
                        M.append(int(char))

                elif ind == 1 and char.isnumeric() == True:
                    ind = -1
                    T.append(int(char))

                elif ind == 2 and char.isnumeric() == True:
                    ind = -1
                    Sv.append(int(char))

                elif ind == 3 and char.isnumeric() == True:
                    ind = -1
                    W.append(int(char))

                elif ind == 4 and char.isnumeric() == True:
                    ind = -1
                    Ld.append(int(char))

                elif ind == 5 and char.isnumeric() == True:
                    ind = -1
                    OC.append(int(char))
                

        return {
            "names": names,
            "M": M,
            "T": T,
            "Sv": Sv,
            "W": W,
            "Ld": Ld,
            "OC": OC,
            "check_lens": [len(names), len(M), len(T), len(Sv), len(W), len(Ld), len(OC)]
            }