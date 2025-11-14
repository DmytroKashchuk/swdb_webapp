-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2003/Hist2003_TRENDCOMM.txt

\copy usa_2003_hist2003_trendcomm FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2003/Hist2003_TRENDCOMM_utf8.txt' WITH (FORMAT csv, HEADER true);
