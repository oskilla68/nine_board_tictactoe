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

class Agent(object):
    def __init__(self, exploration_rate=0.33, learning_rate=0.5, discount_factor=0.01):
        self.exploration_rate = exploration_rate
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.states = {}
    
    @staticmethod
    def string_board(board):
        return ''.join(map(str, [y for x in board for y in x]))
    
    def quit_explore(self):
        self.exploration_rate = 0

    def temporal_learning(self, reward, old_key, new_key):
        old_state = self.states.get(old_key, np.zeros((10, 10)))
        return (1 - self.learning_rate) * old_state + self.learning_rate * (reward + self.discount_factor * self.states[new_key])

    def reward(self, reward, board, prev_board, last_move, at_board):
        tabular_rewards = self.states.get(self.string_board(board), np.zeros((10, 10)))
        reward = self.temporal_learning(reward, self.string_board(board), self.string_board(prev_board))
        # tabular_rewards.itemset((last_move, at_board), reward)
        tabular_rewards[at_board][last_move] += reward[at_board][last_move]
        # have a table 9 by 9 for each mode
    
    def select_move(self, board, curr_num):
        # select a move in the current board, whether it be explore or exploit
        state_key = Agent.string_board(board)
        print_board(board)
        exploration = np.random.random() < self.exploration_rate
        action = 0
        if exploration or state_key not in self.states:
            action = self.explore(board[curr_num])
            self.states[state_key] = np.zeros((10, 10))
        else:
            action = self.exploit(state_key, curr_num)
        # action = self.explore(board[curr_num]) \
        #     if exploration or state_key not in self.states \
        #         else self.exploit(state_key, curr_num)
        return action

    def explore(self, board):
        print("exploring :O")
        zero_x = np.where(board == 0)
        vacant_cells = zero_x[0]
        randomly_selected_vacant_cell = random.randint(0, len(vacant_cells) - 1)
        print("Done exploring")
        return vacant_cells[randomly_selected_vacant_cell]

    def exploit(self, state_key, curr_num):
        print("exploit :O")
        state_values = self.states[state_key]
        state_values = state_values[curr_num]
        best_actions_x, best_actions_y = np.where(state_values == state_values.max())
        # Find the coordinates which correspond to highest reward
        
        best_value_indices = [(x, y) for x,y in zip(best_actions_x, best_actions_y)]
        select_index = np.random.choice(len(best_value_indices))
        return best_value_indices[select_index]


# def optimise(game, bot1, bot2):
agent = Agent()
def train():
    move = agent.select_move(boards, curr)
    place(curr, move, ME)
    print("returning something....")
    return move




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

def winnable(board, player):
    one = 0
    two = 0
    for a in range(1, 10):
        if board[a] == player:
            # vertical cases
            if a <= 3:
                if board[a + 3] == EMPTY and board[a + 6] == EMPTY:
                    one += 1
                elif board[a + 3] == player or board[a + 6] == player:
                    two += 1
                if a == 1:
                    if board[5] == EMPTY and board[9] == EMPTY:
                        one += 1
                    elif board[5] == player or board[9] == player:
                        two += 1
                elif a == 3:
                    if board[5] == EMPTY and board[7] == EMPTY:
                        one += 1
                    elif board[5] == player or board[7] == player:
                        two += 1
            elif a <= 6:
                if board[a - 3] == EMPTY and board[a + 3] == EMPTY:
                    one += 1
                elif board[a + 3] == player:
                    two += 1
                if a == 5:
                    if board[1] == EMPTY and board[9] == EMPTY:
                        one += 1
                    elif board[1] == player or board[9] == player:
                        two += 1
                    if board[3] == EMPTY and board[7] == EMPTY:
                        one += 1
                    elif board[3] == player or board[7] == player:
                        two += 1
            else:
                if board[a - 3] == EMPTY and board[a - 6] == EMPTY:
                    one += 1
                if a == 7:
                    if board[5] == EMPTY and board[3] == EMPTY:
                        one += 1
                    elif board[5] == player or board[3] == player:
                        two += 1
                if a == 9:
                    if board[5] == EMPTY and board[1] == EMPTY:
                        one += 1
                    elif board[5] == player or board[1] == player:
                        two += 1
            # horizontal cases
            if (a - 1)%3 == 0:
                if board[a + 1] == EMPTY and board[a + 2] == EMPTY:
                    one += 1
                elif board[a + 1] == player or board[a + 2] == player:
                    two += 1
            elif (a - 1)%3 == 1:
                if board[a - 1] == EMPTY and board[a + 1] == EMPTY:
                    one += 1
                elif board[a - 1] == player or board[a + 1] == player:
                    two += 1
            elif (a - 1)%3 == 2:
                if board[a - 1] == EMPTY and board[a - 2] == EMPTY:
                    one += 1
                elif board[a - 1] == player or board[a - 2] == player:
                    two += 1

            
    return one, two

