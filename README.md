<h1 align="center">
  <br>
  <br>
  40kAI
  <br>
</h1>

<p align="center">
    <a href="#description">Description</a> •
    <a href="#gameplay">Gameplay</a> •
    <a href="#installation">Installation</a> •
    <a href="#contact-me">Contact</a>
</p>

## Description

I am new to Warhammer 40k and scared to play against others, so I decided to make a model that could play against me using Reinforcement Learning. To accomplish this, I am creating a custom 40k environment using Gymnasium and a DQN using Pytorch. 

## Gameplay

Just like the tabletop game, it is played in turns, with each turn divided into several phases:<br>

1. Movement Phase
   - Players move their units across the battlefield according to their movement characteristic
   - Units can move, advance, and fall back
2. Shooting Phase
   - Units equipped with ranged weapons can target and attack enemy units within their weapon's range
3. Charge Phase
   - Units within 12 inches of each other can attempt to charge and engage in close combat.
   - The player rolls 2D6 and if the result brings the unit within 5 inches of the enemy unit (in Engagement Range) successfully charge, Otherwise the unit fails and does not move
4. Fight Phase
    - Close combat between engaged units is resolved

The object of the game is to kill all of the units on the opposing team.

## Installation

### Application 

Before proceeding make sure your device meets the below requirements:
- Runs a Linux Distribution (Windows and Mac not supported)
   - Confirmed to work on Arch Linux
- Has the following installed:
   - Python and pip
   - gtk and gtkmm
   - make
   - cmake
   - gcc
   - nlohmann-json

```bash
# clone repo
$ git clone https://github.com/coldmayo/40kAI.git

# go into /40kAI/installation/ directory
$ cd installation

# start the install script
$ make run

# while running the script, type "install" into the prompt
> install

# Once finished, exit the script with the "exit" command
> exit
```

Once the above is completed, one should be able to find the .desktop file in the /home/your_username/.local/share/applications directory.

Go <a href="https://github.com/coldmayo/40kAI/blob/main/gui/README.md">here</a> to learn more about how to use the app.

### Bash Scripts

If you don't use the install script you have to install all of the python packages manually. Luckily the list of requirements are a lot smaller (all you need is Python and pip). Instructions are as follows below:

```bash
# create virtual environment
$ python -m venv .venv

# cd into gym_mod folder
$ cd gym_mod

# install packages
$ pip install .

# train model (chmod +x train.sh if permission error)
./train.sh

# play against model (chmod +x play.sh if permission error)
./play.sh
```
## Contact Me

This project is still being worked on, if you have any suggestions or found bugs you can either open an issue or email me <a href="mailto:coldmayo@proton.me">here</a>. 