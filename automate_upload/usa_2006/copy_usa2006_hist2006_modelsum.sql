-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2006/Hist2006_modelsum.txt

\copy usa_2006_hist2006_modelsum FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2006/Hist2006_modelsum_utf8.txt' WITH (FORMAT csv, HEADER true);
