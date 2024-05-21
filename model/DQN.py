import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class DQN(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(n_observations, 128)
        self.layer2 = nn.Linear(128, 128)
        # layer3 for all actions
        self.move_head = nn.Linear(128, n_actions[0])
        self.attack_head = nn.Linear(128, n_actions[1])
        self.shoot_head = nn.Linear(128, n_actions[2])
        self.charge_head = nn.Linear(128, n_actions[3])

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        move_action = self.move_head(x)
        attack_action = self.attack_head(x)
        shoot_action = self.shoot_head(x)
        charge_action = self.charge_head(x)
        return [move_action, attack_action, shoot_action, charge_action]
