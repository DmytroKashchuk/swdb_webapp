-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2001/Hist2001_MODELSUM.txt

\copy europe_2001_hist2001_modelsum FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2001/Hist2001_MODELSUM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
