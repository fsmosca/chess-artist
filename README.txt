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

F. Tests
1. This is tested under Windows 7 OS, with python 2.7.11
   and python-chess 0.14.1 installed.

G. Guide
1. You need to install python 2.7 version (or 3.5 not tested)
   on your computer.
2. You need to install also python-chess on your computer, see section E.
3. Rename your input pgn file to src.pgn.
4. Rename your chess engine filename to engine.exe.
5. Location or directory of src.pgn, engine.exe and this script chess-artist.py
   should be the same. Only Stockfish engine is supported so far. You can
   download the stockfish engine from here,
   https://stockfishchess.org/
6. Run the script.
7. The output filename is out_src.pgn, this is in overwrite mode.
8. In the annotated game the value in the comment is from the point of
   view of white, if it is positive, it is better for white, and if
   negative it is better for black. Example 1. e4 {+0.74} white is ahead
   by 0.74 of a pawn, or almost 3/4 value of a pawn.
   
I. Example annotated game
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
[Annotator "Stockfish 7 64 POPCNT"]

1. e4 {+0.74} c5 {+0.65} 2. Nf3 {+0.95} d6 {+0.39} 3. d4 {+1.12} cxd4 {+0.35} 
4. Nxd4 {+1.17} Nf6 {+0.54} 5. Nc3 {+1.06} a6 {+0.98} 6. Be3 {+1.11} Ng4 {+1.14} 
7. Bc1 {+0.85} Nf6 {+0.98} 8. f3 {+0.90} e5 {+0.27} 9. Nb3 {+0.62} Be6 {+0.30} 
10. Be3 {+0.58} Be7 {+0.52} 11. Qd2 {+0.46} O-O {-0.18} 12. O-O-O {+0.12} Nbd7 {-0.21} 
13. g4 {-0.25} b5 {-0.26} 14. g5 {+0.16} b4 {-0.14} 15. gxf6 {+3.36} bxc3 {-0.52} 
16. Qxc3 {+1.16} Nxf6 {-0.34} 17. Na5 {-0.47} Rc8 {-0.47} 18. Nc6 {+0.22} Qe8 {+0.21} 
19. Nxe7+ {+3.73} Qxe7 {-0.14} 20. Qa5 {-0.36} Rc6 {-0.37} 21. Kb1 {-0.05} Rfc8 {-0.54} 
22. Rd2 {-0.41} Nh5 {-0.20} 23. Rg1 {-0.02} Qh4 {-0.53} 24. Be2 {+0.05} Nf4 {-0.25} 
25. Bd1 {-0.41} f5 {-0.19} 26. exf5 {+0.34} Bxf5 {-0.51} 27. Ka1 {-0.55} d5 {-0.83} 
28. c3 {-0.71} Rg6 {-0.64} 29. Rxg6 {+3.83} hxg6 {+0.31} 30. Bxf4 {+3.97} Qxf4 {-0.26} 
31. Qxd5+ {+1.24} Kh7 {+1.40} 32. Bb3 {+1.57} a5 {+1.69} 33. a4 {+1.52} Re8 {+1.79} 
34. Ka2 {+1.68} Be6 {+1.64} 35. Qc6 {+1.05} Bxb3+ {-2.23} 36. Kxb3 {+0.90} Rb8+ {+0.95} 
37. Kc2 {+0.38} Rxb2+ {-0.44} 38. Kxb2 {+5.69} Qxd2+ {+0.30} 39. Kb3 {+0.06} Qxh2 {-0.03} 
40. Qd5 {+0.07} Qe2 {+0.03} 41. Qxa5 {+0.16} Qd1+ {+0.73} 42. Kb2 {+0.06} Qd2+ {+0.66} 
43. Kb3 {+0.44} Qd1+ {+0.73} 44. Kb2 {+0.06} Qd2+ {+0.66} 45. Ka3 {+0.24} Qc1+ {+0.72} 
46. Kb4 {+0.48} Qb1+ {+1.17} 47. Ka3 {+0.29}  1/2-1/2
