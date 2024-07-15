import time
import os

def sendToGUI(message):
    f = open(os.path.abspath("gui/")+"/response.txt", "w")
    f.write(message)
    f.close()

def recieveGUI():
    time.sleep(1)
    file_path = os.path.abspath("gui/")+"/response.txt"
    if os.path.exists(file_path):
        os.remove(file_path)

    while True: 
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                response = f.read()
            os.remove(file_path)
            return response
