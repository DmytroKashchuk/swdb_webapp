-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2013/Hist2013_Reference.txt

\copy europe_2013_hist2013_reference FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2013/Hist2013_Reference_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
