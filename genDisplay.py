import imageio
import os

images = []

savePath = "display/"

files = os.listdir(savePath)
files = [os.path.join(savePath, f) for f in files]
files.sort(key=lambda x: os.path.getmtime(x))

for fil in files:
    images.append(imageio.imread(fil))
imageio.mimsave('model_train.gif', images)