-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2008/Hist2008_SYSTEM.txt

\copy latinamerica_2008_hist2008_system FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2008/Hist2008_SYSTEM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
