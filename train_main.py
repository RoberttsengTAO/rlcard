#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 13:32:04 2020

@author: robert.tseng
"""

import os
import tensorflow as tf
os.chdir('/Users/robert.tseng/Documents/fix_version/holdem_game')
import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.agents.ac_agent import A2Cagent
from rlcard.envs.holdem import holdemEnv
from rlcard.utils.utils import *
from rlcard.utils.utils import set_global_seed
from rlcard.utils.logger import Logger
import matplotlib.pyplot as plt
import numpy as np
import math
env = holdemEnv(num_players=2)
eval_env = holdemEnv(num_players=2)
state_size = env.state_shape[0]
action_size = env.action_num
sess = tf.Session()
agents = [A2Cagent(sess, state_size, action_size, actor_lr = 0.01, critic_lr = 0.01, discount_factor=.8) for i in range(env.player_num)]
env.set_agents(agents)
eval_env.set_agents(agents)
# =============================================================================
# training code
# =============================================================================
episode_num = 10000
evaluate_num = 100
reward = [0]*env.player_num
data = np.empty((0, env.player_num))
k = 0
max_reward = [-math.inf]*env.player_num
root_path = f'./holdem/model'
# log_path = root_path + 'log.txt'
# csv_path = root_path + 'performance.csv'
# figure_path = root_path + 'figures/'
# Init a Logger to plot the learning curve
# logger = Logger(xlabel='timestep', ylabel='reward', legend='NFSP on ZHJ', log_path=log_path,
#             csv_path=csv_path)
train_count = 0
for episode in range(episode_num):
    print(episode)
        # Generate data from the environment
    trajectories, c = env.run(is_training=True)
    # Feed transitions into agent memory, and train the agent
    train_count +=1
    reward = [0]*env.player_num
    for i in range(env.player_num):
        for ts in trajectories[i]:
            env.agents[i].feed(ts)
            # Train the agent            
        if train_count % 50 == 0:
            print("Train")
            env.agents[i].train(False)
    # Evaluate the performance. Play with random agents.
            print('Predict')
            for eval_episode in range(evaluate_num):
                _, payoffs = eval_env.run(is_training=False)
                reward[i] +=  payoffs[i]
            reward[i] /=  evaluate_num
            #if max_reward[i] < reward[i]:
            env.agents[i].actor.save_weights(root_path+'_'+str(i) +'/eqa2cagentreward'+str(reward[i])+'.h5')
            #max_reward[i] = max(max_reward[i], reward[i])
            print(reward)
            data = np.vstack(((data, np.asarray(reward))))
    if train_count % 50 == 0:
        plt.plot(data)
        plt.show()
    # Make plot
    # if episode % save_plot_every == 0 and episode > 0:
    # logger.make_plot(save_path=figure_path + str(episode) + '.png')
