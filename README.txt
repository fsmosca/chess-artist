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
   
H. Examples of annotated games with static evaluation, search score and cerebellum book move annotations.

(1) Static evaluation

[Event "10th Tal Mem 2016"]
[Site "Moscow RUS"]
[Date "2016.09.26"]
[Round "1.1"]
[White "Aronian, Levon"]
[Black "Gelfand, Boris"]
[Result "1/2-1/2"]
[WhiteTitle "GM"]
[BlackTitle "GM"]
[WhiteElo "2795"]
[BlackElo "2743"]
[ECO "A35"]
[Opening "English"]
[Variation "symmetrical, four knights system"]
[WhiteFideId "13300474"]
[BlackFideId "2805677"]
[EventDate "2016.09.26"]
[Annotator "Brainfish 280816 64 POPCNT"]

{Move comments are from engine static evaluation.}
1. c4 {+0.20} (1. e4 {cerebellum book}) 1... c5 {+0.08} (1... e6 {cerebellum book}) 
2. Nf3 {+0.53} (2. Nf3 {cerebellum book}) 2... Nc6 {+0.04} (2... Nc6 {cerebellum book}) 
3. Nc3 {+0.48} (3. Nc3 {cerebellum book}) 3... Nf6 {+0.08} (3... g6 {cerebellum book}) 
4. g3 {+0.23} (4. g3 {cerebellum book}) 4... d5 {-1.09} (4... d5 {cerebellum book}) 
5. d4 {+0.04} (5. d4 {cerebellum book}) 5... cxd4 {-1.72} (5... cxd4 {cerebellum book}) 
6. Nxd4 {-0.08} (6. Nxd4 {cerebellum book}) 6... dxc4 {-0.83} (6... dxc4 {cerebellum book}) 
7. Nxc6 {+4.95} (7. Nxc6 {cerebellum book}) 7... Qxd1+ {-7.60} (7... Qxd1+ {cerebellum book}) 
8. Nxd1 {+2.00} (8. Nxd1 {cerebellum book}) 8... bxc6 {-0.73} (8... bxc6 {cerebellum book}) 
9. Bg2 {-0.29} (9. Bg2 {cerebellum book}) 9... Nd5 {-0.24} (9... Nd5 {cerebellum book}) 
10. Ne3 {-0.08} (10. Ne3 {cerebellum book}) 10... e6 {-0.32} (10... Ba6 {cerebellum book}) 
11. Nxc4 {+0.53} (11. Nxc4 {cerebellum book}) 11... Ba6 {+0.18} (11... Ba6 {cerebellum book}) 
12. b3 {+0.26} (12. b3 {cerebellum book}) 12... Bb4+ {+0.27} (12... Bb4+ {cerebellum book}) 
13. Bd2 {+0.19} (13. Bd2 {cerebellum book}) 13... Ke7 {+0.14} (13... Bxd2+ {cerebellum book}) 
14. Rc1 {+0.20} (14. Rc1 {cerebellum book}) 14... Rhc8 {+0.31} (14... Rhc8 {cerebellum book}) 
15. Ne5 {+0.16} (15. Bxb4+ {cerebellum book}) c5 {+0.05} 16. Bxb4 {+3.71} cxb4 {-0.03} 
17. Rxc8 {+7.10} Rxc8 {-0.25} 18. Bxd5 {+2.65} Kd6 {+2.46} 
19. Bf3 {+3.11} Kxe5 {-0.78} 20. Kd2 {-0.46} Rc5 {-0.21} 
21. a3 {-0.40} bxa3 {-2.16} 22. Ra1 {-1.63} Bb5 {-1.58} 
23. Rxa3 {-0.17} Rc7 {-0.26} 24. h4 {-0.40} h6 {-0.29} 
25. Ra2 {-0.37} g5 {-0.21} 26. hxg5 {+0.86} hxg5 {-0.14} 
27. Rc2 {-0.18} Rxc2+ {-6.05} 28. Kxc2 {-0.28} Kd4 {-0.07} 
29. e3+ {-0.08} Kc5 {+0.09} 30. Kc3 {+0.03} a5 {+0.15} 
31. Bd1 {-0.10} f6 {+0.02} 32. f4 {-0.19} e5 {-0.05} 
33. Bf3 {-0.07} Be8 {+0.13} 34. Bd1 {-0.14} Bb5 {-0.05} 
35. Bf3 {-0.07} Be8 {+0.13} 36. Bd1 {-0.14} Bb5 {-0.05} 
1/2-1/2

