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
1. See also the README.txt and README.md for some useful informations.
"""


import os
import sys
import subprocess
import argparse
import random
import logging
import chess
import chess.pgn
import chess.polyglot

sr = random.SystemRandom()


# Constants
APP_NAME = 'Chess Artist'
APP_VERSION = '0.3.20'
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


BEST = ['Excellent', 'Outstanding', 'Exceptional', 'Striking', 'Priceless',
        'Top-notch', 'Marvellous', 'Terrific', 'Splendid', 'Magnificient',
        'Admirable', 'Brilliant', 'Cool']
BETTER = ['Better', 'Preferable', 'More useful', 'More appropriate',
          'More suitable', 'Worthier', 'Superior', 'Nicer', 'More expert',
          'More valuable', 'More fitting']
BOOK_COMMENT = 'Polyglot book'
    

def DeleteFile(fn):
    """ Delete fn file """
    if os.path.isfile(fn):
        os.remove(fn)


class Analyze():
    """ An object that will read and annotate games in a pgn file """
    def __init__(self, infn, outfn, eng, **opt):
        """ Initialize """
        self.infn = infn
        self.outfn = outfn
        self.eng = eng
        self.evalType = opt['-eval']
        self.moveTime = opt['-movetime']
        self.analysisMoveStart = opt['-movestart']
        self.jobType = opt['-job']
        self.engineOptions = opt['-engineoptions']
        self.bookFile = opt['-bookfile']
        self.depth = opt['-depth']
        self.bookMove = None
        self.sidePassedPawnIsGood = False
        self.whitePassedPawnCommentCnt = 0
        self.blackPassedPawnCommentCnt = 0
        self.oppKingSafetyIsBad = False
        self.whiteKingSafetyCommentCnt = 0
        self.blackKingSafetyCommentCnt = 0
        self.writeCnt = 0
        self.engIdName = self.GetEngineIdName()
        
    def Send(self, p, msg):
        """ Send msg to engine """
        p.stdin.write('%s\n' % msg)
        logging.debug('>> %s' % msg)
        
    def ReadEngineReply(self, p, command):
        """ Read reply from engine """
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            logging.debug('<< %s' % line)
            if command == 'uci' and 'uciok' in line:
                break
            if command == 'isready' and 'readyok' in line:
                break
    
    @staticmethod
    def UciToSanMove(fen, uciMove):
        """ Returns san move given fen and uci move """
        board = chess.Board(fen)
        return board.san(chess.Move.from_uci(uciMove))

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
        if self.moveTime >= 180000:
            veryGoodMoveChangesThreshold += 2
        elif self.moveTime >= 60000:
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
    
    @staticmethod
    def GetBadNag(side, posScore, engScore):
        """ Returns ??, ?, ?! depending on the player score and analyzing
            engine score. 
            posScore is the score of the move in the game, in pawn unit.
            engScore is the score of the move suggested by the engine,
            in pawn unit.
            Positive score is better for white and negative score is better
            for black, (WPOV).
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
            varComment = '%s is' % sr.choice(BEST)
        elif engScore - posScore > DRAW_SCORE:
            varComment = '%s is' % sr.choice(BETTER)
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
        """ Write moves with score in the output file 
            This could be a case where the engine has no suggestion possibly
            the game move is the same as the engine move
        """
        
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                if self.sidePassedPawnIsGood:
                    f.write('%d. %s {%+0.2f, with a better passed pawn} ' %(moveNumber, sanMove, posScore))
                    self.whitePassedPawnCommentCnt += 1
                elif self.oppKingSafetyIsBad:
#                    print('King safety is written to pgn file')
                    f.write('%d. %s {%+0.2f, with a dangerous king attack} ' %(moveNumber, sanMove, posScore))
                    self.whiteKingSafetyCommentCnt += 1
                else:
                    f.write('%d. %s {%+0.2f} ' %(moveNumber, sanMove, posScore))
            else:
                if self.sidePassedPawnIsGood:
                    f.write('%s {%+0.2f, with a better passed pawn} ' %(sanMove, posScore))
                    self.blackPassedPawnCommentCnt += 1
                elif self.oppKingSafetyIsBad:
