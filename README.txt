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
6. If you want the game to be annotated with moves from Cerebellum_Light.bin book and with static eval
   use the following command line. The book Cerebellum_Light.bin should be in the same directory with
   the Brainfish engine and the script chess-artist.py.
   chess-artist -infile myg.pgn -outfile myg_cere_se.pgn -eng Brainfish.exe -book cerebellum -eval static
7. If you want the game to be annotated with engine search score, at movetime of 1 second per position,
   engine Hash of 128 and Threads of 1, use the following command line.
   chess-artist -infile myg.pgn -outfile myg_es.pgn -eng stockfish.exe -enghash 128 -engthreads 1 -eval search -movetime 1000
8. If you want to annotate an epd file with bm, ce and other op codes at 10s per position. See example output in section H below.
   chess-artist -infile myepd.epd -outfile myepd_out.epd -eng Branfish.exe -enghash 128 -engthreads 1 -movetime 10000
9. If you want to test a uci engine on epd test suite to see how many best moves it could find, add the -job test option value.
   chess-artist -infile wacnew.epd -outfile wacnew_out.txt -eng Sf.exe -enghash 128 -engthreads 1 -movetime 500 -job test
10. In the annotated game the value in the comment is from the point of
   view of white, if it is positive, it is better for white, and if
   negative it is better for black. Example 1. e4 {+0.74} white is ahead
   by 0.74 of a pawn.
   
H. Examples of annotated games with static evaluation, search score and cerebellum book move annotations.

(1) Search score by the engine with cerebellum book

[Event "TCh-RUS w Rapid 2016"]
[Site "Sochi RUS"]
[Date "2016.10.05"]
[Round "2.1"]
[White "Pogonina, Natalija"]
[Black "Sukhareva, Evgeniya"]
[Result "1-0"]
[WhiteTitle "WGM"]
[WhiteElo "2484"]
[BlackElo "2151"]
[ECO "D30"]
[Opening "Queen's gambit declined"]
[WhiteTeam "Yugra (Khanty)"]
[BlackTeam "Tyumen (Tyumen region)"]
[WhiteFideId "4147855"]
[BlackFideId "4167155"]
[Event "TCh-RUS w Rapid 2016"]
[Site "Sochi RUS"]
[Date "2016.10.05"]
[Round "2.1"]
[White "Pogonina, Natalija"]
[Black "Sukhareva, Evgeniya"]
[Result "1-0"]
[WhiteTitle "WGM"]
[WhiteElo "2484"]
[BlackElo "2151"]
[ECO "D30"]
[Opening "Queen's gambit declined"]
[WhiteTeam "Yugra (Khanty)"]
[BlackTeam "Tyumen (Tyumen region)"]
[WhiteFideId "4147855"]
[BlackFideId "4167155"]
[EventDate "2016.10.05"]
[Annotator "Brainfish 280816 64 POPCNT"]

