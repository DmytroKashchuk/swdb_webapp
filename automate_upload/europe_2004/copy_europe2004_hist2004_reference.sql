-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2004/Hist2004_REFERENCE.txt

\copy europe_2004_hist2004_reference FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2004/Hist2004_REFERENCE_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
