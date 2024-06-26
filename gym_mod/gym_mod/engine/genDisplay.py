import imageio
import os
from tqdm import tqdm
import numpy as np

def makeGif(numOfLife, name="", Type = "train", trunc = False):
    print("\nForging model_train.gif...\n")
    images = []

    savePath = "display/"

    files = os.listdir(savePath)
    files = [os.path.join(savePath, f) for f in files]
    files.sort(key=lambda x: os.path.getmtime(x))

    if trunc == True:
        its = np.arange(numOfLife)
        itsChosen = np.random.choice(its-1, 30, replace=False)+1
        newFiles = []
        print(itsChosen)

        for i in files:
            for j in itsChosen:
                digits = len(str(j))
                print()
                if i[:9+digits] == "display/{}_".format(j):
                    newFiles.append(i)
        files = newFiles
        print(files)


    for fil in tqdm(files):
        images.append(imageio.imread(fil))
    if Type == "train":
        imageio.mimsave('metrics/model_train{}.gif'.format(name), images)
        imageio.mimsave('gui/img/model_train{}.gif'.format(name), images)
        imageio.mimsave('gui/build/img/model_train{}.gif'.format(name), images)
        imageio.mimsave('gui/build/Debug/img/model_train{}.gif'.format(name), images)
    elif Type == "val":
        imageio.mimsave('val/model_val.gif', images)
    print("Generated gif")