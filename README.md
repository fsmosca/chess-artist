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
`python chess-artist.py --infile sample.pgn --outfile out_sample.pgn --enginefile Stockfish.exe --engineoptions "Hash value 128, Threads value 1" --eval search --job analyze --movetime 2000`<br><br>
Will analyze games inside sample.pgn and output the analyzed games in out_sample.pgn. It uses engine Stockfish.exe with Hash 128MB and Threads 1 at 2000 millisec or 2 sec analysis time per position. chess-artist.py and Stockfish.exe engine must be in same directory.<br>

### Test engine with test suite
`python chess-artist.py --infile wacnew.epd --outfile result_wacnew.txt --enginefile stockfish_10.exe --engineoptions "Hash value 128, Threads value 1" --eval search --job test --movetime 500`<br><br>
Output file result_wacnew.txt<br>
```
:: EPD wacnew.epd TEST RESULTS ::
Engine        : Stockfish 10 64 POPCNT
Time/pos (sec): 0.5

Total epd lines       : 300
Total tested positions: 300
Total correct         : 279
Correct percentage    : 93.0
```
### Analyze epd file
`python chess-artist.py --infile puzzle.epd --outfile out_puzzle.epd --enginefile stockfish_10.exe --engineoptions "Hash value 128, Threads value 1" --eval search --job analyze --movetime 1000`
