-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2004/Hist2004_DYNAMIC.txt

\copy latinamerica_2004_hist2004_dynamic FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2004/Hist2004_DYNAMIC_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
