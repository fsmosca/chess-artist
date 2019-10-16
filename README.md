# Chess Artist
A python script that can analyze games in the pgn file. It can also analyze epd file, and can also test the engine using epd test suites. Only Python 2 is so far supported.

## A. Requirements
* [Python 2.7](https://www.python.org/downloads/release/python-2715/)
* [Python-chess v0.21.2](https://github.com/niklasf/python-chess)
* [UCI chess engines](https://stockfishchess.org/download/)
* PGN file
* EPD file

## B. Command lines
### 1. Analyze games in pgn file
#### a) Basic command line
`python chess-artist.py --infile sample.pgn --outfile out_sample.pgn --enginefile Stockfish.exe --eval search --job analyze --movetime 2000`  

or  

`chess-artist.exe ...`

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
`python chess-artist.py --infile sample.pgn --outfile out_sample.pgn --enginefile Stockfish.exe --eval search --job analyze --movetime 2000 --movestart 12 --moveend 20 --player "Carlsen, Magnus" --color black`

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
`python chess-artist.py --infile wacnew.epd --outfile result_wacnew.txt --enginefile stockfish_10.exe --engineoptions "Hash value 128, Threads value 1" --eval search --job test --depth 10 --movetime 0'

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
_Calculation of passer and king safety are from Stockfish engine static evaluation._

