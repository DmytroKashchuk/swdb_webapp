-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2015/Hist2015_PLS.txt

\copy usa_2015_hist2015_pls
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2015/Hist2015_PLS_utf8.txt'
WITH (FORMAT csv, HEADER true);