(2) Search score

[Event "10th Tal Mem 2016"]
[Site "Moscow RUS"]
[Date "2016.09.26"]
[Round "1.1"]
[White "Aronian, Levon"]
[Black "Gelfand, Boris"]
[Result "1/2-1/2"]
[WhiteTitle "GM"]
[BlackTitle "GM"]
[WhiteElo "2795"]
[BlackElo "2743"]
[ECO "A35"]
[Opening "English"]
[Variation "symmetrical, four knights system"]
[WhiteFideId "13300474"]
[BlackFideId "2805677"]
[EventDate "2016.09.26"]
[Annotator "Brainfish 280816 64 POPCNT"]

{Move comments are from engine search score.}
1. c4 {-0.05} (1. e4 {cerebellum book}) 1... c5 {+0.21} (1... e6 {cerebellum book}) 
2. Nf3 {+0.26} (2. Nf3 {cerebellum book}) 2... Nc6 {+0.19} (2... Nc6 {cerebellum book}) 
3. Nc3 {+0.17} (3. Nc3 {cerebellum book}) 3... Nf6 {+0.08} (3... g6 {cerebellum book}) 
4. g3 {-0.11} (4. g3 {cerebellum book}) 4... d5 {+0.00} (4... d5 {cerebellum book}) 
5. d4 {+0.03} (5. d4 {cerebellum book}) 5... cxd4 {+0.15} (5... cxd4 {cerebellum book}) 
6. Nxd4 {+0.24} (6. Nxd4 {cerebellum book}) 6... dxc4 {+0.29} (6... dxc4 {cerebellum book}) 
7. Nxc6 {+0.13} (7. Nxc6 {cerebellum book}) 7... Qxd1+ {+0.24} (7... Qxd1+ {cerebellum book}) 
8. Nxd1 {+0.25} (8. Nxd1 {cerebellum book}) 8... bxc6 {+0.27} (8... bxc6 {cerebellum book}) 
9. Bg2 {+0.19} (9. Bg2 {cerebellum book}) 9... Nd5 {+0.20} (9... Nd5 {cerebellum book}) 
10. Ne3 {+0.14} (10. Ne3 {cerebellum book}) 10... e6 {+0.05} (10... Ba6 {cerebellum book}) 
11. Nxc4 {+0.19} (11. Nxc4 {cerebellum book}) 11... Ba6 {+0.25} (11... Ba6 {cerebellum book}) 
12. b3 {+0.10} (12. b3 {cerebellum book}) 12... Bb4+ {+0.25} (12... Bb4+ {cerebellum book}) 
13. Bd2 {+0.26} (13. Bd2 {cerebellum book}) 13... Ke7 {+0.41} (13... Bxd2+ {cerebellum book}) 
14. Rc1 {+0.36} (14. Rc1 {cerebellum book}) 14... Rhc8 {+0.31} (14... Rhc8 {cerebellum book}) 
15. Ne5 {+0.16} (15. Bxb4+ {cerebellum book}) c5 {+0.18} 16. Bxb4 {+0.07} cxb4 {+0.21} 
17. Rxc8 {-0.24} Rxc8 {-0.15} 18. Bxd5 {-0.20} Kd6 {-0.13} 
19. Bf3 {-0.19} Kxe5 {-0.18} 20. Kd2 {-0.18} Rc5 {-0.19} 
21. a3 {-0.12} bxa3 {-0.16} 22. Ra1 {-0.36} Bb5 {+0.00} 
23. Rxa3 {+0.00} Rc7 {+0.01} 24. h4 {+0.00} h6 {+0.00} 
25. Ra2 {+0.00} g5 {+0.00} 26. hxg5 {-0.02} hxg5 {-0.03} 
27. Rc2 {-0.03} Rxc2+ {-0.06} 28. Kxc2 {-0.07} Kd4 {-0.07} 
29. e3+ {-0.08} Kc5 {-0.06} 30. Kc3 {-0.07} a5 {-0.07} 
31. Bd1 {-0.06} f6 {-0.07} 32. f4 {-0.03} e5 {-0.03} 
33. Bf3 {-0.02} Be8 {-0.12} 34. Bd1 {-0.04} Bb5 {-0.03} 
35. Bf3 {-0.02} Be8 {-0.12} 36. Bd1 {-0.04} Bb5 {-0.03} 
1/2-1/2
