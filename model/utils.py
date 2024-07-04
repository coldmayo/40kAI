import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import collections
import numpy as np
import pandas as pd
import os
import json

import itertools

import random
import math

from collections import namedtuple

with open(os.path.abspath("hyperparams.json")) as j:
    data = json.loads(j.read())

EPS_START = data["eps_start"]
EPS_END = data["eps_end"]
EPS_DECAY = data["eps_decay"]
BATCH_SIZE = data["batch_size"]
GAMMA = data["gamma"]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

Transition = namedtuple('Transition',('state', 'action', 'next_state', 'reward'))

def select_action(env, state, steps_done, policy_net, len_model):
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
        math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    
    if isinstance(state, collections.OrderedDict):
        state = torch.tensor([list(state.values())], device=device, dtype=torch.float).unsqueeze(0)
    elif isinstance(state, np.ndarray):
        state = torch.tensor(state, device=device, dtype=torch.float).unsqueeze(0)

    if sample > eps_threshold:
        with torch.no_grad():
            decision = policy_net(state)
            action = []
            for i in decision:
                larg = i.numpy().tolist()
                if len(list(itertools.chain(*larg))) > 1:
                    larg = list(itertools.chain(*larg))
                else: 
                    larg = list(itertools.chain(*larg))[0]
                action.append(pd.Series(larg).idxmax())
            return torch.tensor([action])
    else:
        sampled_action = env.action_space.sample()
        action_list = [
            sampled_action['move'],
            sampled_action['attack'],
            sampled_action['shoot'],
            sampled_action['charge'],
            sampled_action['use_cp'],
            sampled_action['cp_on']
        ]
        for i in range(len_model):
            label = "move_num_"+str(i)
            action_list.append(sampled_action[label])
        action = torch.tensor([action_list])
        return action

def convertToDict(action):
    naction = action.numpy()[0]
    action_dict = {
        'move': naction[0],
        'attack': naction[1],
        'shoot': naction[2],
        'charge': naction[3],
        'use_cp': naction[4],
        'cp_on': naction[5]
    }
    for i in range(len(naction)-6):
        label = "move_num_"+str(i)
        action_dict[label] = naction[i+6]
    return action_dict

def optimize_model(policy_net, target_net, optimizer, memory, n_obs):
    if len(memory) < BATCH_SIZE:
        return 0
    transitions = memory.sample(BATCH_SIZE)
    batch = Transition(*zip(*transitions))

    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                          batch.next_state)), device=device, dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state
                                                if s is not None])
    desired_shape = (1, n_obs)

    state_batch = torch.cat([s.view(desired_shape) if s is not None else torch.zeros(desired_shape) for s in batch.state], dim=0)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    state_action_values = policy_net(state_batch)
    move_action, attack_action, shoot_action, charge_action, use_cp_action, cp_on_action, *move_actions = state_action_values
    arr = [
        move_action.gather(1, action_batch[:, 0].unsqueeze(1)),
        attack_action.gather(1, action_batch[:, 1].unsqueeze(1)),
        shoot_action.gather(1, action_batch[:, 2].unsqueeze(1)),
        charge_action.gather(1, action_batch[:, 3].unsqueeze(1)),
        use_cp_action.gather(1, action_batch[:, 4].unsqueeze(1)),
        cp_on_action.gather(1, action_batch[:, 5].unsqueeze(1))
    ] 
    

    for i in range(len(move_actions)):
        arr.append(move_actions[i].gather(1, action_batch[:, i+6].unsqueeze(1)))
    selected_action_values = torch.cat(arr, dim=1)

    next_state_values = torch.zeros((BATCH_SIZE,6+len(move_actions)), device=device)
    with torch.no_grad():
        decision = target_net(non_final_next_states)
        action = []
        for i in decision:
            larg = i.numpy().tolist()
            if len(list(itertools.chain(*larg))) > 1:
                larg = list(itertools.chain(*larg))
            else: 
                larg = list(itertools.chain(*larg))[0]
            action.append(pd.Series(larg).idxmax())
        next_state_values[non_final_mask] = torch.tensor([action], dtype=torch.float)
    expected_state_action_values = (torch.transpose(next_state_values, 0,1) * GAMMA) + reward_batch

    criterion = nn.SmoothL1Loss()
    loss = criterion(torch.transpose(selected_action_values, 0,1), expected_state_action_values.unsqueeze(1))
    optimizer.zero_grad()
    loss.retain_grad()
    loss.backward()
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    optimizer.step()
    return loss.item()
