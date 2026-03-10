-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2000/Hist2000_MODELSUM.txt

\copy latinamerica_2000_hist2000_modelsum FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2000/Hist2000_MODELSUM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
