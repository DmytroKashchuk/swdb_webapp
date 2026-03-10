-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2005/Hist2005_TRENDCOMM.txt

\copy europe_2005_hist2005_trendcomm FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2005/Hist2005_TRENDCOMM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
