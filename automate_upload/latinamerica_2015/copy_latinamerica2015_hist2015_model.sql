-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2015/Hist2015_MODEL.txt

\copy latinamerica_2015_hist2015_model FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2015/Hist2015_MODEL_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