#                    print('King safety is written to pgn file')
                    f.write('%s {%+0.2f, with a dangerous king attack} ' %(sanMove, posScore))
                    self.blackKingSafetyCommentCnt += 1
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
                    moveNag = Analyze.GetBadNag(side, posScore, engScore)

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
                    else:
                        f.write('{, with the idea of %s} %d. %s %s {%+0.2f} '\
                                % (threatMove, moveNumber, sanMove, moveNag,
                                   posScore))
            else:
                if sanMove != engMove:
                    moveNag = Analyze.GetBadNag(side, posScore, engScore)

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
                        f.write('%s %s {%+0.2f} ' %(sanMove,
                                                    moveNag,
                                                    posScore))
                    else:
                        f.write('{, with the idea of %s} %s %s {%+0.2f} '\
                                %(threatMove, sanMove, moveNag, posScore))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
                    self.writeCnt = 0
                    f.write('\n')

    def WriteBookMove(self, side, moveNumber, sanMove, bookMove):
        """ Write moves with book moves in the output file """
        assert bookMove is not None
        
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                f.write('%d. %s (%d. %s {%s}) ' %(moveNumber, sanMove,
                                                  moveNumber, bookMove,
                                                  BOOK_COMMENT))
            else:
                f.write('%d... %s (%d... %s {%s}) ' %(moveNumber, sanMove,
                                                      moveNumber, bookMove,
                                                      BOOK_COMMENT))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
                    self.writeCnt = 0
                    f.write('\n')

    def WritePosScoreBookMove(self, side, moveNumber, sanMove,
                              bookMove, posScore):
        """ Write moves with score and book moves in the output file """
        assert bookMove is not None
        
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                f.write('%d. %s {%+0.2f} (%d. %s {%s}) ' %(moveNumber, sanMove,
                                                        posScore, moveNumber,
                                                        bookMove, BOOK_COMMENT))
            else:
                f.write('%d... %s {%+0.2f} (%d... %s {%s}) ' %(moveNumber,
                                                        sanMove,
                                                        posScore, moveNumber,
                                                        bookMove, BOOK_COMMENT))
                
                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
                    self.writeCnt = 0
                    f.write('\n') 

    def WritePosScoreBookMoveEngMove(self, side, moveNumber, sanMove, bookMove,
                                     posScore, engMove, engScore,
                                     complexityNumber, moveChanges,
                                     pvLine, threatMove):
        """ Write moves with score and book moves in the output file """
        
        # Write the move and comments
        with open(self.outfn, 'a+') as f:
            self.writeCnt += 1

            # If side to move is white
            if side:
                if sanMove != engMove:
                    moveNag = Analyze.GetBadNag(side, posScore, engScore)

                    # Add better is symbol before the engine variation
                    varComment = self.PreComment(side, engScore, posScore)

                    # Write moves and comments
                    f.write('%d. %s %s {%+0.2f} (%d. %s {%s}) ({%s} %s {%+0.2f}) '\
                            %(moveNumber, sanMove, moveNag, posScore,
                              moveNumber, bookMove, BOOK_COMMENT,
                              varComment, pvLine, engScore))
                else:
                    moveNag = self.GetGoodNag(side, posScore, engScore,
                                              complexityNumber, moveChanges)
                    if threatMove is not None:
                        f.write('{, with the idea of %s} %d. %s {%+0.2f} (%d. %s {%s}) '\
                                %(threatMove, moveNumber, sanMove, posScore,
                                  moveNumber, bookMove, BOOK_COMMENT))
                    else:
                        f.write('%d. %s {%+0.2f} (%d. %s {%s}) ' %(moveNumber,
                                                sanMove, posScore, moveNumber,
                                                bookMove, BOOK_COMMENT))
            else:
                if sanMove != engMove:
                    moveNag = Analyze.GetBadNag(side, posScore, engScore)

                    # Add better is symbol before the engine variation
                    varComment = self.PreComment(side, engScore, posScore)

                    # Write moves and comments
                    f.write('%d... %s %s {%+0.2f} (%d... %s {%s}) ({%s} %s {%+0.2f}) '\
                            %(moveNumber, sanMove, moveNag, posScore,
                              moveNumber, bookMove, BOOK_COMMENT,
                              varComment, pvLine, engScore))
                else:
                    moveNag = self.GetGoodNag(side, posScore, engScore,
                                              complexityNumber, moveChanges)
                    if threatMove is not None:
                        f.write('{, with the idea of %s} %d... %s {%+0.2f} (%d... %s {%s}) '\
                                %(threatMove, moveNumber, sanMove, posScore,
                                  moveNumber, bookMove, BOOK_COMMENT))
                    else:
                        f.write('%d... %s {%+0.2f} (%d... %s {%s}) '\
                                %(moveNumber, sanMove, posScore, moveNumber,
                                  bookMove, BOOK_COMMENT))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
                    self.writeCnt = 0
                    f.write('\n')

    def WriteBookMoveEngMove(self, side, moveNumber, sanMove, bookMove,
                                            engMove, engScore, pvLine):
        """ Write moves with book moves and eng moves in the output file """
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
                              BOOK_COMMENT, pvLine, engScore))
                else:
                    f.write('%d. %s (%d. %s {%s}) '\
                            %(moveNumber, sanMove,
                              moveNumber, bookMove, BOOK_COMMENT))
            else:
                if sanMove != engMove:
                    
                    # Write moves and comments
                    f.write('%d... %s (%d... %s {%s}) (%s {%+0.2f}) '\
                            %(moveNumber, sanMove, moveNumber,
                              bookMove, BOOK_COMMENT, pvLine,
                              engScore))
                else:
                    f.write('%d... %s (%d... %s {%s}) '\
                            %(moveNumber, sanMove,
                              moveNumber, bookMove, BOOK_COMMENT))

                # Format output, don't write movetext in one long line.
                if self.writeCnt >= 2:
                    self.writeCnt = 0
                    f.write('\n')

    def WriteEngMove(self, side, moveNumber, sanMove, engMove,
                     engScore, pvLine):
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
        if isGameOver or (posScore is None and bookMove is None):
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
            
    def MateDistanceToValue(self, d):
        """ Returns value given distance to mate """
        value = 0
        if d < 0:
            value = -2*d - MAX_SCORE
        elif d > 0:
            value = MAX_SCORE - 2*d + 1
        return value
    
    @staticmethod
    def GetMaterialInfo(fen):
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
        bmat = q*9 + r*5 + b*3 + n*3

        # Get queen and pawn counts
        queens = Q+q
        pawns = P+p
        return wmat, bmat, queens, pawns
    
    def GetEngineIdName(self):
        """ Returns the engine id name """
        engineIdName = self.eng[0:-4]
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.Send(p, 'uci')
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if 'id name ' in line:
                idName = line.split()
                engineIdName = ' '.join(idName[2:])            
            if 'uciok' in line:           
                break
        self.Send(p, 'quit')
        p.communicate()
        return engineIdName
    
    def IsKingSafetyBad(self, curFen, nextFen):
        """ Returns True if king safety of side not to move is bad.
            Example line to be parsed:
                      King safety |  3.01  3.87 |  0.08  0.39 |  2.92  3.48
        """
        logging.info('Check king safety')
        curBoard = chess.Board(curFen)
        curSide = curBoard.turn
        
        # (1) Get the king safety based on curFen
        
        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Setup fen and send eval command, the engine should be Stockfish
        # or Brainfish that supports eval command
        p.stdin.write('uci\n')
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if 'uciok' in line:
                break
        p.stdin.write('ucinewgame\n')
        p.stdin.write('position fen %s\n' % curFen)
        p.stdin.write('eval\n')
        
        # Parse the output
        kingSafetyCommentCur = None
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            
            if 'King safety ' in line:
                kingSafetyCommentCur = line
                break
            if 'bestmove ' in line:
                break
            
        if kingSafetyCommentCur is None:
            p.stdin.write('quit\n')
            p.communicate()
            return False
            
        # Net score white POV
        whiteMgKingSafetyCur = float(kingSafetyCommentCur.split()[9])           
        
        # (2) Get the king safety based on nextFen
        
        p.stdin.write('ucinewgame\n')
        p.stdin.write('position fen %s\n' % nextFen)
        p.stdin.write('eval\n')
        
        # Parse the output
        kingSafetyCommentNext = None
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            
            if 'King safety ' in line:
                kingSafetyCommentNext = line
                break
            if 'bestmove ' in line:
                break

        p.stdin.write('quit\n')
        p.communicate()
        
        if kingSafetyCommentNext is None:
            return False

        # Net score white POV
        whiteMgKingSafetyNext = float(kingSafetyCommentNext.split()[9])
        
        # Evaluate the king safety of side not to move based on curFen
        sideToEvaluate = not curSide
        
        # If white
        if sideToEvaluate:
            if whiteMgKingSafetyNext < -3.0 and whiteMgKingSafetyNext < whiteMgKingSafetyCur:
                return True
        else:
            if whiteMgKingSafetyNext > 3.0 and whiteMgKingSafetyNext > whiteMgKingSafetyCur:
                return True

        return False 

    def IsPassedPawnGood(self, fen, side):
        """ Returns True if passed pawn eval of side not to move is good.
            Example line to be parsed:
                      Passed |  3.01  3.87 |  0.08  0.39 |  2.92  3.48
        """
        
        # Evaluate the passed pawn of the side not to move
        sideToEvaluate = not side
        
        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Setup fen and send eval command, the engine should be Stockfish
        # or Brainfish that supports eval command
        p.stdin.write('uci\n')
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if 'uciok' in line:
                break
        p.stdin.write('ucinewgame\n')
        p.stdin.write('position fen %s\n' % fen)
        p.stdin.write('eval\n')
        
        # Parse the output
        passedPawnComment = None
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            
            if 'Passed ' in line:
                passedPawnComment = line
                break
            if 'bestmove ' in line:
                break

        p.stdin.write('quit\n')
        p.communicate()
        
        if passedPawnComment is None:
            return False

        whiteMgPassedValue = float(passedPawnComment.split()[8])
        whiteEgPassedValue = float(passedPawnComment.split()[9])
        
        # Positive is better for white, negative is better for black
        # If side to move is white
        if sideToEvaluate:
            if whiteMgPassedValue >= 2.0 and whiteEgPassedValue >= 2.0:
                return True
        else:
            if whiteMgPassedValue <= -2.0 and whiteEgPassedValue <= -2.0:
                return True

        return False 
    
    def GetPolyglotBookMove(self, fen):
        """ Returns a move from polyglot book """
        polyMove = None
        if self.bookFile is None:
            return polyMove

        # Find the move with highest book weight
        board = chess.Board(fen)
        bestWeight = -1
        bestMove = None        
        with chess.polyglot.open_reader(self.bookFile) as reader:
            for entry in reader.find_all(board):
                if entry.weight > bestWeight:
                    bestWeight = entry.weight
                    bestMove = str(entry.move())
                
        polyMove = bestMove
                
        if polyMove is not None:
            polyMove = Analyze.UciToSanMove(fen, polyMove)
        
        return polyMove

    def GetEngineOptionValue(self, optionName):
        """ Returns value str of option given option name """
        engOptionValue = self.engineOptions
        
        # Return default Hash and threads if engine options are not defined
        if engOptionValue is None:            
            if 'hash' in optionName.lower():
                return str(DEFAULT_HASH)
            elif 'threads' in optionName.lower():
                return str(DEFAULT_THREADS)

        # If there are more than 1 options defined
        elif ',' in engOptionValue:
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
        if engOptionValue is None:
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
        logging.info('Get search score after making the game move.')
        score = TEST_SEARCH_SCORE

        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Send command to engine.
        p.stdin.write("uci\n")

        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "uciok" in line:
                break

        # Set engine options
        self.SetEngineOptions(p, self.engineOptions)
                
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
            if 'total evaluation' in line.lower():
                first = line.split('(')[0]
                score = float(first.split()[2])
                break
                
        # Quit the engine
        p.stdin.write('quit\n')
        p.communicate()
        assert score != TEST_SEARCH_SCORE,\
               'Error! something is wrong in static eval calculation.'
        return score

    def GetThreatMove(self, fen):
        """ 
        Returns threat move after pushing a null move and search.
        """
        logging.debug('Get threat move.')
        bestMove = None
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.Send(p, 'uci')
        self.ReadEngineReply(p, 'uci')
        self.SetEngineOptions(p, self.engineOptions)
        self.Send(p, 'isready')
        self.ReadEngineReply(p, 'isready')

        # Push null move
        b = chess.Board(fen)
        b.push(chess.Move.null())
        newFen = b.fen()
        
        self.Send(p, 'ucinewgame')
        self.Send(p, 'position fen %s' % newFen)
        self.Send(p, 'go movetime %d' % self.moveTime)

        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            if 'bestmove ' in line:
                bestMove = line.split()[1]
                break

        self.Send(p, 'quit')
        p.communicate()

        if bestMove is not None:
            bestMove = Analyze.UciToSanMove(newFen, bestMove)
        
        return bestMove

    def GetSearchScoreBeforeMove(self, fen, side):
        """
        Returns bestmove, pv, score complexity number of the position and
        root move changes. 
        """
        logging.info('Get search score before making the game move.')
        scoreCp = TEST_SEARCH_SCORE
        pvLine = None
        searchDepth = 0
        savedMove = []
        complexityNumber = 0
        moveChanges = 0
        isGetComplexityNumber = self.jobType == 'analyze' and\
                                self.moveTime >= COMPLEXITY_MINIMUM_TIME
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.Send(p, 'uci')
        self.ReadEngineReply(p, 'uci')
        self.SetEngineOptions(p, self.engineOptions)
        self.Send(p, 'isready')
        self.ReadEngineReply(p, 'isready')
        self.Send(p, 'ucinewgame')
        self.Send(p, 'position fen %s' % fen)
        self.Send(p, 'go movetime %d' % self.moveTime)

        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            # Save pv move per depth
            if isGetComplexityNumber:
                if 'info depth ' in line and ' pv ' in line and not\
                   'upperbound' in line and not 'lowerbound' in line:
                    logging.info(line)
                    
                    # Get the depth
                    splitLine = line.split()
                    searchDepth = int(splitLine[splitLine.index('depth')+1])

                    # Get the move and save it
                    pvMove = splitLine[splitLine.index('pv')+1].strip()
                    savedMove.append([searchDepth, pvMove])

            # Save pv line
            if 'info depth ' in line and ' pv ' in line and not\
                   'upperbound' in line and not 'lowerbound' in line:
                splitLine = line.split()
                pvIndex = splitLine.index('pv')
                pvLine = splitLine[pvIndex+1:pvIndex+6]
                    
            if 'score cp ' in line:
                splitStr = line.split()
                scoreIndex = splitStr.index('score')
                scoreCp = int(splitStr[scoreIndex + 2])
            elif 'score mate ' in line:
                splitStr = line.split()
                scoreIndex = splitStr.index('score')
                mateInN = int(splitStr[scoreIndex + 2])

                scoreCp = self.MateDistanceToValue(mateInN)        

            if 'bestmove ' in line:
                bestMove = line.split()[1]
                logging.debug(line)
                break

        self.Send(p, 'quit')
        p.communicate()

        # Get the first move of the pvLine, make sure the this move
        # is the same with the bestMove, if not then set bestMove as pvLine
        firstPvMove = pvLine[0].strip()
        if firstPvMove != bestMove:
            pvLine = []
            pvLine.append(bestMove)

        try:
            board = chess.Board(fen)
            pvLineSan = board.variation_san(
                    [chess.Move.from_uci(m) for m in pvLine])
        except:
            logging.warning('Warning, there is error in pvLine')
            logging.info('pvLine: %s' % pvLine)

        if isGetComplexityNumber:
            complexityNumber, moveChanges = self.GetComplexityNumber(
                    savedMove, fen)
        bestMove = Analyze.UciToSanMove(fen, bestMove)
        if not side:
            scoreCp = -1 * scoreCp

        scoreP = float(scoreCp)/100.0
        return bestMove, scoreP, complexityNumber, moveChanges, pvLineSan

    def GetComplexityNumber(self, savedMove, fen):
        """ Returns complexity number and move changes counts
            savedMove = [[depth1, move1],[depth2, move2]]
        """
        logging.info('Get Complexity number.')
        complexityNumber, moveChanges = 0, 0
        lastMove = None
        lastDepth = 0
        for n in savedMove:
            depth = n[0]
            move = n[1]
            if depth >= 10:
                if move != lastMove and depth != lastDepth:
                    complexityNumber += depth
                    moveChanges += 1
            lastDepth = depth
            lastMove = move

        # Increase complexityNumber when there are queens, and high mat values
        if complexityNumber > 0:
            wmat, bmat, queens, pawns = Analyze.GetMaterialInfo(fen)
            if queens > 0:
                complexityNumber += 5
                
            # High piece values remaining and 2 pawns is at least exchanged
            if wmat + bmat >= 46 and pawns <= 14:
                complexityNumber += 5

        # Reduce complexity number when center is closed
        if self.IsCenterClosed(fen):
            complexityNumber -= 10
            if complexityNumber < 0:
                complexityNumber = 0
                
        logging.info('Complexity number: %d' % complexityNumber)
                
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
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Send command to engine.
        p.stdin.write("uci\n")

        # Parse engine replies.
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            if "uciok" in line:
                break

        # Set engine options
        self.SetEngineOptions(p, self.engineOptions)
                
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
        p.stdin.write("go movetime %d\n" %(self.moveTime))

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
                logging.info(line)
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

    def GetEpdEngineSearchScore(self, fen):
        """ Returns acd, acs, bm, ce and Ae opcodes. """

        # Initialize
        bestMove = None
        scoreCp = TEST_SEARCH_SCORE
        depthSearched = TEST_SEARCH_DEPTH

        # Run the engine, only works with python 2
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.Send(p, 'uci')
        self.ReadEngineReply(p, 'uci')
        self.SetEngineOptions(p, self.engineOptions)
        self.Send(p, 'isready')
        self.ReadEngineReply(p, 'isready')
        self.Send(p, 'ucinewgame')
        self.Send(p, 'position fen %s' % fen)
        
        if self.moveTime > 0:
            if self.depth > 0:
                self.Send(p, 'go movetime %d depth %d' % (self.moveTime, self.depth))
            else:
                self.Send(p, 'go movetime %d' % self.moveTime)
        elif self.depth > 0:
            self.Send(p, 'go depth %d' % self.depth)
        else:
            logging.debug('Error, missing movetime and depth')
            self.Send(p, 'quit')
            return

        # Parse the output and extract the engine search, depth and bestmove
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            if 'bestmove' in line or \
                    'depth' in line and 'score' in line and 'pv' in line:
                logging.debug('<< %s' % line)
                
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
        self.Send(p, 'quit')
        p.communicate()

        # Convert uci move to san move format.
        bestMove = Analyze.UciToSanMove(fen, bestMove)

        # Verify values to be returned
        assert depthSearched != TEST_SEARCH_DEPTH, 'Error the engine does not search at all.'
        assert scoreCp != TEST_SEARCH_SCORE, 'Error!, search failed to return a score.'
        assert bestMove is not None, 'Error! seach failed to return a move.'
        return depthSearched, self.moveTime/1000, bestMove, scoreCp

    def GetEpdEngineStaticScore(self, fen):
        """ Returns ce and Ae opcodes. """

        # Initialize
        scoreP = TEST_SEARCH_SCORE

        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.Send(p, 'uci')
        self.ReadEngineReply(p, 'uci')
        self.SetEngineOptions(p, self.engineOptions)
        self.Send(p, 'isready')
        self.ReadEngineReply(p, 'isready')
        self.Send(p, 'ucinewgame')
        self.Send(p, 'position fen %s' % fen)
        self.Send(p, 'eval')

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
        if fen.split()[1] == 'b':
            scoreP = -1 * scoreP

        # Convert to centipawn
        scoreCp = int(scoreP * 100.0)
        return scoreCp

    def WriteTerminationMarker(self, wcnt, bcnt, werr, berr, res):
        """ Write termination marker and average errror """
        if wcnt and bcnt:
            with open(self.outfn, 'a') as f:
                f.write('{WhiteAveError=%0.2f, BlackAveError=%0.2f} %s\n\n'\
                        %(werr, berr, res))
        else:
            with open(self.outfn, 'a') as f:
                f.write('%s\n\n' %(res)) 
    
    def AnnotatePgn(self):
        """ Parse the pgn file and annotate the games """
        # Get engine id name for the Annotator tag.
        engineIdName = self.engIdName
        pgnHandle = open(self.infn)
        game = chess.pgn.read_game(pgnHandle)

        # Used for displaying progress in console.
        gameCnt = 0

        # Loop thru the games.
        while game:
            gameCnt += 1
            
            # Reset passed pawn comment every game. Passed pawn comment is
            # only done once for white and once for black per game
            self.whitePassedPawnCommentCnt = 0
            self.blackPassedPawnCommentCnt = 0
            self.whiteKingSafetyCommentCnt = 0
            self.blackKingSafetyCommentCnt = 0

            # Initialize move error calculation
            moveError = {'white':0.0, 'black':0.0}
            moveCnt = {'white':0, 'black':0}

            # Used for formatting the output.
            self.writeCnt = 0

            # Show progress in console.
            print('Annotating game %d...' %(gameCnt))

            # Save the tag section of the game.
            for key, value in game.headers.items():
                with open(self.outfn, 'a+') as f:
                    f.write('[%s \"%s\"]\n' %(key, value))

            # Write the annotator tag.
            with open(self.outfn, 'a+') as f:
                f.write('[Annotator "%s"]\n\n' %(engineIdName))

            # Before the movetext are written, add a comment of whether
            # move comments are from static or search score of the engine.
            if self.evalType == 'static':
                with open(self.outfn, 'a+') as f:
                    f.write('{Move comments are from engine static evaluation.}\n')
            elif self.evalType == 'search':
                with open(self.outfn, 'a+') as f:
                    hashValue = self.GetEngineOptionValue('Hash')
                    if hashValue is None:
                        hashValue = str(DEFAULT_HASH)
                    threadsValue = self.GetEngineOptionValue('Threads')
                    if threadsValue is None:
                        threadsValue = str(DEFAULT_THREADS)
                    
                    # Don't write Hash in the comment if the analyzing engine
                    # is Lc0 or Leela Chess Zero
                    if 'lc0' in engineIdName.lower() or\
                            'leela chess zero' in engineIdName.lower():
                        f.write('{Threads %s, @ %0.1fs/pos}\n' %(
                                threadsValue, self.moveTime/1000.0))
                    else:
                        f.write('{Hash %smb, Threads %s, @ %0.1fs/pos}\n' %(
                                hashValue, threadsValue, self.moveTime/1000.0))

            # Save result to be written later as game termination marker.
            res = game.headers['Result']

            # Loop thru the moves within this game.
            gameNode = game        
            while gameNode.variations:
                side = gameNode.board().turn
                fmvn = gameNode.board().fullmove_number     
                curFen = gameNode.board().fen()
                nextNode = gameNode.variation(0)                      
                nextFen = nextNode.board().fen()
                sanMove = nextNode.san()
                complexityNumber, moveChanges = 0, 0
                threatMove = None  
                self.bookMove = None
                self.sidePassedPawnIsGood = False
                self.oppKingSafetyIsBad = False
                
                print('side: %s, move_num: %d' % ('White' if side else 'Black',
                                                  fmvn))

                # (1) Check move start
                if fmvn < self.analysisMoveStart:
                    self.WriteNotation(side, fmvn, sanMove, self.bookMove,
                                       None, False, None, None, 0, 0,
                                       None, threatMove)
                    gameNode = nextNode
                    continue

                # (2) Probe the book file and save the best book move  
                if fmvn <= BOOK_MOVE_LIMIT and self.bookFile is not None:
                    self.bookMove = self.GetPolyglotBookMove(curFen)

                # (3) Get the posScore or the score of the player move.
                # Can be by static eval or search score of the engine
                posScore = None
                if self.evalType == 'static':
                    staticScore = self.GetStaticEvalAfterMove(nextFen)
                    posScore = staticScore
                elif self.evalType == 'search':
                    searchScore = self.GetSearchScoreAfterMove(nextFen, side)
                    posScore = searchScore

                # (4) Analyze the position with the engine. Only do this
                # if posScore is not winning or lossing (more than 3.0 pawns).
                engBestMove, engBestScore, pvLine = None, None, None
                if (posScore is None or abs(posScore) < DECISIVE_SCORE) and\
                        self.jobType == 'analyze':
                    engBestMove, engBestScore, complexityNumber, moveChanges,\
                    pvLine = self.GetSearchScoreBeforeMove(curFen, side)
                        
                    print('Game move: %s (%0.2f), Engine bestmove: %s (%0.2f)'\
                          % (sanMove, posScore, engBestMove, engBestScore))

                    # Calculate move errors and get the average later
                    if fmvn >= 12 and self.evalType == 'search' and\
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
                if moveChanges >= 3 and sanMove == engBestMove and not\
                    gameNode.board().is_check() and abs(engBestScore) <= 2.0:
                    threatMove = self.GetThreatMove(curFen)
                    
                # (5.2) Check if passed pawn of side to move is good. We need
                # to make the move on the board and then evaluate it
                if 'stockfish' in engineIdName.lower() or\
                        'brainfish' in engineIdName.lower():
                    if side and self.whitePassedPawnCommentCnt == 0:
                        self.sidePassedPawnIsGood = self.IsPassedPawnGood(
                                nextFen, not side)
                    elif not side and self.blackPassedPawnCommentCnt == 0:
                        self.sidePassedPawnIsGood = self.IsPassedPawnGood(
                                nextFen, side)
                        
                # (5.3) Calculate the king safety of the side not to move.
                # First calculcate the king safety using the current position
                # (ks1) then calculate the king safety after making the move on
                # the board (ks2) If ks2 < ks1 and ks2 < -3 pawns or worst then
                # the current move increases attack to the opponent's king,
                # we add a comment "with a dangerous king attack" on this move
                if 'stockfish' in engineIdName.lower() or\
                        'brainfish' in engineIdName.lower():
                    if side and self.whiteKingSafetyCommentCnt == 0:
                        self.oppKingSafetyIsBad = self.IsKingSafetyBad(
                                curFen, nextFen)
                    elif not side and self.blackKingSafetyCommentCnt == 0:
                        self.oppKingSafetyIsBad = self.IsKingSafetyBad(
                                curFen, nextFen)
                
                # (6) Write moves and comments.
                self.WriteNotation(side, fmvn, sanMove, self.bookMove,
                                   posScore, isGameOver,
                                   engBestMove, engBestScore,
                                   complexityNumber, moveChanges,
                                   pvLine, threatMove)
                gameNode = nextNode

            # All moves are parsed in this game, calculate average errors.
            averageError = {'white':0.0, 'black':0.0}
            if moveCnt['white']:
                averageError['white'] = moveError['white']/moveCnt['white'] 
            if moveCnt['black']:
                averageError['black'] = moveError['black']/moveCnt['black']
            
            # Write errors, and game termination marker to output file.
            self.WriteTerminationMarker(moveCnt['white'],
                                        moveCnt['black'],
                                        averageError['white'],
                                        averageError['black'], res)
            game = chess.pgn.read_game(pgnHandle)

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
                if self.evalType == 'static':
                    ce = self.GetEpdEngineStaticScore(fen)
                elif self.evalType == 'search':
                    acd, acs, bm, ce = self.GetEpdEngineSearchScore(fen)

                # Show progress in console.
                if self.evalType == 'search':
                    print('bm: %s' %(bm))
                print('ce: %+d\n' %(ce))

                # Save to output file the epd analysis.
                with open(self.outfn, 'a') as f1:
                    if self.evalType == 'static':
                        f1.write('%s ce %+d; c0 \"%s\"; Ae \"%s\";\n' %(epdLine, ce, 'ce is static eval of engine', self.engIdName))
                    elif self.evalType == 'search':
                        f1.write('%s acd %d; acs %d; bm %s; ce %+d; Ae \"%s\";\n' %(epdLine, acd, acs, bm, ce, self.engIdName))

    def GetEpdBmAm(self, epdLine):
        """ Return the bm and am in a list format in the epdLine.
            There can be more than 1 bm and/or more than 1 am.
            bm = best move, based from input epd
            am = avoid move, based from input epd
        """
        # Example epd lines:
        # [pieces] [side] [castle] [ep] bm [best move]; id "id [id name]";
        # rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - bm e4 d4; id "id 1";
        # rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - am a3; id "id 2";
        # rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - bm d4; am a3; id "id 3";
        
        # Save bm and am from the given epd
        bmList, amList = [], []
        
        # (1) Get the bm in the epd
        try:
            # Split epd by semi-colon, then examine every slice to find bm
            bmSplit = epdLine.split(';')
            
            bm = None            
            # Check every slice searching for bm without a quote
            for part in bmSplit:
                if ' bm ' in part and not '"' in part:
                    bm = part.split(' bm ')[1].strip()
                    break
            
            # Convert the bm into list, useful when there are more than 1 bm
            # Expected example output when there are more than 1 bm.
            # bmList = ['e4', 'd4']
            if bm is not None:
                bmList = bm.split()
                logging.info('epd bm: %s' % bmList)
        except IndexError:
            logging.exception('Index error in getting bm of epd')
            logging.debug(epdLine)
            raise
        except Exception:
            logging.exception('Unexpected exception in getting bm of epd')
            logging.debug(epdLine)
            raise
            
        # (2) Get the am in the epd
        try:
            # Split epd by semi-colon, then examine every slice to find am
            amSplit = epdLine.split(';')
            
            am = None            
            # Check every slice searching for am without a quote
            for part in amSplit:
                if ' am ' in part and not '"' in part:
                    am = part.split(' am ')[1].strip()
                    break
            if am is not None:
                amList = am.split()
                logging.info('epd am: %s' % amList)
        except IndexError:
            logging.exception('Index error in getting am of epd')
            logging.debug(epdLine)
            raise
        except Exception:
            logging.exception('Unexpected exception in getting am of epd')
            logging.debug(epdLine)
            raise
            
        return bmList, amList

    def IsCorrectEngineBm(self, engineBm, epdBm, epdAm):
        """ Return True if engineBm is in epdBm or if engineBm is not
            in epdAm, otherwise return False.
        """
        if len(epdBm) >= 1 and engineBm in epdBm:
            return True
        
        if len(epdAm) >= 1 and engineBm not in epdAm:
            return True
        
        return False

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

                # Add hmvc to create a FEN for the engine.
                # Use 1 for fmvn
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

                # Get the bm and/or am move in the epd line.
                epdBm, epdAm = self.GetEpdBmAm(epdLine)  
                
                # If the epd line has no bm or am then we just skip it.
                if len(epdBm) <= 0 and len(epdAm) <= 0:
                    # Show warning in console.
                    print('Warning! epd \"%s\"' %(epd))
                    print('has no bm and am opcodes - skipped.\n')
                    continue

                # Get engine analysis, we are only interested on bm.
                _, _, bm, _ = self.GetEpdEngineSearchScore(fen)
                
                # The percentage correct is based on valid epd only
                cntValidEpd += 1

                # Show progress in console.
                print('engine bm: %s' %(bm))

                # If engine bm is in the epdBm list then increment cntCorrect.
                # If not, check if engine bm is not in epdAm list, if so
                # increment the cntCorrect.
                isCorrect = self.IsCorrectEngineBm(bm, epdBm, epdAm)
                if isCorrect:
                    cntCorrect += 1
                print('correct: %s' % ('Yes' if isCorrect else 'No'))
                print('num correct: %d' % (cntCorrect))

        # Print test summary.
        pctCorrect = 0.0
        if cntValidEpd:
            pctCorrect = (100.0 * cntCorrect)/cntValidEpd

        # Print summary to console
        print(':: EPD %s TEST RESULTS ::\n' %(self.infn))
        print('Total epd lines       : %d' %(cntEpd))
        print('Total tested positions: %d' %(cntValidEpd))
        print('Total correct         : %d' %(cntCorrect))
        print('Correct percentage    : %0.2f' %(pctCorrect))

        # Write to output file, that was specified in -outfile option.
        with open(self.outfn, 'a') as f:
            f.write(':: EPD %s TEST RESULTS ::\n' %(self.infn))
            f.write('Engine        : %s\n' %(self.engIdName))
            f.write('Time/pos (sec): %0.1f\n\n' %(self.moveTime/1000.0))
            f.write('Total epd lines       : %d\n' %(cntEpd))
            f.write('Total tested positions: %d\n' %(cntValidEpd))
            f.write('Total correct         : %d\n' %(cntCorrect))
            f.write('Correct percentage    : %0.2f\n\n' %(pctCorrect))
            

