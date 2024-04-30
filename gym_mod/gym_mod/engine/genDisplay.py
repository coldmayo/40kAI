import imageio
import os
from tqdm import tqdm
import numpy as np

def makeGif(numOfLife, Type = "train", trunc = False):
    print("Starting...")
    images = []

    savePath = "display/"

    files = os.listdir(savePath)
    files = [os.path.join(savePath, f) for f in files]
    files.sort(key=lambda x: os.path.getmtime(x))

    if trunc == True:
        its = np.arange(numOfLife)
        itsChosen = np.random.choice(its, 10, replace=False)
        newFiles = []
        print(itsChosen)

        for i in files:
            for j in itsChosen:
                if i[:9] == "display/{}".format(j) or i[:10] == "display/{}".format(j) or i[:11] == "display/{}".format(j):
                    newFiles.append(i)
        files = newFiles
        print(files)


    for fil in tqdm(files):
        images.append(imageio.imread(fil))
    if Type == "train":
        imageio.mimsave('model_train.gif', images)
        imageio.mimsave('gui/img/model_train.gif', images)
        imageio.mimsave('gui/build/img/model_train.gif', images)
        imageio.mimsave('gui/build/Debug/img/model_train.gif', images)
    elif Type == "val":
        imageio.mimsave('model_val.gif', images)
    print("Done")

if __name__ == "__main__":
    makeGif()