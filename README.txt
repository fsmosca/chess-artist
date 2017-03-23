A. Program name
Chess Artist

B. Program description
A python script that can annotate chess games in pgn file with
static evaluation and/or search score of an engine along with move
annotation symbols such as !!, !, !?, ?!, ? and ??, can annotate games
with cerebellum book moves using the Brainfish engine with its
Cerebellum_Light.bin book file, can annotate an epd file with acd,
acs, bm, and ce opcodes and can test engine with epd test suite.

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

F. Tests
1. This is tested under Windows 7 OS, with python 2.7.11 and python-chess v0.17.0 installed.

G. Guide
1. You need to install python 2.7 version (or 3.5 not tested) on your computer if you want to run the python script.
2. You need to install also python-chess modules on your computer, see section E, if you want to run the python script.
3. Location or directory of input pgn file, engine file and this script chess-artist.py should be the same. However you can
   also specify the path for engine and input pgn. Only Stockfish and Brainfish engines are supported so far if you want the
   moves to be annotated with static scores. If you want to use the cerebellum book only Brainfish is supported.
   For other analysis like search score and without using the cerebellum book, you can use other uci engines that supports
   movetime command. You can download the stockfish engine from here,
   https://stockfishchess.org/
   and Brainfish with Cerebellum_Light.bin book here,
   http://www.zipproth.de/#Brainfish_download
4. If you want the game to be annotated with engine static eval use the following command line.
   chess-artist -infile myg.pgn -outfile out_myg.pgn -eng Sf.exe -eval static -job none
5. If you want the game to be annotated with moves from Cerebellum_Light.bin book use the
   following command line using the -book option and Brainfish engine. The book Cerebellum_Light.bin
   should be in the same directory with the Brainfish engine and the script chess-artist.py.
   chess-artist -infile myg.pgn -outfile out_myg.pgn -eng Bf.exe -book cerebellum -eval none -job none
6. If you want the game to be annotated with moves from Cerebellum_Light.bin book and with static eval.
   chess-artist -infile myg.pgn -outfile out_myg.pgn -eng Bf.exe -book cerebellum -eval static -job none
7. If you want the game to be annotated with engine search score, at movetime of 1 second per position,
   engine Hash of 128 MB and Threads of 1.
   chess-artist -infile myg.pgn -outfile out_myg.pgn -eng Sf.exe -engoptions "Hash value 128, Threads value 1" -eval search -movetime 1000 -job none
7.1. If you want to annotate a game in pgn file with !!, ! and !?, ??, ? and ?! movetime should be 2s or more.
   chess-artist -infile a.pgn -outfile out_a.pgn -eng Sf.exe -eval search -movetime 2000.
7.2. If you want to annotate a game in pgn file with move annotation symbols, book and engine search score and bestmove.
   chess-artist -infile a.pgn -outfile out_a.pgn -eng Sf.exe -eval search -book cerebellum --movetime 2000
8. If you want to annotate an epd file with bm, ce and other op codes at 10s per position. The ce is from side POV.
   See example output in section H below.
   chess-artist -infile myepd.epd -outfile out_myepd.epd -eng Sf.exe -engoptions "Hash value 128, Threads value 1" -movetime 10000
8.1 If you want to annotate the epd file with ce whose value is from static eval of the engine instead of the search.
   chess-artist -infile carlsen.epd -outfile out_carlsen.epd -eng Sf.exe -eval static
9. If you want to test a uci engine on epd test suite to see how many best moves it could find, add the -job test option value.
   chess-artist -infile wacnew.epd -outfile out_wacnew.txt -eng Sf.exe -engoptions "Hash value 128, Threads value 1" -movetime 1000 -job test
10. In the annotated game the value in the comment is in pawn unit and is from the point of
   view of white that is if it is positive, it is better for white, and if negative it is better for black.
   
