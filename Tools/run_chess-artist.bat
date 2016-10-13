:: Lines with two colons (::) are comments,
:: to enable command line that begins with chess-artist, remove the two colons



:: (1) Analyze pgn file

:: chess-artist -infile anderssen_dufresne_1852.pgn -outfile out_anderssen_dufresne_1852.pgn -eng Bf.exe -eval search -movetime 5000 -movestart 8




:: (2) Test engine with epd suite

:: chess-artist -infile wacnew.epd -outfile out_wacnew.txt -eng Bf.exe -eval search -enghash 128 -engthreads 1 -movetime 300 -job test




:: (3) EPD analysis

chess-artist -infile carlsen.epd -outfile out_carlsen.epd -eng Bf.exe -eval search -enghash 128 -engthreads 1 -movetime 10000




pause