def main():
    parser = argparse.ArgumentParser(prog='%s v%s' % (APP_NAME, APP_VERSION),
                description='Read pgn and analyze games in it or analyze ' +
                'epd file or test engines with epd test suites',
                epilog='%(prog)s')
    parser.add_argument('-i', '--infile', 
                        help='input pgn or EPD filename', 
                        required=True)
    parser.add_argument('-o', '--outfile', 
                        help='output filename', 
                        required=True)
    parser.add_argument('-e', '--enginefile', 
                        help='input engine filename', 
                        required=True)
    parser.add_argument('-n', '--engineoptions', 
        help='input engine options, like threads, hash and others ' +
        'example: --engineoptions "Hash value 128, Threads value 1"', 
                        required=False)
    parser.add_argument('--bookfile', 
                        help='input book filename',
                        required=False)
    parser.add_argument('--eval', 
                        help='eval can be static or search. static ' + 
        'uses static evaluation of Stockfish', 
                        choices=['static','search'],
                        required=True)
    parser.add_argument("--movetime", 
                        help='input analysis time per position in ms, ' + 
                        '(default=1000)', default=1000,
                        type=int, required=False)
    parser.add_argument("--depth", 
                        help='input analysis depth, (default=0)', default=0,
                        type=int, required=False)
    parser.add_argument("--movestart", 
                        help='input move number to start the analysis, ' + 
                        'this is used when analyzing games, (default=8)',
                        default=8, type=int, required=False)
    parser.add_argument('--log', action='store_true',
                        help='Save log to chess_artist_log.txt')
    parser.add_argument('--job', 
                        help='type of jobs to execute, can be analyze or ' +
        'test. For game analysis use analyze, for annotating epd use ' + 
        'analyze too, for testing engine with epd suite, use test',
                        choices=['analyze','test'],
                        required=True)

    args = parser.parse_args()
    
    inputFile = args.infile
    outputFile = args.outfile
    engineFile = args.enginefile
    evalType = args.eval  # static, search
    bookFile = args.bookfile  # 'Cerebellum_Light.bin'
    analysisMoveTime = args.movetime  # ms or 1s
    analysisMoveStart = args.movestart
    jobType = args.job  # analyze, test
    engOption = args.engineoptions
        
    # Convert options to dict.
    options = {'-eval': evalType,
               '-movetime': analysisMoveTime,
               '-movestart': analysisMoveStart,
               '-job': jobType,
               '-engineoptions': engOption,
               '-bookfile': bookFile,
               '-depth': args.depth
               }
    
    if args.log:
        log_format = '%(asctime)s :: pid: %(process)d :: tid: %(thread)d :: %(levelname)s :: %(message)s'
        logging.basicConfig(filename='chess_artist_log.txt',
                            filemode='w', level=logging.DEBUG,
                            format=log_format)

    # Create an object of class Analyze.
    g = Analyze(inputFile, outputFile, engineFile, **options)
    g.PrintEngineIdName()

    # Process input file depending on the infile format
    if inputFile.endswith('.epd'):
        if jobType == 'test':
            logging.info('Test engine with epd suite')
            g.TestEngineWithEpd()
        else:
            logging.info('Annotate epd')
            g.AnnotateEpd()            
    elif inputFile.endswith('.pgn'):
        logging.info('Annotate game')
        g.AnnotatePgn()

    print('Done!!\n')  
    sys.exit(0)


if __name__ == "__main__":
    main()
