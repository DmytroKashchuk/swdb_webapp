-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2008/Hist2008_MODELSUM.txt

\copy europe_2008_hist2008_modelsum FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2008/Hist2008_MODELSUM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
