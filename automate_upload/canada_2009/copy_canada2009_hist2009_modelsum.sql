-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2009/Hist2009_MODELSUM.txt

\copy canada_2009_hist2009_modelsum FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2009/Hist2009_MODELSUM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
