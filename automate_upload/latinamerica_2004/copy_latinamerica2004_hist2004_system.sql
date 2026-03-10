-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2004/Hist2004_SYSTEM.txt

\copy latinamerica_2004_hist2004_system FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2004/Hist2004_SYSTEM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
