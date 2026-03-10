-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2005/Hist2005_SYSTEM.txt

\copy latinamerica_2005_hist2005_system FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2005/Hist2005_SYSTEM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
