-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2002/Hist2002_TRENDSYSTEM.txt

\copy latinamerica_2002_hist2002_trendsystem FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2002/Hist2002_TRENDSYSTEM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
