import imageio
import os
from tqdm import tqdm

def makeGif(Type="train"):
    print("Starting...")
    images = []

    savePath = "display/"

    files = os.listdir(savePath)
    files = [os.path.join(savePath, f) for f in files]
    files.sort(key=lambda x: os.path.getmtime(x))

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