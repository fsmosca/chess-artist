A. Program name
Chess Artist

B. Program description
It is a python script that can annotate chess games in pgn file with
static evaluation and search score of an engine. It can also annotate
games with cerebellum book moves using the Brainfish engine with its
Cerebellum_Light.bin book file.

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
[EventDate "2016.10.05"]
[Annotator "Brainfish 280816 64 POPCNT"]

{Hash 128mb, Threads 1, engine search score @ 5.0s/pos}
1. d4 d5 2. c4 e6 3. Nf3 Nf6 4. g3 c6 5. Bg2 Be7 6. O-O O-O 7. b3 b6 8. Bb2 Bb7 9. Nc3 Na6 10. Qd3 Rc8 11. cxd5 cxd5 12. Rac1 $0 {-0.03} (12. Rfc1 {+0.00 - Brainfish 280816 64 POPCNT})12... Nb4 $0 {+0.00} (12... Ne4 {-0.03 - Brainfish 280816 64 POPCNT})
13. Qb1 {+0.06} 13... Qd6 $0 {+0.00} (13... Nc6 {+0.03 - Brainfish 280816 64 POPCNT})
14. Rfd1 $0 {+0.00} (14. a3 {+0.00 - Brainfish 280816 64 POPCNT})14... Ba6 $0 {+0.06} (14... Qb8 {+0.00 - Brainfish 280816 64 POPCNT})
15. e3 $0 {+0.09} (15. a3 {+0.06 - Brainfish 280816 64 POPCNT})15... Qb8 $0 {+0.08} (15... Nc6 {+0.09 - Brainfish 280816 64 POPCNT})
16. Ne5 {+0.08} Bb7 {+0.11} 
17. Bf1 $0 {-0.06} (17. f4 {+0.07 - Brainfish 280816 64 POPCNT})Nc6 {-0.04} 
18. Nf3 {+0.00} 18... Rfd8 $0 {-0.07} (18... h6 {+0.00 - Brainfish 280816 64 POPCNT})
19. a3 $0 {-0.14} (19. Be2 {-0.07 - Brainfish 280816 64 POPCNT})Na5 {-0.15} 
20. Qa2 {-0.03} 20... Rc7 $0 {-0.02} (20... a6 {-0.03 - Brainfish 280816 64 POPCNT})
21. Nd2 $0 {-0.14} (21. Ne5 {-0.02 - Brainfish 280816 64 POPCNT})Rdc8 {-0.11} 
22. b4 $0 {-0.03} (22. Bd3 {-0.11 - Brainfish 280816 64 POPCNT})22... Nc6 $0 {+0.00} (22... Nc4 {-0.03 - Brainfish 280816 64 POPCNT})
23. Nf3 $0 {-0.06} (23. Bd3 {+0.00 - Brainfish 280816 64 POPCNT})Qa8 {+0.00} 
24. Qb3 $0 {-0.08} (24. Qb1 {+0.00 - Brainfish 280816 64 POPCNT})24... h6 $0 {-0.05} (24... a6 {-0.08 - Brainfish 280816 64 POPCNT})
25. h3 $6 {-0.17} (25. Bd3 {-0.05 - Brainfish 280816 64 POPCNT})25... Bf8 $0 {-0.05} (25... a6 {-0.12 - Brainfish 280816 64 POPCNT})
26. Nb5 $0 {-0.04} (26. Rc2 {-0.05 - Brainfish 280816 64 POPCNT})Rd7 {+0.00} 
27. Nc3 $0 {+0.00} (27. Rc2 {+0.00 - Brainfish 280816 64 POPCNT})27... Rdd8 $0 {+0.06} (27... Bd6 {+0.00 - Brainfish 280816 64 POPCNT})
28. Rc2 {-0.03} 28... Ne7 $0 {+0.08} (28... Ne4 {-0.03 - Brainfish 280816 64 POPCNT})
29. Rdc1 {+0.17} Nf5 {+0.10} 
30. Ne5 $0 {+0.15} (30. Nb5 {+0.10 - Brainfish 280816 64 POPCNT})Nd6 {+0.15} 
31. a4 $0 {-0.05} (31. Nb5 {+0.15 - Brainfish 280816 64 POPCNT})31... a6 $6 {+0.41} (31... Nd7 {-0.05 - Brainfish 280816 64 POPCNT})
32. Ba3 $0 {+0.29} (32. b5 {+0.41 - Brainfish 280816 64 POPCNT})32... Nf5 $0 {+0.65} (32... Nfe4 {+0.29 - Brainfish 280816 64 POPCNT})
33. b5 {+0.54} 33... Bxa3 $0 {+0.67} (33... Bd6 {+0.54 - Brainfish 280816 64 POPCNT})
34. Qxa3 {+0.73} 34... axb5 $4 {+1.56} (34... Ne8 {+0.73 - Brainfish 280816 64 POPCNT})
35. Nxb5 {+1.56} Rxc2 {+1.79} 
36. Rxc2 {+1.73} 36... Rc8 $0 {+3.44} (36... Rf8 {+1.73 - Brainfish 280816 64 POPCNT})
37. Rxc8+ {+3.88} Qxc8 {+3.81} 
38. g4 {+3.84} 38... Nh4 $0 {+4.31} (38... Qc2 {+3.84 - Brainfish 280816 64 POPCNT})
39. Qe7 {+4.01} 39... Bc6 $0 {+6.70} (39... Ne4 {+4.01 - Brainfish 280816 64 POPCNT})
40. Qxf7+ {+6.55} 40... Kh7 $0 {+7.19} (40... Kh8 {+6.55 - Brainfish 280816 64 POPCNT})
41. Nd6 $0 {+7.44} (41. Bd3+ {+7.19 - Brainfish 280816 64 POPCNT})Qa8 {+8.56} 
42. Qxe6 $0 {+7.30} (42. Bd3+ {+8.56 - Brainfish 280816 64 POPCNT})42... Bxa4 $0 {+8.38} (42... Qxa4 {+7.30 - Brainfish 280816 64 POPCNT})
43. Nf5 $0 {+5.34} (43. Bd3+ {+8.38 - Brainfish 280816 64 POPCNT})43... Nxf5 $0 {+4.45} (43... Qe8 {+5.34 - Brainfish 280816 64 POPCNT})
44. Qxf5+ {+4.24} 44... Kg8 $0 {+5.75} (44... Kh8 {+4.22 - Brainfish 280816 64 POPCNT})
45. Qe6+ {+6.00} Kh7 {+6.14} 
46. h4 $0 {+4.57} (46. Bd3+ {+6.14 - Brainfish 280816 64 POPCNT})Bc2 {+4.83} 
47. g5 $0 {+4.05} (47. Qxb6 {+4.86 - Brainfish 280816 64 POPCNT})47... hxg5 $0 {+6.01} (47... Qe8 {+3.94 - Brainfish 280816 64 POPCNT})
48. hxg5 {+4.89} 48... Ne8 $0 {+319.81} (48... Qe8 {+5.10 - Brainfish 280816 64 POPCNT})
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
