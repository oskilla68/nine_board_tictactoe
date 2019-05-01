/*********************************************************
 *  agent.c
 *  Nine-Board Tic-Tac-Toe Agent
 *  COMP3411/9414/9814 Artificial Intelligence
 *  Alan Blair, CSE, UNSW
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

#include "common.h"
#include "agent.h"
#include "game.h"

#define MAX_MOVE 81
#define DRAWER 0
#define WINNER 1000                
#define LOSER -1000
#define INFINITY 999999
#define ME 1
#define ENEMY 3
// #define EMPTY 0

int board[10][10];
int move[MAX_MOVE+1];
int player;
int m;

/*********************************************************//*
   Print usage information and exit
*/

int winnable(int board[10], int player) {
  int one = 0;
  int two = 0;
  for(int a = 1; a < 10; a++) {
    if(board[a] == player) {
      if(a <= 3) {
        if(board[a + 3] == EMPTY && board[a + 6] == EMPTY) {
          one += 1;
        } else if(board[a + 3] == player || board[a + 6] == player) {
          two += 1;
        }
        if(a == 1) {
          if(board[5] == EMPTY && board[9] == EMPTY) {
            one += 1;
          } else if(board[5] == player || board[9] == player) {
            two += 1;
          }
        } else if(a == 3) {
          if(board[5] == EMPTY && board[7] == EMPTY) {
            one += 1;
          } else if(board[5] == player || board[7] == player) {
            two += 1;
          }
        }
      } else if(a <= 6) {
        if(board[a - 3] == EMPTY && board[a + 3] == EMPTY) {
          one += 1;
        } else if(board[a + 3] == player || board[a - 3] == player) {
          two += 1;
        }
        if(a == 5) {
          if(board[1] == EMPTY && board[9] == EMPTY) {
            one += 1;
          } else if(board[1] == player || board[9] == player) {
            two += 1;
          }
          if(board[3] == EMPTY && board[7] == EMPTY) {
            one += 1;
          } else if(board[3] == player || board[7] == player) {
            two += 1;
          }
        }
      } else {
        if(board[a - 3] == EMPTY && board[a - 6] == EMPTY) {
          one += 1;
        }
        if(a == 7) {
          if(board[5] == EMPTY && board[3] == EMPTY) {
            one += 1;
          } else if(board[5] == player || board[3] == player) {
            two += 1;
          }
        } else if(a == 9) {
          if(board[5] == EMPTY && board[1] == EMPTY) {
            one += 1;
          } else if(board[5] == player || board[1] == player) {
            two += 1;
          }
        }
      }
      if((a - 1)%3 == 0) {
        if(board[a + 1] == EMPTY && board[a + 2] == EMPTY) {
          one += 1;
        } else if(board[a + 1] == player || board[a + 2] == player) {
          two += 1;
        }
      } else if((a - 1)%3 == 1) {
        if(board[a - 1] == EMPTY && board[a + 1] == EMPTY) {
          one += 1;
        } else if(board[a - 1] == player || board[a + 1] == player) {
          two += 1;
        }
      } else if((a - 1)%3 == 2) {
        if(board[a - 1] == EMPTY && board[a - 2] == EMPTY) {
          one += 1;
        } else if(board[a - 1] == player || board[a - 2] == player) {
          two += 1;
        }
      }
    }
  }
  return (3 * two + one);
}

int minimax(int curr_num, int depth, int player, int alpha, int beta, int prev_num) {
  int bestMove = 0;
  int result;
  if(player == ME) {
    result = -1 * INFINITY;
  } else {
    result = INFINITY;
  }

  if(gamewon(ME, board[prev_num])) {
    return WIN;
  } else if(gamewon(ENEMY, board[prev_num])) {
    return LOSS;
  } else if(full_board(board[curr_num])) {
    return DRAW;
  } 

  int value = 0;
  if(depth == 0) {
    for(int b = 1; b < 10; b++) {
      int player_val = winnable(board[b], ME);
      int enemy_val = winnable(board[b], ENEMY);
      if(b == prev_num) {
        if(player == ME) {
          value += 10 * (player_val - enemy_val);
        } else {
          value -= 10 * (player_val - enemy_val);
        }
      } else {
        if(player == ME) {
          value += (player_val - enemy_val);
        } else {
          value -= (player_val - enemy_val);
        }
      }
    }
    return value;
  }
  
  for(int a = 1; a < 10; a++) {
    if(board[curr_num][a] == EMPTY) {
      board[curr_num][a] = player;
      int calcResult;
      if(player == ME) {
        calcResult = minimax(a, depth - 1, ENEMY, alpha, beta, curr_num);
      } else {
        calcResult = minimax(a, depth - 1, ME, alpha, beta, curr_num);
      }
      board[curr_num][a] = EMPTY;
      if(player == ME) {
        if(calcResult > result) {
          result = calcResult;
          bestMove = a;
          alpha = (alpha > result) ? alpha : result;
        }
        if(alpha >= beta) {
          break;
        }
      } else if(player == ENEMY) {
        if(calcResult < result) {
          result = calcResult;
          bestMove = a;
          beta = (beta < result) ? beta : result;
        }
      }
    }
  }
  return result;
}

