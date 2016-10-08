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
   chess-artist -inpgn mygames.pgn -outpgn mygames_se.pgn -eng stockfish.exe -eval static
5. If you want the game to be annotated with moves from Cerebellum_Light.bin book use the
   following command line using the -book option and Brainfish engine. The book Cerebellum_Light.bin
   should be in the same directory with the Brainfish engine and the script chess-artist.py.
   chess-artist -inpgn myg.pgn -outpgn myg_cere.pgn -eng Brainfish.exe -book cerebellum -eval none
6. If you want the game to be annotated with moves from Cerebellum_Light.bin book and with static eval
   use the following command line. The book Cerebellum_Light.bin should be in the same directory with
   the Brainfish engine and the script chess-artist.py.
   chess-artist -inpgn myg.pgn -outpgn myg_cere_se.pgn -eng Brainfish.exe -book cerebellum -eval static
7. If you want the game to be annotated with engine search score, use the following command line.
   chess-artist -inpgn myg.pgn -outpgn myg_es.pgn -eng stockfish.exe -eval search
8. In the annotated game the value in the comment is from the point of
   view of white, if it is positive, it is better for white, and if
   negative it is better for black. Example 1. e4 {+0.74} white is ahead
   by 0.74 of a pawn, or almost 3/4 value of a pawn.
   
H. Example annotated game with static eval and cerebellum book
[Event "4th Sinquefield Cup 2016"]
[Site "Saint Louis USA"]
[Date "2016.08.05"]
[Round "1.1"]
[White "Giri, Anish"]
[Black "Vachier-Lagrave, Maxime"]
[Result "1/2-1/2"]
[WhiteTitle "GM"]
[BlackTitle "GM"]
[WhiteElo "2769"]
[BlackElo "2819"]
[ECO "B90"]
[Opening "Sicilian"]
[Variation "Najdorf"]
[WhiteFideId "24116068"]
[BlackFideId "623539"]
[EventDate "2016.08.05"]
[Annotator "Brainfish 280816 64 POPCNT"]

1. e4 {+0.83} (1. e4 {cerebellum book}) 1... c5 {+0.71} (1... e5 {cerebellum book}) 
2. Nf3 {+1.05} (2. Nf3 {cerebellum book}) 2... d6 {+0.41} (2... d6 {cerebellum book}) 
3. d4 {+1.21} (3. d4 {cerebellum book}) 3... cxd4 {+0.32} (3... cxd4 {cerebellum book}) 
4. Nxd4 {+1.37} (4. Nxd4 {cerebellum book}) 4... Nf6 {+0.68} (4... Nf6 {cerebellum book}) 
5. Nc3 {+1.26} (5. Nc3 {cerebellum book}) 5... a6 {+1.08} (5... a6 {cerebellum book}) 
6. Be3 {+1.24} (6. Be3 {cerebellum book}) 6... Ng4 {+1.27} (6... e5 {cerebellum book}) 
7. Bc1 {+0.97} (7. Bg5 {cerebellum book}) 7... Nf6 {+1.08} (7... Nf6 {cerebellum book}) 
8. f3 {+1.03} (8. Be3 {cerebellum book}) 8... e5 {+0.40} (8... e5 {cerebellum book}) 
9. Nb3 {+0.72} (9. Nb3 {cerebellum book}) 9... Be6 {+0.37} (9... Be6 {cerebellum book}) 
10. Be3 {+0.66} (10. Be3 {cerebellum book}) 10... Be7 {+0.59} (10... Be7 {cerebellum book}) 
11. Qd2 {+0.53} (11. Be2 {cerebellum book}) 11... O-O {-0.19} (11... O-O {cerebellum book}) 
12. O-O-O {+0.15} (12. h4 {cerebellum book}) 12... Nbd7 {-0.21} (12... Nbd7 {cerebellum book}) 
13. g4 {-0.21} (13. Kb1 {cerebellum book}) 13... b5 {-0.29} (13... b5 {cerebellum book}) 
14. g5 {+0.09} (14. Nd5 {cerebellum book}) 14... b4 {-0.17} (14... Nh5 {cerebellum book}) 
15. gxf6 {+3.36} (15. Ne2 {cerebellum book}) 15... bxc3 {-0.54} (15... bxc3 {cerebellum book}) 
16. Qxc3 {+1.24} (16. Qxc3 {cerebellum book}) 16... Nxf6 {-0.20} (16... Nxf6 {cerebellum book}) 
17. Na5 {-0.35} (17. Na5 {cerebellum book}) 17... Rc8 {-0.44} (17... Qd7 {cerebellum book}) 
18. Nc6 {+0.26} (18. Nc6 {cerebellum book}) 18... Qe8 {+0.15} (18... Qc7 {cerebellum book}) 
19. Nxe7+ {+3.74} (19. Nxe7+ {cerebellum book}) 19... Qxe7 {-0.23} (19... Qxe7 {cerebellum book}) 
20. Qa5 {-0.45} (20. Qa5 {cerebellum book}) 20... Rc6 {-0.45} (20... Rc6 {cerebellum book}) 
21. Kb1 {-0.12} (21. Rg1 {cerebellum book}) 21... Rfc8 {-0.61} (21... Rfc8 {cerebellum book}) 
22. Rd2 {-0.57} (22. Rg1 {cerebellum book}) 22... Nh5 {-0.35} (22... Nh5 {cerebellum book}) 
23. Rg1 {-0.04} (23. Rg1 {cerebellum book}) 23... Qh4 {-0.84} (23... Qf6 {cerebellum book}) 
24. Be2 {+0.00} Nf4 {-0.46} 25. Bd1 {-0.63} f5 {-0.43} 
26. exf5 {+0.23} Bxf5 {-0.66} 27. Ka1 {-0.66} d5 {-1.01} 
28. c3 {-0.85} Rg6 {-0.79} 29. Rxg6 {+3.86} hxg6 {+0.14} 
30. Bxf4 {+4.07} Qxf4 {-0.35} 31. Qxd5+ {+1.21} Kh7 {+1.42} 
32. Bb3 {+1.66} a5 {+1.72} 33. a4 {+1.57} Re8 {+1.92} 
34. Ka2 {+1.80} Be6 {+1.68} 35. Qc6 {+1.05} Bxb3+ {-2.31} 
36. Kxb3 {+0.74} Rb8+ {+0.80} 37. Kc2 {+0.49} Rxb2+ {-0.32} 
38. Kxb2 {+5.97} Qxd2+ {+0.35} 39. Kb3 {+0.15} Qxh2 {+0.07} 
40. Qd5 {+0.08} Qe2 {+0.04} 41. Qxa5 {+0.15} Qd1+ {+0.64} 
42. Kb2 {+0.02} Qd2+ {+0.49} 43. Kb3 {+0.31} Qd1+ {+0.64} 
44. Kb2 {+0.02} Qd2+ {+0.49} 45. Ka3 {+0.26} Qc1+ {+0.54} 
46. Kb4 {+0.72} Qb1+ {+1.03} 47. Ka3 {+0.35} 1/2-1/2

I. Todo list
0. Refactor WriteMoves()
1. Annotate a game using an engine's search score along with standard annotation symbols.
2. Annotate a game with polyglot book.
3. Calculate the players' estimated rating based on engine's analysis.
