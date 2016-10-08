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
import time
import chess
from chess import pgn

# Constants
APP_NAME = 'Chess Artist'
APP_VERSION = '0.1.0'
BOOK_MOVE_LIMIT = 30
BOOK_SEARCH_TIME = 200
MAX_SCORE = 32000
MAX_SEARCH_SCORE = 100000

def PrintProgram():
    """ Prints program name and version """
    print('%s %s\n' %(APP_NAME, APP_VERSION))
    
def DeleteFile(fn):
    """ Delete fn file """
    if os.path.isfile(fn):
        os.remove(fn)

def CheckFiles(infn, outfn, engfn):
    """ Quit program if infn is missing.
        Quit program if infn and outfn is the same.
        Quit program if engfn is missing.
    """
    # input file is missing
    if not os.path.isfile(infn):
        print('Error! %s is missing' %(infn))
        sys.exit(1)

    # input file and output file is the same.
    if infn == outfn:
        print('Error! input filename and output filename is the same')
        sys.exit(1)

    # engine file is missing.
    if not os.path.isfile(engfn):
        print('Error! %s is missing' %(engfn))
        sys.exit(1)

def EvaluateOptions(opt):
    """ Convert opt list to dict and returns it """
    return dict([(k, v) for k, v in zip(opt[::2], opt[1::2])])

def GetOptionValue(opt, optName, var):
    """ Returns value of opt dict given the key """
    if opt.has_key(optName):
        var = opt.get(optName)
    return var