void usage( char argv0[] )
{
  printf("Usage: %s\n",argv0);
  printf("       [-p port]\n"); // tcp port
  printf("       [-h host]\n"); // tcp host
  exit(1);
}

/*********************************************************//*
   Parse command-line arguments
*/
void agent_parse_args( int argc, char *argv[] )
{
  int i=1;
  while( i < argc ) {
    if( strcmp( argv[i], "-p" ) == 0 ) {
      if( i+1 >= argc ) {
        usage( argv[0] );
      }
      port = atoi(argv[i+1]);
      i += 2;
    }
    else if( strcmp( argv[i], "-h" ) == 0 ) {
      if( i+1 >= argc ) {
        usage( argv[0] );
      }
      host = argv[i+1];
      i += 2;
    }
    else {
      usage( argv[0] );
    }
  }
}

/*********************************************************//*
   Called at the beginning of a series of games
*/
void agent_init()
{
  struct timeval tp;

  // generate a new random seed each time
  gettimeofday( &tp, NULL );
  srandom(( unsigned int )( tp.tv_usec ));
}

/*********************************************************//*
   Called at the beginning of each game
*/
void agent_start( int this_player )
{
  reset_board( board );
  m = 0;
  move[m] = 0;
  player = this_player;
}

/*********************************************************//*
   Choose second move and return it
*/
int agent_second_move( int board_num, int prev_move )
{
  int this_move;
  move[0] = board_num;
  move[1] = prev_move;
  board[board_num][prev_move] = !player;
  m = 2;
  
  // do {
  //   this_move = 1 + random()% 9;
  // } while( board[prev_move][this_move] != EMPTY );
  // (int curr_num, int depth, int player, int alpha, int beta, int prev_num) 
  this_move = minimax(board_num, 9, player, -INFINITY, INFINITY, board_num);
  move[m] = this_move;
  board[prev_move][this_move] = player;
  print_board(board);
  return( this_move );
}

/*********************************************************//*
   Choose third move and return it
*/
int agent_third_move(
                     int board_num,
                     int first_move,
                     int prev_move
                    )
{
  int this_move;
  move[0] = board_num;
  move[1] = first_move;
  move[2] = prev_move;
  board[board_num][first_move] =  player;
  board[first_move][prev_move] = !player;
  m=3;
  this_move = minimax(board_num, 9, player, -INFINITY, INFINITY, board_num);
  // do {
  //   this_move = 1 + random()% 9;
  // } while( board[prev_move][this_move] != EMPTY );
  move[m] = this_move;
  board[move[m-1]][this_move] = player;
  return( this_move );
}

/*********************************************************//*
   Choose next move and return it
*/
int agent_next_move( int prev_move )
{
  int this_move;
  m++;
  move[m] = prev_move;
  board[move[m-1]][move[m]] = !player;
  m++;
  this_move = minimax(move[m-1], 9, player, -INFINITY, INFINITY, move[m-1]);
  // do {
  //   this_move = 1 + random()% 9;
  // } while( board[prev_move][this_move] != EMPTY );
  move[m] = this_move;
  board[move[m-1]][this_move] = player;
  return( this_move );
}

/*********************************************************//*
   Receive last move and mark it on the board
*/
void agent_last_move( int prev_move )
{
  m++;
  move[m] = prev_move;
  board[move[m-1]][move[m]] = !player;
}

/*********************************************************//*
   Called after each game
*/
void agent_gameover(
                    int result,// WIN, LOSS or DRAW
                    int cause  // TRIPLE, ILLEGAL_MOVE, TIMEOUT or FULL_BOARD
                   )
{
  // nothing to do here
}

/*********************************************************//*
   Called after the series of games
*/
void agent_cleanup()
{
  // nothing to do here
}


