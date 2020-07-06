:: Annotate games

chess_artist.exe --infile pgn\iommast19.pgn --outfile analyzed_iommast19.pgn ^
--enginefile Engine\stockfish\windows\stockfish_10_x64_popcnt.exe ^
--engineoptions "Hash value 128" ^
--movestart 15 --movetime 5000 ^
--job analyze --eval search

pause

