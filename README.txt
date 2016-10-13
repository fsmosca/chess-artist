A. Program name
Chess Artist

B. Program description
A python script that can annotate chess games in pgn file with
static evaluation or search score of an engine, can annotate games
with cerebellum book moves using the Brainfish engine with its
Cerebellum_Light.bin book file, can annotate an epd file with acd,
acs, bm, and ce op codes and can test engine with epd test suite.

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
1. This is tested under Windows 7 OS, with python 2.7.11
   and python-chess 0.14.1 installed.

G. Guide
1. You need to install python 2.7 version (or 3.5 not tested)
   on your computer.
2. You need to install also python-chess on your computer, see section E.
3. Location or directory of input pgn file, engine file and this script chess-artist.py
   should be the same. Only Stockfish and Brainfish engine are supported so far. You can
   download the stockfish engine from here,
   https://stockfishchess.org/
   and Brainfish with Cerebellum_Light.bin book here,
   http://www.zipproth.de/#Brainfish_download
4. If you want the game to be annotated with engine static eval use the following command line.
   chess-artist -infile mygames.pgn -outfile mygames_se.pgn -eng stockfish.exe -eval static
5. If you want the game to be annotated with moves from Cerebellum_Light.bin book use the
   following command line using the -book option and Brainfish engine. The book Cerebellum_Light.bin
   should be in the same directory with the Brainfish engine and the script chess-artist.py.
   chess-artist -infile myg.pgn -outfile myg_cere.pgn -eng Brainfish.exe -book cerebellum -eval none
6. If you want the game to be annotated with moves from Cerebellum_Light.bin book and with static eval.
   chess-artist -infile myg.pgn -outfile myg_cere_se.pgn -eng Brainfish.exe -book cerebellum -eval static
7. If you want the game to be annotated with engine search score, at movetime of 1 second per position,
   engine Hash of 128 MB and Threads of 1.
   chess-artist -infile myg.pgn -outfile myg_es.pgn -eng Sf.exe -enghash 128 -engthreads 1 -eval search -movetime 1000
7.1. If you want to annotate a game in pgn file with !!, ! and !?, ??, ? and ?! movetime should be 5s or more.
   chess-artist -infile a.pgn -outfile out_a.pgn -eng Sf.exe -eval search -movetime 5000
8. If you want to annotate an epd file with bm, ce and other op codes at 10s per position. The ce is from side POV.
   See example output in section H below.
   chess-artist -infile myepd.epd -outfile myepd_out.epd -eng Sf.exe -enghash 128 -engthreads 1 -movetime 10000
8.1 If you want to annotate the epd file with ce whose value is from static eval of the engine instead of the search.
   chess-artist -infile kasparov.epd -outfile out_kasparov.epd -eng Sf.exe -eval static
9. If you want to test a uci engine on epd test suite to see how many best moves it could find, add the -job test option value.
   chess-artist -infile wacnew.epd -outfile wacnew_out.txt -eng Sf.exe -enghash 128 -engthreads 1 -movetime 500 -job test
10. In the annotated game the value in the comment is in pawn unit and is from the point of
   view of white, if it is positive, it is better for white, and if negative it is better for black.
   
H. Examples of annotated games, epd analysis, and engine epd test

1. Game analysis with cerebellum book use

a. Command line
chess-artist -infile a.pgn -outfile out_a.pgn -eng Brainfish.exe -eval search -movetime 200 -movestart 6 -book cerebellum

