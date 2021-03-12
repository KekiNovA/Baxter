#!/usr/bin/python
"""
Originally by Jason Schapiro 2012

# Next steps:
# X 1. Implement game-over evaluation func
# X 2. Alpha-beta search
# X 3. Alpha-beta info
# 4. Starting screen - choose player
# X 5. Double jumps

Modified by M L Walters, 2014
For use with BAxter Robot Draughts Game

"""




# Load Baxter Robot actions
import baxterDo_Dummy as bxd


BOARD_SIZE = 8
NUM_PLAYERS = 12
DEPTH_LIMIT = 5
# the players array extends to many other arrays in the program
# in these arrays, 0 will refer to black and 1 to white
PLAYERS = ["Black", "White"]
board = [ [[0.0, 0.0]]*8 ] *8 # 2D array, translates game positions for robot

playr = 1 # Human player for Baxter moves, default = 1 = Black 

class Game:
    def __init__(self, player = 0):
        self.board = Board()
        # refers to how many pieces that play
        self.remaining = [NUM_PLAYERS, NUM_PLAYERS]
        # default player is black
        self.player = player
        self.turn = 0
    def run(self):
        while not (self.gameOver(self.board)):
            self.board.drawBoardState()
            print("Current Player: " + PLAYERS[self.turn])
            legal = self.board.calcLegalMoves(self.turn)
            if self.turn == self.player:
                # get player's move
                if len(legal) > 0:
                    #choice = random.randint(0,len(legal)-1)
                    #move = legal[choice]
                    move = self.getMove(legal)                    
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
                        #choice = random.randint(0,len(legal)-1)  
                        #choice = legal[choice]                            
                        #print(legal)
                        #print "Choice",[choice.start, choice.end]

                    self.makeMove(choice)
                    print("Computer chooses (" + str(choice.start) + ", " + str(choice.end) + ")")
                    #################################
                    # Call Baxter move routine here #
                    #################################
                    robot_move(choice) # Note, also takes pieces as necesary
                    #print(move.start, move.end, move.jump) #debug
                    #print (move.jumpOver) # debug
                    
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
            self.remaining[1-self.turn] -= len(move.jumpOver)
            print("Removed " + str(len(move.jumpOver)) + " " + PLAYERS[1 - self.turn] + " pieces")
  
    def getMove(self, legal):
        move = -1
        # repeats until player picks move on the list
        while move not in range(len(legal)):
            # Debug: List valid moves:
            #print("Valid Moves: ")
            #for i in range(len(legal)):
            #    print str(i+1)+": ",#end='')
            #    print str(legal[i].start)+" "+str(legal[i].end)
            ####################################################
            # Get user input - from Baxter IF                 #
            ####################################################
            usr_input=get_user_move(legal)
            print ("usr_input = ", usr_input)
            # Comment out when robot is supplying user move
            #usr_input = raw_input("Pick a move: ") 
                        
            # stops error caused when user inputs nothing
            if usr_input == '':
                 move = 0  
            else:
                move = int(usr_input) - 1            
            #Check move ok
            if move not in range(len(legal)):
                print("Illegal move")
        print("Legal move")
        return (legal[move])
        
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
            # black pieces at end of board - 2 pts
            if board.currPos[0][cell][0] == 0:
                score[0] += 2
            # black pieces not at end - 1 pt
            else:
                score[0] += 1
        # white pieces
        for cell in range(len(board.currPos[1])):
            # white pieces at end of board - 2 pts
            if board.currPos[1][cell][0] == BOARD_SIZE-1:
                score[1] += 2
            # white pieces not at end - 1 pt
            else:
                score[1] += 1
        return score
        
    # state = board, player
    def alpha_beta(self, state):
        result = self.max_value(state, -999, 999, 0)
        print("Total nodes generated: " + str(result.nodes))
        print("Max depth: " + str(result.max_depth))
        print("Max Val Cutoffs: " + str(result.max_cutoff))
        print("Min Val Cutoffs: " + str(result.min_cutoff))
        return result.move
   
   # returns max value and action associated with value
    def max_value(self, state, alpha, beta, node):
      # if terminalTest(state)
      actions = state.board.calcLegalMoves(state.player)
      num_act = len(actions)
      # v <- -inf
      # self, move_value, move, max_depth, total_nodes, max_cutoff, min_cutoff
      v = AB_Value(-999, None, node, 1, 0, 0)
      # depth cutoff
      if node == DEPTH_LIMIT:
         v.move_value = self.evaluation_function(state.board, state.origPlayer)
   #      print("Depth Cutoff. Eval value: "+str(v.move_value))
         return v      
      if len(actions)==0:
         # return Utility(state)
         score = self.calcScore(state.board)
         if score[state.origPlayer] > score[1-state.origPlayer]:
            v.move_value = 100 + (2 * score[state.origPlayer] - score[1 - state.origPlayer])
   #         print("(max) Terminal Node Score: "+str(v.move_value))
         else:
            v.move_value = -100 + (2 * score[state.origPlayer] - score[1 - state.origPlayer])
   #         print("(max) Terminal Node Score: "+str(v.move_value))            
         return v
      for a in actions:
         newState = AB_State(deepcopy(state.board), 1 - state.player, state.origPlayer)
         # RESULT(s,a)
         newState.board.boardMove(a, state.player)
         new_v = self.min_value(newState, alpha, beta, node+1)
         # compute new values for nodes and cutoffs in recursion
         if new_v.max_depth > v.max_depth:
             v.max_depth = new_v.max_depth         
         v.nodes += new_v.nodes
         v.max_cutoff += new_v.max_cutoff
         v.min_cutoff += new_v.min_cutoff
         # v <- Max(v, MIN_VALUE(RESULT(s,a), alpha, beta))
         if new_v.move_value > v.move_value:
            v.move_value = new_v.move_value
            v.move = a
         if v.move_value >= beta:
            v.max_cutoff += 1
            return v
         if v.move_value > alpha:
            alpha = v.move_value
      return v

   # returns min value
    def min_value(self, state, alpha, beta, node):
      #if terminalTest(state)
      actions = state.board.calcLegalMoves(state.player)
      num_act = len(actions)
      # v <- inf
      # self, move_value, move, max_depth, total_nodes, max_cutoff, min_cutoff
      v = AB_Value(999, None, node, 1, 0, 0)
      # depth cutoff
      if node == DEPTH_LIMIT:
         v.move_value = self.evaluation_function(state.board, state.player)
   #      print("Depth Cutoff. Eval value: "+str(v.move_value))
         return v
      if len(actions)==0:
         # return Utility(state)
         score = self.calcScore(state.board)
         if score[state.origPlayer] > score[1-state.origPlayer]:
            v.move_value = 100 + (2 * score[state.origPlayer] - score[1 - state.origPlayer])
    #        print("(min) Terminal Node Score: "+str(v.move_value))            
         else:
            v.move_value = -100 + (2 * score[state.origPlayer] - score[1 - state.origPlayer])
    #        print("(min) Terminal Node Score: "+str(v.move_value))
         return v     
      for a in actions:
         newState = AB_State(deepcopy(state.board), 1 - state.player, state.origPlayer)
         eval = self.evaluation_function(self.board, self.turn)
    #     print("Current Evaluation: "+str(eval))
         # RESULT(s,a)
         newState.board.boardMove(a, state.player)
         new_v = self.max_value(newState, alpha, beta, node+1)
         # compute new values for nodes and cutoffs in recursion
         if new_v.max_depth > v.max_depth:
             v.max_depth = new_v.max_depth
         v.nodes += new_v.nodes
         v.max_cutoff += new_v.max_cutoff
         v.min_cutoff += new_v.min_cutoff
         # v <- Min(v, MAX_VALUE(RESULT(s,a), alpha, beta))
         if new_v.move_value < v.move_value:
            v.move_value = new_v.move_value
            v.move = a
         if v.move_value <= alpha:
            v.min_cutoff += 1
            return v
         if v.move_value < beta:
            beta = v.move_value
      return v

    # returns a utility value for a non-terminal node
    # f(x) = 5(player piece in end)+3(player not in end)-7(opp in end)-3(opp not in end)
    def evaluation_function(self, board, currPlayer):
        blk_far, blk_home_half, blk_opp_half = 0,0,0
        wt_far, wt_home_half, wt_opp_half = 0,0,0 
        # black's pieces
        for cell in range(len(board.currPos[0])):
            # player pieces at end of board
            if board.currPos[0][cell][0] == BOARD_SIZE-1:
                blk_far += 1
            # player pieces in opponents end
            # change to "print 'yes' if 0 < x < 0.5 else 'no'"
            elif BOARD_SIZE/2 <= board.currPos[0][cell][0] < BOARD_SIZE:
                blk_opp_half += 1
            else:
                blk_home_half += 1
        # white's pieces
        for cell in range(len(board.currPos[1])):
            # opp pieces at end of board 
            if board.currPos[1][cell][0] == 0:
                wt_far += 1
            # opp pieces not at own end
            elif 0 <= board.currPos[1][cell][0] < BOARD_SIZE/2:
                wt_opp_half += 1
            else:
                wt_home_half += 1
        white_score = (7 * wt_far) + (5 * wt_opp_half)+ (3 * wt_home_half)
        black_score = (7 * blk_far) + (5 * blk_opp_half)+ (3 * blk_home_half)
        if currPlayer == 0:
            return (black_score - white_score)
        else:
            return (white_score - black_score)       
                 
