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
import math
import chess
from chess import pgn

# Constants
APP_NAME = 'Chess Artist'
APP_VERSION = '0.2.0'
BOOK_MOVE_LIMIT = 30
BOOK_SEARCH_TIME = 200
MAX_SCORE = 32000
TEST_SEARCH_SCORE = 100000
TEST_SEARCH_DEPTH = 1000
EPD_FILE = 1
PGN_FILE = 2
DRAW_SCORE = +0.15
SLIGHT_SCORE = +0.75
MODERATE_SCORE = +1.50
DECISIVE_SCORE = +3.0
COMPLEXITY_MINIMUM_TIME = 2000
DEFAULT_HASH = 32
DEFAULT_THREADS = 1

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
        self.moveStartOpt = opt['-movestart']
        self.jobOpt = opt['-job']
        self.engOpt = opt['-engoptions']
        self.writeCnt = 0
        self.engIdName = self.GetEngineIdName()

    def UciToSanMove(self, pos, uciMove):
        """ Returns san move given uci move """
        board = chess.Board(pos)
        board.push(chess.Move.from_uci(uciMove))
        sanMove = board.san(board.pop())
        return sanMove

    def PrintEngineIdName(self):
        """ Prints engine id name """
        print('Analyzing engine: %s' %(self.engIdName))

    def GetGoodNag(self, side, posScore, engScore,
                   complexityNumber, moveChanges):
        """ Returns !!, !, !? depending on the player score, analyzing
            engine score, complexity number and pv move changes.
        """
        # Convert the posScore and engScore to side POV
        # to easier calculate the move NAG = Numeric Annotation Glyphs.
        if not side:
            posScore = -1 * posScore
            engScore = -1 * engScore

        # Set default NAG, GUI will not display this.
        moveNag = '$0'

        # Adjust !! move changes threshold
        veryGoodMoveChangesThreshold = 4
        if self.moveTimeOpt >= 180000:
            veryGoodMoveChangesThreshold += 2
        elif self.moveTimeOpt >= 60000:
            veryGoodMoveChangesThreshold += 1

        # (0) Position score after a move should not be winning
        if posScore >= DECISIVE_SCORE:
            return moveNag

        # (0.1) Position score after a move should also not be inferior
        if posScore < -SLIGHT_SCORE:
            return moveNag

        # (1) Very good !!
        if moveChanges >= veryGoodMoveChangesThreshold\
                and complexityNumber >= 15 * veryGoodMoveChangesThreshold:
            moveNag = '$3'

        # (1.1) Very good !!, also for very high move changes
        elif moveChanges >= veryGoodMoveChangesThreshold + 2:
            moveNag = '$3'
            
        # (2) Good !
        elif moveChanges >= 3 and complexityNumber >= 35:
            moveNag = '$1'
            
        # (3) Interesting !?
        elif moveChanges >= 2:
            moveNag = '$5'

        # (3.1) Interesting !?, low pv move changes but has high
        # complexity number, meaning the engine changes its best move once
        # but at higher depths. The value 18 is applied with
        # stockfish engine in mind.
        elif moveChanges >= 1 and complexityNumber >= 18:
            moveNag = '$5'
        return moveNag

    def GetBadNag(self, side, posScore, engScore):
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
        if posScore < -MODERATE_SCORE and engScore >= -MODERATE_SCORE:
            moveNag = '$4'
            
        # Mistake ?
        elif posScore < -SLIGHT_SCORE and engScore >= -SLIGHT_SCORE:
            moveNag = '$2'
            
        # Dubious ?!
        elif posScore < -DRAW_SCORE and engScore >= -DRAW_SCORE:
            moveNag = '$6'

        # Mistake ? if engScore is winning and posScore is not winning
        elif engScore > MODERATE_SCORE and posScore <= MODERATE_SCORE:
            moveNag = '$2'

        # Mistake ? if posScore is too far from engScore by 0.50 or more
        elif engScore >= -MODERATE_SCORE and engScore - posScore >= +0.50:
            moveNag = '$2'

        # Exception, add ! if posScore > engScore
        if posScore >= -SLIGHT_SCORE and posScore > engScore:
            moveNag = '$1'

        # Exception, add !? if posScore == engScore
        elif posScore >= -SLIGHT_SCORE and posScore == engScore:
            moveNag = '$5'
        return moveNag

    def PreComment(self, side, engScore, posScore):
        """ returns a comment for the engine variation """
        if not side:
            engScore = -1 * engScore
            posScore = -1 * posScore
        varComment = ''
        if engScore - posScore > 5 * DRAW_SCORE:
            varComment = 'Excellent is'
        elif engScore - posScore > DRAW_SCORE:
            varComment = 'Better is'
        return varComment

    def WriteSanMove(self, side, moveNumber, sanMove):
        """ Write moves only in the output file """
        # Write the moves
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1
            if side:
                f.write('%d. %s ' %(moveNumber, sanMove))
            else:
                f.write('%s ' %(sanMove))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 4:
                    self.writeCnt = 0
                    f.write('\n')

    def WritePosScore(self, side, moveNumber, sanMove, posScore):
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

    def WritePosScoreEngMove(self, side, moveNumber,
                             sanMove, posScore, engMove,
                             engScore, complexityNumber, moveChanges,
                             pvLine, threatMove):
        """ Write moves with score and engMove in the output file """
        
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                if sanMove != engMove:
                    moveNag = self.GetBadNag(side, posScore, engScore)

                    # Add better is symbol before the engine variation
                    varComment = self.PreComment(side, engScore, posScore)

                    # Write moves and comments
                    f.write('%d. %s %s {%+0.2f} ({%s} %s {%+0.2f}) '\
                            %(moveNumber, sanMove, moveNag, posScore,
                              varComment, pvLine, engScore))
                else:
                    moveNag = self.GetGoodNag(side, posScore, engScore,
                                              complexityNumber, moveChanges)
                    if threatMove is None:
                        f.write('%d. %s %s {%+0.2f} ' %(moveNumber, sanMove,
                                                    moveNag, posScore))
                    else :
                        f.write('{, with the idea of %s} %d. %s %s {%+0.2f} ' %(threatMove,
                                        moveNumber, sanMove, moveNag, posScore))
            else:
                if sanMove != engMove:
                    moveNag = self.GetBadNag(side, posScore, engScore)

                    # Add better is symbol before the engine variation
                    varComment = self.PreComment(side, engScore, posScore)

                    # Write moves and comments  
                    f.write('%d... %s %s {%+0.2f} ({%s} %s {%+0.2f}) '\
                            %(moveNumber, sanMove, moveNag, posScore,
                              varComment, pvLine, engScore))
                else:
                    moveNag = self.GetGoodNag(side, posScore, engScore,
                                              complexityNumber, moveChanges)
                    if threatMove is None:
                        f.write('%s %s {%+0.2f} ' %(sanMove, moveNag, posScore))
                    else:
                        f.write('{, with the idea of %s} %s %s {%+0.2f} ' %(threatMove, sanMove, moveNag, posScore))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
                    self.writeCnt = 0
                    f.write('\n')

    def WriteBookMove(self, side, moveNumber, sanMove, bookMove):
        """ Write moves with book moves in the output file """
        bookComment = 'cerebellum'
        assert bookMove is not None
        
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                f.write('%d. %s (%d. %s {%s}) ' %(moveNumber, sanMove,
                                                  moveNumber, bookMove,
                                                  bookComment))
            else:
                f.write('%d... %s (%d... %s {%s}) ' %(moveNumber, sanMove,
                                                      moveNumber, bookMove,
                                                      bookComment))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
                    self.writeCnt = 0
                    f.write('\n')

    def WritePosScoreBookMove(self, side, moveNumber, sanMove,
                              bookMove, posScore):
        """ Write moves with score and book moves in the output file """
        bookComment = 'cerebellum'
        assert bookMove is not None
        
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                f.write('%d. %s {%+0.2f} (%d. %s {%s}) ' %(moveNumber, sanMove,
                                                        posScore, moveNumber,
                                                        bookMove, bookComment))
            else:
                f.write('%d... %s {%+0.2f} (%d... %s {%s}) ' %(moveNumber,
                                                        sanMove,
                                                        posScore, moveNumber,
                                                        bookMove, bookComment))
                
                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
                    self.writeCnt = 0
                    f.write('\n') 

    def WritePosScoreBookMoveEngMove(self, side, moveNumber, sanMove, bookMove,
                                     posScore, engMove, engScore,
                                     complexityNumber, moveChanges,
                                     pvLine, threatMove):
        """ Write moves with score and book moves in the output file """
        bookComment = 'cerebellum'
        assert bookMove is not None
        
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                if sanMove != engMove:
                    moveNag = self.GetBadNag(side, posScore, engScore)

                    # Add better is symbol before the engine variation
                    varComment = self.PreComment(side, engScore, posScore)

                    # Write moves and comments
                    f.write('%d. %s %s {%+0.2f} (%d. %s {%s}) ({%s} %s {%+0.2f}) '\
                            %(moveNumber, sanMove, moveNag, posScore,
                              moveNumber, bookMove, bookComment,
                              varComment, pvLine, engScore))
                else:
                    moveNag = self.GetGoodNag(side, posScore, engScore,
                                              complexityNumber, moveChanges)
                    if threatMove is not None:
                        f.write('{, with the idea of %s} %d. %s {%+0.2f} (%d. %s {%s}) ' %(threatMove,
                                        moveNumber, sanMove, posScore, moveNumber, bookMove, bookComment))
                    else:
                        f.write('%d. %s {%+0.2f} (%d. %s {%s}) ' %(moveNumber,
                                                sanMove, posScore, moveNumber,
                                                bookMove, bookComment))
            else:
                if sanMove != engMove:
                    moveNag = self.GetBadNag(side, posScore, engScore)

                    # Add better is symbol before the engine variation
                    varComment = self.PreComment(side, engScore, posScore)

                    # Write moves and comments
                    f.write('%d... %s %s {%+0.2f} (%d... %s {%s}) ({%s} %s {%+0.2f}) '\
                            %(moveNumber, sanMove, moveNag, posScore,
                              moveNumber, bookMove, bookComment,
                              varComment, pvLine, engScore))
                else:
                    moveNag = self.GetGoodNag(side, posScore, engScore,
                                              complexityNumber, moveChanges)
                    if threatMove is not None:
                        f.write('{, with the idea of %s} %d... %s {%+0.2f} (%d... %s {%s}) ' %(threatMove,
                                        moveNumber, sanMove, posScore, moveNumber, bookMove, bookComment))
                    else:
                        f.write('%d... %s {%+0.2f} (%d... %s {%s}) ' %(moveNumber,
                                        sanMove, posScore, moveNumber, bookMove, bookComment))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
                    self.writeCnt = 0
                    f.write('\n')

    def WriteBookMoveEngMove(self, side, moveNumber, sanMove, bookMove,
                                            engMove, engScore, pvLine):
        """ Write moves with book moves and eng moves in the output file """
        bookComment = 'cerebellum'
        assert bookMove is not None
        
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                if sanMove != engMove:
                    # Write moves and comments
                    f.write('%d. %s (%d. %s {%s}) (%s {%+0.2f}) '\
                            %(moveNumber, sanMove, moveNumber, bookMove,
                              bookComment, pvLine, engScore))
                else:
                    f.write('%d. %s (%d. %s {%s}) '\
                            %(moveNumber, sanMove,
                              moveNumber, bookMove, bookComment))
            else:
                if sanMove != engMove:
                    
                    # Write moves and comments
                    f.write('%d... %s (%d... %s {%s}) (%s {%+0.2f}) '\
                            %(moveNumber, sanMove, moveNumber,
                              bookMove, bookComment, pvLine,
                              engScore))
                else:
                    f.write('%d... %s (%d... %s {%s}) '\
                            %(moveNumber, sanMove,
                              moveNumber, bookMove, bookComment))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
                    self.writeCnt = 0
                    f.write('\n')

    def WriteEngMove(self, side, moveNumber, sanMove, engMove, engScore, pvLine):
        """ Write moves with eng moves in the output file """
        
        # Write the move and comments
        with open(self.outfn, 'a+') as f:

            # If side to move is white
            if side:
                if sanMove != engMove:
                    # Write moves and comments
                    f.write('%d. %s (%s {%+0.2f}) ' %(moveNumber, sanMove,
                                            pvLine, engScore))
                else:
                    f.write('%d. %s ' %(moveNumber, sanMove))
            else:
                if sanMove != engMove:
                    
                    # Write moves and comments
                    f.write('%d... %s (%s {%+0.2f}) ' %(moveNumber,
                                                sanMove, pvLine, engScore))
                else:
                    f.write('%d... %s ' %(moveNumber, sanMove))

    def WriteNotation(self, side, fmvn, sanMove, bookMove, posScore,
                      isGameOver, engMove, engScore, complexityNumber,
                      moveChanges, pvLine, threatMove):
        """ Write moves and comments to the output file """
        # (0) If game is over [mate, stalemate] just print the move.
        if isGameOver:
            self.WriteSanMove(side, fmvn, sanMove)
            return

        # (1) Write sanMove, posScore
        isWritePosScore = posScore is not None and\
                       bookMove is None and\
                       engMove is None
        if isWritePosScore:
            self.WritePosScore(side, fmvn, sanMove, posScore)
            return

        # (2) Write sanMove, posScore, bookMove
        isWritePosScoreBook = posScore is not None and\
                              bookMove is not None and\
                              engMove is None
        if isWritePosScoreBook:
            self.WritePosScoreBookMove(side, fmvn, sanMove, bookMove, posScore)
            return

        # (3) Write sanMove, posScore and engMove
        isWritePosScoreEngMove = posScore is not None and\
                       bookMove is None and\
                       engMove is not None
        if isWritePosScoreEngMove:
            self.WritePosScoreEngMove(side, fmvn, sanMove, posScore, engMove,
                                      engScore, complexityNumber,
                                      moveChanges, pvLine, threatMove)
            return

        # (4) Write sanMove, posScore, bookMove and engMove
        isWritePosScoreBookEngMove = posScore is not None and\
                              bookMove is not None and\
                              engMove is not None
        if isWritePosScoreBookEngMove:
            self.WritePosScoreBookMoveEngMove(side, fmvn, sanMove, bookMove,
                                              posScore, engMove, engScore,
                                              complexityNumber, moveChanges,
                                              pvLine, threatMove)
            return

        # (5) Write sanMove, bookMove
        isWriteBook = posScore is None and\
                      bookMove is not None and\
                      engMove is None
        if isWriteBook:
            self.WriteBookMove(side, fmvn, sanMove, bookMove)
            return

        # (6) Write sanMove, bookMove and engMove
        isWriteBookEngMove = posScore is None and\
                              bookMove is not None and\
                              engMove is not None
        if isWriteBookEngMove:
            self.WriteBookMoveEngMove(side, fmvn, sanMove, bookMove, engMove,
                                      engScore, pvLine)
            return

        # (7) Write sanMove, engMove
        isWriteEngMove = posScore is None and\
                              bookMove is None and\
                              engMove is not None
        if isWriteEngMove:
            self.WriteEngMove(side, fmvn, sanMove, engMove, engScore, pvLine)
            return

        # (8) Write sanMove only
        if posScore is None and bookMove is None:
            self.WriteSanMove(side, fmvn, sanMove)
            return            
            
    def MateDistanceToValue(self, d):
        """ Returns value given distance to mate """
        value = 0
        if d < 0:
            value = -2*d - MAX_SCORE
        elif d > 0:
            value = MAX_SCORE - 2*d + 1
        return value

    def GetMaterialInfo(self, fen):
        """ Returns number of queens, pawns and white and
            black material. Material is calculated based
            on q=9, r=5, b=3, n=3
        """
        # Get piece field of fen
        pieces = fen.split()[0]

        # Count pieces
        Q = pieces.count('Q')
        q = pieces.count('q')
        R = pieces.count('R')
        r = pieces.count('r')
        B = pieces.count('B')
        b = pieces.count('b')
        N = pieces.count('N')
        n = pieces.count('n')
        P = pieces.count('P')
        p = pieces.count('p')

        # Get piece values except pawns
        wmat = Q*9 + R*5 + B*3 + N*3
        bmat = q*9 + r*5 + b*3 + b*3

        # Get queen and pawn counts
        queens = Q+q
        pawns = P+p
        return wmat, bmat, queens, pawns
    
    def GetEngineIdName(self):
        """ Returns the engine id name """
        engineIdName = self.eng[0:-4]

        # Run the engine
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

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
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

        # Send command to engine.
        p.stdin.write("uci\n")

        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "uciok" in line:
                break

        # Set the path of Brainfish cerebellum book. Make sure the Brainfish
        # engine, the script and the cerebellum book are on the same directory.
        p.stdin.write("setoption name BookPath value Cerebellum_Light.bin\n")

        # Set threads to 1.
        p.stdin.write("setoption name Threads value 1\n")
                
        # Send command to engine.
        p.stdin.write("isready\n")
        
        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "readyok" in line:
                break
                
        # Send commands to engine.
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

        # If we did not get info depth from the engine
        # then the bestmove is from the book.
        if not isInfoDepth:
            # Convert uci move to san move format.
            bestMove = self.UciToSanMove(pos, bestMove)
            return bestMove
        return None

    def GetEngineOptionValue(self, optionName):
        """ Returns value str of option given option name """
        engOptionValue = self.engOpt
        if engOptionValue == 'none':
            # Return defaults
            if 'Hash' in optionName:
                return str(DEFAULT_HASH)
            elif 'Threads' in optionName:
                return str(DEFAULT_THREADS)

        # If there are more than 1 options defined
        if ',' in engOptionValue:
            engOptionValueList = engOptionValue.split(',')
            for n in engOptionValueList:
                value = n.strip()
                if optionName in value:
                    return value.split()[2]
        else:
            value = engOptionValue.strip()
            if optionName in value:
                return value.split()[2]

        return None

    def SetEngineOptions(self, p, engOptionValue):
        """ Set engine options for uci engines """
        # If nothing is defined, means that the user relies on the default
        if engOptionValue == 'none':
            return            
        
        # Convert engOptionValue to list
        if ',' in engOptionValue:
            engOptionValueList = engOptionValue.split(',')
            for n in engOptionValueList:
                value = n.strip()

                # Verify threads is 1 or more
                if 'Threads ' in value:
                    assert int(value.split()[2]) >= 1,\
                    'Error! option Threads was set below 1'

                # Verify Hash is 1 or more and not more than 32 GB
                if 'Hash ' in value:
                    hashValue = int(value.split()[2])
                    assert hashValue >= 1 and hashValue <= 32000,\
                    'Error! option Hash was set improperly'

                # Set the value
                p.stdin.write("setoption name %s\n" %(value))
        else:
            value = engOptionValue.strip()
            p.stdin.write("setoption name %s\n" %(value))

    def GetStaticEvalAfterMove(self, pos):
        """ Returns static eval by running the engine,
            setup position pos and send eval command.
        """
        score = TEST_SEARCH_SCORE

        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

        # Send command to engine.
        p.stdin.write("uci\n")

        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "uciok" in line:
                break

        # Set engine options
        self.SetEngineOptions(p, self.engOpt)
                
        # Send command to engine.
        p.stdin.write("isready\n")
        
        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "readyok" in line:
                break
                
        # Send commands to engine.
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
        assert score != TEST_SEARCH_SCORE,\
               'Error! something is wrong in static eval calculation.'
        return score

    def GetThreatMove(self, pos):
        """ Returns threat move after pushing a null move
            and get the engine best move
        """

        # Initialize
        bestMove = None

        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

        # Send command to engine.
        p.stdin.write("uci\n")

        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "uciok" in line:
                break

        # Set engine options
        self.SetEngineOptions(p, self.engOpt)
                
        # Send command to engine.
        p.stdin.write("isready\n")
        
        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "readyok" in line:
                break

        # Push null move
        b = chess.Board(pos)
        b.push(chess.Move.null())
        newPos = b.fen()
        
        # Send commands to engine.
        p.stdin.write("position fen " + newPos + "\n")
        p.stdin.write("go movetime %d\n" %(self.moveTimeOpt))

        # Parse the output and extract the engine search score.
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            if 'bestmove ' in line:
                bestMove = line.split()[1]
                break
                
        # Quit the engine
        p.stdin.write('quit\n')
        p.communicate()

        # Convert uci move to san move format.
        if bestMove is not None:
            bestMove = self.UciToSanMove(newPos, bestMove)
        
        return bestMove

    def GetSearchScoreBeforeMove(self, pos, side):
        """ Returns bestmove, pv, score complexity number of the position
            and root move changes. """

        # Initialize
        scoreCp = TEST_SEARCH_SCORE

        pvLine = None
        searchDepth = 0
        savedMove = []
        complexityNumber = 0
        moveChanges = 0;
        isGetComplexityNumber = self.jobOpt == 'analyze' and\
                                self.moveTimeOpt >= COMPLEXITY_MINIMUM_TIME

        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

        # Send command to engine.
        p.stdin.write("uci\n")

        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "uciok" in line:
                break

        # Set engine options
        self.SetEngineOptions(p, self.engOpt)
                
        # Send command to engine.
        p.stdin.write("isready\n")
        
        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "readyok" in line:
                break
                
        # Send commands to engine.
        p.stdin.write("position fen " + pos + "\n")
        p.stdin.write("go movetime %d\n" %(self.moveTimeOpt))

        # Parse the output and extract the engine search score.
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()                

            # Save pv move per depth
            if isGetComplexityNumber:
                if 'info depth ' in line and 'pv ' in line and not\
                   'upperbound' in line and not 'lowerbound' in line:
                    
                    # Get the depth
                    splitLine = line.split()
                    searchDepth = int(splitLine[splitLine.index('depth')+1])

                    # Get the move and save it
                    pvMove = splitLine[splitLine.index('pv')+1].strip()
                    savedMove.append([searchDepth, pvMove])

            # Save pv line
            if 'info depth ' in line and 'pv ' in line and not\
                   'upperbound' in line and not 'lowerbound' in line:
                splitLine = line.split()
                pvIndex = splitLine.index('pv')
                pvLine = splitLine[pvIndex+1:pvIndex+6]
                    
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

        # Get the first move of the pvLine, make sure the this move
        # is the same with the bestMove, if not then set bestMove as pvLine
        firstPvMove = pvLine[0].strip()
        if firstPvMove != bestMove:
            pvLine = []
            pvLine.append(bestMove)

        # Convert pv line to SAN
        try:
            board = chess.Board(pos)
            pvLineSan = \
                board.variation_san([chess.Move.from_uci(m) for m in pvLine])
        except:
            print('Warning, there is error in pvLine')
            print('pvLine: %s' %(pvLine))

        # Get complexity number and moveChanges count
        if isGetComplexityNumber:
            complexityNumber, moveChanges =\
                              self.GetComplexityNumber(savedMove, pos)

        # Convert uci move to san move format.
        bestMove = self.UciToSanMove(pos, bestMove)

        # Convert score from the point of view of white.
        if not side:
            scoreCp = -1 * scoreCp

        # Convert the score to pawn unit in float type
        scoreP = float(scoreCp)/100.0
        return bestMove, scoreP, complexityNumber, moveChanges, pvLineSan

    def GetComplexityNumber(self, savedMove, fen):
        """ Returns complexity number and move changes counts """
        complexityNumber, moveChanges = 0, 0
        for n in savedMove:
            depth = n[0]
            if depth >= 10:
                if n[1] != lastMove and depth != lastDepth:
                    complexityNumber += n[0]
                    moveChanges += 1
            lastDepth = depth
            lastMove = n[1]

        # Increase complexityNumber when there are queens, and high mat values
        if complexityNumber:
            wmat, bmat, queens, pawns = self.GetMaterialInfo(fen)
            if queens > 0:
                complexityNumber += 5
            if wmat + bmat >= 46 and pawns <= 14:
                complexityNumber += 5

        # Reduce complexity number when center is closed
        if self.IsCenterClosed(fen):
            complexityNumber -= 10
            if complexityNumber < 0:
                complexityNumber = 0
                
        return complexityNumber, moveChanges

    def IsCenterClosed(self, fen):
        """ Given fen check if center is closed. Center is closed
            when there are white pawns at d4 and e5, and there are
            black pawns at e6 and d5 or there are white pawns in
            e4 and d5 and there are black pawns at d6 and e5. """
        bb = chess.BaseBoard(fen.split()[0])

        # Case 1: wpawn at e5/d4 and bpawn at d5/e6 pattern
        
        # Find wpawn at e5/d4
        e5Found, d4Found = False, False
        wpSqList = bb.pieces(chess.PAWN, chess.WHITE)
        if chess.E5 in wpSqList:
            e5Found = True
        if chess.D4 in wpSqList:
            d4Found = True

        # We only check the black pattern when we found the white pattern
        # Find bpawn at d5/e6
        if e5Found and d4Found:
            d5Found, e6Found = False, False
            bpSqList = bb.pieces(chess.PAWN, chess.BLACK)
            if chess.D5 in bpSqList:
                d5Found = True
            if chess.E6 in bpSqList:
                e6Found = True

            # Return early if we found a pattern
            if d5Found and e6Found:
                return True

        # Case 2: wpawn at d5/e4 and bpawn at d6/e5 pattern

        # Find wpawn at d5/e4
        d5Found, e4Found = False, False
        wpSqList = bb.pieces(chess.PAWN, chess.WHITE)
        if chess.D5 in wpSqList:
            d5Found = True
        if chess.E4 in wpSqList:
            e4Found = True

        # We only check the black pattern when we found the white pattern
        # Find bpawn at d6/e5
        if d5Found and e4Found:
            d6Found, e5Found = False, False
            bpSqList = bb.pieces(chess.PAWN, chess.BLACK)
            if chess.D6 in bpSqList:
                d6Found = True
            if chess.E5 in bpSqList:
                e5Found = True

            if d6Found and e5Found:
                return True
                
        return False

    def GetSearchScoreAfterMove(self, pos, side):
        """ Returns search's score, complexity number and
            pv move changes counts.
        """
        # Initialize
        scoreCp = TEST_SEARCH_SCORE

        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

        # Send command to engine.
        p.stdin.write("uci\n")

        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "uciok" in line:
                break

        # Set engine options
        self.SetEngineOptions(p, self.engOpt)
                
        # Send command to engine.
        p.stdin.write("isready\n")
        
        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "readyok" in line:
                break
                
        # Send commands to engine.
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

    def GetEpdEngineSearchScore(self, pos):
        """ Returns acd, acs, bm, ce and Ae opcodes. """

        # Initialize
        bestMove = None
        scoreCp = TEST_SEARCH_SCORE
        depthSearched = TEST_SEARCH_DEPTH

        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

        # Send command to engine.
        p.stdin.write("uci\n")

        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()               
            if "uciok" in line:
                break

        # Set engine options
        self.SetEngineOptions(p, self.engOpt)
                
        # Send command to engine.
        p.stdin.write("isready\n")
        
        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "readyok" in line:
                break
                
        # Send commands to engine.
        p.stdin.write("position fen " + pos + "\n")
        p.stdin.write("go movetime %d\n" %(self.moveTimeOpt))

        # Parse the output and extract the engine search, depth and bestmove
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

        # Verify values to be returned
        assert depthSearched != TEST_SEARCH_DEPTH, 'Error the engine does not search at all.'
        assert scoreCp != TEST_SEARCH_SCORE, 'Error!, search failed to return a score.'
        assert bestMove is not None, 'Error! seach failed to return a move.'
        return depthSearched, self.moveTimeOpt/1000, bestMove, scoreCp

    def GetEpdEngineStaticScore(self, pos):
        """ Returns ce and Ae opcodes. """

        # Initialize
        scoreP = TEST_SEARCH_SCORE

        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

        # Send command to engine.
        p.stdin.write("uci\n")

        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()               
            if "uciok" in line:
                break

        # Set engine options
        self.SetEngineOptions(p, self.engOpt)
                
        # Send command to engine.
        p.stdin.write("isready\n")
        
        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "readyok" in line:
                break
                
        # Send commands to engine.
        p.stdin.write("position fen " + pos + "\n")
        p.stdin.write("eval\n")

        # Parse the output and extract the engine search score, depth and bestmove
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()                  

            # Break search
            if 'Total Evaluation: ' in line:
                first = line.split('(')[0]
                scoreP = float(first.split()[2])
                break
                
        # Quit the engine
        p.stdin.write('quit\n')
        p.communicate()

        # Verify values to be returned
        assert scoreP != TEST_SEARCH_SCORE,\
               'Error!, engine failed to return its static eval.'

        # Convert to side POV
        if pos.split()[1] == 'b':
            scoreP = -1 * scoreP

        # Convert to centipawn
        scoreCp = int(scoreP * 100.0)
        return scoreCp

    def WriteTerminationMarker(self, wcnt, bcnt, werr, berr, rdiff, res):
        """ Write termination marker and average errror """
        if wcnt and bcnt:
            with open(self.outfn, 'a') as f:
                f.write('(-- {WhiteAveError=%0.2f, BlackAveError=%0.2f, ratingDiff=%d}) %s\n\n'\
                        %(werr, berr, rdiff, res))
        else:
            with open(self.outfn, 'a') as f:
                f.write('%s\n\n' %(res)) 

    def WinPercentage(self, pa):
        """ Returns win percentage given pawn advantage, pa """
        y = -pa/4.0
        wp = 1.0/(1.0 + (10**y))
        return wp

    def GetRatingDiff(self, averageError):
        """ Returns rating difference,
            wp = 1/(1+10**m)
            wp x (1+10**m) = 1
            wp + wp x 10**m = 1
            10**m = (1-wp)/wp
            m x log(10) = log((1-wp)/wp)
            log(10) = 1
            m = log((1-wp)/wp)
            m = ratingDiff/400
            ratingDiff = 400 x m
        """
        wp = self.WinPercentage(-averageError)
        m = math.log((1.0 - wp)/wp)
        ratingDiff = 400 * m
        return int(ratingDiff)
    
    def AnnotatePgn(self):
        """ Parse the pgn file and annotate the games """
        # Get engine id name for the Annotator tag.
        engineIdName = self.engIdName

        # Disable bookOpt if engine is not Brainfish.
        if self.bookOpt == 'cerebellum':
            if 'Brainfish' not in engineIdName:
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

            # Initialize move error calculation
            moveError = {'white':0.0, 'black':0.0}
            moveCnt = {'white':0, 'black':0}

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
                f.write('[Annotator "%s"]\n\n' %(engineIdName))

            # Before the movetext are written, add a comment of whether
            # move comments are from static evaluation or search score of the engine.
            if self.evalOpt == 'static':
                with open(self.outfn, 'a+') as f:
                    f.write('{Move comments are from engine static evaluation.}\n')
            elif self.evalOpt == 'search':
                with open(self.outfn, 'a+') as f:
                    hashValue = self.GetEngineOptionValue('Hash')
                    if hashValue is None:
                        hashValue = str(DEFAULT_HASH)
                    threadsValue = self.GetEngineOptionValue('Threads')
                    if threadsValue is None:
                        threadsValue = str(DEFAULT_THREADS)
                    f.write('{Hash %smb, Threads %s, @ %0.1fs/pos}\n'\
                            %(hashValue, threadsValue, self.moveTimeOpt/1000.0))

            # Save result to be written later as game termination marker.
            res = game.headers['Result']

            # Loop thru the moves within this game.
            gameNode = game        
            while gameNode.variations:
                side = gameNode.board().turn
                fmvn = gameNode.board().fullmove_number             
                nextNode = gameNode.variation(0)                      
                sanMove = nextNode.san()
                complexityNumber, moveChanges = 0, 0
                threatMove = None

                # (0) Don't start the engine analysis when fmvn is
                # below moveStart and not using a cerebellum book.
                if fmvn < self.moveStartOpt and self.bookOpt != 'cerebellum':
                    cereBookMove = None
                    self.WriteNotation(side, fmvn, sanMove, cereBookMove,
                                       None, False, None, None, 0, 0,
                                       None, threatMove)
                    gameNode = nextNode
                    continue                    

                # (1) Try to get a cerebellum book move.
                cereBookMove = None
                if self.bookOpt == 'cerebellum' and not isCereEnd:
                    # Use FEN before a move.
                    fenBeforeMove = gameNode.board().fen()
                    cereBookMove = self.GetCerebellumBookMove(fenBeforeMove)

                    # End trying to find cerebellum book move beyond BOOK_MOVE_LIMIT.
                    if cereBookMove is None and fmvn > BOOK_MOVE_LIMIT:
                        isCereEnd = True

                # (2) Don't start the engine analysis when fmvn is below moveStart.
                if fmvn < self.moveStartOpt and cereBookMove is not None:
                    self.WriteNotation(side, fmvn, sanMove, cereBookMove,
                                       None, False, None, None, 0, 0,
                                       None, threatMove)
                    gameNode = nextNode
                    continue 

                # (3) Get the posScore or the score of the player move.
                # Can be by static eval of the engine or search score of the engine
                posScore = None
                if self.evalOpt == 'static':
                    fenAfterMove = nextNode.board().fen()
                    staticScore = self.GetStaticEvalAfterMove(fenAfterMove)
                    posScore = staticScore
                elif self.evalOpt == 'search':
                    fenAfterMove = nextNode.board().fen()
                    searchScore = self.GetSearchScoreAfterMove(fenAfterMove, side)
                    posScore = searchScore

                # (4) Analyze the position with the engine. Only do this
                # if posScore is not winning or lossing (more than 3.0 pawns).
                engBestMove, engBestScore, pvLine = None, None, None
                if (posScore is None or abs(posScore) < DECISIVE_SCORE)\
                   and self.jobOpt == 'analyze':
                    engBestMove, engBestScore, complexityNumber,\
                                 moveChanges, pvLine =\
                        self.GetSearchScoreBeforeMove(gameNode.board().fen(),
                                                      side)

                    # Calculate total move errors incrementally and get the average later
                    if fmvn >= 12 and self.evalOpt == 'search' and\
                       sanMove != engBestMove:
                        if side:
                            scoreError = engBestScore - posScore
                            moveError['white'] += scoreError
                            moveCnt['white'] += 1
                        else:
                            scoreError = -1 * (engBestScore - posScore)
                            moveError['black'] += scoreError
                            moveCnt['black'] += 1
                    
                # (5) If game is over by checkmate and stalemate after a move              
                isGameOver = nextNode.board().is_checkmate() or\
                             nextNode.board().is_stalemate()

                # (5.1) Calculate the threat move if game move and engine best
                # move is the same and the position is complex and the engine
                # score is not winning or lossing
                if moveChanges >= 3 and sanMove == engBestMove\
                        and not gameNode.board().is_check() and abs(engBestScore) <= 2.0:
                    threatMove = self.GetThreatMove(gameNode.board().fen())
                    assert threatMove is not None
                
                # (6) Write moves and comments.
                self.WriteNotation(side, fmvn, sanMove, cereBookMove,
                                   posScore, isGameOver,
                                   engBestMove, engBestScore,
                                   complexityNumber, moveChanges,
                                   pvLine, threatMove)

                # Read the next position.
                gameNode = nextNode

            # All moves are parsed in this game, calculate average
            # errors and rating difference.
            averageError = {'white':0.0, 'black':0.0}
            ratingDiff = {'white':0, 'black':0}                
            if moveCnt['white']:
                averageError['white'] = moveError['white']/moveCnt['white']                
                ratingDiff['white'] = self.GetRatingDiff(averageError['white'])
            if moveCnt['black']:
                averageError['black'] = moveError['black']/moveCnt['black']            
                ratingDiff['black'] = self.GetRatingDiff(averageError['black'])
            
            # Write errors, rating difference and game termination
            # marker to output file.
            ratingDifference = abs(ratingDiff['white'] - ratingDiff['black'])
            self.WriteTerminationMarker(moveCnt['white'],
                                        moveCnt['black'],
                                        averageError['white'],
                                        averageError['black'],
                                        ratingDifference, res)               

            # Read the next game.
            game = chess.pgn.read_game(pgnHandle)

        # Close the file handle.
        pgnHandle.close()

    def AnnotateEpd(self):
        """ Annotate epd file with bm, ce, acs, acd, and Ae opcodes
            Ae - analyzing engine, a special opcode for this script.
        """
        cntEpd = 0
        
        # Open the epd file for reading.
        with open(self.infn, 'r') as f:
            for lines in f:
                cntEpd += 1
                
                # Remove white space at beginning and end of lines.
                epdLine = lines.strip()

                # Get only first 4 fields [pieces side castle_flag ep_sq].
                epdLineSplit = epdLine.split()
                epd = ' '.join(epdLineSplit[0:4])
                hmvc = self.GetHmvcInEpd(epdLine)

                # Add hmvc and fmvn to create a FEN for the engine.
                fen = epd + ' ' + hmvc + ' 1'

                # Show progress in console.
                print('epd %d: %s' %(cntEpd, epd))

                # If this position has no legal move then we skip it.
                pos = chess.Board(fen)
                isGameOver = pos.is_checkmate() or pos.is_stalemate()
                if isGameOver:
                    # Show warning in console.
                    print('Warning! epd \"%s\"' %(epd))
                    print('has no legal move - skipped.\n')
                    continue

                # Get engine analysis.
                if self.evalOpt == 'static':
                    ce = self.GetEpdEngineStaticScore(fen)
                elif self.evalOpt != 'none':
                    acd, acs, bm, ce = self.GetEpdEngineSearchScore(fen)

                # Show progress in console.
                if self.evalOpt == 'search':
                    print('bm: %s' %(bm))
                print('ce: %+d\n' %(ce))

                # Save to output file the epd analysis.
                with open(self.outfn, 'a') as f1:
                    if self.evalOpt == 'static':
                        f1.write('%s ce %+d; c0 \"%s\"; Ae \"%s\";\n'\
                                 %(epd, ce,
                                   'ce is static eval of engine',
                                   self.engIdName))
                    elif self.evalOpt != 'none':
                        f1.write('%s acd %d; acs %d; bm %s; ce %+d; Ae \"%s\";\n'\
                                 %(epd, acd, acs, bm, ce, self.engIdName))

    def GetEpdBm(self, epdLineList):
        """ return the bm in a list format in the epd line.
            There can be more 1 bm in a given epd.
        """
        # Example epd line.
        # [pieces] [side] [castle] [ep] bm e4 Nf3; c0 "id 1";
        bmIndex = epdLineList.index('bm')

        # Extract the string beyond the bm.
        bmStartValue = ' '.join(epdLineList[bmIndex+1:])

        # Remove trailing and leading empty space in the string.
        bmStartValue = bmStartValue.strip()

        # Split at semi colon.
        semiColonSplit = bmStartValue.split(';')

        # Extract the bm by taking the value with index [0].
        bmValue = semiColonSplit[0]

        # There could be more than 1 bm so we save it in a list.
        epdBm = bmValue.split()
        return epdBm

    def IsCorrectEngineBm(self, engineBm, epdBm):
        """ Returns True or False.
            Check if engineBm is correct against epdBm list
        """
        found = False
        for ebm in epdBm:
            if engineBm == ebm:
                found = True
                break
        return found

    def GetHmvcInEpd(self, epdLine):
        """ Returns hmvc in an epd line """        
        if 'hmvc' not in epdLine:
            return '0'
        epdLineSplit = epdLine.split()
        hmvcIndex = epdLineSplit.index('hmvc')
        hmvcValue = epdLineSplit[hmvcIndex+1]

        # Remove ';' at the end
        hmvc = hmvcValue[0:-1]
        return hmvc     

    def TestEngineWithEpd(self):
        """ Test engine with epd test suite, results will
            be in the output file.
        """
        cntEpd = 0
        cntCorrect = 0
        cntValidEpd = 0
        
        # Open the epd file for reading.
        with open(self.infn, 'r') as f:
            for lines in f:
                cntEpd += 1
                
                # Remove white space at beginning and end of lines.
                epdLine = lines.strip()

                # Get the first 4 fields [pieces side castle_flag ep_sq],
                # also search the hmvc opcode.
                epdLineSplit = epdLine.split()
                epd = ' '.join(epdLineSplit[0:4])
                hmvc = self.GetHmvcInEpd(epdLine)

                # Add hmvc and fmvn to create a FEN for the engine.
                fen = epd + ' ' + hmvc + ' 1'

                # Show progress in console.
                print('EPD %d: %s' %(cntEpd, epdLine))
                print('FEN %d: %s' %(cntEpd, fen))

                # If this position has no legal move then we skip it.
                pos = chess.Board(fen)
                isGameOver = pos.is_checkmate() or pos.is_stalemate()
                if isGameOver:
                    # Show warning in console.
                    print('Warning! epd \"%s\"' %(epd))
                    print('has no legal move - skipped.\n')
                    continue

                # If the epd line has no bm then we just skip it.
                if 'bm ' not in epdLine:
                    print('Warning!! epd \"%s\"')
                    print('has no bm opcode - skipped.\n')
                    continue

                # Get the bm(s) move in the epd line, epdBm is a list.
                epdBm = self.GetEpdBm(epdLineSplit)                

                # Get engine analysis, we are only interested on bm.
                _, _, bm, _ = self.GetEpdEngineSearchScore(fen)
                
                # The percentage correct is based on valid epd only
                cntValidEpd += 1

                # Show progress in console.
                print('engine bm: %s' %(bm))

                # Check bm of engine against the bm in epd, if found count it.
                isCorrect = self.IsCorrectEngineBm(bm, epdBm)
                if isCorrect:
                    cntCorrect += 1
                    print('correct: %d' %(cntCorrect))
                print

        # Print test summary.
        cntWrong = cntValidEpd - cntCorrect
        pctCorrect = 0.0
        if cntValidEpd:
            pctCorrect = (100.0 * cntCorrect)/cntValidEpd

        # Print summary to console
        print(':: EPD %s TEST RESULTS ::\n' %(self.infn))
        print('Total epd lines       : %d' %(cntEpd))
        print('Total tested positions: %d' %(cntValidEpd))
        print('Total correct         : %d' %(cntCorrect))
        print('Correct percentage    : %0.1f' %(pctCorrect))

        # Write to output file, that was specified in -outfile option.
        with open(self.outfn, 'a') as f:
            f.write(':: EPD %s TEST RESULTS ::\n' %(self.infn))
            f.write('Engine        : %s\n' %(self.engIdName))
            f.write('Time/pos (sec): %0.1f\n\n' %(self.moveTimeOpt/1000.0))
            f.write('Total epd lines       : %d\n' %(cntEpd))
            f.write('Total tested positions: %d\n' %(cntValidEpd))
            f.write('Total correct         : %d\n' %(cntCorrect))
            f.write('Correct percentage    : %0.1f\n' %(pctCorrect))
            
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
    moveStartOption = 8
    jobOption = 'analyze' # ['none' 'analyze', 'test']
    engOption = 'none'
    
    # Evaluate the command line options.
    options = EvaluateOptions(argv)
    if len(options):
        inputFile = GetOptionValue(options, '-infile', inputFile)
        outputFile = GetOptionValue(options, '-outfile', outputFile)
        engineName = GetOptionValue(options, '-eng', engineName)
        bookOption = GetOptionValue(options, '-book', bookOption)
        evalOption = GetOptionValue(options, '-eval', evalOption)
        moveTimeOption = GetOptionValue(options, '-movetime', moveTimeOption)
        moveStartOption = GetOptionValue(options, '-movestart', moveStartOption)
        jobOption = GetOptionValue(options, '-job', jobOption)
        engOption = GetOptionValue(options, '-engoptions', engOption)

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
    if bookOption == 'none' and evalOption == 'none'\
       and fileType == PGN_FILE and jobOption == 'none':
        print('Error! options were not defined. Nothing has been processed.')
        sys.exit(1)

    # Exit if file type is epd and move time is 0.
    if fileType == EPD_FILE and moveTimeOption <= 0 and evalOption != 'static':
        print('Error! movetime is zero.')
        sys.exit(1)

    # Exit if analyzing epd with -eval none
    if fileType == EPD_FILE and evalOption == 'none' and jobOption != 'test':
        print('Error! -eval was set to none.')
        sys.exit(1)
        
    # Delete existing output file.
    DeleteFile(outputFile)
        
    # Convert options to dict.
    options = {'-book': bookOption,
               '-eval': evalOption,
               '-movetime': moveTimeOption,
               '-movestart': moveStartOption,
               '-job': jobOption,
               '-engoptions': engOption
               }

    # Create an object of class Analyze.
    g = Analyze(inputFile, outputFile, engineName, **options)

    # Print engine id name.
    g.PrintEngineIdName()

    # Process input file depending on the format and options
    if fileType == EPD_FILE:
        if jobOption == 'test':
            g.TestEngineWithEpd()
        else:
            g.AnnotateEpd()
    elif fileType == PGN_FILE:
        g.AnnotatePgn()
    else:
        print('Warning! it is not possbile to reach here')

    print('Done!!\n')    

if __name__ == "__main__":
    main(sys.argv[1:])
