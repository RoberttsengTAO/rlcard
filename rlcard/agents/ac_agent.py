#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 09:57:50 2020

@author: robert.tseng
"""


import numpy as np
import tensorflow as tf
import pylab
import time
#import gym
from keras.layers import Dense, Input
from keras.models import Model
from keras.optimizers import Adam
from keras import backend as K
import rlcard
from rlcard.utils.utils import *
from collections import namedtuple
Transition = namedtuple('Transition', ['state', 'action', 'reward', 'next_state', 'done'])

class A2Cagent:
    def __init__(self,
                 sess, 
                 state_size, 
                 action_size, 
                 actor_lr=0.001,
                 critic_lr=0.001,
                 discount_factor=0.9,
                 layers=[24, 24]):
        ## setting initial value 
        self.state_size = state_size # input layer 
        self.action_size = action_size # output layer 
        self.actor_lr = actor_lr # actor learning rate 
        self.critic_lr = critic_lr # critic leanrning rate 
        self.discount_factor = discount_factor # 
        self.hidden1, self.hidden2 = layers[0], layers[1] ## layer n count
        
        ## create model 
        self.actor, self.critic = self.build_model()
        self.optimizer = [self.actor_optimizer(), self.critic_optimizer()]
        ## setting tensorflow training env 
        self.sess = sess
        K.set_session(self.sess)
        self.sess.run(tf.global_variables_initializer())
        self.memory = Memory()
        # approximate policy and value using Neural Network
    # actor -> state is input and probability of each action is output of network
    # critic -> state is input and value of state is output of network
    # actor and critic network share first hidden layer
    def build_model(self):
        state = Input(batch_shape=(None,  self.state_size))
        shared = Dense(self.hidden1, input_dim=self.state_size, activation='relu', kernel_initializer='glorot_uniform')(state)

        actor_hidden = Dense(self.hidden2, activation='relu', kernel_initializer='glorot_uniform')(shared)
        actor_hidden1 = Dense(self.hidden2, activation='relu', kernel_initializer='glorot_uniform')(actor_hidden)
        action_prob = Dense(self.action_size, activation='softmax', kernel_initializer='glorot_uniform')(actor_hidden1)

        value_hidden = Dense(self.hidden2, activation='relu', kernel_initializer='he_uniform')(shared)
        state_value = Dense(1, activation='linear', kernel_initializer='he_uniform')(value_hidden)

        actor = Model(inputs=state, outputs=action_prob)
        critic = Model(inputs=state, outputs=state_value)

        actor._make_predict_function()
        critic._make_predict_function()

        actor.summary()
        critic.summary()

        return actor, critic
        
    # make loss function for Policy Gradient
    # [log(action probability) * advantages] will be input for the back prop
    # we add entropy of action probability to loss
    def actor_optimizer(self):
        action = K.placeholder(shape=(None, self.action_size))
        advantages = K.placeholder(shape=(None, ))

        policy = self.actor.output

        good_prob = K.sum(action * policy, axis=1)
        eligibility = K.log(good_prob + 1e-10) * K.stop_gradient(advantages)
        loss = -K.sum(eligibility)

        entropy = K.sum(policy * K.log(policy + 1e-10), axis=1)

        actor_loss = loss + 0.05*entropy

        optimizer = Adam(lr=self.actor_lr)
        updates = optimizer.get_updates(self.actor.trainable_weights, [], actor_loss)
        train = K.function([self.actor.input, action, advantages], [], updates=updates)
        return train

    # make loss function for Value approximation
    def critic_optimizer(self):
        discounted_reward = K.placeholder(shape=(None, ))

        value = self.critic.output

        loss = K.mean(K.square(discounted_reward - value))

        optimizer = Adam(lr=self.critic_lr)
        updates = optimizer.get_updates(self.critic.trainable_weights, [], loss)
        train = K.function([self.critic.input, discounted_reward], [], updates=updates)
        return train
    ## 
    def step(self, state):
        ''' Returns the action to be taken.
        Args:
            state (dict): The current state
        Returns:
            action (int): An action id
        '''
        obs = state['obs']
        legal_actions = state['legal_actions']
        action_probs = self.actor.predict(np.expand_dims(obs, 0))[0]
        #probs = agent.actor.predict(np.expand_dims(obs, 0))[0]
        probs = remove_illegal(action_probs, legal_actions)
        action = np.random.choice(len(probs), p=probs)
        return action
    def eval_step(self, state):
        obs = state['obs']
        legal_actions = state['legal_actions']
        action_probs = self.actor.predict(np.expand_dims(obs, 0))[0]
        #probs = agent.actor.predict(np.expand_dims(obs, 0))[0]
        probs = remove_illegal(action_probs, legal_actions)
        action = np.argmax(probs)
        return action
        
    def feed(self, ts):
        ''' Feed data to inner RL agent

        Args:
        '''
        (state, action, reward, next_state, done)=tuple(ts)
        self.memory.save(state['obs'], action, reward, next_state['obs'], done)
    def discount_rewards(self, rewards, states, done=True):
        discounted_rewards = np.zeros_like(rewards)
        
        running_add = 0
        if not done:
            running_add = self.critic.predict(np.reshape(states[-1], (1, self.state_size)))[0]
        for t in reversed(range(0, len(rewards))):
            running_add = running_add * self.discount_factor + rewards[t]
            discounted_rewards[t] = running_add
        return discounted_rewards
    def train(self, done):
        ## data extract 
        data = np.asarray(self.memory.memory)
        ## 'Transition', ['state', 'action', 'reward', 'next_state', 'done']
        # states numpy 
        states = np.asarray(data[:, 0].tolist())
        # action dummy numpy 
        actions = np.zeros([data[:, 1].shape[0], self.action_size])
        for i in range(data[:, 1].shape[0]):
            actions[i, data[:, 1][i]] = 1
        # reward list 
        reward = data[:, 2].astype('int').tolist()
        
        ## compute ploicy and Q value
        discounted_rewards = self.discount_rewards(reward, states, done)
        values = self.critic.predict(states)[:, 0]
        advantages = discounted_rewards - values
        if not done:
            print("Training.....")
            self.optimizer[0]([states, actions, advantages])
            self.optimizer[1]([states, discounted_rewards])
        self.memory.memory = []
        return('OK')
        
class Memory(object):
    ''' Memory for saving transitions 
    '''
    def __init__(self):
        ''' Initialize
        Args:
            memory_size (int): the size of the memroy buffer
        '''
        self.memory = []

    def save(self, state, action, reward, next_state, done):
        ''' Save transition into memory

        Args:
            state (numpy.array): the current state
            action (int): the performed action ID
            reward (float): the reward received
            next_state (numpy.array): the next state after performing the action
            done (boolean): whether the episode is finished
        '''
        transition = Transition(state, action, reward, next_state, done)
        self.memory.append(transition)
        