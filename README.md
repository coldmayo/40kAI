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

### Using the GUI

```bash 
# cd into gui directory
$ cd gui

# run the executable
$ ./main
```

### Using the Shell Script

```bash
# run train.sh
$ ./train.sh
```