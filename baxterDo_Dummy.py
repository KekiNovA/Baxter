#! /usr/bin/python
"""
Baxter draughts program
Baxter actions dummy/simulator module

M L Walters, Jan 2021
V2 Major update Jan 2021 M.L. Walters. Updated to use Python 3.8+, rationalise, simplfy and rename the 
	 main API functions. NOT compatible with old baxterUICheckeers.py program.

This program is a "dummy" robot simulator module which can be used to simulate the 
Baxter robot while devloping the game AI and top level control program to enable Baxter
to play a gameof Draughts (Checkers)python against a human user.

Note, this program/module file should be in the same folder or directory as your top
level game AI control program.
To use the module, simply import it  into your own top level program: 

import baxterDo_Dummy as bxd 
help(bxd)


"""
# V2  


# Standard libs 
import math
pi = math.pi
import pickle
import numpy
from time import sleep
# Standard ROS libs
#import rospy
#import roslib
#import std_msgs.msg
#import tf
#import geometry_msgs.msg
#from sensor_msgs.msg import Image
#from cv_bridge import CvBridge, CvBridgeError
#import cv
#import cv2

# Baxter libs
#import baxter_interface
#from baxter_core_msgs.msg import ITBState
#from moveit_commander import conversions
#from geometry_msgs.msg import (
#    PoseStamped,
#    Pose,
#    Point,
# #   Quaternion,
#    )
#from std_msgs.msg import Header
#from baxter_core_msgs.srv import (
#    SolvePositionIK,
#    SolvePositionIKRequest,
#    )
#import BaxUI

# global variables

home_joint_angles = None # Left arm home/camera position
board_dict = None        # Board and other named postions
zOffset = 0               # z axis offset to add clearance ot table top
zApproach = 0.1          # Clearance for pick and place moves
takeq = 0                # Queue area position for taken pieces.


# Start of function defs

def move_piece (startpos, endpos, limb="left"):
    """
    Will move a game piece from location on the game board. The positions can be
    given by either:
        A string of the form "<C>n", where <C> is a letter from A to H, n is a number 
        from 1 to 8
    The linb string may be either "left" or "right" and will use the right or left arm 
    respectively. 
    """
    print("move_piece(", startpos, ", ", endpos, ")")
    if (startpos in board_dict) and (endpos in board_dict):
        print( "Moving piece from ", startpos, " to ", endpos, ".")
        #say("Moving piece from "+ startpos+ " to "+ endpos+".")
        move_arm_xyz("left", board_dict[startpos]+[zApproach])
        move_arm_xyz("left", board_dict[startpos]+[zOffset])
        sleep(1.0)
        print("Gripper closed")
        sleep(1.0)
        move_arm_xyz("left", board_dict[startpos]+[zApproach])
        # Extra move here to avoid swiping board
        move_arm_xyz("left", board_dict[endpos]+ [zApproach])
        move_arm_xyz("left", board_dict[endpos]+[zOffset])
        sleep(1.0)
        print("Gripper open")
        sleep(1.0)
        move_arm_xyz("left", board_dict[endpos]+[zApproach])
        print("move_piece(", startpos, ", ", endpos,") OK")
        print()
    else:
        print( """"Starting and end positions should be two seperate strings containg board position
        names (e.g. "A2", "C3" etc.) or some other previously defined place name.""")
    return

def move_to(placeName=None, approach = 0, limb = "left"):
    """
    move_to(placeName, approach=0, limb = "left")
    Moves the robot arm gripper to a previously named position within the working envelope of the robot.
    placename is a string which is a key which is paired with set of previously stored co-ordinates
    in the board_dict{} dictionalry. e.g. board_dict["A3"] returns the XYZ co-ords of the plaename "A3".
    """
    if placeName in board_dict:
        print("move_to(", placeName, ")")
        move_arm_xyz(limb, board_dict[placeName] + [approach])
        sleep(1.0)
        print("move_to(", placeName, ") OK")
    else:
        print("Unknown Placename")
    print()
    return


