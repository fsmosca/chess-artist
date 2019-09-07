# Chess Artist
A python script that can analyze games in the pgn file. It can also analyze epd file, and can also test the engine using epd test suites. Only Python 2 is so far supported.

## Requirements
* [Python 2](https://www.python.org/downloads/release/python-2715/)
* [Python-chess](https://github.com/niklasf/python-chess)
* [UCI chess engines](https://stockfishchess.org/download/)
* PGN file
* EPD file

## Command lines
### Analyze games in pgn file
#### Basic command line
`python chess-artist.py --infile sample.pgn --outfile out_sample.pgn --enginefile Stockfish.exe --eval search --job analyze --movetime 2000`
#### Add options to engine, use --engineoptions
`python chess-artist.py --infile sample.pgn --outfile out_sample.pgn --enginefile Stockfish.exe --engineoptions "Hash value 128, Threads value 1" --eval search --job analyze --movetime 2000`<br><br>
Will analyze games inside sample.pgn and output the analyzed games in out_sample.pgn. It uses engine Stockfish.exe with Hash 128MB and Threads 1 at 2000 millisec or 2 sec analysis time per position. chess-artist.py and Stockfish.exe engine must be in same directory.<br>

#### Analyze game with polyglot book
`python chess-artist.py --infile sample.pgn --outfile out_sample.pgn --enginefile Stockfish.exe --engineoptions "Hash value 128, Threads value 1" --bookfile gm2600.bin --eval search --job analyze --movetime 2000`

### Test engine with test suite
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

### Annotate the epd file
#### Use Stockfish to annotate epd file at movetime 30s or 30000ms
`python2 chess-artist.py --infile repertoire.epd --outfile out_repertoire.epd --enginefile stockfish_10.exe --engineoptions "Hash value 128, Threads value 1" --eval search --job analyze --movetime 30000`

Example output:
```
rn1q1rk1/pbp2ppp/1p1ppn2/6B1/2PP4/P1Q1P3/1P3PPP/R3KBNR w KQ - c0 "Nimzo-Indian"; acd 26; acs 30; bm f3; ce +46; Ae "Stockfish 10 64 POPCNT";
rnbq1rk1/pp2ppbp/6p1/2p5/3PP3/2P2N2/P4PPP/1RBQKB1R w K - c0 "Gruenfeld"; acd 26; acs 30; bm Be2; ce +74; Ae "Stockfish 10 64 POPCNT";
```
#### Use Stockfish to annotate epd file with depth equals 16 and no movetime
`python2 chess-artist.py --infile repertoire.epd --outfile out_repertoire.epd --enginefile stockfish_10.exe --engineoptions "Hash value 128, Threads value 1" --eval search --job analyze --depth 16 --movetime 0`

## Credits
* Niklas Fiekas<br>
https://github.com/niklasf/python-chess
* Thomas Zipproth<br>
https://zipproth.de/#Brainfish_download

