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
TEST_SEARCH_SCORE = 100000
TEST_SEARCH_DEPTH = 1000
EPD_FILE = 1
PGN_FILE = 2

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
        Quit program if input file type is not epd or pgn
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

    # If file is not epd or pgn
    if not infn.endswith('.epd') and not infn.endswith('.pgn'):
        print('Error! %s is not an epd or pgn file' %(infn))
        sys.exit(1)

def EvaluateOptions(opt):
    """ Convert opt list to dict and returns it """
    return dict([(k, v) for k, v in zip(opt[::2], opt[1::2])])

def GetOptionValue(opt, optName, var):
    """ Returns value of opt dict given the key """
    if opt.has_key(optName):
        var = opt.get(optName)
        if optName == '-movetime':
            var = int(var)
        elif optName == '-enghash':
            var = int(var)
        elif optName == '-engthreads':
            var = int(var)
        elif optName == '-movestart':
            var = int(var)
    return var

class Analyze():
    """ An object that will read and annotate games in a pgn file """
    def __init__(self, infn, outfn, eng, **opt):
        """ Initialize """
        self.infn = infn
        self.outfn = outfn
        self.eng = eng
        self.bookOpt = opt['-book']
        self.evalOpt = opt['-eval']
        self.moveTimeOpt = opt['-movetime']
        self.engHashOpt = opt['-enghash']
        self.engThreadsOpt = opt['-engthreads']
        self.moveStartOpt = opt['-movestart']
        self.writeCnt = 0
        self.isCereMoveFound = False
        self.engIdName = self.GetEngineIdName()

    def UciToSanMove(self, pos, uciMove):
        """ Returns san move given uci move """
        board = chess.Board(pos)
        board.push(chess.Move.from_uci(uciMove))
        sanMove = board.san(board.pop())
        return sanMove

    def PrintEngineIdName(self):
        """ Prints engine id name """
        print('Engine name: %s' %(self.engIdName))

    def GetMoveNag(self, side, posScore, engScore):
        """ Returns ??, ?, ?! depending on the player score and analyzing engine score.
            posScore is the score of the move in the game, in pawn unit.
            engScore is the score of the move suggested by the engine, in pawn unit.
            Positive score is better for white and negative score is better for black, (WPOV).
            Scoring range from white's perspective:
            Blunder: posScore < -1.50
            Mistake: posScore >= -1.50 and posScore < -0.75
            Dubious: posScore >= -0.75 and posScore < -0.15
            Even   : posScore >= -0.15 and posScore <= +0.15
            Special condition:
            1. If engine score is winning but player score is not winning,
            consider this as a mistake.
            Mistake: engScore > +1.50 and posScore < +1.50
        """
        # Convert the posScore and engScore to side POV
        # to easier calculate the move NAG = Numeric Annotation Glyphs.
        if not side:
            posScore = -1 * posScore
            engScore = -1 * engScore

        # Set default NAG, GUI will not display this.
        moveNag = '$0'
        
        # Blunder ??
        if posScore < -1.50 and engScore >= -1.50:
            moveNag = '$4'
            
        # Mistake ?
        elif posScore < -0.75 and engScore >= -0.75:
            moveNag = '$2'
            
        # Dubious ?!
        elif posScore < -0.15 and engScore >= -0.15:
            moveNag = '$6'

        # Mistake ? if engScore is winning and posScore is not winning
        elif engScore > +1.50 and posScore <= +1.50:
            moveNag = '$2'
        return moveNag            

    def WriteMovesOnly(self, side, moveNumber, sanMove):
        """ Write moves only in the output file """
        # Write the moves
        with open(self.outfn, 'a+') as f:
            if side:
                f.write('%d. %s ' %(moveNumber, sanMove))
            else:
                f.write('%s ' %(sanMove))

    def WriteMovesWithScore(self, side, moveNumber, sanMove, posScore, engMove, engScore):
        """ Write moves with score in the output file """
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                if sanMove != engMove:
                    moveNag = self.GetMoveNag(side, posScore, engScore)                       

                    # Write moves and comments
                    f.write('%d. %s %s {%+0.2f} (%d. %s {%+0.2f - %s})' %(moveNumber, sanMove, moveNag, posScore,
                                                                          moveNumber, engMove, engScore, self.engIdName))
                else:                    
                    f.write('%d. %s {%+0.2f} ' %(moveNumber, sanMove, posScore))
            else:
                if sanMove != engMove:
                    moveNag = self.GetMoveNag(side, posScore, engScore)

                    # Write moves and comments  
                    f.write('%d... %s %s {%+0.2f} (%d... %s {%+0.2f - %s})' %(moveNumber, sanMove, moveNag, posScore,
                                                                           moveNumber, engMove, engScore, self.engIdName))
                else:
                    f.write('%s {%+0.2f} ' %(sanMove, posScore))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
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

    def WriteMovesWithScoreAndBookMove(self, side, moveNumber, sanMove, bookMove, posScore, engMove, engScore):
        """ Write moves with score and book moves in the output file """
        bookComment = 'cerebellum book'
        
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                if sanMove != engMove:
                    moveNag = self.GetMoveNag(side, posScore, engScore)   

                    # Write moves and comments
                    f.write('%d. %s %s {%+0.2f} (%d. %s {%s}) (%d. %s {%+0.2f - %s}) ' %(moveNumber, sanMove, moveNag, posScore,
                                                                                      moveNumber, bookMove, bookComment,
                                                                                      moveNumber, engMove, engScore, self.engIdName))
                else:
                    f.write('%d. %s {%+0.2f} (%d. %s {%s}) ' %(moveNumber, sanMove, posScore, moveNumber, bookMove, bookComment))
            else:
                if sanMove != engMove:
                    moveNag = self.GetMoveNag(side, posScore, engScore)

                    # Write moves and comments
                    f.write('%d... %s %s {%+0.2f} (%d... %s {%s}) (%d... %s {%+0.2f - %s}) ' %(moveNumber, sanMove, moveNag, posScore,
                                                                                       moveNumber, bookMove, bookComment,
                                                                                       moveNumber, engMove, engScore, self.engIdName))
                else:
                    f.write('%d... %s {%+0.2f} (%d... %s {%s}) ' %(moveNumber, sanMove, posScore, moveNumber, bookMove, bookComment))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
                    self.writeCnt = 0
                    f.write('\n')        

    def WriteMoves(self, side, fmvn, sanMove, bookMove, posScore, isGameOver, engMove, engScore):
        """ Write moves and comments to the output file """
        # If game is over [mate, stalemate] just print the move.
        if isGameOver or fmvn < self.moveStartOpt:
            self.WriteMovesOnly(side, fmvn, sanMove)
            return

        # Write rest of moves and comments.
        # (1) With score
        if not self.isCereMoveFound and self.evalOpt != 'none':
            self.WriteMovesWithScore(side, fmvn, sanMove, posScore, engMove, engScore)

        # (2) With book move
        elif self.isCereMoveFound and self.evalOpt == 'none':
            self.WriteMovesWithBookMove(side, fmvn, sanMove, bookMove)

        # (3) With score and book move
        elif self.isCereMoveFound and self.evalOpt != 'none':
            self.WriteMovesWithScoreAndBookMove(side, fmvn, sanMove, bookMove, posScore, engMove, engScore)
            
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

    def GetStaticEvalAfterMove(self, pos):
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

    def GetSearchScoreBeforeMove(self, pos, side):
        """ Returns search bestmove and score from the engine. """

        # Initialize
        scoreCp = TEST_SEARCH_SCORE

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
        p.stdin.write("setoption name Hash value %d\n" %(self.engHashOpt))
        p.stdin.write("setoption name Threads value %d\n" %(self.engThreadsOpt))
                
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
        p.stdin.write("go movetime %d\n" %(self.moveTimeOpt))

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
                bestMove = line.split()[1]
                break
                
        # Quit the engine
        p.stdin.write('quit\n')
        p.communicate()        
        assert scoreCp != TEST_SEARCH_SCORE, 'Error, search failed to return a score.'

        # Convert uci move to san move format.
        bestMove = self.UciToSanMove(pos, bestMove)

        # Convert score from the point of view of white.
        if not side:
            scoreCp = -1 * scoreCp

        # Convert the score to pawn unit in float type
        scoreP = float(scoreCp)/100.0
        return bestMove, scoreP

    def GetSearchScoreAfterMove(self, pos, side):
        """ Returns search bestmove and score from the engine. """

        # Initialize
        scoreCp = TEST_SEARCH_SCORE

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
        p.stdin.write("setoption name Hash value %d\n" %(self.engHashOpt))
        p.stdin.write("setoption name Threads value %d\n" %(self.engThreadsOpt))
                
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
        p.stdin.write("go movetime %d\n" %(self.moveTimeOpt))

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
        assert scoreCp != TEST_SEARCH_SCORE, 'Error, search failed to return a score.'

        # Invert the score sign because we analyze the position after the move.
        scoreCp = -1 * scoreCp

        # Convert score from the point of view of white.
        if not side:
            scoreCp = -1 * scoreCp

        # Convert the score to pawn unit in float type
        scoreP = float(scoreCp)/100.0
        return scoreP

    def GetEpdAnalysis(self, pos):
        """ Returns acd, acs, bm, ce and Ae op codes. """

        # Initialize
        bestMove = None
        engineIdName = self.eng[0:-4]
        scoreCp = TEST_SEARCH_SCORE
        depthSearched = TEST_SEARCH_DEPTH

        # Run the engine.
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

        # Set Hash and Threads options to uci engine
        p.stdin.write("setoption name Hash value %d\n" %(self.engHashOpt))
        p.stdin.write("setoption name Threads value %d\n" %(self.engThreadsOpt))
                
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
        p.stdin.write("go movetime %d\n" %(self.moveTimeOpt))

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
            if 'depth ' in line:
                splitStr = line.split()
                depthIndex = splitStr.index('depth')
                depthSearched = int(splitStr[depthIndex + 1])                     

            # Break search when we receive bestmove
            if 'bestmove ' in line:
                bestMove = line.split()[1]
                break
                
        # Quit the engine
        p.stdin.write('quit\n')
        p.communicate()

        # Convert uci move to san move format.
        bestMove = self.UciToSanMove(pos, bestMove)
        
        assert scoreCp != TEST_SEARCH_SCORE, 'Error!, search failed to return a score.'
        assert bestMove is not None, 'Error! seach failed to return a move.'
        return depthSearched, self.moveTimeOpt/1000, bestMove, scoreCp, engineIdName

    def AnnotatePgn(self):
        """ Parse the pgn file and annotate the games """
        # Get engine id name for the Annotator tag.
        engIdName = self.engIdName

        # Disable bookOpt if engine is not Brainfish.
        if self.bookOpt == 'cerebellum':
            brainFishEngine = self.engIdName
            if 'Brainfish' not in brainFishEngine:
                self.bookOpt = 'none'
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
            if self.evalOpt == 'static':
                with open(self.outfn, 'a+') as f:
                    f.write('{Move comments are from engine static evaluation.}\n')
            elif self.evalOpt == 'search':
                with open(self.outfn, 'a+') as f:
                    f.write('{Hash %dmb, Threads %d, engine search score @ %0.1fs/pos}\n'\
                            %(self.engHashOpt, self.engThreadsOpt, self.moveTimeOpt/1000.0))

            # Save result to be written later as game termination marker.
            res = game.headers['Result']

            # Loop thru the moves within this game.
            gameNode = game        
            while gameNode.variations:
                side = gameNode.board().turn
                fmvn = gameNode.board().fullmove_number             
                nextNode = gameNode.variation(0)                      
                sanMove = nextNode.san()

                # (0) Don't start the engine analysis when fmvn is below self.moveStartOpt
                if fmvn < self.moveStartOpt:
                    self.isCereMoveFound = False
                    self.WriteMoves(side, fmvn, sanMove, None, None, False, None, None)
                    gameNode = nextNode
                    continue                    

                # (1) Try to get a cerebellum book move.
                self.isCereMoveFound = False
                cereBookMove = None
                if self.bookOpt == 'cerebellum' and not isCereEnd:
                    # Use FEN before a move.
                    fenBeforeMove = gameNode.board().fen()
                    cereBookMove, self.isCereMoveFound = self.GetCerebellumBookMove(fenBeforeMove)

                    # End trying to find cerebellum book move beyond BOOK_MOVE_LIMIT.
                    if not self.isCereMoveFound and fmvn > BOOK_MOVE_LIMIT:
                        isCereEnd = True

                # (2) Get the score of the position after a move.
                posScore = None
                if self.evalOpt == 'static':
                    fenAfterMove = nextNode.board().fen()
                    staticScore = self.GetStaticEvalAfterMove(fenAfterMove)
                    posScore = staticScore
                elif self.evalOpt == 'search':
                    fenAfterMove = nextNode.board().fen()
                    searchScore = self.GetSearchScoreAfterMove(fenAfterMove, side)
                    posScore = searchScore

                # (2.1) Search the engine score and move recommendations.
                engBestMove, engBestScore = self.GetSearchScoreBeforeMove(gameNode.board().fen(), side)
                    
                # If game is over by checkmate and stalemate after a move              
                isGameOver = nextNode.board().is_checkmate() or nextNode.board().is_stalemate()
                
                # (3) Write moves and comments.
                self.WriteMoves(side, fmvn, sanMove, cereBookMove, posScore, isGameOver, engBestMove, engBestScore)

                # Read the next position.
                gameNode = nextNode

            # Write the result and a space between games.
            with open(self.outfn, 'a') as f:
                f.write('%s\n\n' %(res))

            # Read the next game.
            game = chess.pgn.read_game(pgnHandle)

        # Close the file handle.
        pgnHandle.close()

    def AnnotateEpd(self):
        """ Annotate epd file with bm, ce, acs, acd, and Ae op codes
            Ae - analyzing engine, a special op code for this script
        """
        cntEpd = 0
        # Open the epd file for reading.
        with open(self.infn, 'r') as f:
            for lines in f:
                cntEpd += 1
                # Remove white space at beginning and end of lines.
                epdLine = lines.strip()

                # Get only first 4 fields [pieces side castle_flag ep_sq]
                epdLineSplit = epdLine.split()
                epd = ' '.join(epdLineSplit[0:4])                

                # Add hmvc and fmvn to create a FEN for the engine
                fen = epd + ' 0 1'

                # If this position has no legal move we skip it.
                b = chess.Board(fen)
                isGameOver = b.is_checkmate() or b.is_stalemate()
                if isGameOver:
                    print('Warning! epd \"%s\"\nhas no legal move - skipped.\n' %(epd))
                    continue

                # Show progress in console
                print('epd %d: %s' %(cntEpd, epd))

                # Get analysis
                acd, acs, bm, ce, Ae = self.GetEpdAnalysis(fen)

                # Show progress in console
                print('bm: %s' %(bm))
                print('ce: %+d\n' %(ce))

                # Save to output file the epd analysis
                with open(self.outfn, 'a') as f1:
                    f1.write('%s acd %d; acs %d; bm %s; ce %+d; Ae \"%s\";\n'\
                             %(epd, acd, acs, bm, ce, Ae))

