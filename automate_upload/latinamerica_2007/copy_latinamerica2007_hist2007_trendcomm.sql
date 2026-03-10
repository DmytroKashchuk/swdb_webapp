-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2007/Hist2007_TRENDCOMM.txt

\copy latinamerica_2007_hist2007_trendcomm FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2007/Hist2007_TRENDCOMM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
