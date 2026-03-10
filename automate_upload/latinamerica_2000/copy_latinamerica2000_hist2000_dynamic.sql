-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2000/Hist2000_DYNAMIC.txt

\copy latinamerica_2000_hist2000_dynamic FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2000/Hist2000_DYNAMIC_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
