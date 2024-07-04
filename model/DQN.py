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
        self.use_cp = nn.Linear(128, n_actions[4])
        self.cp_on = nn.Linear(128, n_actions[5])
        self.move_len = []
        for i in range(len(n_actions)-6):
            self.move_len.append(nn.Linear(128, n_actions[i+6]))

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        move_action = self.move_head(x)
        attack_action = self.attack_head(x)
        shoot_action = self.shoot_head(x)
        charge_action = self.charge_head(x)
        use_cp_action = self.use_cp(x)
        cp_on_action = self.cp_on(x)
        decs = [move_action, attack_action, shoot_action, charge_action, use_cp_action, cp_on_action]
        for i in range(len(self.move_len)):
            decs.append(self.move_len[i](x))
        return decs