def king_piece(kingpos, colour, limb="left"):
    """
    Will king a piece at kingpos, taking a pience form the take area relevant to the player colour,
    "Black" or "White". kingpos is a string (e.g. "A7" which is a key to a set of xyz co-ords
    stored in the board_dict{} dictionary. Note, normally would be in row 7 or 0.
    Parameter limb may be either "left" or "right", default is "left".
    """
    global takeq
    print("king_piece(", kingpos, ")")
    print( "Kinging piece for ", colour, " player.")
    if takeq > 0: takeq -= 1
    # Move to last placed slot in take area
    move_arm_xyz("left", board_dict["take"+str(takeq)]+[zApproach], [pi, 0, pi * 3.0/4.0])
    move_arm_xyz("left", board_dict["take"+str(takeq)]+[zOffset+0.002], [pi, 0, pi * 3.0/4.0])
    # Close Gripper
    print("Gripper closed")
    sleep(1.0)
    move_arm_xyz("left", board_dict["take"+str(takeq)]+[zApproach], [pi, 0, pi * 3.0/4.0]) 
    move_arm_xyz("left", board_dict[kingpos]+[zApproach])
    move_arm_xyz("left", board_dict[kingpos]+[zOffset])
    print("Gripper open")
    sleep(1.0) 
    move_arm_xyz("left", board_dict[kingpos]+[zApproach])
    print("king_piece(", kingpos, ") OK") 
    print()  
    return 
    
    
