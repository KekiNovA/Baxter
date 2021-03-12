#!/usr/bin/python3

# Load Baxter Robot actions

import baxterDo_Dummy as bxd
import getch
# Default Parameters

BOARD_SIZE = 8
NUM_PEICES = 12

# the players array extends to many other arrays in the program
# in these arrays, 0 will refer to black and 1 to white

PLAYERS = ["Black", "White"]
BOARD = [ [[0.0, 0.0]] * 8 ] * 8 # 2D array, translates game positions for robot

PLAYER = 1

class Game:
    def __init__ (self, player = 0):
        # Initializing Board
        self.board = Board()

        # Default player is black
        self.player = player
        self.turn = 0   # Black First always
    def run(self):
        while not (self.gameOver(self.board)):
            self.board.drawBoardState()
            print("Current Player: " + PLAYERS[self.turn])
            legal = self.board.calcLegalMoves(self.turn)
            if self.turn == self.player:
                # get players move
                if 
                

    def gameOver(self, board):
        # all pieces from one side captured
        if len(board.Black) == 0 or len(board.White) == 0:
            return True
        # need to add legal moves condition
        else:
            False
        

class Board:
    def __init__(self, board = [], currBlack = [], currWhite = []):
        if board != []:
            self.boardState = board
        else:
            self.setDefaultBoard()
        self.currPos = [[],[]]  
        if currBlack:
            self.currPos[0] = currBlack   
        else:
            self.currPos[0] = self.calcPos(0)   
        if currWhite:
            self.currPos[1] = currWhite   
        else:
            self.currPos[1] = self.calcPos(1)

    def setDefaultBoard(self):
        # Default or reset Board
        # -1 = empty, 0 = black, 1 = white
        # Keeping it 8*8 can add further
        self.boardState = [
            [-1,1,-1,1,-1,1,-1,1],
            [1,-1,1,-1,1,-1,1,-1],
            [-1,1,-1,1,-1,1,-1,1],
            [-1,-1,-1,-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1,-1,-1,-1],
            [0,-1,0,-1,0,-1,0,-1],
            [-1,0,-1,0,-1,0,-1,0],
            [0,-1,0,-1,0,-1,0,-1],
        ]
    
    def calcPos(self, player):
        pos = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.boardState[row][col] == player:
                    pos.append((row,col))
        return pos
    def drawBoardState(self):
        print("\n------------------------")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.boardState[row][col] == -1:
                    print("+", end = "")
                elif self.boardState[row][col] == 1:
                    print("W", end = "")
                elif self.boardState[row][col] == 0:
                    print("B", end = "")
                else:
                    print(self.boardState[row][col])
            print("|" + str(7 - row))
        print("------------------------")
        print("A  B  C  D  E  F  G  H\n")

    def calcLegalMoves(self, player):  # int array -> [0] reg, [1] jump
        legalMoves = []
        hasJumps = False
        # next goes up if black or down if white
        next = -1 if player == 0 else 1
        boardLimit = 0 if player == 0 else BOARD_SIZE - 1
        # cell refers to a position tuple (row, col)
        for cell in self.currPos[player]:
            if cell[0] == boardLimit:
                continue
            # diagonal right, only search if not at right edge of board
            if cell[1] != 






# Main Fuction
def GettingStarted():
    global PLAYER
    bxd.init()  # Initialise ROS node - only needs to be done once!
    print("Welcome")
    bxd.move_home()
    print("Type 0 to play Black ot 1 to play White")
    while not (player == 0 or player == 1):
        player = int(getch.getch())
    
if __name__ == "__main__":
    GettingStarted()  #calls main function
