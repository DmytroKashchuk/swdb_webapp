-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2007/Hist2007_MODELSUM.txt

\copy europe_2007_hist2007_modelsum FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2007/Hist2007_MODELSUM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