def take_piece(takepos, colour, limb="left"):
    """
    Will take a piece at takepos, and put in the take area relevant to the player colour,
    "Black" or "White". takepos is a string (e.g. "A3" which is a key to a set of xyz co-ords
    stored in the board_dict{} dictionary.
    Parameter limb may be either "left" or "right", default is "left".
    """
    global takeq
    print("take_piece(", takepos, ")")
    print( "Taking piece for ", colour, " player.")
    move_arm_xyz("left", board_dict["take"+str(takeq//12)]+[zApproach], [pi, 0, pi * 3.0/4.0])
    move_arm_xyz("left", board_dict["take"+str(takeq//12)]+[zOffset+0.002], [pi, 0, pi * 3.0/4.0])
    
    # Close Gripper
    print("Gripper closed")
    sleep(1.0)
    move_arm_xyz("left", board_dict["take"+str(takeq//12)]+[zApproach], [pi, 0, pi * 3.0/4.0]) 
   # Move to next free slot in take area
    move_arm_xyz("left", board_dict[takepos]+[zApproach])
    move_arm_xyz("left", board_dict[takepos]+[zOffset])
    print("Gripper open")
    sleep(1.0)  
    move_arm_xyz("left", board_dict[takepos]+[zApproach])
    takeq += 1 
    print("take_piece(", takepos, ") OK") 
    print()  
    return 
    

def move_home(limb = "left"):
    """
    Moves baxters "left" (default)  or "right" arms to its "Home" position, so that camera in "left" or "right"
    arm can view the board from above. Note, the camera position muct be woithin the robot's working
    area/envelope
    """
    print("move_home()")
    print( "Moving to Home position")
    move_arm_xyz("left", campos)
    sleep(2.0) # allow position to settle for camera
    print("move_home() OK")
    print()
    return


def move_navpos():
    """
    move_navpos()
    Moves the robot's right arm to a suitable postion so the the user "Navigator" controls are
    conveniently placed for the user to operate.
    """
    print("move_navpos()")
    print( "Moving right arm for easy access to Navigator")
    move_arm_xyz("right", navpos)
    sleep(2.0)
    print("move_navpos() OK")
    print()
    
                                                                
def calibrate_board():
    """
    Sets up the robot so that it knows the board positions. Settings are saved to a file
    so should only need calibrating if the workspace changes. 
    If the "board.cfg" file is not found, it will use a set of default values for testing purposes.
    On the real robot, it is necessary to Manually move the arm and centalise the gripper over the 
    bottom left square (a0), then press RETURN. 
    Then manually move the arm and centalise the gripper over the top right square (h7), then 
    press RETURN. The robot will automatically calculate all the necessary positions from these two positions.
    """
    print("calibrate_board()")
    global board_dict, zOffset, campos, navpos
    print("Calibrating Game Board")
    # Load/Generate a set of reasonanble default values 
    board_dict = {'H1': [0.7178648524251562, 0.24264081206735347],
         'take0': [0.42334338957794393, 0.3426408120673535], 'take10': [0.4833433895779439, 0.46264081206735347],
         'take11': [0.5433433895779439, 0.46264081206735347], 'take12': [0.6033433895779439, 0.46264081206735347],
         'take8': [0.6033433895779439, 0.40264081206735347], 'C0': [0.7669517628996916, 0.004784862900929679],
         'take9': [0.42334338957794393, 0.46264081206735347], 'G7': [0.42334338957794393, 0.1950696222340687],
         'G6': [0.47243030005247927, 0.1950696222340687], 'G5': [0.5215172105270146, 0.1950696222340687],
         'G4': [0.57060412100155, 0.1950696222340687], 'zoffset': -0.2566477549938345, 
         'G2': [0.6687779419506208, 0.1950696222340687], 'G1': [0.7178648524251562, 0.1950696222340687],
         'G0': [0.7669517628996916, 0.1950696222340687], 'H0': [0.7669517628996916, 0.24264081206735347],
         'take5': [0.42334338957794393, 0.40264081206735347], 'E2': [0.6687779419506208, 0.09992724256749919],
         'A1': [0.7178648524251562, -0.09035751676563983], 'A0': [0.7669517628996916, -0.09035751676563983],
         'A3': [0.6196910314760854, -0.09035751676563983], 'A2': [0.6687779419506208, -0.09035751676563983],
         'A5': [0.5215172105270146, -0.09035751676563983], 'A4': [0.57060412100155, -0.09035751676563983],
         'A7': [0.42334338957794393, -0.09035751676563983], 'A6': [0.47243030005247927, -0.09035751676563983],
         'C3': [0.6196910314760854, 0.004784862900929679], 'C2': [0.6687779419506208, 0.004784862900929679],
         'C1': [0.7178648524251562, 0.004784862900929679], 'E6': [0.47243030005247927, 0.09992724256749919],
         'E1': [0.7178648524251562, 0.09992724256749919], 'C6': [0.47243030005247927, 0.004784862900929679],
         'C5': [0.5215172105270146, 0.004784862900929679], 'C4': [0.57060412100155, 0.004784862900929679],
         'E0': [0.7669517628996916, 0.09992724256749919], 'take7': [0.5433433895779439, 0.40264081206735347],
         'take2': [0.5433433895779439, 0.3426408120673535], 'B3': [0.6196910314760854, -0.042786326932355075],
         'take4': [0.6633433895779439, 0.3426408120673535], 'E3': [0.6196910314760854, 0.09992724256749919],
         'E5': [0.5215172105270146, 0.09992724256749919], 'campos': [1.0669517628996916, 0.3516424832343602, 0.2053522450061655], 
         'E4': [0.57060412100155, 0.09992724256749919], 'G3': [0.6196910314760854, 0.1950696222340687], 
         'E7': [0.42334338957794393, 0.09992724256749919], 'take3': [0.6033433895779439, 0.3426408120673535], 
         'F0': [0.7669517628996916, 0.14749843240078395], 'F1': [0.7178648524251562, 0.14749843240078395], 
         'F2': [0.6687779419506208, 0.14749843240078395], 'F3': [0.6196910314760854, 0.14749843240078395], 
         'F4': [0.57060412100155, 0.14749843240078395], 'F5': [0.5215172105270146, 0.14749843240078395], 
         'F6': [0.47243030005247927, 0.14749843240078395], 'take6': [0.4833433895779439, 0.40264081206735347], 
         'H2': [0.6687779419506208, 0.24264081206735347], 'C7': [0.42334338957794393, 0.004784862900929679], 
         'F7': [0.42334338957794393, 0.14749843240078395], 'take1': [0.4833433895779439, 0.3426408120673535], 
         'H6': [0.47243030005247927, 0.24264081206735347], 'H7': [0.42334338957794393, 0.24264081206735347], 
         'H4': [0.57060412100155, 0.24264081206735347], 'H5': [0.5215172105270146, 0.24264081206735347], 
         'B4': [0.57060412100155, -0.042786326932355075], 'B5': [0.5215172105270146, -0.042786326932355075], 
         'B6': [0.47243030005247927, -0.042786326932355075], 'B7': [0.42334338957794393, -0.042786326932355075], 
         'B0': [0.7669517628996916, -0.042786326932355075], 'B1': [0.7178648524251562, -0.042786326932355075], 
         'B2': [0.6687779419506208, -0.042786326932355075], 'H3': [0.6196910314760854, 0.24264081206735347], 
         'D6': [0.47243030005247927, 0.05235605273421443], 'D7': [0.42334338957794393, 0.05235605273421443], 
         'D4': [0.57060412100155, 0.05235605273421443], 'D5': [0.5215172105270146, 0.05235605273421443], 
         'D2': [0.6687779419506208, 0.05235605273421443], 'D3': [0.6196910314760854, 0.05235605273421443], 
         'D0': [0.7669517628996916, 0.05235605273421443], 'D1': [0.7178648524251562, 0.05235605273421443],
         'take13': [0.4833433895779439, 0.46264081206735347],'take14': [0.4833433895779439, 0.46264081206735347],
         'take15': [0.4833433895779439, 0.46264081206735347],'take16': [0.4833433895779439, 0.46264081206735347],
         'take17': [0.4833433895779439, 0.46264081206735347],'take18': [0.4833433895779439, 0.46264081206735347],
         'take19': [0.4833433895779439, 0.46264081206735347], 'take20': [0.4833433895779439, 0.46264081206735347],
         'take21': [0.4833433895779439, 0.46264081206735347], 'take22': [0.4833433895779439, 0.46264081206735347],
         'take23': [0.4833433895779439, 0.46264081206735347], 'take24': [0.4833433895779439, 0.46264081206735347],
         'navpos': [0.645, -0.377, 0.2] }
    if "zoffset" in board_dict: # z level of board i.e. pick height, z cord
        print("Setting z offset")
        zOffset=board_dict["zoffset"]
    else:
        zOffset = 0.0
    zApproach= zOffset + 0.1 # pick approach height - hardcoded
    
    print("Setting Camara Position")
    if "campos" in board_dict: 
        
        campos = board_dict["campos"] 
    else:
        campos = [0.645, 0.377, 0.332]
    print( "campos= ", campos, " set ok")
    
    if "navpos" in board_dict:
        print("Setting navigator arm Position")
        navpos = board_dict["navpos"]
    else:
        navpos  = [0.645, -0.377, 0.2]
    print( "navpos= ", board_dict["campos"], " set ok")
    
    print("calibrate_board() OK")
    print()
    return

def move_arm_xyz(limb ="left", xyz =[0.67, 0.25, 0.27], rot = [pi, 0, pi]):
    """
    move_arm_xyz(limb="left", xyz= [0.67, 0.25, 0.27], rot = [pi, 0, pi])
    Moves the effector/gripperof the robot arm to position given by list [x, y, z}, with 
    gripper orientation about the x, y, and z axes  given by rot = [ax, ay, az], 
    where ax, ay and az are angles in radians. both xyz and rot are otional. If xyz is not given, 
    it defaults to the robot's "Home" position, and if rot is not oprivided, the default orientation is gripper 
    downwards and alighed with the X axis.
    """
    #try:
    print ("Arm moving to Position ", xyz, " Rotations ", rot)
    sleep(1.0)
    print("move_arm_xyz(", limb, "moved to postition = ", xyz, ", orientation = ", rot, ") OK")
    return
    
def init():
    """
    imit()
    This intialises the robot. it poulates the board_dict{} dictionalry with the board and other important positions, 
    then drives the robot left arm to the Home position, anfd the right arm to the navpos() position. The robot is then
    ready to beused to manipulate pieces on and of fthe board.
    """
    global board_dict
    #move_home("left")
    #move_navpos()
    print("init() Initialising robot")
    # If "board.cfg" file exists, load it
    # board_dict contains robot cords for pick positions etc.
    try:
        print( "Looking for board.cfg file.")
        board_dict = pickle.load(open ("board.cfg", "rb"))
        print ("Successfully loaded board.cfg")
    except:
        print("board.cfg file not found, using defaults")
        calibrate_board()
    move_navpos()
    move_home("left")
    print("init() Robot Initialised OK")
    print()
    return

      

def get_move(legal_moves):
    """
    get_move(legal_moves)
    Shows the user a numbered list of possble (i.e legal) moves as sublists, then allows the
    user to type in a number to select the movce they want to make.
    Returns a list containing the place names as strings, of the start postion and end position
    of the selected move, e.g. [ "A3", "B4"]
    """
    print("get_move(", legal_moves, ")")
    print( "Waiting for User response")
    
    # Show options to user and get selection
    user_input = None
    while user_input == None:
        index = 0
        for m in legal_moves:
            print(str(index + 1)+": "+ str(m))
            index += 1
        try:
            user_input = int(input("Type in number of move to make. Press RETURN: "))-1
        except:
            user_input = None
        if user_input != None and user_input >= index:
            user_input = None
        if user_input == None: print("User input must be an integer in the range 1 to ",index )
    print("get_move(legal_moves) return selected move = ", legal_moves[user_input])
    move_piece(legal_moves[user_input][0], legal_moves[user_input][1])
    print("get_move() return ", legal_moves[user_input], " OK")
    print()
    return legal_moves[user_input]
    

def test():
    init() # Initialise ROS node (has to be done in main module!)
    # Test moves here
    print("Testing:")
    king_piece("A7")
    move_home("left")
    move_piece ("A0", "B1")
    move_to("C7")
    take_piece("A3")
    next_move = get_move([["A3", "B4"], ["C2", "D4"], ["E5", "F7"]])
    move_piece (next_move[0], next_move[1])
    

# Start of module code
# Only runs if main module for testing
if __name__ == "__main__":
    
    #test() # run the tests
    # Then nteractively test
    while 1: 
        msg = input("Function to test or 'q' to Quit: ")
        if msg =="q" or msg == "Q": break
        try:
            print( eval(msg))
        except:
            pass
    
