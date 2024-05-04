import json
import os
import sys

def makeFile(numIters):

    data = {
        "Army1":"Space Marines",
        "Army2":"Space Marines",
        "numLife": int(numIters)
    }

    with open('data.json', 'w') as f:
        json.dump(data, f)
    
def getNumLife():

    with open(os.path.abspath("data.json")) as j:
        data = json.loads(j.read())

    return data["numLife"]

def delFile():
    os.system("rm data.json")

if __name__ == "__main__":
    makeFile(sys.argv[1])