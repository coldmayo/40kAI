<h1 align="center">
  <br>
  <br>
  40kAI
  <br>
</h1>

## Contents


1. <a href="#description">Description</a>
2. <a href="#gameplay">Gameplay</a>
	- <a href="#phases">Phases</a>
	- <a href="#victory-conditions">Victory Conditions</a>
	- <a href="#stratagems">Stratagems</a>
	- <a href="#factions">Factions</a>
3. <a href="#installation">Installation</a>
4. <a href="#contact-me">Contact</a>

## Description

I was new to the Warhammer 40k tabletop game and I unfortunitly had no one to play with. So, I took matters into my own hands. I decided to make an RL model to play against, to sharpen my skills. To accomplish this, I am making a custom 40k Gymnasium environment and a DQN using PyTorch.

## Gameplay

### Phases

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

### Deployment

Before the game is played, a deployment card is drawn at random. These cards determine where the players can place their units on the board. The ones currently available are:
- Search and Destroy
- Hammer and Anvil
- Dawn of War

### Victory Conditions

The only mission available is Only War and the Victory Conditions are described below:
- Major Victory:
   - All foes are eliminated
- Slay and Secure:
   - At the end of the game each Objective Marker are worth 2 Victory Points to the player that controls it. Players also earn D3 Victory Points if the opposing Warlord is defeated
- Ancient Relic:
   - At the start of the first battle round, but before the first turn begins, select an objective marker. At the end of the battle, whoever controls that objective marker receives 6 Victory Points
- Domination:
   - At the end of each turn each objective marker is worth 1 Victory Point to the player who controls it. Keep a running score from turn to turn

These victory conditions are decided by a roll of a D3 before the first turn and there will be 5 total turns in a game. (or less if one army gets a Major Victory before then)

### Stratagems

Also, players can use Command Points on Stratagems, which are special abilities that can be activated during certian points of the game. The ones that are supported so far are:
- Fire Overwatch
	- This strategem allows the selected unit to act as if it's their Shooting Phase before the opponent's charge roll
- Insane Bravery
	- If a unit fails a Battle shock test, the player can use this strategem so the unit is not effected by it
- Smokescreen
	- Gives all models in unit the Benefit of Cover and the Stealth ability until the end of their opponent's next turn
- Heroic Intervention
	- The player can select one of their units and use 2 CP to charge an enemy unit while they are in combat with another unit. So essentailly the player can switch units in combat. This only works if the unit is within 6 inches of the enemy.
### Factions

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
   - Confirmed to work on Arch Linux (working on more)
- Has the following installed:
   - Python and pip
   - gtkmm
   - make
   - cmake
   - gcc
   - nlohmann-json

```bash
# clone repo
$ git clone https://github.com/coldmayo/40kAI.git

# go into /40kAI/installation/ directory
$ cd installation

# (optional) build install script
$ make

# run install script
$ make run

# or
$ ./install

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
