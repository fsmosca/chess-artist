# Chess Artist
A python script that can analyze games in the pgn file. It can also analyze epd file, and can also test the engine using epd test suites. Only Python 2 is so far supported.

### Command line
1. Basic example<br><br>
`python2 chess-artist.py --infile sample.pgn --outfile out_sample.pgn --enginefile Stockfish.exe --engineoptions "Hash value 128, Threads value 1" --eval search --job analyze --movetime 2000`<br><br>
Will analyze games inside sample.pgn and output the analyzed games in out_sample.pgn. It uses engine Stockfish.exe with Hash 128MB and Threads 1 at 2000 millisec or 2 sec analysis time per position. chess-artist.py and Stockfish.exe engine must be in same directory.
