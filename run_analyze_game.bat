:: Analyze games


:: Example command line

:: chess_artist.py --infile PGN/tatagpa20.pgn --outfile ana_tatagpa20.pgn --enginefile D:\Chess\Engines\Stockfish\stockfish_20071122_x64_modern.exe --enginename "Stockfish_2020-07-11" --engineoptions "Threads value 1, Hash value 128" --movestart 8 --movetime 3000 --job analyze --eval search --log

:: Analyze atomic variant
:: chess_artist.py --infile PGN/sample_atomic.pgn --outfile ana_sample_atomic.pgn --enginefile D:\github\chess-artist\Engine\Stockfish_2020-06-13_Multi-Variant.exe --enginename "Stockfish_multi-variant" --engineoptions "Threads value 1, Hash value 128, UCI_Variant value Atomic" --movestart 2 --movetime 2000 --job analyze --eval search --log

:: Analyze atomic960
chess_artist.py --game960 --infile PGN/sample_atomic_chess960.pgn --outfile ana_sample_atomic_chess960.pgn --enginefile D:\github\chess-artist\Engine\Stockfish_2020-06-13_Multi-Variant.exe --enginename "Stockfish_multi-variant" --engineoptions "Threads value 1, Hash value 128, UCI_Variant value Atomic, UCI_Chess960 value true" --movestart 2 --movetime 3000 --job analyze --eval search --log

pause