{Hash 128mb, Threads 1, engine search score @ 1.0s/pos}
1. d4 (1. e4 {cerebellum book}) 1... d5 (1... d5 {cerebellum book}) 
2. c4 (2. c4 {cerebellum book}) 2... e6 (2... e6 {cerebellum book}) 
3. Nf3 (3. Nf3 {cerebellum book}) 3... Nf6 (3... Nf6 {cerebellum book}) 
4. g3 (4. Nc3 {cerebellum book}) 4... c6 (4... Bb4+ {cerebellum book}) 
5. Bg2 (5. Bg2 {cerebellum book}) 5... Be7 (5... Be7 {cerebellum book}) 
6. O-O {+0.10} (6. O-O {cerebellum book}) 6... O-O $0 {+0.03} (6... O-O {cerebellum book}) (6... Nbd7 {+0.10 - Brainfish 280816 64 POPCNT}) 
7. b3 $0 {+0.08} (7. b3 {cerebellum book}) (7. e3 {+0.03 - Brainfish 280816 64 POPCNT}) 7... b6 $6 {+0.24} (7... b6 {cerebellum book}) (7... Nbd7 {+0.08 - Brainfish 280816 64 POPCNT}) 
8. Bb2 {+0.20} (8. Bb2 {cerebellum book}) 8... Bb7 {+0.27} (8... Nbd7 {cerebellum book}) 
9. Nc3 {+0.24} (9. Nc3 {cerebellum book}) 9... Na6 $0 {+0.39} (9... Ne4 {cerebellum book}) (9... Nbd7 {+0.24 - Brainfish 280816 64 POPCNT}) 
10. Qd3 $0 {+0.15} (10. Ne5 {cerebellum book}) (10. Ne5 {+0.40 - Brainfish 280816 64 POPCNT}) 10... Rc8 $6 {+0.16} (10... c5 {+0.15 - Brainfish 280816 64 POPCNT})
11. cxd5 $0 {-0.11} (11. Ne5 {+0.16 - Brainfish 280816 64 POPCNT})11... cxd5 $0 {-0.17} (11... Nb4 {-0.11 - Brainfish 280816 64 POPCNT})
12. Rac1 $0 {-0.09} (12. Qd2 {-0.11 - Brainfish 280816 64 POPCNT})12... Nb4 $0 {+0.00} (12... Ne4 {-0.09 - Brainfish 280816 64 POPCNT})
13. Qb1 {-0.02} 13... Qd6 $0 {+0.00} (13... Nc6 {+0.02 - Brainfish 280816 64 POPCNT})
14. Rfd1 $0 {-0.03} (14. a3 {+0.00 - Brainfish 280816 64 POPCNT})14... Ba6 $0 {+0.08} (14... Nc6 {-0.03 - Brainfish 280816 64 POPCNT})
15. e3 $0 {+0.08} (15. Ne5 {+0.08 - Brainfish 280816 64 POPCNT})15... Qb8 $0 {+0.02} (15... Nc6 {+0.08 - Brainfish 280816 64 POPCNT})
16. Ne5 $0 {+0.06} (16. a3 {+0.02 - Brainfish 280816 64 POPCNT})Bb7 {+0.08} 
17. Bf1 $0 {-0.09} (17. f4 {+0.08 - Brainfish 280816 64 POPCNT})Nc6 {-0.03} 
18. Nf3 {-0.09} 18... Rfd8 $0 {-0.10} (18... h6 {-0.09 - Brainfish 280816 64 POPCNT})
19. a3 $0 {+0.00} (19. Be2 {-0.09 - Brainfish 280816 64 POPCNT})Na5 {-0.04} 
20. Qa2 $0 {-0.15} (20. Nd2 {-0.04 - Brainfish 280816 64 POPCNT})20... Rc7 $0 {-0.05} (20... a6 {-0.08 - Brainfish 280816 64 POPCNT})
21. Nd2 {-0.05} Rdc8 {-0.17} 
22. b4 $0 {+0.00} (22. Bd3 {-0.17 - Brainfish 280816 64 POPCNT})Nc6 {+0.00} 
23. Nf3 $0 {-0.15} (23. Bd3 {+0.00 - Brainfish 280816 64 POPCNT})Qa8 {-0.12} 
24. Qb3 $0 {-0.07} (24. Qb1 {-0.12 - Brainfish 280816 64 POPCNT})24... h6 $0 {-0.04} (24... a6 {-0.07 - Brainfish 280816 64 POPCNT})
25. h3 $6 {-0.17} (25. Bd3 {-0.04 - Brainfish 280816 64 POPCNT})25... Bf8 $0 {-0.03} (25... Nb8 {-0.17 - Brainfish 280816 64 POPCNT})
26. Nb5 $0 {+0.00} (26. h4 {-0.03 - Brainfish 280816 64 POPCNT})Rd7 {-0.01} 
27. Nc3 $0 {-0.10} (27. Ne5 {-0.01 - Brainfish 280816 64 POPCNT})27... Rdd8 $0 {+0.00} (27... Qb8 {-0.10 - Brainfish 280816 64 POPCNT})
28. Rc2 $0 {+0.00} (28. Bd3 {+0.00 - Brainfish 280816 64 POPCNT})28... Ne7 $0 {+0.15} (28... Bd6 {+0.00 - Brainfish 280816 64 POPCNT})
29. Rdc1 {+0.13} 29... Nf5 $0 {+0.05} (29... Nc6 {+0.13 - Brainfish 280816 64 POPCNT})
30. Ne5 {+0.10} Nd6 {+0.09} 
31. a4 $0 {+0.00} (31. Nb5 {+0.09 - Brainfish 280816 64 POPCNT})31... a6 $6 {+0.41} (31... Nd7 {+0.00 - Brainfish 280816 64 POPCNT})
32. Ba3 $0 {+0.00} (32. b5 {+0.41 - Brainfish 280816 64 POPCNT})32... Nf5 $6 {+0.57} (32... Nc4 {+0.00 - Brainfish 280816 64 POPCNT})
33. b5 {+0.70} Bxa3 {+0.68} 
34. Qxa3 {+0.64} 34... axb5 $2 {+1.33} (34... Ne8 {+0.64 - Brainfish 280816 64 POPCNT})
35. Nxb5 {+1.49} 35... Rxc2 $4 {+1.58} (35... Ne4 {+1.49 - Brainfish 280816 64 POPCNT})
36. Rxc2 {+1.13} 36... Rc8 $4 {+3.55} (36... Ne4 {+1.13 - Brainfish 280816 64 POPCNT})
37. Rxc8+ {+3.50} Qxc8 {+3.63} 
38. g4 {+3.57} 38... Nh4 $0 {+3.77} (38... Qc2 {+3.35 - Brainfish 280816 64 POPCNT})
39. Qe7 {+3.75} 39... Bc6 $0 {+5.93} (39... Ne4 {+3.75 - Brainfish 280816 64 POPCNT})
40. Qxf7+ {+6.03} 40... Kh7 $0 {+6.46} (40... Kh8 {+6.03 - Brainfish 280816 64 POPCNT})
41. Nd6 $0 {+6.75} (41. Bd3+ {+6.46 - Brainfish 280816 64 POPCNT})41... Qa8 $0 {+7.19} (41... Qb8 {+6.75 - Brainfish 280816 64 POPCNT})
42. Qxe6 $0 {+6.98} (42. Bd3+ {+7.19 - Brainfish 280816 64 POPCNT})42... Bxa4 $0 {+7.67} (42... Qxa4 {+6.98 - Brainfish 280816 64 POPCNT})
43. Nf5 $0 {+4.36} (43. Bd3+ {+7.67 - Brainfish 280816 64 POPCNT})Nxf5 {+4.17} 
44. Qxf5+ {+3.94} 44... Kg8 $0 {+5.06} (44... Kh8 {+3.94 - Brainfish 280816 64 POPCNT})
45. Qe6+ {+4.71} 45... Kh7 $0 {+5.77} (45... Kh8 {+4.71 - Brainfish 280816 64 POPCNT})
46. h4 $0 {+3.93} (46. Bd3+ {+5.77 - Brainfish 280816 64 POPCNT})Bc2 {+4.22} 
47. g5 $0 {+3.21} (47. Qxb6 {+4.19 - Brainfish 280816 64 POPCNT})47... hxg5 $0 {+5.66} (47... Qe8 {+3.21 - Brainfish 280816 64 POPCNT})
48. hxg5 {+4.32} 48... Ne8 $0 {+319.81} (48... Qe8 {+4.32 - Brainfish 280816 64 POPCNT})
49. g6+ {+319.82} 1-0

(2) Epd analysis, annotate epd with acd, acs, bm, ce and Ae op codes

Input:
r1bk1b1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK1 w - -

Output:
r1bk1b1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK1 w - - acd 17; acs 10; bm Nc3; ce 30; Ae "Brainfish 280816 64 POPCNT";

(3) Sample output on engine testing on epd test suites.

:: EPD wacnewpartial.epd TEST RESULTS ::
Engine        : Brainfish 280816 64 POPCNT
Time/pos (sec): 0.3

Total epd lines       : 24
Total tested positions: 24
Total correct         : 23
Correct percentage    : 95.8
