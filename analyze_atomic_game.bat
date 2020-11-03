:: Analyze atomic variant game

:: atomic960
chess_artist.py --game960 --infile ./PGN/sample_atomic_chess960.pgn --outfile ana_sample_atomic_chess960.pgn --enginefile ./Engine/stockfish/Stockfish_2020-06-13_Multi-Variant.exe --enginename "Stockfish_multi-variant" --engineoptions "Threads value 1, Hash value 128, UCI_Variant value Atomic, UCI_Chess960 value true" --movestart 2 --movetime 500 --job analyze --eval search --log

pause
