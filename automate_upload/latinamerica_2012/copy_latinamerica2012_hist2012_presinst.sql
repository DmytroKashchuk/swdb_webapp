-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2012/Hist2012_PRESINST.txt

\copy latinamerica_2012_hist2012_presinst FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2012/Hist2012_PRESINST_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
