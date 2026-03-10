-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2005/Hist2005_TRENDSYSTEM.txt

\copy latinamerica_2005_hist2005_trendsystem FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2005/Hist2005_TRENDSYSTEM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
