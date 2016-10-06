"""
A. Program name
Chess Artist

B. Program description
It is a python script that can annotate a chess pgn file with
static evaluation of an engine.

C. License notice
This program is free software, you can redistribute it and/or modify
it under the terms of the GPLv3 License as published by the
Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License (LICENSE)
along with this program, if not visit https://www.gnu.org/licenses/gpl.html

D. Dependent modules and/or programs
1. python-chess
https://pypi.python.org/pypi/python-chess

E. Programming language
1. Python v2.7.11
https://www.python.org/

F. Other
1. See also the README.txt for some useful informations.
"""

import subprocess
import os
import sys
import chess
from chess import pgn
    
def DeleteFile(fn):
    """ Delete fn file """
    if os.path.isfile(fn):
        os.remove(fn)

def CheckFile(fn):
    """ Verify if fn is present or not.
        If file is not available the program will exit.
    """
    if not os.path.isfile(fn):
        print('Error! %s is missing' %(fn))
        sys.exit(1)

def GetEngineIdName(engine):
    """ Returns the engine id name """
    engineIdName = engine[0:-4]

    # Run the engine
    p = subprocess.Popen(engine, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

    # Send command to engine
    p.stdin.write("uci\n")
    
    # Parse engine replies
    for eline in iter(p.stdout.readline, ''):
        line = eline.strip()

        # Print engine output after uci command
        print(line)

        # Save id name
        if 'id name ' in line:
            idName = line.split()
            engineIdName = ' '.join(idName[2:])            
        if "uciok" in line:           
            break
    p.stdin.write('quit\n')
    p.communicate()
    return engineIdName    

def GetStaticEval(engine, pos):
    """ Returns static eval by running the engine,
        setup position pos and send eval command.
    """
    score = -32000.0

    # Run the engine
    p = subprocess.Popen(engine, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

    # Send command to engine
    p.stdin.write("uci\n")

    # Parse engine replies
    for eline in iter(p.stdout.readline, ''):
        line = eline.strip()
        if "uciok" in line:
            break
            
    # Send command to engine
    p.stdin.write("isready\n")
    
    # Parse engine replies
    for eline in iter(p.stdout.readline, ''):
        line = eline.strip()
        if "readyok" in line:
            break
            
    # Send commands to engine
    p.stdin.write("ucinewgame\n")
    p.stdin.write("position fen " + pos + "\n")
    p.stdin.write("eval\n")

    # Parse the output and extract the engine static eval
    for eline in iter(p.stdout.readline, ''):        
        line = eline.strip()
        if 'Total Evaluation: ' in line:
            first = line.split('(')[0]
            score = float(first.split()[2])
            break
    p.stdin.write('quit\n')
    p.communicate()
    assert score != -32000.0, 'Something is wrong in the eval'
    return score 

def EvaluateOptions(opt):
    """ Convert opt list to dict """
    return dict([(k, v) for k,v in zip (opt[::2], opt[1::2])])

def GetOptionValue(opt, optName, var):
    """ Returns value of options """
    if opt.has_key(optName):
        var = opt.get(optName)
    return var

def main(argv):
    """ start """
    inputFile = 'src.pgn'
    outputFile = 'out_src.pgn'
    engineName = 'engine.exe'
    
    # Evaluate the command line options
    options = EvaluateOptions(argv)
    if len(options):
        inputFile = GetOptionValue(options, '-inpgn', inputFile)
        outputFile = GetOptionValue(options, '-outpgn', outputFile)
        engineName = GetOptionValue(options, '-eng', engineName)

    # Verify presence of input pgn file
    CheckFile(inputFile)

    # Verify presence of engine file
    CheckFile(engineName)

    # Delete existing specified output filename
    DeleteFile(outputFile)

    # Get engine id name for the Annotator tag
    engIdName = GetEngineIdName(engineName)

    # Open the input pgn file
    pgnHandle = open(inputFile, 'r')

    # Read the input pgn file using the python-chess module
    game = chess.pgn.read_game(pgnHandle)
    game_cnt = 0

    # Loop thru the games
    while game:
        game_cnt += 1
        print('Annotating game %d...' %(game_cnt))       

        # Save the tag section of the game
        for key, value in game.headers.items():
            with open(outputFile, 'a+') as f:
                f.write('[%s \"%s\"]\n' %(key, value))

        # Write the annotator tag
        with open(outputFile, 'a+') as f:
            f.write('[Annotator "%s"]\n\n' %(engIdName))

        # Get result to be written later as game termination marker
        res = game.headers['Result']

        # Loop thru the moves
        gameNode = game        
        while gameNode.variations:
            side = gameNode.board().turn
            fmvn = gameNode.board().fullmove_number             
            nextNode = gameNode.variation(0)                      
            sanMove = nextNode.san()

            # Use FEN after a move to get the static eval
            fen = nextNode.board().fen()

            # Get engine static eval
            staticEval = GetStaticEval(engineName, fen)

            # Write the move and score as comment
            with open(outputFile, 'a+') as f:
                if side:
                    f.write('%d. %s {%+0.2f} ' %(fmvn, sanMove, staticEval))
                else:
                    f.write('%s {%+0.2f} ' %(sanMove, staticEval))

                    # Don't write in one long line
                    if fmvn % 3 == 0:
                        f.write('\n')

            # Read the next position
            gameNode = nextNode

        # Write the result and a space between games
        with open(outputFile, 'a') as f:
            f.write('%s\n\n' %(res))

        # Read the next game 
        game = chess.pgn.read_game(pgnHandle)

    # Close the file handle
    pgnHandle.close()  

    print('Done!!\n')    

if __name__ == "__main__":
    main(sys.argv[1:])
