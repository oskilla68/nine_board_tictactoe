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
import timeit
import copy

# a board cell can hold:
#   0 - Empty
#   1 - I played here
#   2 - They played here

# the boards are of size 10 because index 0 isn't used
boards = np.zeros((10, 10), dtype="int8")
s = [".","X","O"]
curr = 0 # this is the current board to play in

DRAW = 0
WIN = 10000000                
LOSS = -10000000
INFINITY = 99999999999
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

def positions(board, player):
    position = 0
    if board[1] == player: position += 3
    if board[2] == player: position += 2
    if board[3] == player: position += 3
    if board[4] == player: position += 2
    if board[5] == player: position += 4
    if board[6] == player: position += 2
    if board[7] == player: position += 3
    if board[8] == player: position += 2
    if board[9] == player: position += 3
    return position

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

def dict_contains(dictionary_list, value):
    for unit in dictionary_list:
        if unit[0] == value: return True
    return False
# a dictionary of arrays of arrays
killers = {}
enemy_killers = {}
def minimax(whole_board, curr_num, depth, player, alpha, beta, prev_num):
    if player == ME:
        bestMove = None
        result = -INFINITY
    else:
        bestMove = None
        result = INFINITY

    # curr_board = whole_board[curr_num]

    if gamewon(ME, whole_board[prev_num]):
        return curr_num, WIN
    elif gamewon(ENEMY, whole_board[prev_num]):
        return curr_num, LOSS
    
    if full_board(whole_board[curr_num]):
        return curr_num, DRAW

    value = 0
    if depth == 0:
        for b in range(1, 10):
            one, two = winnable(whole_board[b], ME)
            enemy_one, enemy_two = winnable(whole_board[b], ENEMY)
            if b == prev_num:
                if player == ME:
                    value += 100 * (3 * two + one - 3 * enemy_two - enemy_one)
                else:
                    value += -100 * (3 * two + one - 3 * enemy_two - enemy_one)
            else:
                if player == ME:
                    value += 1 * (3 * two + one - 3 * enemy_two - enemy_one)
                else:
                    value += -1 * (3 * two + one - 3 * enemy_two - enemy_one)
        return curr_num, value


    # moves = range(1, 10)
    moves = [1, 2, 3, 4, 5, 6, 7, 8 ,9]
    killer_moves = killers.get(depth, [])
    if killer_moves != []:
        for killer_move in killer_moves:
            moves.remove(killer_move[0])
            moves = [killer_move[0]] + moves
    for a in moves:
        if whole_board[curr_num][a] == EMPTY:
            whole_board[curr_num][a] = player
            if player == ME:
                move, calcResult = minimax(whole_board, a, depth - 1, ENEMY, alpha, beta, curr_num)
            elif player == ENEMY:
                move, calcResult = minimax(whole_board, a, depth - 1, ME, alpha, beta, curr_num)
            whole_board[curr_num][a] = EMPTY
            if player == ME:
                if calcResult > result:
                    result = calcResult                                                                                                                                                                                                                                                                                                                                                                                                                                          
                    bestMove = a
                    alpha = max(alpha, result)
                if alpha >= beta:
                    try:
                        killer_moves = killers[depth]
                    except Exception as e:
                        killer_moves = []
                        killers[depth] = killer_moves
                    if not dict_contains(killers[depth], a):
                        if len(killer_moves) >= 2:
                            if killer_moves[0][1] > killer_moves[1][1]:
                                killer_moves.pop(0)
                            else:
                                killer_moves.pop(1)
                        killer_moves.append([a, 0])
                        killers[depth] = killer_moves
                    else:
                        for play in killers[depth]:
                            if play[0] == a:
                                play[1] += 1
                    break
            elif player == ENEMY:
                if calcResult == LOSS:
                    try:
                        killer_moves = enemy_killers[depth]
                    except Exception as e:
                        enemy_killers[depth] = []
                    contains = False
                    for kills in enemy_killers[depth]:
                        if a == kills[0]: contains = True
                    if contains:
                        enemy_killers[depth].append((a, 0))
                if calcResult < result:
                    result = calcResult
                    bestMove = a
                    beta = min(beta, result)
                if beta <= alpha: break

    return bestMove, result

# choose a move to play
def play():
    move, result = minimax(boards, curr, 5, ME, -INFINITY, INFINITY, curr)
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
        return -1
    elif command == "loss":
        print("We lost :(")
        return -2
    return 0

# connect to socket
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = int(sys.argv[2]) # Usage: ./agent.py -p (port)
    losses = 0
    wins = 0
    global boards
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
                wins += 1
                boards = np.zeros((10, 10), dtype="int8")
            elif response == -2:
                losses += 1
                # global boards
                boards = np.zeros((10, 10), dtype="int8")
            elif response > 0:
                s.sendall((str(response) + "\n").encode())
        print("Wins: " + str(wins) + " Losses: " + str(losses))
    s.close()

if __name__ == "__main__":
    main()
