-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2013/Hist2013_ITSPEND.txt

\copy canada_2013_hist2013_itspend FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2013/Hist2013_ITSPEND_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
