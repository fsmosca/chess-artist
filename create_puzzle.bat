:: Generate puzzles


:: Example command line
:: chess_artist.py --infile pgn\tatagpa20.pgn --outfile out_tatagpa20.pgn --enginename "Lc0 v0.23.2 w591097 blas" --enginefile D:\Chess\Engines\Lc0\lc0-v0.23.2-591097-10X128\lc0.exe --engineoptions "Threads value 2, MinibatchSize value 8, MaxPrefetch value 0" --movestart 15 --movetime 10000 --job createpuzzle --eval search --log


:: Create puzzle using atomic variant
:: chess_artist.py --infile pgn\sample_atomic.pgn --outfile dummy.pgn --enginename "Stockfish_2020-06-13_Multi-Variant" --enginefile D:\github\chess-artist\Engine\Stockfish_2020-06-13_Multi-Variant.exe --engineoptions "Threads value 1, Hash value 128, UCI_Variant value Atomic" --movestart 2 --movetime 1000 --job createpuzzle --eval search --log


:: Create puzzle from an atomic960 game
chess_artist.py --game960 --infile pgn\sample_atomic_chess960.pgn --outfile dummy.pgn --enginename "Stockfish_2020-06-13_Multi-Variant" --enginefile D:\github\chess-artist\Engine\Stockfish_2020-06-13_Multi-Variant.exe --engineoptions "Threads value 1, Hash value 128, UCI_Variant value Atomic, UCI_Chess960 value true" --movestart 2 --movetime 10000 --job createpuzzle --eval search --log

pause