H. Options
-infile <input filename> : Default is src.pgn
-outfile <output filename> : Default is out_src.pgn
-eng <engine filename> : Default is engine.exe, an engine with path is also possible for example in windows, if your engine is located in c:\chess\engines\Stockfish and your engine is Sf.exe, you can use, -eng "c:\chess\engines\stockfish\Sf8.exe"
-engoptions <options> : Example, -engoptions "Hash value 64, Threads value 1, SyzygyPath value C:\chess\egtb\syzygy"
-book <none | cerebellum> : Default is none, used to add book moves to the game annotation when value is cerebellum.
-eval <none | static | search> : Default is static, it is used to calculate the score of the move of the player in the game. If the
    value is static, it will call the eval command of Stockfish engine to get its static eval. If the value is search, it will
    analyze the position by searching at given movetime.
-job <none | search | test> : Default is search, when the infile is pgn and value is search, the engine will search for bestmove
    and bestscore of the position, it will be compared to the score of the move of the player to get move annotation symbols,
    and generate comments. If the infile is epd and the value is search, it will annotate an epd file with acd, acs, bm and other
    opcodes. If the infile is epd and the value is test, it will test the engine of the epd test suite.
-movetime <integer value> : Default is 0, this is the time in millisec for engine search time for engine solving the epd test suite.
-movestart <move number> : Default is 8, it is the move number that the engine will start analyzing a pgn file. The -book setting
    will not be affected by this.
   
I. Examples of annotated games, epd analysis, and engine epd test

1. Game analysis with cerebellum book use

a. Command line
chess-artist -infile a.pgn -outfile out_a.pgn -eng Brainfish.exe -eval search -movetime 200 -movestart 6 -book cerebellum

b. Command line interpretation
-infile a.pgn: The input file option.
-outfile out_a.pgn: The output file option.
-eng Brainfish.exe: Engine that evaluates positions.
-eval search: The move of the player is evaluated by engine search score.
-movetime 200: Engine analysis time per position is 200 milliseconds or 0.2 second.
-movestart 6: Engine analysis starts at move 6, the book annotation is not affected by this.
-book cerebellum: Will use the cerebellum book file, Cerebellum_Light.bin, Brainfish engine shall be used.

c. Annotation output

[Event "42nd Olympiad 2016"]
[Site "Baku AZE"]
[Date "2016.09.02"]
[Round "1.1"]
[White "Kigigha, Bomo"]
[Black "Karjakin, Sergey"]
[Result "0-1"]
[Board "1"]
[WhiteTitle "FM"]
[BlackTitle "GM"]
[WhiteElo "2340"]
[BlackElo "2769"]
[ECO "A05"]
[Opening "Reti opening"]
[WhiteTeam "Nigeria"]
[BlackTeam "Russia"]
[WhiteFideId "8500037"]
[BlackFideId "14109603"]
[EventDate "2016.09.02"]
[Annotator "Brainfish 280816 64 POPCNT"]

