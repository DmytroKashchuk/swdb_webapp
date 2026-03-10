-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2010/Hist2010_MODEL.txt

\copy latinamerica_2010_hist2010_model FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2010/Hist2010_MODEL_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