b. Command line interpretation
-infile a.pgn: The input file option.
-outfile out_a.pgn: The output file option.
-eng brainfish.exe: Engine that evaluates positions, this engine is used when cerebellum book is used too.
-eval search: The move of the player is evaluated by engine search score.
-movetime 200: Engine analysis time per position is 200 milliseconds or 0.2 second.
-movestart 6: Engine analysis starts at move 6, the book annotation is not affected by this.
-book cerebellum: Will use the cerebellum book file, Cerebellum_Light.bin

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
1. e4 d6 2. d4 Nf6 
3. Nc3 g6 4. Be3 Bg7 
5. Qd2 c6 6. f3 b5 
7. Nge2 Nbd7 8. Bh6 $0 {+0.06} (8. h4 {+0.12 - Brainfish}) Bxh6 $0 {+0.22} 
9. Qxh6 $1 {+0.05} 9... Bb7 $6 {+0.24} (9... Qb6 {+0.05 - Brainfish}) 
10. a3 $0 {+0.10} (10. Nd1 {+0.24 - Brainfish}) 10... e5 $6 {+0.18} (10... a5 {+0.10 - Brainfish}) 
11. O-O-O $5 {+0.28} (11. dxe5 {+0.18 - Brainfish}) Qe7 $0 {+0.22} 
12. Kb1 $0 {+0.06} (12. Ng3 {+0.22 - Brainfish}) 12... a6 $6 {+0.42} (12... a5 {+0.06 - Brainfish}) 
13. Nc1 $5 {+0.55} (13. g4 {+0.42 - Brainfish}) 13... O-O-O $5 {+0.51} (13... exd4 {+0.55 - Brainfish}) 
14. Nb3 $5 {+0.55} (14. Qe3 {+0.51 - Brainfish}) exd4 $0 {+0.41} 
15. Rxd4 $5 {+0.42} (15. Nxd4 {+0.41 - Brainfish}) 15... c5 $2 {+0.91} (15... Nc5 {+0.42 - Brainfish}) 
16. Rd1 $0 {+0.53} (16. Rd2 {+0.91 - Brainfish}) 16... Nb6 $5 {+0.43} (16... Ne5 {+0.53 - Brainfish}) 
17. g3 $0 {+0.34} (17. Qh4 {+0.43 - Brainfish}) 17... Kb8 $0 {+0.44} (17... d5 {+0.34 - Brainfish}) 
18. Na5 $0 {+0.00} (18. g4 {+0.44 - Brainfish}) 18... Ba8 $6 {+0.48} (18... d5 {+0.00 - Brainfish}) 
19. Bh3 $0 {+0.08} (19. Ka1 {+0.48 - Brainfish}) d5 $5 {+0.00} 
20. Qf4+ $5 {+0.00} (20. Rhe1 {+0.00 - Brainfish}) Ka7 $5 {+0.10} 
21. Rhe1 $0 {+0.06} d4 $5 {+0.00} 
22. Nd5 $6 {-0.61} (22. Na2 {+0.00 - Brainfish}) Nbxd5 $0 {-0.63} 
23. exd5 $5 {-0.57} (23. Nc6+ {-0.63 - Brainfish}) Qd6 $0 {-0.60} 
24. Rxd4 $5 {-0.50} (24. Nc6+ {-0.60 - Brainfish}) 24... cxd4 $0 {+0.00} (24... Kb6 {-0.50 - Brainfish}) 
25. Re7+ $0 {+0.00} Kb6 $0 {+0.00} 
26. Qxd4+ $0 {+0.00} Kxa5 $0 {+0.00} 
27. b4+ $0 {+0.24} Ka4 $0 {+0.59} 
28. Qc3 $0 {+0.00} (28. Ra7 {+0.59 - Brainfish}) Qxd5 $0 {+0.00} 
29. Ra7 $0 {+0.00} Bb7 $0 {+0.00} 
30. Rxb7 $5 {+0.00} (30. Qc7 {+0.00 - Brainfish}) 30... Qc4 $6 {+0.69} (30... Rhe8 {+0.00 - Brainfish}) 
31. Qxf6 $0 {+0.55} 31... Kxa3 $4 {+3.94} (31... Rd1+ {+0.55 - Brainfish}) 
32. Qxa6+ $0 {+3.97} Kxb4 $0 {+3.93} 
33. c3+ $0 {+4.04} Kxc3 $0 {+4.12} 
34. Qa1+ $0 {+4.10} Kd2 $0 {+4.98} 
35. Qb2+ $0 {+4.35} Kd1 $0 {+4.46} 
36. Bf1 $0 {+4.22} Rd2 $0 {+4.45} 
37. Rd7 $0 {+4.37} Rxd7 $0 {+4.25} 
38. Bxc4 $0 {+4.46} bxc4 $0 {+4.35} 
39. Qxh8 $0 {+4.45} Rd3 $0 {+4.41} 
40. Qa8 $0 {+4.41} 40... c3 $0 {+4.86} (40... Rb3+ {+4.41 - Brainfish}) 
41. Qa4+ $0 {+4.46} Ke1 $0 {+4.63} 
42. f4 $5 {+5.29} (42. Qf4 {+4.63 - Brainfish}) 42... f5 $0 {+5.74} (42... Rd2 {+5.29 - Brainfish}) 
43. Kc1 {+6.37} Rd2 $0 {+5.85} 
44. Qa7 {+6.68} 1-0

2. Epd analysis, annotate epd with acd, acs, bm, ce and Ae op codes

a. Command line
chess-artist -infile a.epd -outfile out_a.epd -eng Branfish.exe -enghash 128 -engthreads 1 -movetime 10000 -eval search

b. Command line interpretation
-enghash 128: The main memory size in MB used by the uci engine, also call Hash in uci engines.
-engthreads 1: The number of threads used by the uci engine, also called Threads in uci engines.
-eval search: Will use use the engine to search the position. -eval static, will only use the static eval of the engine.

c. An example epd line in an epd file
r1bk1b1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK1 w - -

d. An example output using -eval search
r1bk1b1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK1 w - - acd 17; acs 10; bm Nc3; ce 30; Ae "Brainfish 280816 64 POPCNT";

e. An example output using -eval static
r1bk1b1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK1 w - - ce 30; c0 "ce is static eval of engine"; Ae "Brainfish 280816 64 POPCNT";

3. Testing engine on epd test suite.

a. Command line
chess-artist -infile wac.epd -outfile wac_out.txt -eng Bf.exe -enghash 128 -engthreads 1 -movetime 300 -job test

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