# wrapper for alpha-beta info
# v = [move_value, move, max tree depth, # child nodes, # max/beta cutoff, # min/alpha cutoff]
class AB_Value:
    def __init__(self, move_value, move, max_depth, child_nodes, max_cutoff, min_cutoff):
        self.move_value = move_value
        self.move = move
        self.max_depth = max_depth
        self.nodes = child_nodes
        self.max_cutoff = max_cutoff
        self.min_cutoff = min_cutoff
         

# wrapper for state used in alpha-beta
class AB_State:
   def __init__(self, boardState, currPlayer, originalPlayer):
      self.board = boardState
      self.player = currPlayer
      self.origPlayer = originalPlayer
      
class Move:
    def __init__(self, start, end, jump=False):
            self.start = start
            self.end = end # tuple (row, col)
            self.jump = jump # bool
            self.jumpOver = [] # array of pieces jumped over
    
class Board:
    def __init__(self, board=[], currBlack=[], currWhite=[]):
        if board!=[]:
            self.boardState = board     
        else:
            self.setDefaultBoard()
        self.currPos = [[],[]]
        if currBlack != []:
            self.currPos[0] = currBlack
        else:
            self.currPos[0] = self.calcPos(0)
        if currWhite != []:
            self.currPos[1] = currWhite
        else:
            self.currPos[1] = self.calcPos(1)   
                     
    def boardMove(self, move_info, currPlayer):
        move = [move_info.start, move_info.end]
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
            if cell[0] == boardLimit:
                continue
            # diagonal right, only search if not at right edge of board
            if cell[1] != BOARD_SIZE - 1:
                #empty, regular move
                if self.boardState[cell[0] + next][cell[1] + 1]==-1 and not hasJumps:
                    temp = Move((cell[0], cell[1]), (cell[0] + next, cell[1] + 1)) 
                    legalMoves.append(temp)
                # has enemy, can jump it?
                elif self.boardState[cell[0] + next][cell[1] + 1] == 1 - player:
                    jumps = self.checkJump((cell[0], cell[1]), False, player)
                    if len(jumps) != 0:
                        # if first jump, clear out regular moves
                        if not hasJumps:
                            hasJumps = True
                            legalMoves = []
                        legalMoves.extend(jumps)
            # diagonal left, only search if not at left edge of board
            if cell[1]!=0:
                if self.boardState[cell[0] + next][cell[1] - 1] == -1 and not hasJumps:
                    temp = Move((cell[0], cell[1]), (cell[0] + next, cell[1] - 1)) 
                    legalMoves.append(temp)                    
                elif self.boardState[cell[0] + next][cell[1] - 1] == 1 - player:
                    jumps = self.checkJump((cell[0], cell[1]), True, player)
                    if len(jumps)!=0:
                        if not hasJumps:
                            hasJumps = True
                            legalMoves = []                        
                        legalMoves.extend(jumps)                        
        return legalMoves

    # enemy is the square we plan to jump over
    # change later to deal with double jumps
    def checkJump(self, cell, isLeft, player):
        jumps = []
        next = -1 if player == 0 else 1
        # check boundaries!
        if cell[0] + next == 0 or cell[0] + next == BOARD_SIZE - 1:
            return jumps
        #check top left
        if isLeft:
            if cell[1] > 1 and self.boardState[cell[0] + next + next][cell[1] - 2] == -1:
                temp = Move(cell, (cell[0]+next+next, cell[1]-2), True)
                temp.jumpOver = [(cell[0]+next,cell[1]-1)]
                # can has double jump?
                helper = temp.end
                if temp.end[0] + next > 0 and temp.end[0] + next < BOARD_SIZE - 1:
                    #enemy in top left of new square?
                    if temp.end[1] > 1 and self.boardState[temp.end[0] + next][temp.end[1] - 1] == 1 - player:
                        test = self.checkJump(temp.end, True, player)
                        if test != []:
                            dbl_temp = deepcopy(temp) #deepcopy needed?
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)                      
                    # top right?
                    if temp.end[1] < BOARD_SIZE - 2 and self.boardState[temp.end[0] + next][temp.end[1] + 1] == 1 - player:
                        test = self.checkJump(temp.end, False, player)                  
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
                        test = self.checkJump(temp.end, True, player)
                        if test != []:
                            dbl_temp = deepcopy(temp) #deepcopy needed?
                            dbl_temp.end = test[0].end 
                            dbl_temp.jumpOver.extend(test[0].jumpOver)
                            jumps.append(dbl_temp)                              
                    # top right?
                    if temp.end[1] < BOARD_SIZE - 2 and self.boardState[temp.end[0] + next][temp.end[1] + 1] == 1 - player:
                        test = self.checkJump(temp.end, False, player) 
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
         
    def drawBoardState(self):
        """
        Draws and updates board to terminal
        """
        #for colnum in range(BOARD_SIZE):
        #    print str(colnum)+" ",#end="")
        x = 7
        print ("\n------------------------")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.boardState[row][col] == -1:
                    print("+ ", end='')
                elif self.boardState[row][col] == 1:
                    print("W ", end='')
                elif self.boardState[row][col] == 0:
                    print ("B ", end='')
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

