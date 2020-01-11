# Chess Artist
A python script and exe file that can analyze games in the pgn file, annotate epd file, test engine on chess puzzles or problems and can generate chess puzzles.

## A. Requirements
### 1. Python 2.7
* chess-artist.py version <= 1.0
* [Python 2.7](https://www.python.org/downloads/release/python-2715/)
* [Python-chess v0.21.2](https://github.com/niklasf/python-chess)
* UCI chess engine (preferably Stockfish version >= 10)
* PGN file
* EPD file

Without using python 2.7 and python source file, just download the exe file in releases link at https://github.com/fsmosca/chess-artist/releases

### 2. Python 3.7
* chess-artist.py version >= 2.0
* [Python 3.7](https://www.python.org/downloads/)
* [Python-chess version >= v0.28.3](https://github.com/niklasf/python-chess)
* UCI chess engine (preferably Stockfish version >= 10)
* PGN file
* EPD file

## B. Command lines
### 1. Analyze games in pgn file
#### a) Basic command line
`chess-artist.exe --infile sample.pgn --outfile out_sample.pgn --enginefile engine\stockfish\windows\stockfish_10_x64_popcnt.exe --eval search --job analyze --movetime 2000`

#### b) Add options to engine, use --engineoptions
`python chess-artist.py --infile sample.pgn --outfile out_sample.pgn --enginefile Stockfish.exe --engineoptions "Hash value 128, Threads value 1" --eval search --job analyze --movetime 2000`<br><br>
Will analyze games inside sample.pgn and output the analyzed games in out_sample.pgn. It uses engine Stockfish.exe with Hash 128MB and Threads 1 at 2000 millisec or 2 sec analysis time per position. chess-artist.py and Stockfish.exe engine must be in same directory.<br>

#### c) Analyze game with polyglot book
`python chess-artist.py --infile sample.pgn --outfile out_sample.pgn --enginefile Stockfish.exe --engineoptions "Hash value 128, Threads value 1" --bookfile gm2600.bin --eval search --job analyze --movetime 2000`

#### d) Analyze game with polyglot book in book dir at chess-artist folder
`python chess-artist.py --infile sample.pgn --outfile out_sample.pgn --enginefile Stockfish.exe --engineoptions "Hash value 128, Threads value 1" --bookfile book/book.bin --eval search --job analyze --movetime 2000`

#### e) Analyze between move 12 to move 20
`python chess-artist.py --infile sample.pgn --outfile out_sample.pgn --enginefile Stockfish.exe --eval search --job analyze --movetime 2000 --movestart 12 --moveend 20`

#### f) Analyze certain player name say Carlsen, Magnus
`python chess-artist.py --infile sample.pgn --outfile out_sample.pgn --enginefile Stockfish.exe --eval search --job analyze --movetime 2000 --movestart 12 --moveend 20 --player "Carlsen, Magnus"`

#### g) Analyze games of Carlsen, Magnus where he is black
`python chess-artist.py --infile iommast19.pgn --outfile magnus_black.pgn --enginefile Stockfish.exe --eval search --job analyze --movetime 2000 --movestart 12 --moveend 20 --player "Carlsen, Magnus" --color black`

#### h) Analyze lost games of Movsesian, Sergei, also analyze moves of its opponent, using --playerandopp option
`chess-artist.exe --infile iommast19.pgn --outfile sergie_loses.pgn --enginefile Stockfish.exe --eval search --job analyze --movetime 5000 --playerandopp "Movsesian, Sergei" --loss`

#### i) Sample analyzed Fischer Random Chess game
```
[Event "World Fischer Random 2019"]
[Site "Hovikodden NOR"]
[Date "2019.11.02"]
[Round "3.5"]
[White "Carlsen, Magnus"]
[Black "So, Wesley"]
[Result "1/2-1/2"]
[BlackElo "2767"]
[BlackFideId "5202213"]
[BlackTitle "GM"]
[EventDate "2019.10.04"]
[FEN "nrkbqnbr/pppppppp/8/8/8/8/PPPPPPPP/NRKBQNBR w HBhb - 0 1"]
[SetUp "1"]
[Variant "chess960"]
[WhiteElo "2876"]
[WhiteFideId "1503014"]
[WhiteTitle "GM"]
[Annotator "engine: Stockfish 2019-12-30 64 POPCNT, prog: Chess Artist v2.6"]

{Hash 256mb, Threads 2, analysis 60.0s per position, move score is in pawn unit,
positive is good for white and negative is good for black}
1. Nb3 $1 {-0.13} 1... f5 $6 {+0.55} (1...f6 {-0.03}) 
2. f3 {+0.12} (2. f4 {+0.39}) 2... Nb6 {+0.53} 
3. e4 $6 {-0.19} (3. c3 {+0.60}) 3... fxe4 $5 {+0.46} 
4. fxe4 {-0.07, with a better piece mobility} 4... e5 {+0.52} 
5. Ne3 $6 {-0.30} (5. Bf3 {+0.48}) 5... Ne6 $6 {+0.35} (5...d6 {-0.24}) 
6. c3 $6 {-0.33} (6. d3 {+0.60}) 6... Bg5 $6 {+0.61} (6...a5 7. Nxa5 Nf4 8. Qf1 Ra8 {-0.17}) 
7. Bc2 $2 {+0.00} (7. h4 {+0.69}) 7... O-O-O $6 {+0.52} (7...Bf7 {+0.10}) 
8. O-O-O $2 {-0.13} (8. g3 Bf7 9. h4 Bxe3 10. Bxe3 {+0.55}) 8... Bf7 $5 {+0.41} 
9. Kb1 $6 {-0.32} (9. h4 {+0.38}) 9... Bh5 $5 {+0.35} 
10. Rc1 $5 {-0.12} {, planning h4} 10... Rf8 $3 {+0.36} 
11. h4 {+0.00} (11. Nf5 {+0.35}) {, with the idea of hxg5} 11... Bxe3 $3 {+0.14} 
12. Bxe3 {-0.05} 12... Nf4 $6 {+0.39} (12...Kb8 {-0.20}) 
13. Rg1 $6 {-0.67} (13. Bxf4 Rxf4 14. d3 Kb8 15. g3 {+0.17}) 13... Bg4 $2 {+0.09} (13...Ne2 14. Bg5 Nxg1 15. Qxg1 Kb8 {-0.86}) 
{, followed by d6} 14. Bxf4 $3 {-0.29} 14... Rxf4 {+0.00} 
{, with the idea of d6} 15. g3 $3 {-0.42} {, planning gxf4} 15... Rf6 $3 {-0.09} 
16. d4 {-0.31} (16. Qe3 Qe7 17. Rgf1 Rdf8 18. Rxf6 {-0.20}) 16... d6 {-0.10} (16...Qe7 17. Bd3 d6 18. Rf1 Rxf1 {-0.27}) 
17. Bd3 $6 {-0.63} (17. Nd2 Qb5 18. Qe3 Qe2 19. Qg5 {+0.00}) 17... Kb8 $5 {-0.22} 
18. Ka1 {-0.48} (18. Nd2 {-0.23}) 18... Qf7 {-0.13} (18...Qe7 {-0.60}) 
19. d5 $2 {-0.84} (19. Qe3 {-0.15}) {, planning c4} 19... Rf3 $3 {-0.66} 
20. Bb1 $2 {-1.23} (20. Qd2 {-0.57}) 20... Rf8 $2 {-0.28} (20...Nc4 21. Nd2 Nxd2 22. Qxd2 Rf8 {-1.28}) 
21. c4 {-0.69} 21... Nd7 {-0.45} 
22. Qb4 $4 {-1.81} (22. c5 Nxc5 23. Nxc5 dxc5 24. Rxc5 {-0.51}) 22... b6 $5 {-0.92} 
23. Na5 {-2.74} (23. Rce1 Rf2 24. Rc1 Ka8 25. Qa4 {-1.54}) 23... Nc5 {-2.43} 
24. Nc6+ {-3.28} 24... Kb7 {-2.89} (24...Ka8 25. Rc3 Rxc3 26. Qxc3 a5 {-3.16}) 
25. Na5+ {-3.74} 25... Ka8 {-2.88} 
26. Nc6 {-3.67} 26... Kb7 {-3.00} 27. Na5+ {-3.60} 27... Ka8 {-3.11} 
28. Nc6 {-3.38} {WhiteBlunder=1, BlackBunder=0, WhiteBad=4, BlackBad=2} 1/2-1/2
```

### 2. Test engine with test suite
#### Use movetime of 500ms
`python chess-artist.py --infile wacnew.epd --outfile result_wacnew.txt --enginefile stockfish_10.exe --engineoptions "Hash value 128, Threads value 1" --eval search --job test --movetime 500`<br><br>
Output file result_wacnew.txt<br>
```
:: EPD wacnew.epd TEST RESULTS ::
Engine        : Stockfish 10 64 POPCNT
Time/pos (sec): 5.0

Total epd lines       : 300
Total tested positions: 300
Total correct         : 292
Correct percentage    : 97.33

:: EPD wacnew.epd TEST RESULTS ::
Engine        : Stockfish 10 64 POPCNT
Time/pos (sec): 0.5

Total epd lines       : 300
Total tested positions: 300
Total correct         : 274
Correct percentage    : 91.33
```
#### Use depth of 10 without movetime
`python chess-artist.py --infile wacnew.epd --outfile result_wacnew.txt --enginefile stockfish_10.exe --engineoptions "Hash value 128, Threads value 1" --eval search --job test --depth 10 --movetime 0`

### 3. Annotate the epd file
#### Use Stockfish to annotate epd file at movetime 30s or 30000ms
`python2 chess-artist.py --infile repertoire.epd --outfile out_repertoire.epd --enginefile stockfish_10.exe --engineoptions "Hash value 128, Threads value 1" --eval search --job analyze --movetime 30000`

Example output:
```
rn1q1rk1/pbp2ppp/1p1ppn2/6B1/2PP4/P1Q1P3/1P3PPP/R3KBNR w KQ - c0 "Nimzo-Indian"; acd 26; acs 30; bm f3; ce +46; Ae "Stockfish 10 64 POPCNT";
rnbq1rk1/pp2ppbp/6p1/2p5/3PP3/2P2N2/P4PPP/1RBQKB1R w K - c0 "Gruenfeld"; acd 26; acs 30; bm Be2; ce +74; Ae "Stockfish 10 64 POPCNT";
```
#### Use Stockfish to annotate epd file with depth equals 16 and no movetime
`python2 chess-artist.py --infile repertoire.epd --outfile out_repertoire.epd --enginefile stockfish_10.exe --engineoptions "Hash value 128, Threads value 1" --eval search --job analyze --depth 16 --movetime 0`

### 4. Generate chess puzzles or test positions
`chess-artist.exe --infile iommast19.pgn --outfile out_iommast19.pgn --enginefile C:\chess\engines\stockfish_19100908_x64_modern.exe --engineoptions "Hash value 128" --movestart 8 --movetime 10000 --job createpuzzle --eval search`  

positions are saved in puzzle.epd  

Example output:  
```
r2qkb1r/pp3p2/1np1b2p/3p2p1/3PP3/2N2NP1/PPQ2PP1/2KR1B1R w kq - bm Bd3; Ubm f1d3;
r3kb1r/pp3pq1/1np1b2p/3pP3/3P2p1/2NB2P1/PPQ2PPN/2KR3R w kq - bm Kb1; Ubm c1b1;
1rbk1b1r/pp1ppppp/4qn2/2R5/2Q5/2N1P3/P1P2PPP/4KBNR w K - bm Qxe6; Ubm c4e6;
1r1k3r/1bqpbpp1/p3pn2/1p5p/8/1R1BPN1Q/P1P1NPPP/5RK1 b - - bm h4; Ubm h5h4;
```  

The Ubm refers to best move in uci move format.

## C. Credits
* Niklas Fiekas<br>
https://github.com/niklasf/python-chess  
_Uses chess.pgn and chess.polyglot modules_
* Stockfish team  
https://github.com/official-stockfish/Stockfish  
_Calculation of passed pawn, king safety and mobility for move comments are from Stockfish engine static evaluation._  
_Windows Stockfish files can also be found under Engine folder_
* TheWeekInChess  
https://theweekinchess.com/  
_Good source of games with pgn files_

