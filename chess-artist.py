"""
Chess Artist
"""


import os
import sys
import subprocess
import argparse
import random
import logging
import time
import chess.pgn
import chess.polyglot

sr = random.SystemRandom()


# Constants
APP_NAME = 'Chess Artist'
APP_VERSION = 'v2.5'
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
        'Marvellous', 'Terrific', 'Splendid', 'Magnificient', 'Admirable',
        'Brilliant', 'Cool']
BETTER = ['Better', 'Preferable', 'More useful', 'Worthier', 'Superior',
          'More valuable']
BOOK_COMMENT = 'Polyglot book'
PLAN_COMMENT = ['with the idea of', 'planning', 'followed by']
    

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
        self.analysisMoveEnd = opt['-moveend']
        self.jobType = opt['-job']
        self.engineOptions = opt['-engineoptions']
        self.bookFile = opt['-bookfile']
        self.depth = opt['-depth']
        self.puzzlefn = opt['-puzzle']
        self.wordyComment = opt['-wordy']
        self.player = opt['-player']
        self.playerandopp = opt['-playerandopp']
        self.color = opt['-color']
        self.loss = opt['-loss']
        self.draw = opt['-draw']
        self.minScoreStopAnalysis = opt['-min-score-stop-analysis']
        self.maxScoreStopAnalysis = opt['-max-score-stop-analysis']
        self.bookMove = None
        self.passedPawnIsGood = False
        self.whitePassedPawnCommentCnt = 0
        self.blackPassedPawnCommentCnt = 0
        self.kingSafetyIsGood = False
        self.whiteKingSafetyCommentCnt = 0
        self.blackKingSafetyCommentCnt = 0
        self.mobilityIsGood = False
        self.whiteMobilityCommentCnt = 0
        self.blackMobilityCommentCnt = 0
        self.writeCnt = 0
        self.engIdName = self.GetEngineIdName()
        self.matBal = []
        self.matIsSacrificed = False
        self.blunderCnt = {'w': 0, 'b': 0}
        self.badCnt = {'w': 0, 'b': 0}
        self.variantTag = None
        
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
    
    def GetBadNag(self, side, posScore, engScore):
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
            self.blunderCnt['w' if side else 'b'] += 1
            
        # Mistake ?
        elif posScore < -SLIGHT_SCORE and engScore >= -SLIGHT_SCORE:
            moveNag = '$2'
            self.badCnt['w' if side else 'b'] += 1
            
        # Dubious ?!
        elif posScore < -DRAW_SCORE and engScore >= -DRAW_SCORE:
            moveNag = '$6'

        # Mistake ? if engScore is winning and posScore is not winning
        elif engScore > MODERATE_SCORE and posScore <= MODERATE_SCORE:
            moveNag = '$2'
            self.badCnt['w' if side else 'b'] += 1

        # Mistake ? if posScore is too far from engScore by 0.50 or more
        elif engScore >= -MODERATE_SCORE and engScore - posScore >= +0.50:
            moveNag = '$2'
            self.badCnt['w' if side else 'b'] += 1

        # Exception, add ! if posScore > engScore
        if posScore >= -SLIGHT_SCORE and posScore > engScore:
            moveNag = '$1'

        # Exception, add !? if posScore == engScore
        elif posScore >= -SLIGHT_SCORE and posScore == engScore:
            moveNag = '$5'
        return moveNag

    def PreComment(self, side, engScore, posScore):
        """ returns a comment for the engine variation """
        if not self.wordyComment:
            return ''
        
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
                if self.passedPawnIsGood:
                    f.write('%d. %s {%+0.2f, %s} ' % (moveNumber, sanMove,
                            posScore, 'with a better passer'))
                    self.whitePassedPawnCommentCnt += 1
                elif self.kingSafetyIsGood:
                    f.write('%d. %s {%+0.2f, with a better king safety} ' %(
                            moveNumber, sanMove, posScore))
                    self.whiteKingSafetyCommentCnt += 1
                elif self.mobilityIsGood:
                    f.write('%d. %s {%+0.2f, with a better piece mobility} ' %(
                            moveNumber, sanMove, posScore))
                    self.whiteMobilityCommentCnt += 1
                elif self.matIsSacrificed:
                    f.write('%d. %s {%+0.2f, black had sacrificed material} ' %(
                            moveNumber, sanMove, posScore))
                else:
                    f.write('%d. %s {%+0.2f} ' %(moveNumber, sanMove, posScore))
            else:
                if self.passedPawnIsGood:
                    f.write('%d... %s {%+0.2f, %s} ' % (moveNumber, sanMove,
                            posScore, 'with a better passer'))
                    self.blackPassedPawnCommentCnt += 1
                elif self.kingSafetyIsGood:
                    f.write('%d... %s {%+0.2f, with a better king safety} ' %(
                            moveNumber, sanMove, posScore))
                    self.blackKingSafetyCommentCnt += 1
                elif self.mobilityIsGood:
                    f.write('%d... %s {%+0.2f, with a better piece mobility} ' %(
                            moveNumber, sanMove, posScore))
                    self.blackMobilityCommentCnt += 1
                elif self.matIsSacrificed:
                    f.write('%d... %s {%+0.2f, white had sacrificed material} ' %(
                            moveNumber, sanMove, posScore))
                else:
                    f.write('%d... %s {%+0.2f} ' % (moveNumber, sanMove, posScore))

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

                    if self.matIsSacrificed:
                        if moveNag == '$0':
                            f.write('%d. %s {%+0.2f, black had sacrificed material} ({%s} %s {%+0.2f}) ' % (
                                    moveNumber, sanMove, posScore, varComment,
                                    pvLine, engScore))
                        else:
                            f.write('%d. %s %s {%+0.2f, black had sacrificed material} ({%s} %s {%+0.2f}) ' % (
                                    moveNumber, sanMove, moveNag, posScore, varComment,
                                    pvLine, engScore))
                    else:  
                        if moveNag == '$0':
                            f.write('%d. %s {%+0.2f} ({%s} %s {%+0.2f}) ' % (
                                    moveNumber, sanMove, posScore, varComment,
                                    pvLine, engScore))
                        else:
                            f.write('%d. %s %s {%+0.2f} ({%s} %s {%+0.2f}) ' % (
                                    moveNumber, sanMove, moveNag, posScore, varComment,
                                    pvLine, engScore))
                else:
                    moveNag = self.GetGoodNag(side, posScore, engScore,
                                              complexityNumber, moveChanges)
                    if threatMove is None:
                        if self.passedPawnIsGood:
                            self.whitePassedPawnCommentCnt += 1
                            if moveNag == '$0':
                                f.write('%d. %s {%+0.2f, with a better passer} ' % (
                                        moveNumber, sanMove, posScore))
                            else:
                                f.write('%d. %s %s {%+0.2f, with a better passer} ' % (
                                        moveNumber, sanMove, moveNag, posScore))
                        elif self.kingSafetyIsGood:
                            self.whiteKingSafetyCommentCnt += 1
                            if moveNag == '$0':
                                f.write('%d. %s {%+0.2f, with a better king safety} ' % (
                                        moveNumber, sanMove, posScore))
                            else:
                                f.write('%d. %s %s {%+0.2f, with a better king safety} ' % (
                                        moveNumber, sanMove, moveNag, posScore))
                        elif self.mobilityIsGood:
                            self.whiteMobilityCommentCnt += 1
                            if moveNag == '$0':
                                f.write('%d. %s {%+0.2f, with a better piece mobility} ' % (
                                        moveNumber, sanMove, posScore))
                            else:
                                f.write('%d. %s %s {%+0.2f, with a better piece mobility} ' % (
                                        moveNumber, sanMove, moveNag, posScore))
                        elif self.matIsSacrificed:
                            if moveNag == '$0':
                                f.write('%d. %s {%+0.2f, black had sacrificed material} ' % (
                                        moveNumber, sanMove, posScore))
                            else:
                                f.write('%d. %s %s {%+0.2f, black had sacrificed material} ' % (
                                        moveNumber, sanMove, moveNag, posScore))
                        else:
                            if moveNag == '$0':
                                f.write('%d. %s {%+0.2f} ' %(
                                        moveNumber, sanMove, posScore))
                            else:
                                f.write('%d. %s %s {%+0.2f} ' %(moveNumber, sanMove,
                                        moveNag, posScore))
                    else:
                        if moveNag == '$0':
                            f.write('{, %s %s} %d. %s {%+0.2f} ' % (
                                    sr.choice(PLAN_COMMENT), threatMove,
                                    moveNumber, sanMove, posScore))
                        else:
                            f.write('{, %s %s} %d. %s %s {%+0.2f} ' % (
                                    sr.choice(PLAN_COMMENT), threatMove,
                                    moveNumber, sanMove, moveNag, posScore))
            else:
                if sanMove != engMove:
                    moveNag = self.GetBadNag(side, posScore, engScore)

                    # Add better is symbol before the engine variation
                    varComment = self.PreComment(side, engScore, posScore)

                    if self.matIsSacrificed:
                        if moveNag == '$0':
                            f.write('%d... %s {%+0.2f, white had sacrificed material} ({%s} %s {%+0.2f}) ' % (
                                    moveNumber, sanMove, posScore,
                                    varComment, pvLine, engScore))
                        else:
                            f.write('%d... %s %s {%+0.2f, white had sacrificed material} ({%s} %s {%+0.2f}) ' % (
                                    moveNumber, sanMove, moveNag, posScore,
                                    varComment, pvLine, engScore))
                    else:
                        if moveNag == '$0':
                            f.write('%d... %s {%+0.2f} ({%s} %s {%+0.2f}) ' % (
                                    moveNumber, sanMove, posScore,
                                    varComment, pvLine, engScore))
                        else:
                            f.write('%d... %s %s {%+0.2f} ({%s} %s {%+0.2f}) ' % (
                                    moveNumber, sanMove, moveNag, posScore,
                                    varComment, pvLine, engScore))
                else:
                    moveNag = self.GetGoodNag(side, posScore, engScore,
                                              complexityNumber, moveChanges)
                    if threatMove is None:
                        if self.passedPawnIsGood:
                            self.blackPassedPawnCommentCnt += 1
                            if moveNag == '$0':
                                f.write('%d... %s {%+0.2f, with a better passer} ' % (
                                        moveNumber, sanMove, posScore))
                            else:
                                f.write('%d... %s %s {%+0.2f, with a better passer} ' % (
                                        moveNumber, sanMove, moveNag, posScore))
                        elif self.kingSafetyIsGood:
                            self.blackKingSafetyCommentCnt += 1
                            if moveNag == '$0':
                                f.write('%d... %s {%+0.2f, with a better king safety} ' % (
                                        moveNumber, sanMove, posScore))
                            else:
                                f.write('%d... %s %s {%+0.2f, with a better king safety} ' % (
                                        moveNumber, sanMove, moveNag, posScore))
                        elif self.mobilityIsGood:
                            self.blackMobilityCommentCnt += 1
                            if moveNag == '$0':
                                f.write('%d... %s {%+0.2f, with a better piece mobility} ' % (
                                        moveNumber, sanMove, posScore))
                            else:
                                f.write('%d... %s %s {%+0.2f, with a better piece mobility} ' % (
                                        moveNumber, sanMove, moveNag, posScore))
                        elif self.matIsSacrificed:
                            if moveNag == '$0':
                                f.write('%d... %s {%+0.2f, white had sacrificed material} ' % (
                                        moveNumber, sanMove, posScore))
                            else:
                                f.write('%d... %s %s {%+0.2f, white had sacrificed material} ' % (
                                        moveNumber, sanMove, moveNag, posScore))
                        else:
                            if moveNag == '$0':
                                f.write('%d... %s {%+0.2f} ' % (
                                        moveNumber, sanMove, posScore))
                            else:
                                f.write('%d... %s %s {%+0.2f} ' % (
                                        moveNumber, sanMove, moveNag, posScore))
                    else:
                        if moveNag == '$0':
                            f.write('{, %s %s} %d... %s {%+0.2f} ' % (
                                    sr.choice(PLAN_COMMENT), threatMove,
                                    moveNumber, sanMove, posScore))
                        else:
                            f.write('{, %s %s} %d... %s %s {%+0.2f} ' % (
                                    sr.choice(PLAN_COMMENT), threatMove,
                                    moveNumber, sanMove, moveNag, posScore))

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
                    moveNag = self.GetBadNag(side, posScore, engScore)
                    moveNag = '$0' if self.moveTime < 20000 else moveNag

                    # Add better is symbol before the engine variation
                    varComment = self.PreComment(side, engScore, posScore)

                    if moveNag == '$0':
                        f.write('%d. %s {%+0.2f} (%d. %s {%s}) ({%s} %s {%+0.2f}) '\
                                %(moveNumber, sanMove, posScore,
                                  moveNumber, bookMove, BOOK_COMMENT,
                                  varComment, pvLine, engScore))
                    else:
                        f.write('%d. %s %s {%+0.2f} (%d. %s {%s}) ({%s} %s {%+0.2f}) '\
                                %(moveNumber, sanMove, moveNag, posScore,
                                  moveNumber, bookMove, BOOK_COMMENT,
                                  varComment, pvLine, engScore))
                else:
                    moveNag = self.GetGoodNag(side, posScore, engScore,
                                              complexityNumber, moveChanges)
                    if threatMove is not None:
                        if moveNag == '$0':
                            f.write('{, %s %s} %d. %s {%+0.2f} (%d. %s {%s}) '%(
                                    sr.choice(PLAN_COMMENT), threatMove,
                                    moveNumber, sanMove, posScore,
                                    moveNumber, bookMove, BOOK_COMMENT))
                        else:
                            f.write('{, %s %s} %d. %s %s {%+0.2f} (%d. %s {%s}) '%(
                                    sr.choice(PLAN_COMMENT), threatMove,
                                    moveNumber, sanMove, moveNag, posScore,
                                    moveNumber, bookMove, BOOK_COMMENT))
                    else:
                        if moveNag == '$0':
                            f.write('%d. %s {%+0.2f} (%d. %s {%s}) ' %(
                                    moveNumber, sanMove, posScore, moveNumber,
                                    bookMove, BOOK_COMMENT))
                        else:
                            f.write('%d. %s %s {%+0.2f} (%d. %s {%s}) ' %(
                                    moveNumber, sanMove, moveNag, posScore, moveNumber,
                                    bookMove, BOOK_COMMENT))
            else:
                if sanMove != engMove:
                    moveNag = self.GetBadNag(side, posScore, engScore)
                    moveNag = '$0' if self.moveTime < 20000 else moveNag

                    # Add better is symbol before the engine variation
                    varComment = self.PreComment(side, engScore, posScore)

                    if moveNag == '$0':
                        f.write('%d... %s {%+0.2f} (%d... %s {%s}) ({%s} %s {%+0.2f}) '\
                                %(moveNumber, sanMove, posScore,
                                  moveNumber, bookMove, BOOK_COMMENT,
                                  varComment, pvLine, engScore))
                    else:
                        f.write('%d... %s %s {%+0.2f} (%d... %s {%s}) ({%s} %s {%+0.2f}) '\
                                %(moveNumber, sanMove, moveNag, posScore,
                                  moveNumber, bookMove, BOOK_COMMENT,
                                  varComment, pvLine, engScore))
                else:
                    moveNag = self.GetGoodNag(
                            side, posScore, engScore, complexityNumber,
                            moveChanges)
                    moveNag = '$0' if self.moveTime < 20000 else moveNag
                    if threatMove is not None:
                        if moveNag == '$0':
                            f.write('{, %s %s} %d... %s {%+0.2f} (%d... %s {%s}) '\
                                    %(sr.choice(PLAN_COMMENT), threatMove,
                                    moveNumber, sanMove, posScore, moveNumber,
                                    bookMove, BOOK_COMMENT))
                        else:
                            f.write('{, %s %s} %d... %s %s {%+0.2f} (%d... %s {%s}) '\
                                    %(sr.choice(PLAN_COMMENT), threatMove,
                                    moveNumber, sanMove, moveNag, posScore, moveNumber,
                                    bookMove, BOOK_COMMENT))
                    else:
                        if moveNag == '$0':
                            f.write('%d... %s {%+0.2f} (%d... %s {%s}) ' % (
                                    moveNumber, sanMove, posScore, moveNumber,
                                    bookMove, BOOK_COMMENT))
                        else:
                            f.write('%d... %s %s {%+0.2f} (%d... %s {%s}) ' % (
                                    moveNumber, sanMove, moveNag, posScore,
                                    moveNumber, bookMove, BOOK_COMMENT))

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
        isWritePosScore = posScore is not None and bookMove is None and \
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
        isWritePosScoreEngMove = posScore is not None and bookMove is None and\
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
    
    @staticmethod
    def GetMaterialBalance(fen):
        """ 
        Returns material balance in wpov from a given fen.
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
        
        return 10*(Q - q) + 5*(R - r) + 3*(B - b) + 3*(N - n) + (P - p)
    
    def GetEngineIdName(self):
        """ Returns the engine id name """
        engineIdName = self.eng[0:-4]
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, bufsize=1)
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
    
    def IsKingSafetyGood(self, nextFen, side):
        """ 
        Returns True if king safety of side not to move is bad. This is only
        applicable for Stockfish or Brainfish engines.
        Example line to be parsed:
            King safety |  3.01  3.87 |  0.08  0.39 |  2.92  3.48
        """
        logging.info('Check king safety')
        
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, bufsize=1)
        
        self.Send(p, 'uci')
        self.ReadEngineReply(p, 'uci')      
        self.Send(p, 'ucinewgame')
        self.Send(p, 'position fen %s' % nextFen)
        self.Send(p, 'eval')
        
        # Parse the output
        kingSafetyCommentNext = None
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            
            if 'King safety ' in line:
                kingSafetyCommentNext = line
                break
            if 'total evaluation:' in line.lower():
                break

        self.Send(p, 'quit')
        p.communicate()
        
        if kingSafetyCommentNext is None:
            return False

        # Net score white POV
        whiteMgKingSafetyNext = float(kingSafetyCommentNext.split()[9])
        
        # Evaluate the king safety of side not to move based on curFen
        sideToEvaluate = not side
        
        # If white
        if sideToEvaluate:
            if whiteMgKingSafetyNext >= 1.0:
                return True
        else:
            if whiteMgKingSafetyNext <= -1.0:
                return True

        return False 

    def IsPassedPawnGood(self, fen, side):
        """ 
        Return True if passed pawn eval of side to move is good. We send a fen
        and eval command to stockfish or brainfish engines.
        Example output:
            Passed |  3.01  3.87 |  0.08  0.39 |  2.92  3.48
            We will extract the mg=2.92, and eg=3.48. These values are  wpov
            and in pawn unit. 2.92 is 2 plus pawns or almost 3 pawns.
        """
        logging.info('Checking for a good passer')
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, bufsize=1)
        self.Send(p, 'uci')
        self.ReadEngineReply(p, 'uci')
        self.Send(p, 'ucinewgame')
        self.Send(p, 'position fen %s' % fen)
        self.Send(p, 'eval')
        
        # Parse the output
        passedPawnComment = None
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            logging.info(line)
            
            if 'Passed ' in line:
                passedPawnComment = line
                break
            if 'total evaluation:' in line.lower():
                break

        self.Send(p, 'quit')
        p.communicate()
        
        if passedPawnComment is None:
            return False
        
        MgPassedValue = float(passedPawnComment.split()[8])
        EgPassedValue = float(passedPawnComment.split()[9])
        logging.info('mgpassed: %0.1f, egpassed: %0.1f' % (MgPassedValue, EgPassedValue))
        
        if side:
            if MgPassedValue >= 1.0 and EgPassedValue >= 1.0:
                logging.info('white passed pawn value %0.1f is good' % MgPassedValue)
                return True
        else:
            if MgPassedValue <= -1.0 and EgPassedValue <= -1.0:
                logging.info('black passed pawn value %0.1f is good' % MgPassedValue)
                return True

        return False
    
    def IsMobilityGood(self, fen, side):
        """ 
        Return True if net mobility of side to move is good. We send a fen
        and eval command to stockfish or brainfish engines and then extract
        the Mobility Mg/Eg values (white pov).
        Tested on engine Stockfish 091019, win 7 OS.
        """
        MOBILITY_THRESHOLD = 0.5
        logging.info('Checking if side to move has a good mobility')
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, bufsize=1)
        self.Send(p, 'uci')
        self.ReadEngineReply(p, 'uci')
        self.Send(p, 'ucinewgame')
        self.Send(p, 'position fen %s' % fen)
        self.Send(p, 'eval')
        
        # Parse the output
        mobilityComment = None
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            logging.info(line)
            
            if 'Mobility ' in line:
                mobilityComment = line
            if 'total evaluation:' in line.lower():
                break

        self.Send(p, 'quit')
        p.communicate()
        
        if mobilityComment is None:
            logging.warning('Mobility comment from eval command is missing.')
            return False
        
        MgMobilityValue = float(mobilityComment.split()[8])
        EgMobilityValue = float(mobilityComment.split()[9])
        logging.info('mgmob: %0.2f, egmob: %0.2f' % (MgMobilityValue,
                                                     EgMobilityValue))
        
        if side:
            if MgMobilityValue >= MOBILITY_THRESHOLD and \
                    EgMobilityValue >= MOBILITY_THRESHOLD:
                logging.info('white net mg mobility value of %0.2f is good' % MgMobilityValue)
                logging.info('white net eg mobility value of %0.2f is good' % EgMobilityValue)
                return True
        else:
            if MgMobilityValue <= -MOBILITY_THRESHOLD and \
                    EgMobilityValue <= -MOBILITY_THRESHOLD:
                logging.info('black net mg mobility value of %0.2f is good' % MgMobilityValue)
                logging.info('black net eg mobility value of %0.2f is good' % EgMobilityValue)
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
        
        if self.variantTag in ['chess960', 'chess 960']:
            self.Send(p, 'setoption name UCI_Chess960 value true')
            
        # If nothing is defined, means that the user relies on the default
        if engOptionValue is None:
            return

        # Convert engOptionValue to list
        if ',' in engOptionValue:
            engOptionValueList = engOptionValue.split(',')
            for n in engOptionValueList:
                value = n.strip()
                self.Send(p, 'setoption name %s' % value)
        else:
            value = engOptionValue.strip()
            self.Send(p, 'setoption name %s' % value)

    def GetStaticEvalAfterMove(self, fen):
        """ 
        Returns static eval by running the engine, setup position fen and
        send eval command. This is only applicable for Stockfish engine or
        engines that returns similar output when given an eval command.
        """
        logging.info('Get search score after making the game move.')
        score = TEST_SEARCH_SCORE

        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, bufsize=1)

        # Send command to engine.
        self.Send(p, 'uci')
        self.ReadEngineReply(p, 'uci')
        self.SetEngineOptions(p, self.engineOptions)
        self.Send(p, 'isready')
        self.ReadEngineReply(p, 'isready')
        self.Send(p, 'ucinewgame')
        self.Send(p, 'position fen %s' % fen)
        self.Send(p, 'eval')

        # Parse the output and extract the engine static eval.
        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            if 'total evaluation' in line.lower():
                first = line.split('(')[0]
                score = float(first.split()[2])
                logging.info('fen: %s, static score: %0.2f' % (fen, score))
                break
                
        # Quit the engine
        self.Send(p, 'quit')
        p.communicate()
        assert score != TEST_SEARCH_SCORE,\
               'Error! something is wrong in static eval calculation.'
        return score

    def GetThreatMove(self, fen):
        """ 
        Returns threat move after pushing a null move and searching the
        subsequent position.
        """
        logging.debug('Get threat move.')
        bestMove = None
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, bufsize=1)
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
        self.Send(p, 'isready')
        self.ReadEngineReply(p, 'isready')
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
        Returns bestmove, score in pawn unit wpov, complexity number,
        move changes and pv san. 
        """
        logging.info('Get search score before making the game move.')
        scoreCp = TEST_SEARCH_SCORE
        pvLine, pvLineSan = None, None
        searchDepth = 0
        savedMove = []
        complexityNumber = 0
        moveChanges = 0
        isGetComplexityNumber = self.jobType == 'analyze' and\
                                self.moveTime >= COMPLEXITY_MINIMUM_TIME
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, bufsize=1)
        self.Send(p, 'uci')
        self.ReadEngineReply(p, 'uci')
        self.SetEngineOptions(p, self.engineOptions)
        self.Send(p, 'isready')
        self.ReadEngineReply(p, 'isready')
        self.Send(p, 'ucinewgame')
        self.Send(p, 'isready')
        self.ReadEngineReply(p, 'isready')
        self.Send(p, 'position fen %s' % fen)
        self.Send(p, 'go movetime %d' % self.moveTime)

        for eline in iter(p.stdout.readline, ''):        
            line = eline.strip()
            # Save pv move per depth
            if isGetComplexityNumber:
                if 'info depth ' in line and ' pv ' in line and not\
                   'upperbound' in line and not 'lowerbound' in line:
                    logging.debug('<< %s' % line)
                    
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
                logging.debug('<< %s' % line)
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
            
            if len(pvLine) % 2 == 0:
                logging.info('pvLine is even, %s' % pvLine)               
                pvLine = pvLine[:-1]
                logging.info('Change to odd, %s' % pvLine)
                
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

    def GetSearchScoreAfterMove(self, fen, side):
        """ 
        Returns search's score in wpov and in pawn unit.
        """
        scoreCp = None
        
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, bufsize=1)
        self.Send(p, 'uci')
        self.ReadEngineReply(p, 'uci')
        self.SetEngineOptions(p, self.engineOptions)
        self.Send(p, 'isready')
        self.ReadEngineReply(p, 'isready')
        self.Send(p, 'ucinewgame')
        self.Send(p, 'isready')
        self.ReadEngineReply(p, 'isready')
        self.Send(p, 'position fen %s' % fen)
        self.Send(p, 'go movetime %d' % self.moveTime)

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
                logging.info('<< %s' % line)
                break

        self.Send(p, 'quit')
        p.communicate()
        
        if scoreCp is None:
            return scoreCp
            
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
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, bufsize=1)
        self.Send(p, 'uci')
        self.ReadEngineReply(p, 'uci')
        self.SetEngineOptions(p, self.engineOptions)
        self.Send(p, 'isready')
        self.ReadEngineReply(p, 'isready')
        self.Send(p, 'ucinewgame')
        self.Send(p, 'isready')
        self.ReadEngineReply(p, 'isready')
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
        """ 
        Returns ce and Ae opcodes. This is only applicable for Stockfish.
        """

        # Initialize
        scoreP = TEST_SEARCH_SCORE

        # Run the engine.
        p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, bufsize=1)
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
            if 'total evaluation: ' in line.lower():
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

    def WriteTerminationMarker(self, playerColor, res):
        """
        Write termination marker in the output game.
        """
        with open(self.outfn, 'a') as f:
            if self.playerandopp is not None:
                if self.color == 'white' and playerColor == 'white' or \
                        self.color == 'black' and playerColor == 'black':
                    f.write('{WhiteBlunder=%d, BlackBunder=%d, WhiteBad=%d, BlackBad=%d} %s\n\n' % (
                                self.blunderCnt['w'], self.blunderCnt['b'],
                                self.badCnt['w'], self.badCnt['b'], res))
                else:
                    f.write('%s\n\n' % (res))
            else:
                if self.color is None and self.player is None:
                    f.write('{WhiteBlunder=%d, BlackBunder=%d, WhiteBad=%d, BlackBad=%d} %s\n\n' % (
                            self.blunderCnt['w'], self.blunderCnt['b'],
                            self.badCnt['w'], self.badCnt['b'], res))
                elif self.color is not None and self.player is not None:
                    if playerColor == 'white' and self.color == 'white':
                        f.write('{WhiteBlunder=%d, WhiteBad=%d} %s\n\n' % (
                            self.blunderCnt['w'], self.badCnt['w'], res))
                    elif playerColor == 'black' and self.color == 'black':
                        f.write('{BlackBlunder=%d, BlackBad=%d} %s\n\n' % (
                            self.blunderCnt['b'], self.badCnt['b'], res))
                    else:
                        f.write('%s\n\n' % (res))
                elif self.color is not None:
                    if self.color == 'white':
                        f.write('{WhiteBlunder=%d, WhiteBad=%d} %s\n\n' % (
                            self.blunderCnt['w'], self.badCnt['w'], res))
                    else:
                        f.write('{BlackBlunder=%d, BlackBad=%d} %s\n\n' % (
                            self.blunderCnt['b'], self.badCnt['b'], res))
                else:
                    assert self.player is not None
                    if playerColor == 'white':
                        f.write('{WhiteBlunder=%d, WhiteBad=%d} %s\n\n' % (
                            self.blunderCnt['w'], self.badCnt['w'], res))
                    else:
                        f.write('{BlackBlunder=%d, BlackBad=%d} %s\n\n' % (
                            self.blunderCnt['b'], self.badCnt['b'], res))                

    @staticmethod
    def SaveMaterialBalance(game):
        """
        Visit all positions of the game and returns material balance in wpov.
        Returned value is a list of list [[fen1, matbal1], [fen2, matbal2] ...]
        """
        mat = []
        gameNode = game
        while gameNode.variations:
            board = gameNode.board()
            fen = board.fen()
            mbal = Analyze.GetMaterialBalance(board.fen())
            mat.append([fen, mbal])
            
            nextNode = gameNode.variation(0)
            
            gameNode = nextNode
            
        endFen = nextNode.board().fen()
        mat.append([endFen, Analyze.GetMaterialBalance(endFen)])
            
        return mat
    
    @staticmethod
    def GetSacrificedMaterial(fen, matBal):
        """
        Returns value of sacrificed material, Q=10, R=5, B=N=3, P=1
        
        :matBal: Is a list of list or [[fen1, matbal1], [fen2, matbal2] ...]
                 where fen1 can be startpos fen
        
        Pattern [0, 1, 1]: white is ahead so black had sacs material
        Pattern [0, -1, -1]: black is ahead so white had sacs material
        0, 1, 1 are material balance wpov from fen1 to fen n, n = total plies.
        """
        for i, n in enumerate(matBal):
            fenVal = n[0]
            
            if fen != fenVal:
                continue
            
            # Material balance that starts from 0 and look ahead of 2 plies
            if matBal[i][1] == 0:
                if i + 2 < len(matBal):
                    # White is pawn ahead
                    if matBal[i+1][1] == 1 and matBal[i+2][1] == 1:
                        logging.info(fenVal)
                        logging.info('Black sacs 1 pawn')
                        return 1
                    
                    if matBal[i+1][1] == 2 and matBal[i+2][1] == 2:
                        logging.info(fenVal)
                        logging.info('Black sacs 2 pawn')
                        return 2
                    
                    if matBal[i+1][1] == 3 and matBal[i+2][1] == 3:
                        logging.info(fenVal)
                        logging.info('Black sacs 3 pawn')
                        return 3
                    
                    # Black is a pawn ahead
                    if matBal[i+1][1] == -1 and matBal[i+2][1] == -1:
                        logging.info(fenVal)
                        logging.info('White sacs 1 pawn')
                        return -1
                    
                    if matBal[i+1][1] == -2 and matBal[i+2][1] == -2:
                        logging.info(fenVal)
                        logging.info('White sacs 2 pawn')
                        return -2
                    
                    if matBal[i+1][1] == -3 and matBal[i+2][1] == -3:
                        logging.info(fenVal)
                        logging.info('White sacs 3 pawn')
                        return -3
                    
        return 0 
    
    @staticmethod
    def relative_score(side, score):
        """
        Return score in side pov.
        
        :score: is wpov in pawn unit        
        """
        return score if side else -score
    
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
            
            self.variantTag = None            
            try:
                self.variantTag = game.headers["Variant"]
                logging.info(f'game Variant tag: {self.variantTag}')
            except KeyError:
                logging.info('There is no Variant tag in the game header.')
            except:
                logging.exception('Error in getting game variant tag value')
            
            # Analyze games by player            
            if self.player is not None or self.playerandopp is not None:
                playerName = self.player or self.playerandopp
                wplayer = game.headers['White']
                bplayer = game.headers['Black']

                if playerName != wplayer and playerName != bplayer:
                    game = chess.pgn.read_game(pgnHandle)
                    continue
                
                if self.loss and not self.draw:
                    gameResult = game.headers['Result']
                    if not (playerName == wplayer and gameResult == '0-1' or \
                            playerName == bplayer and gameResult == '1-0'):
                        game = chess.pgn.read_game(pgnHandle)
                        continue
                elif not self.loss and self.draw:
                    gameResult = game.headers['Result']
                    if not (playerName == wplayer and gameResult == '1/2-1/2' or \
                            playerName == bplayer and gameResult == '1/2-1/2'):
                        game = chess.pgn.read_game(pgnHandle)
                        continue
                elif self.loss and self.draw:
                    gameResult = game.headers['Result']
                    if not (playerName == wplayer and gameResult != '1-0' or \
                            playerName == bplayer and gameResult != '0-1'):
                        game = chess.pgn.read_game(pgnHandle)
                        continue                       

            # Reset passed pawn comment every game. Passed pawn comment is
            # only done once for white and once for black per game
            self.whitePassedPawnCommentCnt = 0
            self.blackPassedPawnCommentCnt = 0
            self.whiteKingSafetyCommentCnt = 0
            self.blackKingSafetyCommentCnt = 0
            self.whiteMobilityCommentCnt = 0
            self.blackMobilityCommentCnt = 0

            # Initialize blunder/bad move counts in every game
            self.blunderCnt = {'w': 0, 'b': 0}
            self.badCnt = {'w': 0, 'b': 0}

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
                f.write('[Annotator "engine: %s, prog: %s %s"]\n\n' %(
                        engineIdName, APP_NAME, APP_VERSION))

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
                        f.write('{Threads %s, @ %0.1fs/pos, move eval is in pawn unit wpov}\n' %(
                                threadsValue, self.moveTime/1000.0))
                    else:
                        f.write('{Hash %smb, Threads %s, @ %0.1fs/pos, move eval is in pawn unit wpov}\n' %(
                                hashValue, threadsValue, self.moveTime/1000.0))

            # Save result to be written later as game termination marker.
            res = game.headers['Result']
            
            self.matBal = Analyze.SaveMaterialBalance(game)
            logging.info('Material blance wpov:')
            logging.info('%s' % self.matBal)

            # Loop thru the moves within this game.
            gameNode = game        
            while gameNode.variations:
                board = gameNode.board()
                side = board.turn
                fmvn = board.fullmove_number
                curFen = board.fen()
                nextNode = gameNode.variation(0)
                logging.info('game_move: %s, san: %s, iscap: %d' % (
                        nextNode.move, nextNode.san(), board.is_capture(nextNode.move)))
                nextFen = nextNode.board().fen()
                sanMove = nextNode.san()
                complexityNumber, moveChanges = 0, 0
                threatMove = None  
                self.bookMove = None
                self.passedPawnIsGood = False
                self.kingSafetyIsGood = False
                self.mobilityIsGood = False
                self.matIsSacrificed = False
                
                # If --player is specified
                if self.player is not None:
                    if side and self.player == bplayer or not side and self.player == wplayer:
                        self.WriteNotation(side, fmvn, sanMove, self.bookMove,
                                       None, False, None, None, 0, 0,
                                       None, threatMove)
                        gameNode = nextNode
                        continue
                    
                # Analyze specific color or side to move                
                if self.color is not None:
                    isEvaluatePos = False
                    if self.playerandopp is None:
                        if side and self.color == 'black' or not side and self.color == 'white':
                            self.WriteNotation(side, fmvn, sanMove, self.bookMove,
                                           None, False, None, None, 0, 0,
                                           None, threatMove)
                            gameNode = nextNode
                            continue
                    else:
                        # Analyze position of a player by color and its opp
                        if self.playerandopp == wplayer and self.color == 'white':
                            isEvaluatePos = True
                        elif self.playerandopp == bplayer and self.color == 'black':
                            isEvaluatePos = True
                            
                    if not isEvaluatePos:
                        self.WriteNotation(side, fmvn, sanMove, self.bookMove,
                                           None, False, None, None, 0, 0,
                                           None, threatMove)
                        gameNode = nextNode
                        continue                            
                
                print('side: %s, move_num: %d' % ('White' if side else 'Black',
                                                  fmvn))

                # (1) Check move start
                if fmvn < self.analysisMoveStart:
                    self.WriteNotation(side, fmvn, sanMove, self.bookMove,
                                       None, False, None, None, 0, 0,
                                       None, threatMove)
                    gameNode = nextNode
                    continue
                
                # (1.1) Don't analyze beyond analysis move end
                if fmvn > self.analysisMoveEnd:
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
                if self.evalType == 'static':
                    staticScore = self.GetStaticEvalAfterMove(nextFen)
                    posScore = staticScore
                elif self.evalType == 'search':
                    searchScore = self.GetSearchScoreAfterMove(nextFen, side)
                    posScore = searchScore

                # (4) Analyze the position with the engine. Only do this
                # if posScore is not winning or lossing (more than 3.0 pawns).
                engBestMove, engBestScore, pvLine = None, None, None
                if Analyze.relative_score(side, posScore) < self.maxScoreStopAnalysis and \
                        Analyze.relative_score(side, posScore) > self.minScoreStopAnalysis and \
                        self.jobType == 'analyze':
                    engBestMove, engBestScore, complexityNumber, moveChanges,\
                    pvLine = self.GetSearchScoreBeforeMove(curFen, side)

                    if sanMove == engBestMove:
                        print('Game move: %s (%0.2f), Engine bestmove: %s (%0.2f)' % (
                            sanMove, posScore, engBestMove, posScore))
                    else:
                        print('Game move: %s (%0.2f), Engine bestmove: %s (%0.2f)' % (
                            sanMove, posScore, engBestMove, engBestScore))
                    
                # (5) If game is over by checkmate and stalemate after a move              
                isGameOver = nextNode.board().is_checkmate() or\
                        nextNode.board().is_stalemate()

                # (5.1) Calculate the threat move if game move and engine best
                # move is the same and the position is complex and the engine
                # score is not winning or lossing
                if moveChanges >= 3 and sanMove == engBestMove and not\
                    gameNode.board().is_check() and abs(engBestScore) <= 2.0:
                    threatMove = self.GetThreatMove(curFen)
                    
                # (5.2) Check if passed pawn of side to move is good.
                if any(s in engineIdName.lower() for s in ['stockfish', 'brainfish']):
                    if side and self.whitePassedPawnCommentCnt == 0:
                        self.passedPawnIsGood = self.IsPassedPawnGood(
                                curFen, side)
                    elif not side and self.blackPassedPawnCommentCnt == 0:
                        self.passedPawnIsGood = self.IsPassedPawnGood(
                                curFen, side)
                        
                # (5.3) Calculate the king safety of the side to move
                if any(s in engineIdName.lower() for s in ['stockfish', 'brainfish']):
                    if not board.is_capture(nextNode.move) and abs(posScore) <= 1.5:
                        if side and self.whiteKingSafetyCommentCnt == 0:
                            self.kingSafetyIsGood = self.IsKingSafetyGood(nextFen, not side)
                        elif not side and self.blackKingSafetyCommentCnt == 0:
                            self.kingSafetyIsGood = self.IsKingSafetyGood(nextFen, not side)
                            
                # (5.4) Check if mobility of side to move is good.
                if any(s in engineIdName.lower() for s in ['stockfish', 'brainfish']):
                    if abs(posScore) <= 3.0:
                        if side and self.whiteMobilityCommentCnt == 0:
                            self.mobilityIsGood = self.IsMobilityGood(nextFen, side)
                        elif not side and self.blackMobilityCommentCnt == 0:
                            self.mobilityIsGood = self.IsMobilityGood(nextFen, side)
                            
                # Check if a move sacrifices material
                sacMat = Analyze.GetSacrificedMaterial(curFen, self.matBal)
                self.matIsSacrificed = True if sacMat != 0 else False
                
                # (6) Write moves and comments.
                self.WriteNotation(side, fmvn, sanMove, self.bookMove,
                                   posScore, isGameOver,
                                   engBestMove, engBestScore,
                                   complexityNumber, moveChanges,
                                   pvLine, threatMove)
                gameNode = nextNode
            
            # Write blunder/bad counts, and game termination marker to output file.
            pColor = None
            if self.player is not None:
                pColor = 'white' if self.player == wplayer else 'black'
            elif self.playerandopp is not None:
                pColor = 'white' if self.playerandopp == wplayer else 'black'
            self.WriteTerminationMarker(pColor, res)
            
            # Read next game
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
            
    def CreatePuzzle(self):
        """
        Generate chess position puzzle or test positions from a given pgn file.
        
        Analyze position in the game from pgn file, record its pvmove and score
        for the early part of analysis and final bestmove and bestscore after
        the search. If pvmove and bestmove are not the same and score of
        bestmove is higher than score at pvmove then save this as a test
        position.
        """
        print('Creating test positions ...')
        with open(self.infn) as h:
            game = chess.pgn.read_game(h)
            while game:
                gameNode = game        
                while gameNode.variations:
                    board = gameNode.board()
                    fmvn = board.fullmove_number
                    
                    nextNode = gameNode.variation(0)
                    
                    if fmvn < 12:
                        gameNode = nextNode
                        continue

                    fen = board.fen()
                    print('analyzing fen %s ...' % fen)
                    
                    bestMove, bestScore, pvMove, pvScore = \
                            None, -MAX_SCORE, None, -MAX_SCORE
                    
                    # Analyze the current fen                    
                    p = subprocess.Popen(self.eng, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, bufsize=1)
                    self.Send(p, 'uci')
                    self.ReadEngineReply(p, 'uci')
                    self.SetEngineOptions(p, self.engineOptions)
                    self.Send(p, 'isready')
                    self.ReadEngineReply(p, 'isready')
                    self.Send(p, 'ucinewgame')
                    self.Send(p, 'isready')
                    self.ReadEngineReply(p, 'isready')
                    self.Send(p, 'position fen %s' % fen)
                    
                    start_time = time.time()
                    self.Send(p, 'go movetime %s' % self.moveTime)
                    
                    for eline in iter(p.stdout.readline, ''):       
                        line = eline.strip()
                        
                        if 'info depth ' in line and ' pv ' in line and not\
                           'upperbound' in line and not 'lowerbound' in line\
                           and 'score' in line:
                            logging.debug('<< %s' % line)
                            
                            splitLine = line.split()
        
                            # Save pv move and score at quarter of movetime                            
                            if (time.time() - start_time) * 1000 < self.moveTime//4:
                                pvMove = splitLine[splitLine.index('pv')+1].strip()
                                
                                if 'score cp ' in line:
                                    splitStr = line.split()
                                    scoreIndex = splitStr.index('score')
                                    pvScore = int(splitStr[scoreIndex + 2])
                                elif 'score mate ' in line:
                                    splitStr = line.split()
                                    scoreIndex = splitStr.index('score')
                                    mateInN = int(splitStr[scoreIndex + 2])            
                                    pvScore = self.MateDistanceToValue(mateInN)
                                    
                                # Don't save winning or losing positions
                                if abs(pvScore) > 1000:
                                    break
                            else:
                                if 'score cp ' in line:
                                    splitStr = line.split()
                                    scoreIndex = splitStr.index('score')
                                    bestScore = int(splitStr[scoreIndex + 2])
                                elif 'score mate ' in line:
                                    splitStr = line.split()
                                    scoreIndex = splitStr.index('score')
                                    mateInN = int(splitStr[scoreIndex + 2])            
                                    bestScore = self.MateDistanceToValue(mateInN)
            
                        if 'bestmove ' in line:
                            bestMove = line.split()[1]
                            logging.debug('<< %s' % line)
                            break
            
                    self.Send(p, 'quit')
                    p.communicate()
                    
                    logging.info('bestPv: %s, pvScore: %d' % (pvMove, pvScore))
                    logging.info('bestmove: %s, bestScore: %d' % (bestMove, bestScore))
                    
                    # Compare pv move in the first half of the search and bestmove
                    if bestMove != pvMove and bestScore >= pvScore + 10:
                        with open(self.puzzlefn, 'a') as f:
                            f.write('%s bm %s; Ubm %s;\n' % (
                                    board.epd(),
                                    board.san(chess.Move.from_uci(bestMove)),
                                    bestMove))
                    
                    gameNode = nextNode
                    
                game = chess.pgn.read_game(h)    
            