### for testing
##    def setDefaultBoard(self):
##        # reset board
##        # -1 = empty, 0=black, 1=white
##        self.boardState = [
##            [-1,1,-1,-1,-1,-1,-1,-1],
##            [-1,-1,1,-1,1,-1,1,-1],
##            [-1,-1,-1,-1,-1,1,-1,-1],
##            [0,-1,0,-1,1,-1,-1,-1],
##            [-1,0,-1,-1,-1,0,-1,-1],
##            [-1,-1,-1,-1,0,-1,-1,-1],
##            [-1,-1,-1,-1,-1,-1,0,-1],
##            [-1,-1,-1,-1,-1,-1,-1,-1]
##        ]            

## Robot move functions
def robot_move(move):
    global playr
    print ("Player moving = ", playr)
    print ("Robot moving")
    #print move.start
    #print move.end
    #print move.jump
    #print move.jumpOver
    # Translate to robot placenames
    start = "ABCDEFGH"[move.start[1]] + "76543210"[move.start[0]]
    end = "ABCDEFGH"[move.end[1]] + "76543210"[move.end[0]]
    print ([start, end])
    # Send to robot
    bxd.move_piece(start, end)
    if move.jump==True:
        for piece in move.jumpOver:
            takePiece = "ABCDEFGH"[piece[1]] + "76543210"[piece[0]]
            print ("Taking pieces ", takePiece)
            bxd.take_piece(takePiece)
    bxd.move_home()
    return

