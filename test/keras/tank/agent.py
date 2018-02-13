# -*- coding: utf-8 -*-
import random
import numpy as np
from collections import deque

from keras.models import Sequential
from keras.layers import Dense, Flatten, Conv2D
from keras.optimizers import Adam
from keras import backend as K


class Agent:
    def __init__(self, batch_size, action_size, input_rows, input_cols, input_channels):
        self.batch_size = batch_size
        self.action_size = action_size
        self.input_rows = input_rows
        self.input_cols = input_cols
        self.input_channels = input_channels
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.01
        self.model = self._build_model()

    def _build_model(self):
        if K.image_data_format() == 'channels_first':
            input_shape = (self.input_channels, self.input_rows, self.input_cols)
        else:
            input_shape = (self.input_rows, self.input_cols, self.input_channels)

        model = Sequential()
        # Conv2D Param Count: (3[宽] * 3[高] * 3[通道数] + 1[bias]) * 32[filter数] = 320
        model.add(Conv2D(filters=32,
                         kernel_size=(3, 3),
                         activation='relu',
                         input_shape=input_shape))
        # Conv2D Param Count: (3 * 3 * 32 + 1) * 64 = 18496
        model.add(Conv2D(filters=64,
                         kernel_size=(3, 3),
                         activation='relu'))
        model.add(Conv2D(filters=64,
                         kernel_size=(3, 3),
                         activation='relu'))
        model.add(Flatten())
        model.add(Dense(128, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        print('input shape:', input_shape)
        model.summary()

        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def action(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        else:
            act_values = self.model.predict(state)
            return np.argmax(act_values[0])  # returns action

    def repeat(self):
        minibatch = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = self.model.predict(state)
            if done:
                target[0][action] = reward
            else:
                next_target = self.model.predict(next_state)
                target[0][action] = reward + self.gamma * np.amax(next_target[0])
            self.model.fit(state, target, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)
