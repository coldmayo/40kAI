from gym.envs.registration import register

register(
    id='40kAI-v0',
    entry_point='gym_mod.gym_mod.envs:Warhammer40kEnv',
    max_episode_steps=300,
)