def get_user_move(legal):
    # legal is list of legal moves
    #Convert legal to robot coords
    index = 0
    robot_legal = [0] * len(legal)
    for m in legal:
        #print " Start =",m.start, " End=", m.end
        start = "ABCDEFGH"[m.start[1]] + "76543210"[m.start[0]]
        end = "ABCDEFGH"[m.end[1]] + "76543210"[m.end[0]]
        robot_legal[index]= [start, end]
        index = index + 1
        print (index , ": " , robot_legal[index-1] )
 
    #usr_input = bxd.showList(mainmenu) 
    #print "Move for you = ", usr_input
    
    ret = bxd.get_move(robot_legal)
    print ("&&&" , ret )
    bxd.move_piece(ret[0], ret[1])
    return ret + 1


## Callbacks for BaxUI
def setPlayer(selected=0):
    global playr
    print ("set player " , selected)
    bxd.BaxUI.runit=False
    playr = selected

def calibrate_board (selected=0):
    # Dumps the parameter returned by the callback
    # Calls the baxter calibrate routine
    bxd.calibrate_board()
    

playr=0
def main():
    bxd.init() # Initialise ROS node - only needs to be done once!
    print ("reset")
    bxd.move_home()
    print("Type 0 to play Black ot 1 to play White")
    while True:
        player = int(getch.getch())
        print(player)
        if player == 0 or player == 1:
            break
        else:
            print("Invalid Choice, try again..")
    game = Game(playr)
    game.run()
    
if __name__ == "__main__":
    main()
