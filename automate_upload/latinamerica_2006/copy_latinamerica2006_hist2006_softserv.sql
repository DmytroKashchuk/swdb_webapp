-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2006/Hist2006_SOFTSERV.txt

\copy latinamerica_2006_hist2006_softserv FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2006/Hist2006_SOFTSERV_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
