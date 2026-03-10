-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2012/Hist2012_PLS.txt

\copy europe_2012_hist2012_pls FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2012/Hist2012_PLS_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