class Analyze():
    """ An object that will read and annotate games in a pgn file """
    def __init__(self, infn, outfn, eng, **opt):
        """ Initialize """
        self.infn = infn
        self.outfn = outfn
        self.eng = eng
        self.bookTypeOpt = opt['-book']
        self.evalTypeOpt = opt['-eval']
        self.writeCnt = 0
        self.isCereMoveFound = False

    def UciToSanMove(self, pos, uciMove):
        """ Returns san move given uci move """
        board = chess.Board(pos)
        board.push(chess.Move.from_uci(uciMove))
        sanMove = board.san(board.pop())
        return sanMove

    def PrintEngineIdName(self):
        """ Prints engine id name """
        print('Engine name: %s' %(self.GetEngineIdName()))

    def WriteMovesOnly(self, side, moveNumber, sanMove):
        """ Write moves only in the output file """
        # Write the moves
        with open(self.outfn, 'a+') as f:
            if side:
                f.write('%d. %s ' %(moveNumber, sanMove))
            else:
                f.write('%s ' %(sanMove))

    def WriteMovesWithScore(self, side, moveNumber, sanMove, posScore):
        """ Write moves with score in the output file """
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                f.write('%d. %s {%+0.2f} ' %(moveNumber, sanMove, posScore))
            else:
                f.write('%s {%+0.2f} ' %(sanMove, posScore))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 4:
                    self.writeCnt = 0
                    f.write('\n')

    def WriteMovesWithBookMove(self, side, moveNumber, sanMove, bookMove):
        """ Write moves with book moves in the output file """
        bookComment = 'cerebellum book'
        
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                f.write('%d. %s (%d. %s {%s}) ' %(moveNumber, sanMove, moveNumber, bookMove, bookComment))
            else:
                f.write('%d... %s (%d... %s {%s}) ' %(moveNumber, sanMove, moveNumber, bookMove, bookComment))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
                    self.writeCnt = 0
                    f.write('\n')

    def WriteMovesWithScoreAndBookMove(self, side, moveNumber, sanMove, bookMove, posScore):
        """ Write moves with score and book moves in the output file """
        bookComment = 'cerebellum book'
        
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                f.write('%d. %s {%+0.2f} (%d. %s {%s}) ' %(moveNumber, sanMove, posScore, moveNumber, bookMove, bookComment))
            else:
                f.write('%d... %s {%+0.2f} (%d... %s {%s}) ' %(moveNumber, sanMove, posScore, moveNumber, bookMove, bookComment))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
                    self.writeCnt = 0
                    f.write('\n')        

    def WriteMoves(self, side, fmvn, sanMove, bookMove, posScore, isGameOver):
        """ Write moves and comments to the output file """
        # If game is over [mate, stalemate] just print the move.
        if isGameOver:
            self.WriteMovesOnly(side, fmvn, sanMove)
            return

        # Write rest of moves and comments.
        # (1) With score
        if not self.isCereMoveFound and self.evalTypeOpt != 'none':
            self.WriteMovesWithScore(side, fmvn, sanMove, posScore)

        # (2) With book move
        elif self.isCereMoveFound and self.evalTypeOpt == 'none':
            self.WriteMovesWithBookMove(side, fmvn, sanMove, bookMove)

        # (3) With score and book move
        elif self.isCereMoveFound and self.evalTypeOpt != 'none':
            self.WriteMovesWithScoreAndBookMove(side, fmvn, sanMove, bookMove, posScore)
            
    def MateDistanceToValue(self, d):
        """ Returns value given distance to mate """
        value = 0
        if d < 0:
            value = -2*d - MAX_SCORE
        elif d > 0:
            value = MAX_SCORE - 2*d + 1
        return value

    def GetEngineIdName(self):
        """ Returns the engine id name """
        engineIdName = self.eng[0:-4]

        # Run the engine
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Send command to engine.
        p.stdin.write("uci\n")
        
        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()

            # Save id name.
            if 'id name ' in line:
                idName = line.split()
                engineIdName = ' '.join(idName[2:])            
            if "uciok" in line:           
                break
                
        # Quit the engine
        p.stdin.write('quit\n')
        p.communicate()
        return engineIdName

    def GetCerebellumBookMove(self, pos):
        """ Returns a move from cerebellum book """
        isInfoDepth = False
        
        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Send command to engine.
        p.stdin.write("uci\n")

        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "uciok" in line:
                break

        # Set the path of Brainfish cerebellum book. Make sure the Brainfish engine,
        # the script and the cerebellum book are on the same directory.
        p.stdin.write("setoption name BookPath value Cerebellum_Light.bin\n")

        # Set threads to 1 just in case the default threads is changed in the future.
        p.stdin.write("setoption name Threads value 1\n")
                
        # Send command to engine.
        p.stdin.write("isready\n")
        
        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "readyok" in line:
                break
                
        # Send commands to engine.
        p.stdin.write("ucinewgame\n")
        p.stdin.write("position fen " + pos + "\n")
        p.stdin.write("go movetime %d\n" %(BOOK_SEARCH_TIME))

        # Parse the output and extract the bestmove.
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            
            # If the engine shows info depth ... it is no longer using a book
            if 'info depth' in line:
                isInfoDepth = True
            
            # Break search when we receive bestmove string from engine
            if 'bestmove ' in line:
                moveLine = line.split()[1]
                bestMove = moveLine.strip()
                break
                
        # Quit the engine
        p.stdin.write('quit\n')
        p.communicate()

        # Convert uci move to san move format.
        bestMove = self.UciToSanMove(pos, bestMove)

        # If we did not get info depth from engine, then the bestmove is from the book.
        if not isInfoDepth:
            # True indicates that the bestMove is from cerebellum book.
            return bestMove, True
        return bestMove, False

    def GetStaticEval(self, pos):
        """ Returns static eval by running the engine,
            setup position pos and send eval command.
        """
        score = -32000.0

        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Send command to engine.
        p.stdin.write("uci\n")

        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "uciok" in line:
                break
                
        # Send command to engine.
        p.stdin.write("isready\n")
        
        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "readyok" in line:
                break
                
        # Send commands to engine.
        p.stdin.write("ucinewgame\n")
        p.stdin.write("position fen " + pos + "\n")
        p.stdin.write("eval\n")

        # Parse the output and extract the engine static eval.
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            if 'Total Evaluation: ' in line:
                first = line.split('(')[0]
                score = float(first.split()[2])
                break
                
        # Quit the engine
        p.stdin.write('quit\n')
        p.communicate()
        assert score != -32000.0, 'Error! something is wrong in static eval calculation.'
        return score

    def GetSearchScore(self, pos, side):
        """ Returns search bestmove and score from the engine. """

        # Initialize
        engOptionHash = 64
        engOptionThreads = 1
        engMoveTime = 500
        scoreCp = MAX_SEARCH_SCORE

        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Send command to engine.
        p.stdin.write("uci\n")

        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "uciok" in line:
                break

        # Set Hash and Threads options to uci engine
        p.stdin.write("setoption name Hash value %d\n" %(engOptionHash))
        p.stdin.write("setoption name Threads value %d\n" %(engOptionThreads))
                
        # Send command to engine.
        p.stdin.write("isready\n")
        
        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "readyok" in line:
                break
                
        # Send commands to engine.
        p.stdin.write("ucinewgame\n")
        p.stdin.write("position fen " + pos + "\n")
        p.stdin.write("go movetime %d\n" %(engMoveTime))

        # Parse the output and extract the engine search score.
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            if 'score cp ' in line:
                splitStr = line.split()
                scoreIndex = splitStr.index('score')
                scoreCp = int(splitStr[scoreIndex + 2])
            if 'score mate ' in line:
                splitStr = line.split()
                scoreIndex = splitStr.index('score')
                mateInN = int(splitStr[scoreIndex + 2])

                # Convert mate in move number to value
                scoreCp = self.MateDistanceToValue(mateInN)        
                
            # Break search when we receive bestmove string from engine
            if 'bestmove ' in line:
                break
                
        # Quit the engine
        p.stdin.write('quit\n')
        p.communicate()        
        assert scoreCp != MAX_SEARCH_SCORE, 'Error, search failed to return a score.'

        # Invert the score sign because we analyze the position after the move.
        scoreCp = -1 * scoreCp

        # Convert score from the point of view of white.
        if not side:
            scoreCp = -1 * scoreCp

        # Convert the score to pawn unit in float type
        scoreP = float(scoreCp)/100.0
        return scoreP

    def Annotate(self):
        """ Parse the pgn file and annotate the games """
        # Get engine id name for the Annotator tag.
        engIdName = self.GetEngineIdName()

        # Disable bookTypeOpt if engine is not Brainfish.
        if self.bookTypeOpt == 'cerebellum':
            brainFishEngine = self.GetEngineIdName()
            if 'Brainfish' not in brainFishEngine:
                self.bookTypeOpt = 'none'
                print('\nWarning!! engine is not Brainfish, cerebellum book is disabled.\n')
        
        # Open the input pgn file
        pgnHandle = open(self.infn, 'r')

        # Read the input pgn file using the python-chess module.
        game = chess.pgn.read_game(pgnHandle)

        # Used for displaying progress in console.
        gameCnt = 0

        # Loop thru the games.
        while game:
            gameCnt += 1

            # Used for formatting the output.
            self.writeCnt = 0

            # Show progress in console.
            print('Annotating game %d...' %(gameCnt))

            # We don't access cere book if isCereEnd is true.
            isCereEnd = False

            # Save the tag section of the game.
            for key, value in game.headers.items():
                with open(self.outfn, 'a+') as f:
                    f.write('[%s \"%s\"]\n' %(key, value))

            # Write the annotator tag.
            with open(self.outfn, 'a+') as f:
                f.write('[Annotator "%s"]\n\n' %(engIdName))

            # Before the movetext are written, add a comment of whether
            # move comments are from static evaluation or search score of the engine.
            if self.evalTypeOpt == 'static':
                with open(self.outfn, 'a+') as f:
                    f.write('{Move comments are from engine static evaluation.}\n')
            elif self.evalTypeOpt == 'search':
                with open(self.outfn, 'a+') as f:
                    f.write('{Move comments are from engine search score.}\n')

            # Save result to be written later as game termination marker.
            res = game.headers['Result']

            # Loop thru the moves within this game.
            gameNode = game        
            while gameNode.variations:
                side = gameNode.board().turn
                fmvn = gameNode.board().fullmove_number             
                nextNode = gameNode.variation(0)                      
                sanMove = nextNode.san()

                # (1) Try to get a cerebellum book move.
                self.isCereMoveFound = False
                cereBookMove = None
                if self.bookTypeOpt == 'cerebellum' and not isCereEnd:
                    # Use FEN before a move.
                    fenBeforeMove = gameNode.board().fen()
                    cereBookMove, self.isCereMoveFound = self.GetCerebellumBookMove(fenBeforeMove)

                    # End trying to find cerebellum book move beyond BOOK_MOVE_LIMIT.
                    if not self.isCereMoveFound and fmvn > BOOK_MOVE_LIMIT:
                        isCereEnd = True

                # (2) Get the score of the position after a move.
                posScore = None
                if self.evalTypeOpt == 'static':
                    fenAfterMove = nextNode.board().fen()
                    staticScore = self.GetStaticEval(fenAfterMove)
                    posScore = staticScore
                elif self.evalTypeOpt == 'search':
                    fenAfterMove = nextNode.board().fen()
                    searchScore = self.GetSearchScore(fenAfterMove, side)
                    posScore = searchScore
                    
                # If game is over by checkmate and stalemate                
                isGameOver = nextNode.board().is_checkmate() or nextNode.board().is_stalemate()
                
                # (3) Write moves and comments.
                self.WriteMoves(side, fmvn, sanMove, cereBookMove, posScore, isGameOver)

                # Read the next position.
                gameNode = nextNode

            # Write the result and a space between games.
            with open(self.outfn, 'a') as f:
                f.write('%s\n\n' %(res))

            # Read the next game.
            game = chess.pgn.read_game(pgnHandle)

        # Close the file handle.
        pgnHandle.close()
        