{Hash 32mb, Threads 1, @ 0.2s/pos}
1. Nf3 (1. e4 {cerebellum}) 1... Nf6 (1... d5 {cerebellum}) 
2. g3 (2. d4 {cerebellum}) 2... d5 (2... d5 {cerebellum}) 
3. c4 (3. Bg2 {cerebellum}) 3... d4 (3... d4 {cerebellum}) 
4. Bg2 (4. b4 {cerebellum}) 4... c5 (4... c5 {cerebellum}) 
5. b4 (5. b4 {cerebellum}) 5... cxb4 (5... cxb4 {cerebellum}) 
6. O-O $0 {-0.61} (6. a3 {cerebellum}) (6. e3 {-0.34 - Brainfish}) Nc6 {-0.63} 
7. e3 {-0.55} 7... e5 $0 {-0.56} (7... dxe3 {-0.55 - Brainfish}) 
8. exd4 {-0.98} e4 {-0.91} 
9. Ng5 $4 {-3.28} (9. d5 {-0.25 - Brainfish}) Qxd4 {-1.47} 
10. Qb3 {-1.59} Qxa1 {-1.72} 
11. Bb2 {-1.84} 11... Na5 $0 {-1.75} (11... Nd4 {-1.84 - Brainfish}) 
12. Bxa1 {-1.75} Nxb3 {-1.32} 
13. axb3 {-1.58} 13... Bf5 $0 {-1.90} (13... Be7 {-1.58 - Brainfish}) 
14. Bxf6 $0 {-2.91} (14. d3 {-1.90 - Brainfish}) gxf6 {-2.91} 
15. Nxe4 $0 {-3.09} (15. Bxe4 {-2.91 - Brainfish}) O-O-O {-2.97} 
16. Re1 {-3.08} 16... Kb8 $0 {-2.75} (16... Be7 {-3.18 - Brainfish}) 
17. g4 $0 {-3.39} (17. Nxf6 {-2.75 - Brainfish}) 17... Bg6 $0 {-2.96} (17... Bxg4 {-3.39 - Brainfish}) 
18. f4 $0 {-3.41} (18. Nxf6 {-2.96 - Brainfish}) f5 {-3.25} 
19. Ng3 {-2.80} Bc5+ {-3.26} 
20. Kf1 {-3.37} Rd4 {-2.89} 
21. Ne2 {-3.20} 21... Rhd8 $0 {-2.89} (21... Rd6 {-3.20 - Brainfish}) 
22. g5 $0 {-2.98} (22. Nxd4 {-2.89 - Brainfish}) Bh5 {-3.10} 
23. Nxd4 {-3.02} Rxd4 {-3.25} 
24. Bd5 $0 {-3.24} (24. Re8+ {-3.25 - Brainfish}) Rxf4+ {-3.23} 
25. Kg2 {-3.19} 25... Rf2+ $0 {-3.77} (25... Rg4+ {-3.42 - Brainfish}) 
26. Kg3 $0 {-3.82} (26. Kh1 {-3.74 - Brainfish}) f4+ {-3.71} 
27. Kh3 {-4.04} f3 {-3.77} 
0-1

1.1 Sample game analysis with move annotations ! and !? based on position complexity,
and ??, ? ?! based on player move score and engine move score.

[Event "Hoogovens A Tournament"]
[Site "Wijk aan Zee NED"]
[Date "1999.01.20"]
[Round "4"]
[White "Garry Kasparov"]
[Black "Veselin Topalov"]
[Result "1-0"]
[EventDate "?"]
[ECO "B06"]
[WhiteElo "2812"]
[BlackElo "2700"]
[PlyCount "87"]
[Annotator "Brainfish 280816 64 POPCNT"]

