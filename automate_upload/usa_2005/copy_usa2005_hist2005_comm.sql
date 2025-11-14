-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2005/Hist2005_comm.txt

\copy usa_2005_hist2005_comm
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2005/Hist2005_comm_utf8.txt'
WITH (FORMAT csv, HEADER true);