def main(argv):
    """ start """
    PrintProgram()

    # Initialize
    inputFile = 'src.pgn'
    outputFile = 'out_src.pgn'
    engineName = 'engine.exe'
    bookTypeOption = 'none' # ['none', 'cerebellum', 'polyglot']
    evalTypeOption = 'static' # ['none', 'static', 'search']
    cereBookFile = 'Cerebellum_Light.bin'
    
    # Evaluate the command line options.
    options = EvaluateOptions(argv)
    if len(options):
        inputFile = GetOptionValue(options, '-inpgn', inputFile)
        outputFile = GetOptionValue(options, '-outpgn', outputFile)
        engineName = GetOptionValue(options, '-eng', engineName)
        bookTypeOption = GetOptionValue(options, '-book', bookTypeOption)
        evalTypeOption = GetOptionValue(options, '-eval', evalTypeOption)

    # Check input, output and engine files.
    CheckFiles(inputFile, outputFile, engineName)
    
    # Disable use of cerebellum book when Cerebellum_Light.bin is missing.
    if bookTypeOption == 'cerebellum':
        if not os.path.isfile(cereBookFile):
            bookTypeOption = 'none'
            print('Warning! cerebellum book is missing.')

    # Exit if options are none.
    if bookTypeOption == 'none' and evalTypeOption == 'none':
        print('Warning! options were not defined. Nothing has been processed.')
        sys.exit(1)
        
    # Delete existing output file.
    DeleteFile(outputFile)
        
    # Convert options to dict
    options = {'-book': bookTypeOption, '-eval': evalTypeOption}

    # Create an object of class Analyze.
    g = Analyze(inputFile, outputFile, engineName, **options)

    # Print engine id name.
    g.PrintEngineIdName()

    # Call method Annotate of class Analyze to annotate the game.
    g.Annotate()      

    print('Done!!\n')    

if __name__ == "__main__":
    main(sys.argv[1:])
