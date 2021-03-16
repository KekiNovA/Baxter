#!/usr/bin/python3


# Load Baxter Robot actions
import baxterDo_Dummy as bxd
import getch
from copy import deepcopy
import math

BOARD_SIZE = 8
NUM_PLAYERS = 12
DEPTH_LIMIT = 5
# the players array extends to many other arrays in the program
# in these arrays, 0 will refer to black and 1 to white
PLAYERS = ["Black", "White"]
board = [ [[0.0, 0.0]] * 8 ] *8 # 2D array, translates game positions for robot



class Game:
    def __init__(self, player = 0):
        self.board = Board()
        # refers to how many pieces that play
        self.remaining = [NUM_PLAYERS, NUM_PLAYERS]
        # default player is black
        self.player = player
        self.computer = 1 if player == 0 else 0
        self.turn = 0
    def run(self):
        move = None 
        while not (self.gameOver(self.board)):
            self.board.drawBoardState()
            print("Current Player: " + PLAYERS[self.turn])
            legal = self.board.calcLegalMoves(self.turn)
            if self.turn == self.player:
                # get player's move
                if len(legal) > 0:
                    move = get_user_move(legal, PLAYERS[self.turn])                    
                    self.makeMove(move)
                else:
                    print("No legal moves available, skipping turn...")
            else:
                print("Valid Moves: ")
                for i in range(len(legal)):
                    print (str(i+1) + ": ", end='')
                    print (str(legal[i].start) + " " + str(legal[i].end))
                if len(legal) > 0:
                    # no need for AI if there's only one choice!
                    if len(legal)==1:
                        choice = legal[0]
                    else:
                        state = AB_State(self.board, self.turn, self.turn)
                        choice = self.alpha_beta(state)

                    self.makeMove(choice)
                    print("Computer chooses (" + str(choice.start) + ", " + str(choice.end) + ")")
                    #################################
                    # Call Baxter move routine here #
                    #################################
                    move = robot_move(choice, PLAYERS[self.turn]) # Note, also takes pieces as necesary
            print(move.start, move.end, move.jump) #debug
            print (move.jumpOver) # debug

            # switch player after move
            self.turn = 1 - self.turn
        print("Game OVER")
        print("Black Captured: " + str(NUM_PLAYERS - self.remaining[1]))
        print("White Captured: " + str(NUM_PLAYERS - self.remaining[0]))
        score = self.calcScore(self.board)
        print("Black Score: " + str(score[0]))
        print("White Score: " + str(score[1]))
        if score[0] > score[1]:
            print("Black wins!")
        elif (score[1] > score[0]):
            print("White wins!")
        else:
            print("It's a tie!")
        self.board.drawBoardState()

    def makeMove(self, move):
        self.board.boardMove(move, self.turn) # Update board
        if move.jump:
            self.remaining[1 - self.turn] -= len(move.jumpOver)
            print("Removed " + str(len(move.jumpOver)) + " " + PLAYERS[1 - self.turn] + " pieces")
  

        
    # returns a boolean value determining if game finished
    def gameOver(self, board):
        # all pieces from one side captured
        if len(board.currPos[0]) == 0 or len(board.currPos[1]) == 0:
            return True
        # no legal moves available, stalemate
        elif len(board.calcLegalMoves(0)) == 0 and len(board.calcLegalMoves(1)) == 0:
            return True
        else:
            # continue onwards
            return False
            
    #calculates the final score for the board
    def calcScore(self, board):
        score = [0,0]
        # black pieces
        for cell in range(len(board.currPos[0])):
            # If King - 5 pts
            if cell in board.kingPos[0]:
                score[0] += 5
            # black pieces not at end - 2 pt
            else:
                score[0] += 2
        # white pieces
        for cell in range(len(board.currPos[1])):
            # If King - 5 pts
            if cell in board.kingPos[1]:
                score[1] += 5
            # white pieces not at end - 2 pt
            else:
                score[1] += 2
        return score
        
    # state = board, player
    def alpha_beta(self, state):
        #result = self.max_value(state, -999, 999, 0)
        result = self.minmax(state, -math.inf, math.inf, 0, True)
        print("Max depth: " + str(result.max_depth))
        return result.move
   
    def minmax(self, state, alpha, beta, depth, maximizing):
        actions = state.board.calcLegalMoves(state.player)
        Main = AB_Value(-math.inf, None, depth) 
        Main.max_depth = DEPTH_LIMIT
        if depth == DEPTH_LIMIT:
            Main.move_value = self.evaluation_function(state.board)
            return Main
        if maximizing == True:
            Main.move_value = max_eval = -math.inf
            if len(actions) == 0:
                return Main
            for a in actions:
                temp = AB_State(deepcopy(state.board), 1 - state.player, state.originalPlayer)
                temp.board.boardMove(a, state.player)
                temp = self.minmax(temp, alpha, beta, depth + 1, False)
                if temp.move_value > max_eval:
                    Main.move_value = max_eval = temp.move_value
                    Main.move = a
                alpha = max(alpha, temp.move_value)
                if beta <= alpha:
                    break
        else:
            Main.move_value = min_eval = math.inf
            if len(actions) == 0:
                return Main
            for a in actions:
                temp = AB_State(deepcopy(state.board), 1 - state.player, state.originalPlayer)
                temp.board.boardMove(a, state.player)
                temp = self.minmax(temp, alpha, beta, depth + 1, True)
                if temp.move_value < min_eval:
                    Main.move_value = min_eval = temp.move_value
                    Main.move = a
                beta = min(beta, temp.move_value)
                if beta <= alpha:
                    break
        return Main

    # returns a utility value for a non-terminal node
    # Optimized evaluation function
    def evaluation_function(self, board):
        result = 0
        mine = 0
        opp = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if (i,j) in board.currPos[self.computer]:
                    mine += 1
                    result += 5
                    if (i,j) in board.kingPos[self.computer]:
                        result += 5
                    if i == 0 or j == 0 or i == 7 or j == 7:
                        result += 7
                    if i + 1 > 7 or j - 1 <  0 or i - 1 < 0 or j + 1 > 7:
                        continue
                    if (i + 1,j - 1) in board.currPos[self.player] and board.boardState[i - 1][j + 1] == "+":
                        result -= 3
                    if (i + 1, j + 1) in board.currPos[self.player] and board.boardState[i - 1][j - 1] == "+":
                        result -= 3
                    if (i - 1, j + 1) in board.kingPos[self.player] and board.boardState[i + 1][j + 1] == "+":
                        result -= 3
                    if (i - 1, j + 1) in board.kingPos[self.player] and board.boardState[i + 1][j - 1] == "+":
                        result -= 3
                    if i + 2 > 7 or i - 2 < 0:
                        continue
                    if (i + 1,j - 1) in board.kingPos[self.player] and board.boardState[i + 2][j - 2] == "+":
                        result += 6
                    if i + 2 > 7 or j + 2 > 7:
                        continue
                    if (i + 1, j + 1) in board.currPos[self.player] and board.boardState[i + 2][j + 2] == "+":
                        result += 6
                elif (i, j) in board.currPos[self.player]:
                    opp += 1
        
        return result + (mine - opp) * 1000
             
