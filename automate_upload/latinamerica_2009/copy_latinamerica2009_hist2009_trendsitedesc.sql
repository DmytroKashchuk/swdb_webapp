-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2009/Hist2009_TRENDSITEDESC.txt

\copy latinamerica_2009_hist2009_trendsitedesc FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2009/Hist2009_TRENDSITEDESC_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
