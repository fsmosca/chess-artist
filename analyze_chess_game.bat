:: Analyze games in tatasteel 2020 using Stockfish 14.1

python chess_artist.py --infile ./PGN/skillingopp20.pgn --outfile ana_skillingopp20.pgn --enginefile ./Engine/stockfish/stockfish_14.1_win_x64_popcnt.exe --engineoptions "Threads value 1, Hash value 128" --movestart 8 --movetime 2000 --job analyze --eval search --log


pause
