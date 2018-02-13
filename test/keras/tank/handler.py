from player.ttypes import *
import logging
import threading
from agent import Agent
import numpy as np

episodes = 10000

input_rows = 19
input_cols = 19
input_channels = 7
batch_size = 32

action_size = 8
ACTIONS = [(1, 'move', Direction.UP),
           (1, 'move', Direction.DOWN),
           (1, 'move', Direction.LEFT),
           (1, 'move', Direction.RIGHT),
           (1, 'fire', Direction.UP),
           (1, 'fire', Direction.DOWN),
           (1, 'fire', Direction.LEFT),
           (1, 'fire', Direction.RIGHT)]
'''
ACTIONS = [(1, 'move', Direction.UP),
           (1, 'move', Direction.DOWN),
           (1, 'move', Direction.LEFT),
           (1, 'move', Direction.RIGHT),
           (1, 'fire', Direction.UP),
           (1, 'fire', Direction.DOWN),
           (1, 'fire', Direction.LEFT),
           (1, 'fire', Direction.RIGHT),
           (2, 'move', Direction.UP),
           (2, 'move', Direction.DOWN),
           (2, 'move', Direction.LEFT),
           (2, 'move', Direction.RIGHT),
           (2, 'fire', Direction.UP),
           (2, 'fire', Direction.DOWN),
           (2, 'fire', Direction.LEFT),
           (2, 'fire', Direction.RIGHT),
           (3, 'move', Direction.UP),
           (3, 'move', Direction.DOWN),
           (3, 'move', Direction.LEFT),
           (3, 'move', Direction.RIGHT),
           (3, 'fire', Direction.UP),
           (3, 'fire', Direction.DOWN),
           (3, 'fire', Direction.LEFT),
           (3, 'fire', Direction.RIGHT),
           (4, 'move', Direction.UP),
           (4, 'move', Direction.DOWN),
           (4, 'move', Direction.LEFT),
           (4, 'move', Direction.RIGHT),
           (4, 'fire', Direction.UP),
           (4, 'fire', Direction.DOWN),
           (4, 'fire', Direction.LEFT),
           (4, 'fire', Direction.RIGHT)]
'''


class PlayerServerHandler:
    def __init__(self):
        self.state = None
        self.agent = Agent(batch_size, action_size, input_rows, input_cols, input_channels)

    def uploadMap(self, gamemap):
        logging.info('gamemap: %s', gamemap)
        self.gamemap = gamemap

    def uploadParamters(self, arguments):
        logging.info('arguments: %s', arguments)
        self.arguments = arguments

    def assignTanks(self, tanks):
        logging.info('tanks: %s', tanks)
        self.tanks = tanks

    def latestState(self, state):
        logging.info('state: %s', state)
        if not self.state:
            self.state = state
            logging.info('prev state no value, return')
            return
        prev_state = self.state
        self.state = state
        prev_astate = self._to_agent_state(prev_state)
        astate = self._to_agent_state(state)

        reward = self._get_reward(prev_state, state)

        self.agent.remember(prev_astate, self.action, reward, astate, False)

        if len(self.agent.memory) > batch_size:
            # logging.info('thread starting...')
            # thread = threading.Thread(target=self.agent.repeat)
            # thread.start()
            self.agent.repeat()

    def getNewOrders(self):
        astate = self._to_agent_state(self.state)
        logging.info('agent state shape: %s', astate.shape)
        action_idx = self.agent.action(astate)
        action = ACTIONS[action_idx]
        self.action = action_idx
        orders = []
        if self.state.tanks:
            orders.append(Order(self.tanks[0], action[1], action[2]))
        logging.info('action: %s', orders)
        return orders

    def _get_reward(self, prev_state, state):
        my_tanks0, enemy_tanks0 = self._split_tanks(prev_state)
        my_tanks1, enemy_tanks1 = self._split_tanks(state)
        reward = (my_tanks0[0].hp - my_tanks1[0].hp) * 1
        reward = + (state.yourFlagNo - prev_state.yourFlagNo) * 2
        if enemy_tanks0 and enemy_tanks1:
            reward = + (enemy_tanks0[0].hp - enemy_tanks1[0].hp) * (-1)
        reward = + (state.enemyFlagNo - prev_state.enemyFlagNo) * (-2)

        return reward

    def _split_tanks(self, state):
        my_tanks = []
        enemy_tanks = []
        for tank in state.tanks:
            if tank.id in self.tanks:
                my_tanks.append(tank)
            else:
                enemy_tanks.append(tank)
        return my_tanks, enemy_tanks

    def _split_shells(self, state):
        my_shells = []
        enemy_shells = []
        for shell in state.shells:
            if shell.id in self.tanks:
                my_shells.append(shell)
            else:
                enemy_shells.append(shell)
        return my_shells, enemy_shells

    def _to_agent_state(self, state):
        my_tanks, enemy_tanks = self._split_tanks(state)
        my_shells, enemy_shells = self._split_shells(state)

        map_channel = self.gamemap

        mytank_hp_channel = np.zeros([input_rows, input_cols])
        for t in my_tanks:
            mytank_hp_channel[t.pos.x][t.pos.y] = t.hp

        mytank_dir_channel = np.zeros([input_rows, input_cols])
        for t in my_tanks:
            mytank_dir_channel[t.pos.x][t.pos.y] = t.dir

        myshell_dir_channel = np.zeros([input_rows, input_cols])
        for t in my_shells:
            myshell_dir_channel[t.pos.x][t.pos.y] = t.dir

        entank_hp_channel = np.zeros([input_rows, input_cols])
        for t in enemy_tanks:
            entank_hp_channel[t.pos.x][t.pos.y] = t.hp

        entank_dir_channel = np.zeros([input_rows, input_cols])
        for t in enemy_tanks:
            entank_dir_channel[t.pos.x][t.pos.y] = t.dir

        enshell_dir_channel = np.zeros([input_rows, input_cols])
        for t in enemy_shells:
            enshell_dir_channel[t.pos.x][t.pos.y] = t.dir
        astate = np.stack((map_channel, mytank_hp_channel, mytank_dir_channel, myshell_dir_channel,
                           entank_hp_channel, entank_dir_channel, enshell_dir_channel), axis=2)
        shape = astate.shape
        return astate.reshape(1, shape[0], shape[1], shape[2])
