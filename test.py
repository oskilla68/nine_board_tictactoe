#!/usr/bin/python3
# Sample starter bot by Zac Partridge
# Contact me at z.partridge@unsw.edu.au
# 06/04/19
# Feel free to use this and modify it however you wish

import socket
import sys
import numpy as np
import time
import random
import copy

# a board cell can hold:
#   0 - Empty
#   1 - I played here
#   2 - They played here

# the boards are of size 10 because index 0 isn't used
boards = np.zeros((10, 10), dtype="int8")
s = [".","X","O"]
curr = 0 # this is the current board to play in
last_move = 0
at_board = 0
prev_board = np.zeros((10, 10), dtype="int8")

DRAW = 0
WIN = 1                
LOSS = -1
INFINITY = 9999999
ME = 1
ENEMY = 2
EMPTY = 0

def full_board_won(player, board):
    for a in range(1, 10):
        if gamewon(player, board[a]):
            return True
    return False

def gamewon(p, bb):
  return (( bb[1] == p and bb[2] == p and bb[3] == p )
         or( bb[4] == p and bb[5] == p and bb[6] == p )
         or( bb[7] == p and bb[8] == p and bb[9] == p )
         or( bb[1] == p and bb[4] == p and bb[7] == p )
         or( bb[2] == p and bb[5] == p and bb[8] == p )
         or( bb[3] == p and bb[6] == p and bb[9] == p )
         or( bb[1] == p and bb[5] == p and bb[9] == p )
         or( bb[3] == p and bb[5] == p and bb[7] == p ))


# print a row
# This is just ported from game.c
def print_board_row(board, a, b, c, i, j, k):
    print(" "+s[board[a][i]]+" "+s[board[a][j]]+" "+s[board[a][k]]+" | " \
             +s[board[b][i]]+" "+s[board[b][j]]+" "+s[board[b][k]]+" | " \
             +s[board[c][i]]+" "+s[board[c][j]]+" "+s[board[c][k]])

# Print the entire board
# This is just ported from game.c
def print_board(board):
    print_board_row(board, 1,2,3,1,2,3)
    print_board_row(board, 1,2,3,4,5,6)
    print_board_row(board, 1,2,3,7,8,9)
    print(" ------+-------+------")
    print_board_row(board, 4,5,6,1,2,3)
    print_board_row(board, 4,5,6,4,5,6)
    print_board_row(board, 4,5,6,7,8,9)
    print(" ------+-------+------")
    print_board_row(board, 7,8,9,1,2,3)
    print_board_row(board, 7,8,9,4,5,6)
    print_board_row(board, 7,8,9,7,8,9)
    print()
def full_board(bb):
  c = 1
  while c <= 9 and bb[c] != 0:
    c += 1
  return c == 10 

# print a row
# This is just ported from game.c
def print_board_row(board, a, b, c, i, j, k):
    print(" "+s[board[a][i]]+" "+s[board[a][j]]+" "+s[board[a][k]]+" | " \
             +s[board[b][i]]+" "+s[board[b][j]]+" "+s[board[b][k]]+" | " \
             +s[board[c][i]]+" "+s[board[c][j]]+" "+s[board[c][k]])

# Print the entire board
# This is just ported from game.c
def print_board(board):
    print_board_row(board, 1,2,3,1,2,3)
    print_board_row(board, 1,2,3,4,5,6)
    print_board_row(board, 1,2,3,7,8,9)
    print(" ------+-------+------")
    print_board_row(board, 4,5,6,1,2,3)
    print_board_row(board, 4,5,6,4,5,6)
    print_board_row(board, 4,5,6,7,8,9)
    print(" ------+-------+------")
    print_board_row(board, 7,8,9,1,2,3)
    print_board_row(board, 7,8,9,4,5,6)
    print_board_row(board, 7,8,9,7,8,9)
    print()

