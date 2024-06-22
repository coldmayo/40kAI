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

1. Command Phase
   - Both players gain 1 Command Point and resolve BattleShock tests
2. Movement Phase
   - Players move their units across the battlefield according to their movement characteristic
   - Units can move, advance, and fall back
3. Shooting Phase
   - Units equipped with ranged weapons can target and attack enemy units within their weapon's range
4. Charge Phase
   - Units within 12 inches of each other can attempt to charge and engage in close combat.
   - The player rolls 2D6 and if the result brings the unit within 5 inches of the enemy unit (in Engagement Range) successfully charge, Otherwise the unit fails and does not move
5. Fight Phase
    - Close combat between engaged units is resolved

Before the game is played, a deployment card is drawn at random. These cards determine where the players can place their units on the board.<br>

The only mission available is Only War and the Victory Conditions are described below:
- Major Victory:
   - All foes are eliminated
- Slay and Secure:
   - At the end of the game each Objective Marker are worth 2 Victory Points to the player that controls it. Players also earn D3 Victory Points if the opposing Warlord is defeated
- Ancient Relic:
   - At the start of the first battle round, but before the first turn begins, select an objective marker. At the end of the battle, whoever controls that objective marker receives 6 Victory Points
- Domination:
   - At the end of each turn each objective marker is worth 1 Victory Point to the player who controls it. Keep a running score from turn to turn

These victory conditions are decided by a roll of a D3 before the first turn and there will be 5 total turns in a game. (or less if one army is completely slain before then)

Current factions available are:
- Space Marines
- Adeptus Custodes
- Adepta Sororitas
- Orks
- Tyranids
- Adeptus Mechanicus
- Astra Militarum
- Tau

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
