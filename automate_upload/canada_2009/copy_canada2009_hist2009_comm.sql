-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2009/Hist2009_COMM.txt

\copy canada_2009_hist2009_comm FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2009/Hist2009_COMM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