# wrapper for alpha-beta info
# v = [move_value, move, max tree depth, # child nodes, # max/beta cutoff, # min/alpha cutoff]
class AB_Value:
    def __init__(self, move_value, move, max_depth):
        self.move_value = move_value
        self.move = move
        self.max_depth = max_depth
         

# wrapper for state used in alpha-beta
class AB_State:
   def __init__(self, boardState, currPlayer, originalPlayer):
      self.board = boardState
      self.player = currPlayer
      self.originalPlayer = originalPlayer
      
class Move:
    def __init__(self, start, end, jump=False):
            self.start = start
            self.end = end # tuple (row, col)
            self.jump = jump # bool
            self.jumpOver = [] # array of pieces jumped over
    
class Board:
    def __init__(self, board = [], currBlack = [], currWhite = [], kingBlack = [], kingWhite = []):
        if board!=[]:
            self.boardState = board     
        else:
            self.setDefaultBoard()
        self.currPos = [[], []]
        self.kingPos = [[], []]
        if currBlack != []:
            self.currPos[0] = currBlack
        else:
            self.currPos[0] = self.calcPos(0)
        if currWhite != []:
            self.currPos[1] = currWhite
        else:
            self.currPos[1] = self.calcPos(1)   
        #check for given kings
        if kingBlack != []:
            self.kingPos[0] = kingBlack
        else:
            self.kingPos[0] = self.calcKingPos(0)
        if currWhite != []:
            self.kingPos[1] = kingWhite
        else:
            self.kingPos[1] = self.calcKingPos(1)   
        
                     
    def boardMove(self, move_info, currPlayer):
        move = [move_info.start, move_info.end]
        if move_info.end[0] == 0 or move_info.end[0] == 7:
            self.kingPos[currPlayer].append(move_info.end)
        if move_info.start in self.kingPos[currPlayer]:
            self.kingPos[currPlayer].remove(move_info.start)
            self.kingPos[currPlayer].append(move_info.end)
  #      print(move)
  #      self.drawBoardState()
        remove = move_info.jumpOver
        jump = move_info.jump      
        # start by making old space empty
        self.boardState[move[0][0]][move[0][1]] = -1
        # then set the new space to player who moved
        self.boardState[move[1][0]][move[1][1]] = currPlayer
        if jump:
            #remove jumped over enemies
            for enemy in move_info.jumpOver:
                self.boardState[enemy[0]][enemy[1]] = -1
                if enemy in self.kingPos[currPlayer]:
                    self.kingPos[currPlayer].remove(currPlayer)
            # update currPos array
            # if its jump, the board could be in many configs, just recalc it
            self.currPos[0] = self.calcPos(0)
            self.currPos[1] = self.calcPos(1)
            # otherwise change is predictable, so faster to just set it
        else:
            self.currPos[currPlayer].remove((move[0][0], move[0][1]))
            self.currPos[currPlayer].append((move[1][0], move[1][1]))
  #      print(self.currPos[currPlayer])

    def calcLegalMoves(self, player): # int array  -> [0] reg, [1] jump
        legalMoves = []
        hasJumps = False
        # next goes up if black or down if white
        next = -1 if player == 0 else 1
        boardLimit = 0 if player == 0 else BOARD_SIZE-1
        # cell refers to a position tuple (row, col)
        for cell in self.currPos[player]:
            #check for diagonal left
            if cell in self.kingPos[player]:
                #empty, regular move
                if cell[1]!=0:
                    if self.boardState[cell[0] - next][cell[1] - 1] == -1 and not hasJumps:
                        temp = Move(cell, (cell[0] - next, cell[1] - 1))
                        legalMoves.append(temp)
                    # has enemy, can jump it?
                    elif self.boardState[cell[0] - next][cell[1] - 1] == 1 - player:
                        jumps = self.checkJump(cell, True, player, True)
                        if len(jumps) != 0:
                            # if first jump, clear out regular moves
                            if not hasJumps:
                                hasJumps = True
                                legalMoves = []
                            legalMoves.extend(jumps)
                if cell[1] != BOARD_SIZE - 1:
                    if self.boardState[cell[0] - next][cell[1] + 1] == -1 and not hasJumps:
                        temp = Move(cell, (cell[0] - next, cell[1] + 1))
                        legalMoves.append(temp)
                    elif self.boardState[cell[0] - next][cell[1] + 1] == 1 - player:
                        jumps = self.checkJump(cell, False, player, True)
                        if len(jumps) != 0:
                            # if first jump, clear out regular moves
                            if not hasJumps:
                                hasJumps = True
                                legalMoves = []
                            legalMoves.extend(jumps)
            if cell[0] == boardLimit:
                continue
            # diagonal right, only search if not at right edge of board
            if cell[1] != BOARD_SIZE - 1:
                #empty, regular move
                if self.boardState[cell[0] + next][cell[1] + 1] == -1 and not hasJumps:
                    temp = Move(cell, (cell[0] + next, cell[1] + 1)) 
                    legalMoves.append(temp)
                # has enemy, can jump it?
                elif self.boardState[cell[0] + next][cell[1] + 1] == 1 - player:
                    jumps = self.checkJump(cell, False, player)
                    if len(jumps) != 0:
                        # if first jump, clear out regular moves
                        if not hasJumps:
                            hasJumps = True
                            legalMoves = []
                        legalMoves.extend(jumps)
            # diagonal left, only search if not at left edge of board
            if cell[1]!=0:
                if self.boardState[cell[0] + next][cell[1] - 1] == -1 and not hasJumps:
                    temp = Move(cell, (cell[0] + next, cell[1] - 1)) 
                    legalMoves.append(temp)                    
                elif self.boardState[cell[0] + next][cell[1] - 1] == 1 - player:
                    jumps = self.checkJump(cell, True, player)
                    if len(jumps)!=0:
                        if not hasJumps:
                            hasJumps = True
                            legalMoves = []                        
                        legalMoves.extend(jumps)                        
        return legalMoves

    # enemy is the square we plan to jump over
    # change later to deal with double jumps
    def checkJump(self, cell, isLeft, player, kinging = False):   #kinging is only true when we want to use king condition
        jumps = []
        next = -1 if player == 0 else 1
        if kinging:
            next *= -1
        # check boundaries!
        if cell[0] + next == 0 or cell[0] + next == BOARD_SIZE - 1:
            return jumps
        #check top left
        if isLeft:
            if cell[1] > 1 and self.boardState[cell[0] + next + next][cell[1] - 2] == -1:
                temp = Move(cell, (cell[0] + next + next, cell[1] - 2), True)
                temp.jumpOver = [(cell[0] + next,cell[1]-1)]
                # can has double jump?
                if temp.end[0] + next > 0 and temp.end[0] + next < BOARD_SIZE - 1:
                    #enemy in top left of new square?
                    if temp.end[1] > 1 and self.boardState[temp.end[0] + next][temp.end[1] - 1] == 1 - player:
                        test = self.checkJump(temp.end, True, player, kinging)
                        if test != []:
                            dbl_temp = deepcopy(temp) #deepcopy needed?
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)                      
                    # top right?
                    if temp.end[1] < BOARD_SIZE - 2 and self.boardState[temp.end[0] + next][temp.end[1] + 1] == 1 - player:
                        test = self.checkJump(temp.end, False, player, kinging)                  
                        if test != []:
                            dbl_temp = deepcopy(temp) #deepcopy needed?
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)     
                jumps.append(temp)
        else:
        #check top right
            if cell[1] < BOARD_SIZE - 2 and self.boardState[cell[0] + next + next][cell[1] + 2] == -1:
                # ([original cell, new cell], enemy cell])
                temp = Move(cell, (cell[0] + next + next, cell[1] + 2), True)
                temp.jumpOver = [(cell[0] + next, cell[1] + 1)]
                # can has double jump?
                if temp.end[0] + next > 0 and temp.end[0] + next < BOARD_SIZE - 1:
                    #enemy in top left of new square?
                    if temp.end[1] > 1 and self.boardState[temp.end[0] + next][temp.end[1] - 1] == 1 - player:
                        test = self.checkJump(temp.end, True, player, kinging)
                        if test != []:
                            dbl_temp = deepcopy(temp) #deepcopy needed?
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)                              
                    # top right?
                    if temp.end[1] < BOARD_SIZE - 2 and self.boardState[temp.end[0] + next][temp.end[1] + 1] == 1 - player:
                        test = self.checkJump(temp.end, False, player, kinging) 
                        if test != []:
                            dbl_temp = deepcopy(temp) #deepcopy needed?
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)                              
                jumps.append(temp)                
    # uncomment this when its time to try double jumps
     #   print("Jumps:")
     #   for mov in jumps:
     #       print(str(mov.start)+" "+str(mov.end)+" Jump over: "+str(mov.jumpOver))
        return jumps
    
    def calcPos(self, player):
        pos = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.boardState[row][col] == player:
                    pos.append((row,col))
        return pos
    def calcKingPos(self, player):
        pos = []
        boardLimit = 0 if player == 0 else BOARD_SIZE-1
        for cell in self.currPos[player]:
            if cell[0] == boardLimit:
                pos.append(cell)
        return pos
    def drawBoardState(self):
        """
        Draws and updates board to terminal
        """
        x = 7
        print ("\n------------------------")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row,col) in self.kingPos[0]:
                    print("BK ", end = ' ')
                elif (row,col) in self.kingPos[1]:
                    print("WK ", end = ' ')
                elif self.boardState[row][col] == -1:
                    print("+ ", end = ' ')
                elif self.boardState[row][col] == 1:
                    print("W ", end = ' ')
                elif self.boardState[row][col] == 0:
                    print ("B ", end = ' ')
            print ("| " + str(x))
            x -= 1
        print ("------------------------")
        print ("A  B  C  D  E  F  G  H\n")

    def setDefaultBoard(self):
        # reset board
        # -1 = empty, 0=black, 1=white
        self.boardState = [
            [-1,1,-1,1,-1,1,-1,1],
            [1,-1,1,-1,1,-1,1,-1],
            [-1,1,-1,1,-1,1,-1,1],
            [-1,-1,-1,-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1,-1,-1,-1],
            [0,-1,0,-1,0,-1,0,-1],
            [-1,0,-1,0,-1,0,-1,0],
            [0,-1,0,-1,0,-1,0,-1]
        ]

