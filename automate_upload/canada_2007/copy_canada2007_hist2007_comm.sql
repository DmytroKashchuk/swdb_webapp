-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2007/Hist2007_COMM.txt

\copy canada_2007_hist2007_comm FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2007/Hist2007_COMM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
