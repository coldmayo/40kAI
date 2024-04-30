# Compiling code

To compile:

```bash
$ cd gui/build
$ cmake ..
$ cmake --build . --config Debug
```

To test: 

Open the GUI.desktop file in a text editor

Set Path equal to the absolute directory of the gui folder. For example:
```bash
$ Path = /home/usr/40kAI/gui/
```
Then run the GUI.desktop file as an executable