class Agent(object):
    def __init__(self, player, exploration_rate=0, learning_rate=0.1, discount_factor=0.01):
        self.exploration_rate = exploration_rate
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.states = {}
        self.order = []
        self.player = player
    
    @staticmethod
    def string_board(board):
        return ''.join(map(str, [y for x in board for y in x]))
    
    def quit_explore(self):
        self.exploration_rate = 0

    def append(self, board, action):
        state_key = self.string_board(board)
        self.order.append((state_key, action))

    def temporal_learning(self, reward, old_key, new_key):
        old_state = self.states.get(old_key, np.zeros((10, 10)))
        return (1 - self.learning_rate) * old_state + self.learning_rate * (reward + self.discount_factor * self.states[new_key])

    def reward(self, reward):
        if len(self.order) == 0:
            return None
        new_key, new_action = self.order.pop()
        self.states[new_key] = np.zeros((10, 10))
        self.states[new_key].itemset(new_action, reward)
         
        while self.order:
            state_key, action = self.order.pop()

            if state_key in self.states:
                reward += self.temporal_learning(reward, state_key, new_key).item(new_action)
                self.states[state_key].itemset(action, reward)
            else:
                self.states[state_key] = np.zeros((10, 10))
                reward += self.temporal_learning(reward, state_key, new_key).item(new_action)
                self.states[state_key].itemset(action, reward)
            new_key = state_key
            new_action = action

        # reward = self.temporal_learning(reward, self.string_board(board), self.string_board(prev_board))
        # tabular_rewards.itemset((last_move, at_board), reward)
        # tabular_rewards += reward
        # have a table 9 by 9 for each mode
    
    def select_move(self, board, curr_num):
        # select a move in the current board, whether it be explore or exploit
        state_key = Agent.string_board(board)
        # print_board(board)
        exploration = np.random.random() < self.exploration_rate
        action = 0
        if exploration or state_key not in self.states:
            action = self.explore(board[curr_num])
        else:
            action = self.exploit(state_key, curr_num)
        self.append(board, (curr_num, action))
        return action

    def explore(self, board):
        zero_x = np.where(board == 0)
        vacant_cells = zero_x[0]
        if len(vacant_cells) == 1: return vacant_cells[0]
        randomly_selected_vacant_cell = random.randint(1, len(vacant_cells) - 1)
        return vacant_cells[randomly_selected_vacant_cell]

    def exploit(self, state_key, curr_num):
        state_values = self.states[state_key]
        state_values = state_values[curr_num]
        if self.player == ME:
            best_actions_x = np.where(state_values == state_values.max())
        else:
            best_actions_x = np.where(state_values == state_values.min())
        # Find the coordinates which correspond to highest reward
        best_value_indices = best_actions_x[0]
        # best_value_indices = [(x, y) for x,y in zip(best_actions_x, best_actions_y)]
        select_index = np.random.choice(len(best_value_indices))
        return best_value_indices[select_index]

agent = Agent(ME)

# choose a move to play
def play():
    
    move = agent.select_move(boards, curr)
    place(curr, move, 1)
    return move

# place a move in the global boards
def place(board, num, player):
    global curr
    curr = num
    boards[board][num] = player

# read what the server sent us and
# only parses the strings that are necessary
def parse(string):
    if "(" in string:
        command, args = string.split("(")
        args = args.split(")")[0]
        args = args.split(",")
    else:
        command, args = string, []

    if command == "second_move":
        place(int(args[0]), int(args[1]), 2)
        return play()
    elif command == "third_move":
        # place the move that was generated for us
        place(int(args[0]), int(args[1]), 1)
        # place their last move
        place(curr, int(args[2]), 2)
        return play()
    elif command == "next_move":
        place(curr, int(args[0]), 2)
        return play()
    elif command == "win":
        print("Yay!! We win!! :)")
        agent.reward(WIN)
        return -1
    elif command == "loss":
        print("We lost :(")
        agent.reward(LOSS)
        return -1
    return 0

# def optimise(game, bot1, bot2):
def train():
    agent_wins = 0
    agent2_wins = 0
    on_turned_off = 0
    for i in range(10000):
        boards = np.zeros((10, 10), dtype="int8")
        curr = 1
        if i > 6000:
            print("Turned off!")
            agent.quit_explore()
        while True:
            move = agent.select_move(boards, curr)
            boards[curr][move] = ME
            if gamewon(ME, boards[curr]):
                print("W")
                agent.reward(WIN)
                agent2.reward(LOSS)
                agent_wins += 1
                print_board(boards)
                if i > 6000:
                    on_turned_off += 1
                break
            curr = move
            if full_board(boards[curr]):
                agent.reward(DRAW)
                agent2.reward(DRAW)
                break
            move = agent2.select_move(boards, curr)
            boards[curr][move] = ENEMY
            if gamewon(ENEMY, boards[curr]):
                print("L")
                agent.reward(LOSS)
                agent2.reward(WIN)
                agent2_wins += 1
                print_board(boards)
                break
            curr = move
        # time.sleep(20)
    print(agent_wins)
    print(agent2_wins)
    print(on_turned_off)
        
    # return move

# connect to socket
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = int(sys.argv[2]) # Usage: ./agent.py -p (port)
    s.connect(('localhost', port))
    games = 0
    while True:
        text = s.recv(1024).decode()
        if not text:
            continue
        for line in text.split("\n"):
            response = parse(line)
            if response == -1:
                # s.close()
                # return
                global boards
                boards = np.zeros((10, 10), dtype="int8")
                games += 1
                print(games)
            elif response > 0:
                s.sendall((str(response) + "\n").encode())
    s.close()

if __name__ == "__main__":
    main()