def robot_move(move, colour):
    print ("Robot moving")
    # Translate to robot placenames
    start = "ABCDEFGH"[move.start[1]] + "76543210"[move.start[0]]
    end = "ABCDEFGH"[move.end[1]] + "76543210"[move.end[0]]
    print ([start, end])
    # Send to robot
    bxd.move_piece(start, end)
    # check for king piece
    if end == "0" or end == "7":
        # It's a king
        bxd.king_piece(ret[1], colour)
    if move.jump==True:
        for piece in move.jumpOver:
            takePiece = "ABCDEFGH"[piece[1]] + "76543210"[piece[0]]
            print ("Taking pieces ", takePiece)
            bxd.take_piece(takePiece, colour)
    bxd.move_home()
    return move


def get_user_move(legal, colour):
    # legal is list of legal moves
    #Convert legal to robot coords
    robot_legal = [0] * len(legal)
    for m in range(len(legal)):
        #print " Start =",m.start, " End=", m.end
        start = "ABCDEFGH"[legal[m].start[1]] + "76543210"[legal[m].start[0]]
        end = "ABCDEFGH"[legal[m].end[1]] + "76543210"[legal[m].end[0]]
        robot_legal[m]= [start, end]
 
    
    ret = bxd.get_move(robot_legal)
    print ("&&&" , ret)
    # check for king piece
    if ret[1][1] == "0" or ret[1][1] == "7":
        # It's a king
        bxd.king_piece(ret[1], colour)
    # To return move object
    move = None
    for i in legal:
        if "ABCDEFGH"[i.start[1]] == ret[0][0] and "76543210"[i.start[0]] == ret[0][1] and "ABCDEFGH"[i.end[1]] == ret[1][0] and "76543210"[i.end[0]] == ret[1][1]:
            move = i
    # If jump exists call robot's function
    if move.jump==True:
        for piece in move.jumpOver:
            takePiece = "ABCDEFGH"[piece[1]] + "76543210"[piece[0]]
            print ("Taking pieces ", takePiece)
            bxd.take_piece(takePiece, colour)
    # return to home 
    bxd.move_home() 
    return move



def GettingStarted():
    bxd.init() # Initialise ROS node - only needs to be done once!
    print("Welcome")
    bxd.move_home()
    player = None
    # user choice 
    while player == None:
        try:
            player = int(input("Type 0 to play as Black or 1 to play as White: "))
        except:
            player == None
        if player != None and player not in [0, 1]:
            player == None
        if player == None:
            print("Try again.")
    # Let the game begin
    Game(player).run()

if __name__ == "__main__":
    GettingStarted()  #calls main function
