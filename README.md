<h1 align="center">
  <br>
  <br>
  40kAI
  <br>
</h1>

<p align="center">
    <a href="#description">Description</a> •
    <a href="#how-to-use">How to Use</a>
</p>

## Description

I am new to Warhammer 40k and scared to play against others, so I decided to make a model that can play against me using Reinforcement Learning. To accomplish this, I am creating a custom 40k environment to be used with the Gym API. 

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

## How to Use

Before training the gym environment must be installed. Follow the instructions below:

```bash
# Clone this repository
$ git clone https://github.com/coldmayo/40kAI.git

# cd into the gym_mod directory
$ cd gym_mod

# create Python package
$ pip install .
```

### Using the GUI (for Linux)

Make sure you have gtkmm installed

```bash 
# cd into gui directory
$ cd gui/build

# run the executable
$ ./Application
```

### Using the Shell Script

```bash
# run train.sh
$ ./train.sh
```