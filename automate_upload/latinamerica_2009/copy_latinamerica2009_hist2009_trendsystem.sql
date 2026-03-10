-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2009/Hist2009_TRENDSYSTEM.txt

\copy latinamerica_2009_hist2009_trendsystem FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2009/Hist2009_TRENDSYSTEM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
