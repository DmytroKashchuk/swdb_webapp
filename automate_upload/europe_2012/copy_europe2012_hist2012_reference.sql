-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2012/Hist2012_REFERENCE.txt

\copy europe_2012_hist2012_reference FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2012/Hist2012_REFERENCE_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