{Hash 32mb, Threads 1, @ 10.0s/pos}
1. e4 (1. e4 {cerebellum}) 1... d6 (1... e5 {cerebellum}) 
2. d4 (2. d4 {cerebellum}) 2... Nf6 (2... g6 {cerebellum}) 
3. Nc3 (3. Nc3 {cerebellum}) 3... g6 (3... g6 {cerebellum}) 
4. Be3 (4. Be3 {cerebellum}) 4... Bg7 (4... c6 {cerebellum}) 
5. Qd2 (5. Qd2 {cerebellum}) 5... c6 (5... O-O {cerebellum}) 
6. f3 (6. Bh6 {cerebellum}) 6... b5 (6... b5 {cerebellum}) 
7. Nge2 (7. O-O-O {cerebellum}) 7... Nbd7 (7... O-O {cerebellum}) 
8. Bh6 $0 {+0.06} (8. g4 {cerebellum}) ({} 8. a3 Bb7 9. g4 Nb6 10. b3 {+0.17 - Brainfish}) 8... Bxh6 {+0.03} (8... Bxh6 {cerebellum}) 
9. Qxh6 {+0.03} (9. Qxh6 {cerebellum}) 9... Bb7 $6 {+0.19} (9... Qb6 {cerebellum}) ({} 9...b4 {+0.10 - Brainfish}) 
10. a3 $0 {+0.07} (10. a4 {cerebellum}) ({Better is} 10. Nd1 Ba6 11. a3 Qb6 12. c3 {+0.26 - Brainfish}) 10... e5 $6 {+0.30} (10... a5 {cerebellum}) ({Better is} 10...a5 11. Ng3 b4 12. Na4 Nb6 {+0.07 - Brainfish}) 
11. O-O-O {+0.13} (11. dxe5 {cerebellum}) 11... Qe7 {+0.12} (11... a5 {cerebellum}) 
12. Kb1 $0 {-0.02} (12. Kb1 {cerebellum}) ({} 12. Ng3 O-O-O 13. Kb1 Kb8 14. Be2 {+0.12 - Brainfish}) 12... a6 $6 {+0.46} (12... a5 {cerebellum}) ({Better is} 12...a5 13. dxe5 dxe5 14. g4 b4 {-0.02 - Brainfish}) 
13. Nc1 $0 {+0.43} (13. Nc1 {cerebellum}) ({} 13. g4 a5 14. g5 Nh5 15. Bh3 {+0.46 - Brainfish}) 13... O-O-O $0 {+0.53} (13... O-O-O {cerebellum}) ({} 13...exd4 14. Rxd4 O-O-O 15. Rd2 Ne5 {+0.43 - Brainfish}) 
14. Nb3 $1 {+0.58} (14. Nb3 {cerebellum}) ({} 14. dxe5 dxe5 15. g3 Kb8 16. Qe3 {+0.53 - Brainfish}) 14... exd4 {+0.53} (14... exd4 {cerebellum}) 
15. Rxd4 $0 {+0.36} (15. Rxd4 {cerebellum}) ({Better is} 15. Nxd4 Kb8 16. Be2 Rhe8 17. Rd2 {+0.53 - Brainfish}) 15... c5 $0 {+0.71} (15... c5 {cerebellum}) ({Better is} 15...Nc5 16. Nxc5 dxc5 17. Rxd8+ Rxd8 {+0.36 - Brainfish}) 
16. Rd1 $0 {+0.56} (16. Rd1 {cerebellum}) ({} 16. Rd2 Ne5 17. Qe3 Nfd7 18. Be2 {+0.71 - Brainfish}) 16... Nb6 $1 {+0.47} (16... Nb6 {cerebellum}) ({} 16...Ne5 17. Na5 Rhe8 18. Nxb7 Kxb7 {+0.56 - Brainfish}) 
17. g3 $0 {+0.43} (17. Qe3 {cerebellum}) ({} 17. Qe3 Kb8 18. Qf2 Rhe8 19. Na5 {+0.47 - Brainfish}) 17... Kb8 $1 {+0.40} (17... Kb8 {cerebellum}) ({} 17...d5 18. Bh3+ Kb8 19. e5 Nfd7 {+0.43 - Brainfish}) 
18. Na5 $0 {+0.13} (18. Bg2 {cerebellum}) ({Better is} 18. g4 d5 19. Qf4+ Ka8 20. Nxc5 {+0.40 - Brainfish}) 18... Ba8 $6 {+0.42} (18... Ba8 {cerebellum}) ({Better is} 18...d5 19. Qf4+ Ka7 20. Bxb5 axb5 {+0.13 - Brainfish}) 
19. Bh3 $0 {+0.00} (19. Bh3 {cerebellum}) ({Better is} 19. g4 Nfd7 20. Bg2 Ne5 21. Rhe1 {+0.49 - Brainfish}) 19... d5 {+0.00} (19... d5 {cerebellum}) 
20. Qf4+ $0 {-0.07} (20. Rhe1 {cerebellum}) ({} 20. Rhe1 d4 21. Qf4+ Ka7 22. Na2 {+0.00 - Brainfish}) 20... Ka7 {+0.12} (20... Ka7 {cerebellum}) 
21. Rhe1 {+0.03} (21. Rhe1 {cerebellum}) 21... d4 {-0.06} (21... d4 {cerebellum}) 
22. Nd5 $6 {-0.68} (22. Na2 {cerebellum}) ({Better is} 22. Na2 Nh5 23. Qd2 Qc7 24. Qf2 {-0.06 - Brainfish}) 22... Nbxd5 {-0.57} (22... Nbxd5 {cerebellum}) 
23. exd5 $0 {-0.65} (23. exd5 {cerebellum}) ({} 23. Nc6+ Bxc6 24. exd5 Qd6 25. Qxd6 {-0.57 - Brainfish}) 23... Qd6 {-0.52} (23... Qd6 {cerebellum}) 
24. Rxd4 $5 {-0.52} (24. Rxd4 {cerebellum}) ({} 24. Nc6+ Bxc6 25. Qxd6 Rxd6 26. dxc6 {-0.52 - Brainfish}) 24... cxd4 $0 {+0.00} (24... Kb6 {cerebellum}) ({Better is} 24...Kb6 25. b4 Qxf4 26. Rxf4 Nxd5 {-0.45 - Brainfish}) 
25. Re7+ {+0.00} (25. Re7+ {cerebellum}) 25... Kb6 {+0.00} (25... Kb8 {cerebellum}) 
26. Qxd4+ {+0.00} (26. Qxd4+ {cerebellum}) 26... Kxa5 {+0.00} (26... Qc5 {cerebellum}) 
27. b4+ {+1.68} (27. b4+ {cerebellum}) 27... Ka4 {+3.05} (27... Ka4 {cerebellum}) 
28. Qc3 $2 {+0.06} (28. Ra7 {cerebellum}) ({Excellent is} 28. Ra7 {+3.05 - Brainfish}) 28... Qxd5 {+0.24} (28... Qxd5 {cerebellum}) 
29. Ra7 {+0.00} (29. Ra7 {cerebellum}) 29... Bb7 {+0.00} (29... Bb7 {cerebellum}) 
30. Rxb7 $1 {+0.30} (30. Rxb7 {cerebellum}) ({} 30. Qc7 Qd1+ 31. Ka2 Bd5+ 32. Kb2 {+0.00 - Brainfish}) 30... Qc4 $0 {+0.39} (30... Qc4 {cerebellum}) ({} 30...Rhe8 31. Rb6 Ra8 32. Rc6 Re2 {+0.30 - Brainfish}) 
31. Qxf6 {+0.51} (31. Qxf6 {cerebellum}) 31... Kxa3 {+4.25} (31... Rd1+ {cerebellum}) 
32. Qxa6+ {+3.97} (32. Qxa6+ {cerebellum}) Kxb4 {+4.17} 33. c3+ {+4.32} Kxc3 {+4.26} 
34. Qa1+ {+4.17} Kd2 {+5.07} 35. Qb2+ {+4.46} Kd1 {+4.74} 
36. Bf1 {+4.59} Rd2 {+4.69} 37. Rd7 {+4.51} Rxd7 {+4.29} 
38. Bxc4 {+4.81} bxc4 {+4.45} 39. Qxh8 {+4.45} Rd3 {+5.01} 
40. Qa8 {+4.48} c3 {+5.02} 41. Qa4+ {+4.86} Ke1 {+4.81} 
42. f4 {+5.44} f5 {+5.88} 43. Kc1 {+6.72} Rd2 {+6.17} 
44. Qa7 {+6.90} {[WhiteAveError=0.34, BlackAveError=0.21] [ratingDiff=30]} 1-0

