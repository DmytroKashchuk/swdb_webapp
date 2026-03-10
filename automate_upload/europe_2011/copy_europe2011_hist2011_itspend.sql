-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2011/Hist2011_ITSPEND.txt

\copy europe_2011_hist2011_itspend FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2011/Hist2011_ITSPEND_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
