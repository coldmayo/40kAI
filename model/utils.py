import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import collections
import numpy as np
import pandas as pd

import itertools

import random
import math

from collections import namedtuple

EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 1000
BATCH_SIZE = 128
GAMMA = 0.99

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

Transition = namedtuple('Transition',('state', 'action', 'next_state', 'reward'))

def select_action(env, state, steps_done, policy_net):
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
            sampled_action['charge']
        ]
        action = torch.tensor([action_list], device=device, dtype=torch.long)
        return action

def convertToDict(action):
    naction = action.numpy()[0]
    action_dict = {
        'move': naction[0],
        'attack': naction[1],
        'shoot': naction[2],
        'charge': naction[3]
    }
    return action_dict

def optimize_model(policy_net, target_net, optimizer, memory):
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)
    batch = Transition(*zip(*transitions))

    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                          batch.next_state)), device=device, dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state
                                                if s is not None])
    desired_shape = (1, 13)

    state_batch = torch.cat([s.view(desired_shape) if s is not None else torch.zeros(desired_shape) for s in batch.state], dim=0)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    state_action_values = policy_net(state_batch)
    move_action, attack_action, shoot_action, charge_action = state_action_values
    selected_action_values = torch.cat([
        move_action.gather(1, action_batch[:, 0].unsqueeze(1)),
        attack_action.gather(1, action_batch[:, 1].unsqueeze(1)),
        shoot_action.gather(1, action_batch[:, 2].unsqueeze(1)),
        charge_action.gather(1, action_batch[:, 3].unsqueeze(1))
    ], dim=1)

    next_state_values = torch.zeros((BATCH_SIZE,4), device=device)
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
    loss.backward()
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    optimizer.step()