1.2 Game analysis with annotation symbols based on version 0.2.0

Command line used:
chess-artist.py -infile Carlsen-Karjakin-R10.pgn -outfile out_Carlsen-Karjakin-R10.pgn -eng Bf.exe -engoptions "Hash value 128" -eval search -book cerebellum -movetime 5000 -movestart 10

[Event "WCh 2016"]
[Site "New York USA"]
[Date "2016.11.24"]
[Round "10"]
[White "Carlsen, Magnus"]
[Black "Karjakin, Sergey"]
[Result "1-0"]
[WhiteTitle "GM"]
[BlackTitle "GM"]
[WhiteElo "2853"]
[BlackElo "2772"]
[ECO "C65"]
[Opening "Ruy Lopez"]
[Variation "Berlin defence"]
[WhiteFideId "1503014"]
[BlackFideId "14109603"]
[EventDate "2016.11.11"]
[Annotator "Brainfish 191116 64 POPCNT"]

{Hash 128mb, Threads 1, @ 5.0s/pos}
1. e4 (1. e4 {cerebellum}) 1... e5 (1... e5 {cerebellum}) 
2. Nf3 (2. Nf3 {cerebellum}) 2... Nc6 (2... Nc6 {cerebellum}) 
3. Bb5 (3. Bc4 {cerebellum}) 3... Nf6 (3... Nf6 {cerebellum}) 
4. d3 (4. O-O {cerebellum}) 4... Bc5 (4... Bc5 {cerebellum}) 
5. c3 (5. Nbd2 {cerebellum}) 5... O-O (5... O-O {cerebellum}) 
6. Bg5 (6. Nbd2 {cerebellum}) 6... h6 (6... h6 {cerebellum}) 
7. Bh4 (7. Bh4 {cerebellum}) 7... Be7 (7... d6 {cerebellum}) 
8. O-O (8. O-O {cerebellum}) 8... d6 (8... d6 {cerebellum}) 
9. Nbd2 (9. Nbd2 {cerebellum}) 9... Nh5 (9... Nh5 {cerebellum}) 
10. Bxe7 {-0.06} (10. Bxe7 {cerebellum}) 10... Qxe7 {-0.07} (10... Qxe7 {cerebellum}) 
11. Nc4 {+0.22} (11. Nc4 {cerebellum}) Nf4 $0 {-0.04} 
12. Ne3 $0 {+0.00} 12... Qf6 $0 {+0.12} ({} 12...f5 13. Bc4+ {+0.00}) 
13. g3 $1 {+0.15} ({} 13. Kh1 Bd7 14. a4 a6 15. Bc4 {+0.12}) Nh3+ $0 {+0.07} 
14. Kh1 $5 {+0.15} {, with the idea of a4} Ne7 $3 {+0.00} 
15. Bc4 $0 {-0.10} ({} 15. a4 Be6 16. Bc4 Bxc4 17. Nxc4 {+0.00}) 15... c6 $0 {+0.13} ({Better is} 15...b5 16. Bd5 Rb8 17. Qe2 Bd7 {-0.10}) 
16. Bb3 $5 {+0.02} 16... Ng6 $6 {+0.20} ({Better is} 16...a5 17. a4 Rd8 18. Qe2 d5 {+0.02}) 
17. Qe2 $5 {+0.27} {, with the idea of Rad1} a5 $1 {+0.25} 
18. a4 $0 {+0.11} ({} 18. d4 Be6 19. Bc2 b5 20. a3 {+0.25}) 18... Be6 $6 {+0.28} ({Better is} 18...Re8 19. Nd2 {+0.11}) 
19. Bxe6 $0 {+0.00} ({Better is} 19. Nd2 Rae8 20. f3 Bc8 21. Rae1 {+0.28}) fxe6 $0 {+0.00} 
20. Nd2 $0 {+0.00} 20... d5 $6 {+0.38} ({Better is} 20...Nxf2+ 21. Kg2 Nh4+ 22. Kg1 Nh3+ {+0.00}) 
21. Qh5 $0 {+0.00} ({Better is} 21. f3 {+0.38}) 21... Ng5 $6 {+0.66} ({Better is} 21...Nxf2+ 22. Kg2 Qf7 23. Kg1 Qf6 {+0.00}) 
22. h4 $0 {+0.41} ({Better is} 22. Rae1 Nf3 23. Ng4 Qg5 24. Qxg5 {+0.66}) Nf3 $0 {+0.22} 
23. Nxf3 $0 {+0.34} Qxf3+ $0 {+0.19} 
24. Qxf3 $0 {+0.23} Rxf3 $0 {+0.24} 
25. Kg2 $0 {+0.38} Rf7 $0 {+0.37} 
26. Rfe1 $0 {+0.26} ({} 26. Rae1 h5 {+0.37}) 26... h5 $0 {+0.50} ({Better is} 26...Raf8 {+0.26}) 
27. Nf1 $0 {+0.45} ({} 27. Nc2 Rd8 28. Re2 Rdf8 29. Rf1 {+0.50}) 27... Kf8 $0 {+0.66} ({Better is} 27...Raf8 28. Re2 Rf3 29. Ne3 R3f6 {+0.45}) 
28. Nd2 $0 {+0.73} {, with the idea of Nf3} Ke7 $1 {+0.57} 
29. Re2 $1 {+0.81} ({} 29. b4 {+0.57}) Kd6 $0 {+0.82} 
30. Nf3 $0 {+0.83} 30... Raf8 $1 {+0.70} ({} 30...Re7 31. d4 exd4 32. Nxd4 Kd7 {+0.83}) 
31. Ng5 $0 {+0.71} Re7 $0 {+0.73} 
32. Rae1 $0 {+0.71} ({} 32. b4 Ra8 33. b5 cxb5 34. exd5 {+0.73}) 32... Rfe8 $1 {+0.68} ({} 32...b6 33. d4 {+0.71}) 
33. Nf3 $1 {+0.82} ({} 33. b4 Ra8 34. Rb2 axb4 35. Rxb4 {+0.68}) 33... Nh8 $0 {+0.76} ({} 33...Nf8 34. b4 Nd7 35. bxa5 Ra8 {+0.82}) 
34. d4 $0 {+0.53} ({Better is} 34. b4 axb4 35. cxb4 Nf7 36. a5 {+0.76}) exd4 $0 {+0.62} 
35. Nxd4 $0 {+0.65} {, with the idea of exd5} g6 $3 {+0.47} 
36. Re3 $1 {+0.49} ({} 36. e5+ Kd7 37. b4 axb4 38. cxb4 {+0.47}) Nf7 $0 {+0.72} 
37. e5+ $0 {+0.59} Kd7 $0 {+0.59} 
38. Rf3 $0 {+0.50} ({} 38. b4 Nh6 39. Nb3 Nf5 40. Rf3 {+0.59}) 38... Nh6 $0 {+0.70} ({Better is} 38...g5 39. hxg5 Nxg5 40. Rf4 Rf7 {+0.50}) 
39. Rf6 $0 {+0.71} 39... Rg7 $2 {+0.90} ({Better is} 39...Rg8 40. Nf3 Nf7 41. Ng5 Nxg5 {+0.71}) 
40. b4 $0 {+0.87} ({} 40. c4 {+0.90}) axb4 $0 {+0.84} 
41. cxb4 $0 {+0.86} 41... Ng8 $0 {+0.78} ({} 41...Ng4 42. Rf4 Nh6 43. a5 Rf7 {+0.86}) 
42. Rf3 $0 {+0.93} Nh6 $5 {+0.73} 
43. a5 $1 {+0.85} ({} 43. Nb3 Kc7 44. a5 Nf5 45. Nc5 {+0.73}) 43... Nf5 $0 {+0.85} ({} 43...Rf7 {+0.85}) 
44. Nb3 $0 {+0.80} 44... Kc7 $1 {+0.68} ({} 44...Rge7 {+0.80}) 
45. Nc5 $5 {+0.83} 45... Kb8 $0 {+0.83} ({} 45...Rge7 46. Ra3 Ra8 47. Nd3 Kd7 {+0.83}) 
{, with the idea of Rge7} 46. Rb1 $1 {+0.87} {, with the idea of Rfb3} Ka7 $0 {+1.16} 
47. Rd3 $0 {+0.78} ({Better is} 47. Rf4 Rge7 {+1.16}) 47... Rc7 $0 {+0.81} ({} 47...Rge7 {+0.78}) 
48. Ra3 $1 {+0.90} ({} 48. Rd2 Rce7 49. Rdb2 Nd4 50. Rd1 {+0.81}) 48... Nd4 $1 {+0.75} ({} 48...Rg7 49. f4 Rc7 50. Raa1 Rh7 {+0.90}) 
49. Rd1 $1 {+0.83} ({} 49. Rd3 Nf5 50. Rd2 Rcc8 51. Nd3 {+0.75}) Nf5 $0 {+0.80} 
50. Kh3 $1 {+0.92} ({} 50. Rb3 Nh6 51. Rd2 Nf5 52. Rdb2 {+0.80}) Nh6 $0 {+0.85} 
51. f3 $0 {+0.72} ({} 51. Kg2 {+0.85}) 51... Rf7 $2 {+0.90} ({Better is} 51...Rg7 52. Kg2 Nf5 53. Rh1 Rh7 {+0.72}) 
52. Rd4 $0 {+0.80} ({} 52. Rc1 Nf5 53. Rd3 Rfe7 54. g4 {+0.90}) {, with the idea of Rb3} Nf5 $0 {+0.90} 
53. Rd2 $1 {+1.00} ({} 53. Rd1 {+0.90}) 53... Rh7 $1 {+0.74} ({} 53...Ree7 54. Rad3 Rf8 55. Rb2 d4 {+1.00}) 
{, with the idea of Rg8} 54. Rb3 $1 {+0.87} 54... Ree7 $0 {+0.98} ({} 54...Rf7 55. Rdd3 Nh6 56. Ra3 Rh7 {+0.87}) 
55. Rdd3 $0 {+0.73} ({Better is} 55. b5 cxb5 {+0.98}) Rh8 $5 {+0.65} 
{, with the idea of Rg8} 56. Rb1 $3 {+0.79} 56... Rhh7 $4 {+1.92} ({Excellent is} 56...Rf8 57. Re1 Nh6 58. Re2 Nf5 {+0.79}) 
57. b5 $0 {+1.82} cxb5 $0 {+1.86} 
58. Rxb5 $0 {+1.93} {, with the idea of Rb6} d4 $0 {+1.83} 
{, with the idea of Rh8} 59. Rb6 $3 {+1.83} Rc7 $0 {+1.85} 
60. Nxe6 $0 {+1.85} Rc3 $0 {+1.77} 
61. Nf4 $0 {+1.95} 61... Rhc7 $0 {+2.61} ({Better is} 61...Rg7 {+1.95}) 
62. Nd5 $2 {+1.31} ({Excellent is} 62. Rxg6 {+2.61}) Rxd3 $0 {+1.32} 
63. Nxc7 $0 {+1.36} Kb8 $0 {+1.19} 
64. Nb5 $0 {+1.30} Kc8 $0 {+1.23} 
65. Rxg6 $5 {+1.32} Rxf3 $0 {+1.16} 
66. Kg2 $0 {+1.45} Rb3 $0 {+1.20} 
67. Nd6+ $0 {+1.47} Nxd6 $0 {+1.36} 
68. Rxd6 $0 {+1.41} 68... Re3 $4 {+2.59} ({Excellent is} 68...Kc7 {+1.41}) 
69. e6 $0 {+2.64} Kc7 $0 {+2.89} 
70. Rxd4 $0 {+2.66} Rxe6 {+3.04} 71. Rd5 {+3.01} Rh6 {+3.13} 
72. Kf3 $0 {+2.98} ({} 72. Rc5+ Kd6 73. Rf5 Rh8 74. Kf3 {+3.06}) Kb8 {+5.61} 73. Kf4 {+4.84} Ka7 {+8.66} 
74. Kg5 {+4.65} Rh8 {+4.60} 75. Kf6 {+4.70} (-- {WhiteAveError=0.11, BlackAveError=0.20, ratingDiff=20}) 1-0

