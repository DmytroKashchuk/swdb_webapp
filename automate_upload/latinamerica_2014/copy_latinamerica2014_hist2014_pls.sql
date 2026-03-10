-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2014/Hist2014_PLS.txt

\copy latinamerica_2014_hist2014_pls FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2014/Hist2014_PLS_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