def main():
    parser = argparse.ArgumentParser(prog='%s %s' % (APP_NAME, APP_VERSION),
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
    parser.add_argument("--moveend", 
                        help='input move number to end the analysis, '
                        'this is used when analyzing games, (default=1000)',
                        default=1000, type=int, required=False)
    parser.add_argument('--log', action='store_true',
                        help='Save log to chess_artist_log.txt')
    parser.add_argument('--job', 
                        help='type of jobs to execute, can be analyze or '
                        'test or createpuzzle. '
                        'To create puzzle: '
                        '--infile games.pgn --job createpuzzle, '
                        'To analyze pgn: --infile games.pgn --job analyze, '
                        'To annotate epd: --infile positions.epd --job analyze, '
                        'To test engine with epd: --infile test.epd --job test',
                        choices=['analyze', 'test', 'createpuzzle'],
                        required=True)
    parser.add_argument('--wordycomment', action='store_true',
                        help='There are more words in the move comments such as '
                        'better is, planning, excellent is, Cool is and others.')
    parser.add_argument("--color", 
                        help='enter color of player to analyze, (default=None) ',
                        default=None, required=False)
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--player", 
                        help='enter player name to analyze, (default=None). '
                        'Player opponent moves are not analyzed. '
                        'If you use --player do not use --playerandopp.',
                        default=None, required=False)
    group.add_argument("--playerandopp", 
                        help='enter player name to analyze. Player opponent moves '
                        'are also analyzed, (default=None). '
                        'If you use --playerandopp do not use --player.',
                        default=None, required=False)
    parser.add_argument('--loss', action='store_true',
                        help='This is used to analyze games where a player '
                        'lost his/her game. Example to analyze lost games by '
                        'Mangnus, use: chess-artist.exe --player "Carlsen, Magnus" '
                        '--loss ... other options')
    parser.add_argument('--draw', action='store_true',
                        help='This is used to analyze games where a player '
                        'has drawn his/her game. Example to analyze drawn games by '
                        'Mangnus, use: chess-artist.exe --player "Carlsen, Magnus" '
                        '--draw ... other options')
    parser.add_argument("--min-score-stop-analysis", 
                        help='enter a value in pawn unit to stop the engine analysis, (default=-3.0) '
                        'If the score of the game move is -3.0 or less '
                        'chess-artist would no longer analyze the position to look '
                        'for alternative move.',
                        default=-3.0, type=float, required=False)
    parser.add_argument("--max-score-stop-analysis", 
                        help='enter a value in pawn unit to stop the engine analysis, (default=3.0) '
                        'If the score of the game move is 3 or more '
                        'chess-artist would no longer analyze the position to look '
                        'for alternative move.',
                        default=3.0, type=float, required=False)

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
               '-moveend': args.moveend,
               '-job': jobType,
               '-engineoptions': engOption,
               '-bookfile': bookFile,
               '-depth': args.depth,
               '-puzzle': 'puzzle.epd',
               '-wordy': args.wordycomment,
               '-player': args.player,
               '-playerandopp': args.playerandopp,
               '-color': args.color,
               '-loss': args.loss,
               '-min-score-stop-analysis': args.min_score_stop_analysis,
               '-max-score-stop-analysis': args.max_score_stop_analysis,
               '-draw': args.draw
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
        if jobType == 'analyze':
            logging.info('Annotate game')
            g.AnnotatePgn()
        elif jobType == 'createpuzzle':
            g.CreatePuzzle()
        else:
            logging.info('There is error in command line.')
            print('There is error in command line.')

    print('Done!!\n')  
    sys.exit(0)


if __name__ == "__main__":
    main()