2. Epd analysis, annotate epd with acd, acs, bm, ce and Ae opcodes

a. Command line
chess-artist -infile a.epd -outfile out_a.epd -eng Branfish.exe -engoptions "Hash value 128, Threads value 1" -movetime 10000 -eval search

b. Command line interpretation
-engoptions "Hash value 128, Threads value 1": The main memory size in Hash value is in MB used by the uci engine. Threads value 1
    means the engine will only 1 thread.
-eval search: Will use use the engine to search the position. -eval static, will only use the static eval of the engine. Only stockfish
   engine is supported, usig its eval command.

c. An example epd line in an epd file
r1bk1b1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK1 w - -

d. An example output using -eval search
r1bk1b1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK1 w - - acd 17; acs 10; bm Nc3; ce 30; Ae "Brainfish 280816 64 POPCNT";

e. An example output using -eval static
r1bk1b1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK1 w - - ce 30; c0 "ce is static eval of engine"; Ae "Brainfish 280816 64 POPCNT";

3. Testing engine on epd test suite.

a. Command line
chess-artist -infile wac.epd -outfile wac_out.txt -eng Bf.exe -engoptions "Hash value 128, Threads value 1" -movetime 300 -job test

b. Command line interpretation
-job test: Tells the script that the engine will be tested on epd file.

c. Example output wac_out.txt
:: EPD wac.epd TEST RESULTS ::
Engine        : Brainfish 280816 64 POPCNT
Time/pos (sec): 0.3

Total epd lines       : 24
Total tested positions: 24
Total correct         : 23
Correct percentage    : 95.8