def main(argv):
    """ start """
    PrintProgram()

    # Initialize
    inputFile = 'src.pgn'
    outputFile = 'out_src.pgn'
    engineName = 'engine.exe'
    bookOption = 'none'   # ['none', 'cerebellum', 'polyglot']
    evalOption = 'static' # ['none', 'static', 'search']
    cereBookFile = 'Cerebellum_Light.bin'
    moveTimeOption = 0
    engHashOption = 32 # 32 mb
    engThreadsOption = 1
    moveStartOption = 8
    
    # Evaluate the command line options.
    options = EvaluateOptions(argv)
    if len(options):
        inputFile = GetOptionValue(options, '-infile', inputFile)
        outputFile = GetOptionValue(options, '-outfile', outputFile)
        engineName = GetOptionValue(options, '-eng', engineName)
        bookOption = GetOptionValue(options, '-book', bookOption)
        evalOption = GetOptionValue(options, '-eval', evalOption)
        moveTimeOption = GetOptionValue(options, '-movetime', moveTimeOption)
        engHashOption = GetOptionValue(options, '-enghash', engHashOption)
        engThreadsOption = GetOptionValue(options, '-engthreads', engThreadsOption)
        moveStartOption = GetOptionValue(options, '-movestart', moveStartOption)

    # Check input, output and engine files.
    CheckFiles(inputFile, outputFile, engineName)
    
    # Disable use of cerebellum book when Cerebellum_Light.bin is missing.
    if bookOption == 'cerebellum':
        if not os.path.isfile(cereBookFile):
            bookOption = 'none'
            print('Warning! cerebellum book is missing.')

    # Determine if input file is epd or pgn or None.
    if inputFile.endswith('.epd'):
        fileType = EPD_FILE
    elif inputFile.endswith('.pgn'):
        fileType = PGN_FILE
    
    # Exit if book and eval options are none and file type is pgn.
    if bookOption == 'none' and evalOption == 'none' and fileType == PGN_FILE:
        print('Error! options were not defined. Nothing has been processed.')
        sys.exit(1)

    # Exit if file type is epd and move time is 0.
    if fileType == EPD_FILE and moveTimeOption <= 0:
        print('Error! movetime is zero.')
        sys.exit(1)        
        
    # Delete existing output file.
    DeleteFile(outputFile)

    # Check Limits
    if engThreadsOption <= 0:
        engThreadsOption = 1
        
    # Convert options to dict
    options = {'-book': bookOption,
               '-eval': evalOption,
               '-movetime': moveTimeOption,
               '-enghash': engHashOption,
               '-engthreads': engThreadsOption,
               '-movestart': moveStartOption
               }

    # Create an object of class Analyze.
    g = Analyze(inputFile, outputFile, engineName, **options)

    # Print engine id name.
    g.PrintEngineIdName()

    # If input file is epd
    if fileType == EPD_FILE:
        g.AnnotateEpd()
    # Else if input file is pgn
    elif fileType == PGN_FILE:
        g.AnnotatePgn()
    # else would not reach here because it is checked under CheckFiles()

    print('Done!!\n')    

if __name__ == "__main__":
    main(sys.argv[1:])