def heuristic(board, player):
    return ((board[1] == player and board[2] == player and board[3] == EMPTY)
    or (board[1] == EMPTY and board[2] == player and board[3] == player)
    or (board[1] == player and board[2] == EMPTY and board[3] == player) 
    or (board[1] == player and board[4] == player and board[7] == EMPTY)
    or (board[1] == EMPTY and board[4] == player and board[7] == player)
    or (board[1] == player and board[4] == EMPTY and board[7] == player)
    or (board[2] == player and board[3] == player and board[4] == EMPTY) 
    or (board[2] == EMPTY and board[3] == player and board[4] == player)
    or (board[2] == player and board[3] == EMPTY and board[4] == player)
    or (board[2] == player and board[5] == player and board[8] == EMPTY)
    or (board[2] == EMPTY and board[5] == player and board[8] == player)
    or (board[2] == player and board[5] == EMPTY and board[8] == EMPTY)
    or (board[3] == player and board[6] == player and board[9] == EMPTY) 
    or (board[3] == player and board[6] == EMPTY and board[9] == player) 
    or (board[3] == EMPTY and board[6] == player and board[9] == player) 
    or (board[4] == player and board[5] == player and board[6] == EMPTY)
    or (board[4] == player and board[5] == EMPTY and board[6] == player)
    or (board[4] == EMPTY and board[5] == player and board[6] == player)
    or (board[7] == player and board[8] == player and board[9] == EMPTY) 
    or (board[7] == player and board[8] == EMPTY and board[9] == player)
    or (board[7] == EMPTY and board[8] == player and board[9] == player)
    or (board[1] == player and board[5] == player and board[9] == EMPTY)
    or (board[1] == player and board[5] == EMPTY and board[9] == player)
    or (board[1] == EMPTY and board[5] == player and board[9] == player)
    or (board[3] == player and board[5] == player and board[7] == EMPTY)
    or (board[3] == player and board[5] == EMPTY and board[7] == player)
    or (board[3] == EMPTY and board[5] == player and board[7] == player))
# arraylist of tuples?
def minimax(whole_board, curr_num, depth, player, alpha, beta):
    if player == ME:
        bestMove = None
        result = -INFINITY
    else:
        bestMove = None
        result = INFINITY

    curr_board = whole_board[curr_num]

    value = 0
    if depth == 0:
        return curr_num, DRAW
    # if depth == 0:
    #     one, two = winnable(curr_board, ME)
    #     enemy_one, enemy_two = winnable(curr_board, ENEMY)
    #     # value = 0
    #     # for a in range(1, 10):
    #     #     one, two = winnable(whole_board[a], ME)
    #     #     enemy_one, enemy_two = winnable(whole_board[a], ENEMY)
    #     #     value += (3 * two + one - 3 * enemy_two - enemy_one)
    #     #     # value += (3 * enemy_two + enemy_one - 3 * two - one)
    #     # return curr_num, value
    #     return curr_num, (3 * enemy_two + enemy_one - 3 * two - one)
    #     # move = a
    #     # calcResult = (3 * enemy_two + enemy_one - 3 * two - one)
    
    if full_board(curr_board):
        return curr_num, DRAW
        
    for a in range(1, 10):
        if whole_board[curr_num][a] == EMPTY:
            whole_board[curr_num][a] = player
            # board_copy = copy.deepcopy(whole_board)
            if gamewon(ME, whole_board[curr_num]):
                whole_board[curr_num][a] = EMPTY
                return a, WIN
            elif gamewon(ENEMY, whole_board[curr_num]):
                whole_board[curr_num][a] = EMPTY
                return a, LOSS
            
            if depth == 0:
                move = a
                one, two = winnable(whole_board[curr_num], ME)
                enemy_one, enemy_two = winnable(whole_board[curr_num], ENEMY)
                # calcResult = (3 * enemy_two + enemy_one - 3 * two - one)
                calcResult = (3 * two + one - 3 * enemy_two - enemy_one)
                # heuristic(whole_board[curr_num], ENEMY)
            else:
                if player == ME:
                    move, calcResult = minimax(whole_board, a, depth - 1, ENEMY, alpha, beta)
                elif player == ENEMY:
                    move, calcResult = minimax(whole_board, a, depth - 1, ME, alpha, beta)
            whole_board[curr_num][a] = EMPTY
            if player == ME:
                if calcResult > result:
                    result = calcResult                                                                                                                                                                                                                                                                                                                                                                                                                                          
                    bestMove = a
                    alpha = max(alpha, result)
                    # if alpha >= beta: break
            elif player == ENEMY:
                if calcResult < result:
                    result = calcResult
                    bestMove = a
                    beta = min(beta, result)
            if alpha >= beta: break

    return bestMove, result

# choose a move to play
def play():
    # just play a random move for now
    # board_copy = copy.deepcopy(boards)
    move, result = minimax(boards, curr, 8, ME, -INFINITY, INFINITY)
    # print(result)
    # print(str(move) + " THE MOVE")
    # while move is None:
    #     rand = random.randint(1, 8)
    #     if boards[curr][rand] == EMPTY:
    #         move = rand
    # move += 1
    # print(curr)
    # print("^ current number")
    place(curr, move, 1)
    # print(str(move), " hehe")
    return move

# place a move in the global boards
def place(board, num, player):
    global curr
    global last_move
    global at_board
    global prev_board

    curr = num
    last_move = num
    at_board = board
    prev_board = copy.deepcopy(boards)
    boards[board][num] = player
    # print_board(boards)

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
        return train()
    elif command == "third_move":
        # place the move that was generated for us
        place(int(args[0]), int(args[1]), 1)
        # place their last move
        place(curr, int(args[2]), 2)
        return train()
    elif command == "next_move":
        place(curr, int(args[0]), 2)
        return train()
    elif command == "win":
        print("Yay!! We win!! :)")
        agent.reward(WIN, boards, prev_board, last_move, at_board)
        return -1
    elif command == "loss":
        print("We lost :(")
        agent.reward(LOSS, boards, prev_board, last_move, at_board)
        return -1
    return 0

# connect to socket
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = int(sys.argv[2]) # Usage: ./agent.py -p (port)

    s.connect(('localhost', port))
    while True:
        text = s.recv(1024).decode()
        if not text:
            continue
        for line in text.split("\n"):
            response = parse(line)
            if response == -1:
                # s.close()
                # return
                boards = np.zeros((10, 10), dtype="int8")
            elif response > 0:
                s.sendall((str(response) + "\n").encode())
    s.close()

if __name__ == "__main__":
    main()
