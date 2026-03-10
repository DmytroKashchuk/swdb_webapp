-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2015/Hist2015_Technology.txt

\copy latinamerica_2015_hist2015_technology FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2015/Hist2015_Technology_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
