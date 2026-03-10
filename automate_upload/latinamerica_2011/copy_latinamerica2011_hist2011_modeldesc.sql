-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2011/Hist2011_MODELDESC.txt

\copy latinamerica_2011_hist2011_modeldesc FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2011/Hist2011_MODELDESC_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
